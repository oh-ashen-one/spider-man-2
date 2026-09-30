// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
#include "Life/WHLifeTraffic.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"

DEFINE_LOG_CATEGORY_STATIC(LogWHLife, Log, All);

using namespace WHLife;

namespace
{
	struct FTypeDef { const TCHAR* Name; float Len, Wid; bool bBig; };
	// src/world/npc/traffic.js VTYPES (real-world sizes of the Blender models)
	const FTypeDef GTypes[NumTypes] = {
		{TEXT("taxi"), 5.39f, 1.99f, false}, {TEXT("taxi_hy"), 4.54f, 1.76f, false}, {TEXT("taxi_mv"), 5.08f, 1.99f, false}, {TEXT("taxi_gr"), 4.86f, 1.84f, false},
		{TEXT("sedan"), 4.85f, 1.84f, false}, {TEXT("hatch"), 4.26f, 1.79f, false}, {TEXT("sedan2"), 4.9f, 1.85f, false}, {TEXT("cross"), 4.6f, 1.86f, false},
		{TEXT("suv"), 4.9f, 1.95f, false}, {TEXT("suv2"), 5.35f, 2.03f, false}, {TEXT("pickup"), 5.9f, 2.03f, false}, {TEXT("van"), 5.98f, 2.06f, false},
		{TEXT("truck"), 7.3f, 2.3f, true}, {TEXT("bus"), 12.2f, 2.55f, true}, {TEXT("tour"), 11.f, 2.55f, true} };
	enum ET : int32 { T_taxi, T_taxi_hy, T_taxi_mv, T_taxi_gr, T_sedan, T_hatch, T_sedan2, T_cross, T_suv, T_suv2, T_pickup, T_van, T_truck, T_bus, T_tour };

	// npc/traffic.js CAR_COLORS (sRGB hex; the browser converts with pow 2.2)
	const uint32 GCarColors[] = { 0x0e0e0f, 0x151517, 0x1b1c1f, 0x101418, 0xe2e2df, 0xd8d8d4, 0xcfcfca, 0xe6e3da, 0xa9adb1, 0x9c9fa3, 0xb7b9bb, 0x8e9296, 0x6d7074, 0x55585c, 0x44474b,
		0x1b2a4a, 0x223a63, 0x2f4c7a, 0x5a1216, 0x6e1a1a, 0x8a1f1f, 0xb3a98f, 0x9b8f75, 0x2c3d2e, 0x44563f, 0x6b86a0, 0x4a3a2c, 0x3b4450, 0x7c8a8f, 0x2a2d33 };
	const uint32 GLivery[] = { 0x0b0b0c, 0x0e0e10, 0x121315, 0x0d1014 };
	const uint32 GVan[] = { 0xd6d6d2, 0xcfccc4, 0xc9c9c7, 0xd9d7d0 };
	inline FLinearColor Lin(uint32 C) { return FLinearColor(FMath::Pow(((C >> 16) & 255) / 255.f, 2.2f), FMath::Pow(((C >> 8) & 255) / 255.f, 2.2f), FMath::Pow((C & 255) / 255.f, 2.2f)); }

	inline uint32 Xs(uint32& S) { S ^= S << 13; S ^= S >> 17; S ^= S << 5; return S; }
	inline float Ff(uint32& S) { return (Xs(S) & 0xFFFFFF) / 16777216.f; }

	const float DensityByKind[4] = { 31.f, 44.f, 20.f, 41.f }; // cars per km of lane: av, st, ws, dg (traffic.js DENSITY)
	constexpr float StopBack = 5.f;                            // roads.js STOP_BACK
	constexpr float CompDecel = 3.2f;

	float Idm(float V, float V0, float Gap, float VLead, float A, float B, float S0, float T)
	{
		const float Dv = V - VLead;
		const float SStar = S0 + FMath::Max(0.f, V * T + V * Dv / (2.f * FMath::Sqrt(A * B)));
		const float Free = 1.f - FMath::Pow(FMath::Max(V, 0.f) / FMath::Max(V0, 0.1f), 4.f);
		const float Inter = FMath::Square(SStar / FMath::Max(Gap, 0.15f));
		return FMath::Clamp(A * (Free - Inter), -9.f, A);
	}
}

AWHLifeTraffic::AWHLifeTraffic()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickGroup = TG_PrePhysics;
	USceneComponent* Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);
}

void AWHLifeTraffic::EndPlay(const EEndPlayReason::Type Reason)
{
	Super::EndPlay(Reason);
	bReady = false;
}

float AWHLifeTraffic::Frand(uint32& R) { return Ff(R); }

int32 AWHLifeTraffic::SigPhase(double T, int32 Axis)
{
	// props.js phase(): 40 s cycle. Axis 0 (avenue): green 0-22, amber 22-25, red 25-40. Axis 1 (street): red 0-26, green 26-37, amber 37-39, red 39-40. 2 green, 1 amber, 0 red.
	double C = FMath::Fmod(T, 40.0); if (C < 0.0) C += 40.0;
	if (Axis == 0) return C < 22.0 ? 2 : (C < 25.0 ? 1 : 0);
	return C < 26.0 ? 0 : (C < 37.0 ? 2 : (C < 39.0 ? 1 : 0));
}

FVector2D AWHLifeTraffic::ConnPos(const FConn& K, float S) const
{
	if (K.Poly.Num() < 2) return FVector2D::ZeroVector;
	S = FMath::Clamp(S, 0.f, K.Len);
	int32 I = 1; while (I < K.Cum.Num() - 1 && K.Cum[I] < S) ++I;
	const float Seg = FMath::Max(1e-4f, K.Cum[I] - K.Cum[I - 1]);
	return FMath::Lerp(K.Poly[I - 1], K.Poly[I], FMath::Clamp((S - K.Cum[I - 1]) / Seg, 0.f, 1.f));
}

// point `Behind` metres behind the car's front along its path (link -> connector -> link)
FVector2D AWHLifeTraffic::PathPoint(const FCar& C, float Behind) const
{
	float Q = C.S - Behind;
	if (C.Where == 2)
	{
		if (Q >= 0.f) { const FLink& L = Links[C.L1]; return LinkPos(L, FMath::Min(Q, L.Len)); }
		const FConn& K = Conns[C.K]; Q += K.Len;
		if (Q >= 0.f) return ConnPos(K, Q);
		const FLink& L0 = Links[C.L0]; Q += L0.Len; return LinkPos(L0, FMath::Max(0.f, Q));
	}
	if (C.Where == 1)
	{
		const FConn& K = Conns[C.K];
		if (Q >= 0.f) return ConnPos(K, Q);
		const FLink& L0 = Links[C.L0]; Q += L0.Len; return LinkPos(L0, FMath::Max(0.f, Q));
	}
	const FLink& L = Links[C.L0];
	return L.A + L.D * FMath::Max(0.f, Q); // on the link: the rear is behind the start only for a fresh spawn (clamped)
}

// ------------------------------------------------------------------------------------------------ data
void AWHLifeTraffic::ParseLanes()
{
	Links.Reset(); Conns.Reset(); LinkIdx.Reset();
	TMap<int32, int32> ConnIdx;
	TArray<FString> Lines; LaneData.ParseIntoArrayLines(Lines);
	TArray<TArray<int32>> Xdefs;
	for (const FString& Ln : Lines)
	{
		if (Ln.IsEmpty() || Ln[0] == '#') continue;
		TArray<FString> P; Ln.ParseIntoArray(P, TEXT(" "), true);
		if (P.Num() < 2) continue;
		auto F = [&P](int32 I) { return I < P.Num() ? FCString::Atof(*P[I]) : 0.f; };
		auto N = [&P](int32 I) { return I < P.Num() ? FCString::Atoi(*P[I]) : 0; };
		if (P[0] == TEXT("L") && P.Num() >= 15)
		{
			FLink L; L.Id = N(1); L.From = N(2); L.To = N(3);
			L.A = FVector2D(F(4), F(5)); L.D = FVector2D(F(6), F(7)); L.Len = F(8);
			L.Kind = N(9); L.Lane = N(10); L.Axis = N(11); L.bSig = N(12) != 0; L.bNoPark = N(13) != 0; L.bNarrow = N(14) != 0;
			for (int32 I = 15; I < P.Num(); ++I) L.ParkSides.Add(F(I));
			LinkIdx.Add(L.Id, Links.Num()); Links.Add(MoveTemp(L));
		}
		else if (P[0] == TEXT("C") && P.Num() >= 7)
		{
			FConn K; K.Id = N(1); K.FromLink = N(2); K.ToLink = N(3); K.Turn = N(4); K.Len = F(5);
			const int32 Np = N(6);
			for (int32 I = 0; I < Np && 7 + 2 * I + 1 < P.Num(); ++I) K.Poly.Add(FVector2D(F(7 + 2 * I), F(8 + 2 * I)));
			K.Cum.Add(0.f);
			for (int32 I = 1; I < K.Poly.Num(); ++I) K.Cum.Add(K.Cum.Last() + (K.Poly[I] - K.Poly[I - 1]).Size());
			if (K.Cum.Num() > 1) K.Len = K.Cum.Last();
			ConnIdx.Add(K.Id, Conns.Num()); Conns.Add(MoveTemp(K));
		}
		else if (P[0] == TEXT("X") && P.Num() >= 3)
		{
			TArray<int32> D; for (int32 I = 1; I < P.Num(); ++I) D.Add(N(I)); Xdefs.Add(MoveTemp(D));
		}
	}
	for (FConn& K : Conns)
	{
		const int32* A = LinkIdx.Find(K.FromLink); const int32* B = LinkIdx.Find(K.ToLink);
		K.FromLink = A ? *A : -1; K.ToLink = B ? *B : -1;
	}
	for (const TArray<int32>& D : Xdefs)
	{
		const int32* Ci = ConnIdx.Find(D[0]); if (!Ci) continue;
		for (int32 J = 1; J < D.Num(); ++J) if (const int32* Cj = ConnIdx.Find(D[J])) Conns[*Ci].Conflicts.Add(*Cj);
	}
	for (int32 I = 0; I < Conns.Num(); ++I)
	{
		if (Conns[I].FromLink < 0 || Conns[I].ToLink < 0) continue;
		Links[Conns[I].FromLink].Outs.Add(I); Links[Conns[I].ToLink].Ins.Add(I);
	}
	for (FLink& L : Links) L.bEntry = L.Ins.Num() == 0;
	int32 NEntry = 0, NExit = 0; for (const FLink& L : Links) { NEntry += L.bEntry; NExit += L.Outs.Num() == 0; }
	UE_LOG(LogWHLife, Log, TEXT("[life] lanes: %d links, %d connectors, %d entries, %d exits"), Links.Num(), Conns.Num(), NEntry, NExit);
}

void AWHLifeTraffic::BuildComponents()
{
	MovingISM.Reset(); ParkedISM.Reset(); FreeInst.SetNum(NumTypes); Xf.SetNum(NumTypes); HighWater.Init(0, NumTypes); Dirty.Init(false, NumTypes);
	for (int32 T = 0; T < NumTypes; ++T)
	{
		UStaticMesh* M = VehicleMeshes.IsValidIndex(T) ? VehicleMeshes[T].Get() : nullptr;
		for (int32 Pass = 0; Pass < 2; ++Pass)
		{
			UInstancedStaticMeshComponent* C = NewObject<UInstancedStaticMeshComponent>(this, *FString::Printf(TEXT("%s_%s"), Pass ? TEXT("Parked") : TEXT("Moving"), GTypes[T].Name));
			C->SetupAttachment(GetRootComponent());
			C->SetStaticMesh(M);
			if (VehicleMaterial) { for (int32 S = 0; S < (M ? M->GetStaticMaterials().Num() : 1); ++S) C->SetMaterial(S, VehicleMaterial); }
			C->SetMobility(Pass ? EComponentMobility::Static : EComponentMobility::Movable);
			C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
			C->SetCanEverAffectNavigation(false);
			C->SetGenerateOverlapEvents(false);
			C->SetCastShadow(bCastShadows);
			C->SetVisibleInRayTracing(bVisibleInRayTracing);
			C->bAffectDistanceFieldLighting = false;
			C->NumCustomDataFloats = 4;
			C->SetCullDistances(FMath::RoundToInt(CullDistance * 0.85f), FMath::RoundToInt(CullDistance));
			C->RegisterComponent();
			(Pass ? ParkedISM : MovingISM).Add(C);
		}
	}
}

void AWHLifeTraffic::PlaceParked()
{
	NumParked = 0; NumParkedTaxis = 0; ParkedPts.Reset(); ParkedTypes.Reset();
	TArray<FString> Lines; ParkedData.ParseIntoArrayLines(Lines);
	TArray<TArray<FTransform>> Tx; Tx.SetNum(NumTypes);
	TArray<TArray<float>> Cd; Cd.SetNum(NumTypes);
	for (const FString& Ln : Lines)
	{
		if (Ln.IsEmpty() || Ln[0] == '#') continue;
		TArray<FString> P; Ln.ParseIntoArray(P, TEXT(" "), true);
		if (P.Num() < 7) continue;
		const int32 T = FCString::Atoi(*P[0]); if (T < 0 || T >= NumTypes) continue;
		const float X = FCString::Atof(*P[1]) * 100.f, Y = FCString::Atof(*P[2]) * 100.f, Yaw = FCString::Atof(*P[3]);
		Tx[T].Add(FTransform(FRotator(0.f, Yaw, 0.f), FVector(X, Y, 1.f)));
		ParkedPts.Add(FVector(X, Y, 80.f)); ParkedTypes.Add(T);
		Cd[T].Append({ FCString::Atof(*P[4]), FCString::Atof(*P[5]), FCString::Atof(*P[6]), P.Num() > 7 ? FCString::Atof(*P[7]) : 0.f });
		++NumParked; if (T <= T_taxi_gr) ++NumParkedTaxis;
	}
	for (int32 T = 0; T < NumTypes; ++T)
	{
		if (Tx[T].Num() == 0 || !ParkedISM.IsValidIndex(T)) continue;
		UInstancedStaticMeshComponent* C = ParkedISM[T];
		C->AddInstances(Tx[T], false, true, false);
		C->SetCustomData(0, Tx[T].Num() - 1, Cd[T], false);
		C->MarkRenderStateDirty();
	}
}

int32 AWHLifeTraffic::PickType(const FLink& L, uint32& R) const
{
	const bool bBig = L.Kind != 1 && L.Lane == 1;
	float r = Ff(R);
	if (bBig && r < 0.07f) return T_bus;
	if (bBig && r < 0.09f) return T_tour;
	r = Ff(R);
	if (r < 0.13f) return T_truck; if (r < 0.21f) return T_van; if (r < 0.28f) return T_taxi_hy; if (r < 0.34f) return T_taxi_mv;
	if (r < 0.41f) return T_taxi_gr; if (r < 0.44f) return T_taxi; if (r < 0.52f) return T_sedan; if (r < 0.60f) return T_sedan2;
	if (r < 0.66f) return T_hatch; if (r < 0.74f) return T_suv; if (r < 0.82f) return T_cross; if (r < 0.93f) return T_suv2;
	return T_pickup;
}

FLinearColor AWHLifeTraffic::PickColor(int32 T, uint32& R) const
{
	const float r = Ff(R);
	if (T == T_taxi_gr) return r < 0.3f ? Lin(0x9aae4c) : Lin(0xf5a900);
	if (T <= T_taxi_gr) return Lin(0xf5a900);
	if ((T == T_suv2 && r < 0.7f) || (T == T_sedan2 && r < 0.4f) || (T == T_suv && r < 0.3f)) return Lin(GLivery[FMath::FloorToInt(r * 97.f) % 4]);
	if (T == T_truck || T == T_van) return Lin(GVan[FMath::FloorToInt(r * 4.f) % 4]);
	if (T == T_tour) return Lin(0xb3121a);
	if (T == T_bus) return Lin(0xe4e4e0);
	return Lin(GCarColors[FMath::FloorToInt(r * UE_ARRAY_COUNT(GCarColors)) % UE_ARRAY_COUNT(GCarColors)]);
}

// ------------------------------------------------------------------------------------------------ lifecycle
void AWHLifeTraffic::BeginPlay()
{
	Super::BeginPlay();
	FParse::Value(FCommandLine::Get(), TEXT("WHLifeStats="), StatsInterval);
	if (FParse::Param(FCommandLine::Get(), TEXT("WHLifeRT"))) bVisibleInRayTracing = true;
	if (FParse::Param(FCommandLine::Get(), TEXT("WHLifeNoShadow"))) bCastShadows = false;
	if (FParse::Param(FCommandLine::Get(), TEXT("WHLifeOff")) || FParse::Param(FCommandLine::Get(), TEXT("WHTrafficOff"))) { UE_LOG(LogWHLife, Display, TEXT("[life] traffic disabled by command line")); return; }
	GlobalRng = 0x9E3779B9u * (uint32)(Seed + 1);
	ParseLanes();
	if (Links.Num() == 0) { UE_LOG(LogWHLife, Warning, TEXT("[life] no lane data")); return; }
	BuildComponents();
	PlaceParked();
	Cars.SetNum(MaxCars + 8);
	FreeCars.Reset(); for (int32 I = Cars.Num() - 1; I >= 0; --I) FreeCars.Add(I);
	SimClock = 3.0 + Ff(GlobalRng) * 30.0;
	if (bSimulate)
	{
		PopulateInitial();
		const float Step = 0.1f; const int32 N = FMath::RoundToInt(PreRollSeconds / Step);
		for (int32 I = 0; I < N; ++I) StepSim(Step);
	}
	bReady = true;
	PushInstances();
	UE_LOG(LogWHLife, Log, TEXT("[life] BeginPlay: %d moving, %d parked (%d taxis) instances, pre-roll %.0f s"), NumMoving, NumParked, NumParkedTaxis, PreRollSeconds);
}

void AWHLifeTraffic::Tick(float Dt)
{
	Super::Tick(Dt);
	if (!bReady || !bSimulate) return;
	const double T0 = FPlatformTime::Seconds();
	Accum += FMath::Min(Dt, 0.1f);
	const float Step = 1.f / 30.f;
	int32 Guard = 0;
	while (Accum >= Step && Guard++ < 4) { StepSim(Step); Accum -= Step; }
	const double T1 = FPlatformTime::Seconds();
	PushInstances();
	const double T2 = FPlatformTime::Seconds();
	LastSimMs = (T1 - T0) * 1000.f; LastPushMs = (T2 - T1) * 1000.f;
	if (StatsInterval > 0.f) { StatsT += Dt; if (StatsT >= StatsInterval) { StatsT = 0.f; UE_LOG(LogWHLife, Log, TEXT("%s"), *StatsString()); } }
}

void AWHLifeTraffic::DumpCars(const FString& Path) const
{
	FString Out = TEXT("x,z,v,link,where,type,reserved,wait,acc\n");
	for (const FCar& C : Cars)
	{
		if (!C.bActive) continue;
		const FVector2D P = PathPoint(C, C.Len * 0.5f);
		const int32 LinkId = C.Where == 2 ? Links[C.L1].Id : Links[C.L0].Id;
		Out += FString::Printf(TEXT("%.2f,%.2f,%.2f,%d,%d,%d,%d,%.1f,%.2f\n"), P.X, P.Y, C.V, LinkId, (int32)C.Where, C.Type, C.bReserved ? 1 : 0, C.WaitT, C.Acc);
	}
	FFileHelper::SaveStringToFile(Out, *Path);
}

FString AWHLifeTraffic::StatsString() const
{
	return FString::Printf(TEXT("[life] moving %d (stopped %d) parked %d (taxis %d) sim %.2f ms push %.2f ms clock %.1f"), NumMoving, NumStopped, NumParked, NumParkedTaxis, LastSimMs, LastPushMs, SimClock);
}

void AWHLifeTraffic::GetPoints(TArray<FVector>& Moving, TArray<int32>& MovingType, TArray<FVector>& Parked, TArray<int32>& ParkedType) const
{
	Moving.Reset(); MovingType.Reset();
	for (const FCar& C : Cars)
	{
		if (!C.bActive) continue;
		const FVector2D P = PathPoint(C, C.Len * 0.5f);
		Moving.Add(FVector(P.X * 100.f, P.Y * 100.f, 80.f)); MovingType.Add(C.Type);
	}
	Parked = ParkedPts; ParkedType = ParkedTypes;
}

int32 AWHLifeTraffic::CountInCone(FVector Eye, FVector Forward, float HalfAngleDeg, float Range) const
{
	int32 N = 0; const FVector F = Forward.GetSafeNormal(); const float CosA = FMath::Cos(FMath::DegreesToRadians(HalfAngleDeg));
	for (const FCar& C : Cars)
	{
		if (!C.bActive) continue;
		const FVector2D P = PathPoint(C, C.Len * 0.5f); const FVector W(P.X * 100.f, P.Y * 100.f, 80.f);
		const FVector D = W - Eye; const float Dist = D.Size();
		if (Dist < Range && Dist > 100.f && FVector::DotProduct(D / Dist, F) > CosA) ++N;
	}
	return N;
}

// ------------------------------------------------------------------------------------------------ spawning
int32 AWHLifeTraffic::SpawnCar(int32 LinkI, float Front, float V, bool)
{
	if (FreeCars.Num() == 0) return -1;
	const FLink& L = Links[LinkI];
	uint32 R = Xs(GlobalRng) ^ (uint32)(LinkI * 7919 + 13);
	if (R == 0) R = 1;
	const int32 T = PickType(L, R);
	const int32 CI = FreeCars.Pop();
	FCar& C = Cars[CI]; C = FCar();
	C.bActive = true; C.Type = T; C.Len = GTypes[T].Len; C.Wid = GTypes[T].Wid; C.Rng = R;
	C.V0 = (L.Kind == 1 ? 9.f : 12.5f) + Ff(C.Rng) * 3.5f; C.V = FMath::Min(V, C.V0);
	C.DA = 1.6f + Ff(C.Rng) * 0.8f; C.DTH = 0.8f + Ff(C.Rng) * 0.6f; C.DS0 = 1.5f + Ff(C.Rng);
	C.Lat = (Ff(C.Rng) < 0.25f ? 0.3f : 0.1f) * (Ff(C.Rng) < 0.5f ? -1.f : 1.f);
	C.Color = PickColor(T, C.Rng);
	C.L0 = LinkI; C.Where = 0; C.S = FMath::Max(Front, C.Len + 1.f); C.K = -1;
	C.K = ChooseNext(C, L);
	// instance slot
	int32 Slot;
	if (FreeInst[T].Num() > 0) Slot = FreeInst[T].Pop();
	else
	{
		Slot = HighWater[T]++;
		const FTransform Hidden(FRotator::ZeroRotator, FVector(0, 0, -1e6), FVector::ZeroVector);
		MovingISM[T]->AddInstance(Hidden, true);
		Xf[T].Add(Hidden);
	}
	C.Inst = Slot;
	const float CD[4] = { C.Color.R, C.Color.G, C.Color.B, 0.f };
	MovingISM[T]->SetCustomData(Slot, TConstArrayView<float>(CD, 4), false);
	Dirty[T] = true;
	return CI;
}

void AWHLifeTraffic::DespawnCar(int32 CI)
{
	FCar& C = Cars[CI]; if (!C.bActive) return;
	Release(C, CI);
	if (C.Inst >= 0) { Xf[C.Type][C.Inst] = FTransform(FRotator::ZeroRotator, FVector(0, 0, -5000.f), FVector(0.001f)); FreeInst[C.Type].Add(C.Inst); Dirty[C.Type] = true; }
	C.bActive = false; C.Inst = -1; FreeCars.Add(CI);
}

void AWHLifeTraffic::PopulateInitial()
{
	for (int32 LI = 0; LI < Links.Num(); ++LI)
	{
		FLink& L = Links[LI];
		uint32 R = 0x51ED27u ^ (uint32)(L.Id * 2654435761u); if (!R) R = 1;
		const float Target = L.Len / 1000.f * DensityByKind[FMath::Clamp(L.Kind, 0, 3)] * DensityScale * (0.8f + 0.4f * Ff(R));
		const int32 N = FMath::RoundToInt(Target + Ff(R) - 0.5f);
		TArray<float> Placed;
		for (int32 K = 0; K < N; ++K)
		{
			for (int32 Try = 0; Try < 12; ++Try)
			{
				const float S = 8.f + Ff(R) * FMath::Max(1.f, L.Len - 12.f);
				bool bOk = true; for (float P : Placed) if (FMath::Abs(P - S) < 14.f) { bOk = false; break; }
				if (!bOk) continue;
				const int32 CI = SpawnCar(LI, S, 6.f + Ff(R) * 6.f, true);
				if (CI >= 0) Placed.Add(S);
				break;
			}
		}
		L.NextSpawn = (float)SimClock + 0.5f + Ff(R) * 3.f;
	}
}

int32 AWHLifeTraffic::ChooseNext(FCar& C, const FLink& L)
{
	if (L.Outs.Num() == 0) return -1;
	float Tot = 0.f; TArray<float, TInlineAllocator<8>> W;
	const bool bBig = GTypes[C.Type].bBig;
	for (int32 KI : L.Outs)
	{
		const FConn& K = Conns[KI];
		float X = K.Turn == 0 ? 0.66f : (bBig && K.Turn == 1 ? 0.02f : 0.17f);
		// drivers avoid an out link that is backed up to the corner
		const FLink& N = Links[K.ToLink];
		if (N.Cars.Num() > 0) { const FCar& Q = Cars[N.Cars[0]]; const float Tail = Q.S - Q.Len; if (Tail < C.Len + 8.f) X *= 0.08f + 0.92f * FMath::Max(0.f, Tail) / (C.Len + 8.f); }
		W.Add(X); Tot += X;
	}
	float R = Ff(C.Rng) * Tot;
	for (int32 I = 0; I < W.Num(); ++I) { R -= W[I]; if (R <= 0.f) return L.Outs[I]; }
	return L.Outs.Last();
}

// ------------------------------------------------------------------------------------------------ junction control
void AWHLifeTraffic::Release(FCar& C, int32 CI)
{
	if (!C.bReserved) return;
	if (C.K >= 0) Conns[C.K].Reserved.RemoveSingleSwap(CI);
	C.bReserved = false;
}

bool AWHLifeTraffic::CanClear(const FCar& C, const FLink& L) const
{
	// amber: a car that can stop comfortably at the line must; otherwise it goes on
	const float D = (L.Len - StopBack) - C.S;
	return !(D > C.V * C.V / (2.f * CompDecel) + 0.5f);
}

bool AWHLifeTraffic::TryReserve(FCar& C)
{
	// (find our own id) cars are addressed by index; C is a reference into Cars
	const int32 Me = (int32)(&C - Cars.GetData());
	if (C.K < 0) return true;
	FConn& K = Conns[C.K];
	if (K.Reserved.Contains(Me)) { C.bReserved = true; return true; }
	for (int32 Kc : K.Conflicts) if (Conns[Kc].Reserved.Num() > 0) return false;
	// exit space on the out link (whole car + margin + the cars already committed to this connector)
	const FLink& Out = Links[K.ToLink];
	float Space = 1e9f;
	if (Out.Cars.Num() > 0) { const FCar& Q = Cars[Out.Cars[0]]; Space = Q.S - Q.Len; }
	float Need = C.Len + 2.5f;
	for (int32 Id : K.Reserved) { const FCar& Q = Cars[Id]; if (Q.Where < 2) Need += Q.Len + 2.f; }
	if (Space < Need) return false;
	// left turns give way to oncoming traffic that is close to the box and moving (patience 9 s)
	if (K.Turn == 1 && C.WaitT < 9.f)
	{
		for (int32 Kc : K.Conflicts)
		{
			const FConn& X = Conns[Kc]; if (X.Turn == 1) continue;
			const FLink& Src = Links[X.FromLink];
			for (int32 Oi : Src.Cars)
			{
				const FCar& Q = Cars[Oi]; if (Q.Where != 0 || Q.bReserved) continue;
				if (Src.Len - Q.S < 24.f && Q.V > 2.5f) return false;
			}
		}
	}
	K.Reserved.Add(Me); C.bReserved = true; return true;
}

// ------------------------------------------------------------------------------------------------ leader search
void AWHLifeTraffic::FindLeader(int32 CI, float& Gap, float& VLead)
{
	const FCar& C = Cars[CI];
	Gap = 1e9f; VLead = C.V;
	auto Consider = [&](float G, float V) { if (G < Gap) { Gap = G; VLead = V; } };
	if (C.Where == 1)
	{
		const FConn& K = Conns[C.K];
		for (int32 Oi : K.Cars) { if (Oi == CI) continue; const FCar& Q = Cars[Oi]; if (Q.S > C.S) Consider(Q.S - Q.Len - C.S, Q.V); }
		if (Gap > 1e8f && K.ToLink >= 0)
		{
			const FLink& Out = Links[K.ToLink];
			if (Out.Cars.Num() > 0) { const FCar& Q = Cars[Out.Cars[0]]; Consider(K.Len - C.S + (Q.S - Q.Len), Q.V); }
		}
		return;
	}
	const int32 LI = C.Where == 0 ? C.L0 : C.L1;
	const FLink& L = Links[LI];
	for (int32 Oi : L.Cars) { if (Oi == CI) continue; const FCar& Q = Cars[Oi]; if (Q.S > C.S) { Consider(Q.S - Q.Len - C.S, Q.V); break; } }
	if (C.Where == 0)
	{
		// cars whose front is already in the box but whose rear is still on this link
		for (int32 KI : L.Outs)
			for (int32 Oi : Conns[KI].Cars)
			{
				if (Oi == CI) continue; const FCar& Q = Cars[Oi];
				if (Q.S < Q.Len) Consider(L.Len + (Q.S - Q.Len) - C.S, Q.V);
			}
		if (Gap > 1e8f && C.K >= 0)
		{
			const FConn& K = Conns[C.K]; const float Base = L.Len - C.S;
			for (int32 Oi : K.Cars) { const FCar& Q = Cars[Oi]; Consider(Base + (Q.S - Q.Len), Q.V); }
			if (Gap > 1e8f)
			{
				const FLink& Out = Links[K.ToLink];
				if (Out.Cars.Num() > 0) { const FCar& Q = Cars[Out.Cars[0]]; Consider(Base + K.Len + (Q.S - Q.Len), Q.V); }
			}
		}
	}
}

// ------------------------------------------------------------------------------------------------ the step
void AWHLifeTraffic::StepSim(float Dt)
{
	SimClock += Dt;
	const double Clock = SimClock + SignalOffset;
	// 1. per-link / per-connector lists (front on it), ascending S
	for (FLink& L : Links) L.Cars.Reset();
	for (FConn& K : Conns) K.Cars.Reset();
	for (int32 I = 0; I < Cars.Num(); ++I)
	{
		const FCar& C = Cars[I]; if (!C.bActive) continue;
		if (C.Where == 0) Links[C.L0].Cars.Add(I); else if (C.Where == 1) Conns[C.K].Cars.Add(I); else Links[C.L1].Cars.Add(I);
	}
	for (FLink& L : Links) L.Cars.Sort([this](int32 A, int32 B) { return Cars[A].S < Cars[B].S; });
	for (FConn& K : Conns) K.Cars.Sort([this](int32 A, int32 B) { return Cars[A].S < Cars[B].S; });

	// 2. accelerations
	NumStopped = 0;
	for (int32 I = 0; I < Cars.Num(); ++I)
	{
		FCar& C = Cars[I]; if (!C.bActive) continue;
		float Gap, VL; FindLeader(I, Gap, VL);
		float V0 = C.V0, Acc;
		float StopGap = 1e9f;
		if (C.Where == 0)
		{
			const FLink& L = Links[C.L0]; const float ToEnd = L.Len - C.S;
			if (C.K < 0 && L.Outs.Num() > 0) C.K = ChooseNext(C, L);
			if (C.K >= 0)
			{
				const FConn& K = Conns[C.K];
				const float Vt = K.Turn == 0 ? 1e9f : (K.Turn == 1 ? 5.5f : 4.5f);
				if (Vt < C.V + 3.f && ToEnd < 60.f) { const float G2 = FMath::Max(0.3f, ToEnd - 0.5f); if (C.V > Vt && G2 < Gap) { Gap = G2; VL = Vt; } }
				if (L.bSig && C.S < L.Len - StopBack - 0.25f)
				{
					const int32 Ph = SigPhase(Clock, L.Axis);
					if (Ph == 0 || (Ph == 1 && !CanClear(C, L))) StopGap = (L.Len - StopBack) - C.S;
				}
				if (StopGap > 1e8f && !C.bReserved)
				{
					const float Look = 7.f + C.V * C.V / 6.f;
					if (ToEnd < Look && !TryReserve(C)) StopGap = FMath::Max(0.f, ToEnd - 0.4f);
				}
			}
		}
		else if (C.Where == 1)
		{
			const FConn& K = Conns[C.K];
			V0 = FMath::Min(V0, K.Turn == 0 ? V0 : (K.Turn == 1 ? 6.f : 4.8f));
		}
		Acc = Idm(C.V, V0, Gap, VL, C.DA, 3.2f, C.DS0, C.DTH);
		if (StopGap < 1e8f)
		{
			const float G = FMath::Max(0.05f, StopGap + C.DS0 * 0.75f - 0.2f);
			Acc = FMath::Min(Acc, Idm(C.V, V0, G, 0.f, C.DA, 3.2f, C.DS0, C.DTH));
			if (C.V < 0.3f) C.WaitT += Dt;
		}
		else if (C.V > 0.5f) C.WaitT = 0.f;
		if (C.V < 0.2f) { NumStopped++; C.StuckT += Dt; } else C.StuckT = 0.f;
		C.Acc = Acc;
		C.Brake = (Acc < -0.7f || (C.V < 0.4f && (StopGap < 1e8f || Gap < 8.f))) ? 1 : 0;
	}

	// 3. integrate + transitions
	for (int32 I = 0; I < Cars.Num(); ++I)
	{
		FCar& C = Cars[I]; if (!C.bActive) continue;
		C.Age += Dt;
		float NV = C.V + C.Acc * Dt;
		if (NV < 0.f) { NV = 0.f; }
		const float DS = 0.5f * (C.V + NV) * Dt;
		C.V = NV; C.S += DS;
		if (C.Where == 0)
		{
			const FLink& L = Links[C.L0];
			if (C.S >= L.Len)
			{
				if (C.K < 0) { DespawnCar(I); continue; }
				if (!C.bReserved) { Conns[C.K].Reserved.Add(I); C.bReserved = true; } // overshoot safety
				C.S -= L.Len; C.Where = 1;
			}
		}
		if (C.Where == 1)
		{
			const FConn& K = Conns[C.K];
			if (C.S >= K.Len) { C.S -= K.Len; C.Where = 2; C.L1 = K.ToLink; }
		}
		if (C.Where == 2 && C.S >= C.Len)
		{
			Release(C, I);
			C.L0 = C.L1; C.L1 = -1; C.K = -1; C.Where = 0;
			C.K = ChooseNext(C, Links[C.L0]);
		}
		if (C.StuckT > 120.f) { DespawnCar(I); }
	}

	// 4. inflow at the region boundary
	int32 Alive = 0; for (const FCar& C : Cars) Alive += C.bActive;
	for (int32 LI = 0; LI < Links.Num(); ++LI)
	{
		FLink& L = Links[LI];
		if (!L.bEntry || Clock < 0 || (float)SimClock < L.NextSpawn || Alive >= MaxCars) continue;
		{ // inflow only tops the link up to the browser's steady-state density (traffic.js linkTarget), so cross streets do not fill with standing queues
			const float Target = L.Len / 1000.f * DensityByKind[FMath::Clamp(L.Kind, 0, 3)] * DensityScale;
			if ((float)L.Cars.Num() >= Target) { L.NextSpawn = (float)SimClock + 1.5f; continue; }
		}
		float Tail = 1e9f; for (int32 Oi : L.Cars) { const FCar& Q = Cars[Oi]; Tail = FMath::Min(Tail, Q.S - Q.Len); }
		uint32 R = Xs(GlobalRng);
		const float Gap = 4.f + Ff(R) * 10.f;
		if (Tail > 6.f + Gap)
		{
			const int32 CI = SpawnCar(LI, 6.f, 9.f, true);
			if (CI >= 0) { ++Alive; L.Cars.Add(CI); }
		}
		const float Flow = FMath::Max(0.05f, DensityByKind[FMath::Clamp(L.Kind, 0, 3)] * DensityScale * (L.Kind == 1 ? 9.f : 12.f) / 1000.f); // veh/s
		L.NextSpawn = (float)SimClock + (0.5f + Ff(R)) / Flow;
	}
	NumMoving = Alive;
}

// ------------------------------------------------------------------------------------------------ render push
void AWHLifeTraffic::PushInstances()
{
	for (int32 I = 0; I < Cars.Num(); ++I)
	{
		FCar& C = Cars[I]; if (!C.bActive || C.Inst < 0) continue;
		const FVector2D PF = PathPoint(C, 0.9f), PR = PathPoint(C, C.Len - 0.9f);
		FVector2D Ctr = (PF + PR) * 0.5f, Dir = PF - PR;
		if (Dir.SizeSquared() < 1e-6f) Dir = FVector2D(1, 0);
		Dir.Normalize();
		if (C.Where == 0) { Ctr += FVector2D(-Dir.Y, Dir.X) * C.Lat; }
		const float Yaw = FMath::RadiansToDegrees(FMath::Atan2(Dir.Y, Dir.X));
		const float Pitch = C.Brake && C.V > 1.f ? 0.6f : 0.f;
		Xf[C.Type][C.Inst] = FTransform(FRotator(Pitch, Yaw, 0.f), FVector(Ctr.X * 100.f, Ctr.Y * 100.f, 1.f));
		// brake-light state changes are rare: only write custom data when it differs from the ISM copy
		UInstancedStaticMeshComponent* M = MovingISM[C.Type];
		const int32 Idx = C.Inst * 4 + 3;
		if (M->PerInstanceSMCustomData.IsValidIndex(Idx) && M->PerInstanceSMCustomData[Idx] != (float)C.Brake)
		{
			const float CD[4] = { C.Color.R, C.Color.G, C.Color.B, (float)C.Brake };
			M->SetCustomData(C.Inst, TConstArrayView<float>(CD, 4), false); Dirty[C.Type] = true;
		}
	}
	for (int32 T = 0; T < NumTypes; ++T)
	{
		if (HighWater[T] == 0 || !MovingISM.IsValidIndex(T)) continue;
		MovingISM[T]->BatchUpdateInstancesTransforms(0, Xf[T], true, true, false);
		Dirty[T] = false;
	}
}
