// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
#include "Life/WHLifeCrowd.h"
#include "Life/WHLifeTraffic.h"
#include "Characters/WHCharAnimInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Animation/AnimInstance.h"
#include "Camera/PlayerCameraManager.h"
#include "Kismet/GameplayStatics.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

DEFINE_LOG_CATEGORY_STATIC(LogWHCrowd, Log, All);
using namespace WHLife;

namespace
{
	inline uint32 Xs(uint32& S) { S ^= S << 13; S ^= S >> 17; S ^= S << 5; return S; }
	inline float Ff(uint32& S) { return (Xs(S) & 0xFFFFFF) / 16777216.f; }
	inline float WrapPi(float A) { while (A > PI) A -= 2.f * PI; while (A < -PI) A += 2.f * PI; return A; }
	constexpr float CrossSpeed = 1.35f;   // m/s on a crosswalk
	int32 Gcd(int32 A, int32 B) { return B ? Gcd(B, A % B) : A; }
}

AWHLifeCrowd::AWHLifeCrowd()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickGroup = TG_PrePhysics;
	SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
}

double AWHLifeCrowd::SignalClock() const { return Traffic ? Traffic->GetSignalClock() : Clock; }

FVector AWHLifeCrowd::CameraLocation() const
{
	if (!FocusOverride.IsNearlyZero()) return FocusOverride;
	if (UWorld* W = GetWorld()) if (APlayerCameraManager* CM = UGameplayStatics::GetPlayerCameraManager(W, 0)) return CM->GetCameraLocation();
	return GetActorLocation();
}

void AWHLifeCrowd::ParseWalk()
{
	Pts.Reset(); Edges.Reset(); Adj.Reset();
	TArray<FString> Lines; WalkData.ParseIntoArrayLines(Lines);
	for (const FString& Ln : Lines)
	{
		if (Ln.IsEmpty() || Ln[0] == '#') continue;
		TArray<FString> P; Ln.ParseIntoArray(P, TEXT(" "), true);
		if (P[0] == TEXT("P") && P.Num() >= 4) Pts.Add(FVector2D(FCString::Atof(*P[2]), FCString::Atof(*P[3])));
		else if (P[0] == TEXT("E") && P.Num() >= 7)
		{
			FEdge E; E.A = FCString::Atoi(*P[2]); E.B = FCString::Atoi(*P[3]); E.Kind = FCString::Atoi(*P[4]); E.Axis = FCString::Atoi(*P[5]); E.Len = FCString::Atof(*P[6]);
			Edges.Add(E);
		}
	}
	Adj.SetNum(Pts.Num());
	for (int32 I = 0; I < Edges.Num(); ++I)
	{
		FEdge& E = Edges[I];
		if (!Pts.IsValidIndex(E.A) || !Pts.IsValidIndex(E.B)) { E.Len = 0.f; continue; }
		const FVector2D D = Pts[E.B] - Pts[E.A]; E.Len = D.Size(); E.U = E.Len > 1e-3f ? D / E.Len : FVector2D(1, 0);
		Adj[E.A].Add(I); Adj[E.B].Add(I);
	}
	UE_LOG(LogWHCrowd, Log, TEXT("[crowd] walk graph: %d corners, %d edges"), Pts.Num(), Edges.Num());
}

void AWHLifeCrowd::Populate()
{
	Walkers.Reset();
	const int32 M = FMath::Max(1, Meshes.Num());
	int32 Step = 7; while (Gcd(Step, M) != 1) ++Step;
	uint32 R = 0xC0FFEE ^ (uint32)(Seed * 2654435761u); if (!R) R = 1;
	int32 Counter = 0;
	for (int32 EI = 0; EI < Edges.Num(); ++EI)
	{
		const FEdge& E = Edges[EI]; if (E.Kind != 0 || E.Len < 3.f) continue;
		const float Dens = PerKmSidewalk * (E.Axis == 0 ? AvenueBoost : 1.f);
		const float Target = E.Len / 1000.f * Dens;
		int32 N = FMath::FloorToInt(Target); if (Ff(R) < Target - N) ++N;
		TArray<float> Ss; for (int32 I = 0; I < N; ++I) Ss.Add(Ff(R) * E.Len);
		Ss.Sort();
		int32 Base = FMath::FloorToInt(Ff(R) * M);
		for (int32 I = 0; I < N && Walkers.Num() < MaxWalkers; ++I)
		{
			FWalker W; W.Rng = Xs(R) | 1u;
			W.Model = (Base + (Counter++) * Step) % M;
			W.Edge = EI; W.Dir = Ff(R) < 0.5f ? 1 : -1; W.S = W.Dir > 0 ? Ss[I] : E.Len - Ss[I];
			W.Base = (SpeedMin + Ff(R) * (SpeedMax - SpeedMin)) / 100.f;
			if (Ff(R) < 0.08f) W.Base = 1.45f; // the odd hurried walker
			W.Speed = W.Target = W.Base;
			W.Lat = 0.35f + Ff(R) * 1.15f;
			W.Scale = 0.95f + Ff(R) * 0.1f;
			W.Node = W.Dir > 0 ? E.B : E.A;
			const FVector2D Dv = E.U * W.Dir, Rt(-Dv.Y, Dv.X);
			W.Pos = LinePos(E, W.Dir, W.S) + Rt * W.Lat;
			W.Heading = FMath::Atan2(Dv.Y, Dv.X);
			Walkers.Add(W);
		}
	}
	NumWalkers = Walkers.Num();
}

void AWHLifeCrowd::BeginPlay()
{
	Super::BeginPlay();
	FParse::Value(FCommandLine::Get(), TEXT("WHLifeStats="), StatsInterval);
	if (FParse::Param(FCommandLine::Get(), TEXT("WHLifeOff")) || FParse::Param(FCommandLine::Get(), TEXT("WHCrowdOff"))) { UE_LOG(LogWHCrowd, Display, TEXT("[crowd] disabled by command line")); return; }
	if (Meshes.Num() == 0 || !AnimClass) { UE_LOG(LogWHCrowd, Warning, TEXT("[crowd] no citizen meshes / anim class")); return; }
	ParseWalk(); Populate();
	Pool.Reset(); PoolModel.Reset(); SlotOwner.Reset(); FreeSlots.SetNum(Meshes.Num());
	for (int32 M = 0; M < Meshes.Num(); ++M)
	{
		for (int32 K = 0; K < PoolPerModel; ++K)
		{
			USkeletalMeshComponent* C = NewObject<USkeletalMeshComponent>(this, *FString::Printf(TEXT("Cit_%d_%d"), M, K));
			C->SetupAttachment(GetRootComponent());
			C->SetSkeletalMesh(Meshes[M]);
			C->SetAnimationMode(EAnimationMode::AnimationBlueprint);
			C->SetAnimInstanceClass(AnimClass);
			if (MaterialOverrides.IsValidIndex(M) && MaterialOverrides[M]) for (int32 Mi = 0; Mi < FMath::Max(1, C->GetNumMaterials()); ++Mi) C->SetMaterial(Mi, MaterialOverrides[M]);
			C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
			C->SetCanEverAffectNavigation(false);
			C->SetCastShadow(bCastShadows);
			C->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
			C->RegisterComponent();
			C->SetVisibility(false); C->SetComponentTickEnabled(false);
			FreeSlots[M].Add(Pool.Num()); PoolModel.Add(M); SlotOwner.Add(-1); Pool.Add(C);
		}
	}
	uint32 Rc = 0xBEEF1u ^ (uint32)Seed; Clock = 5.0 + Ff(Rc) * 30.0;
	for (int32 I = 0; I < 40; ++I) { for (FWalker& W : Walkers) StepWalker(W, 0.5f); Clock += 0.5; } // let the crowd mix before the first frame
	bReady = true;
	RefreshLive(CameraLocation());
	UE_LOG(LogWHCrowd, Log, TEXT("[crowd] BeginPlay: %d walkers, %d live, %d models, pool %d"), NumWalkers, NumLive, Meshes.Num(), Pool.Num());
}

bool AWHLifeCrowd::MayCross(const FEdge& E, float Speed) const
{
	const double T = SignalClock();
	if (AWHLifeTraffic::SigPhase(T, E.Axis) != 0) return false;
	double C = FMath::Fmod(T, 40.0); if (C < 0.0) C += 40.0;
	double Rem = 0.0;
	if (E.Axis == 0) Rem = 40.0 - C;                       // avenue traffic red 25..40
	else Rem = C < 26.0 ? 26.0 - C : (C >= 39.0 ? 40.0 - C + 26.0 : 0.0); // street traffic red 39..40 + 0..26
	return Rem >= 0.7 * E.Len / CrossSpeed;
}

void AWHLifeCrowd::EnterEdge(FWalker& W, int32 Edge, int32 FromNode, bool)
{
	const FEdge& E = Edges[Edge];
	W.Edge = Edge; W.Dir = (E.A == FromNode) ? 1 : -1; W.State = 0; W.WaitT = 0.f;
	W.Lat = E.Kind == 1 ? 0.3f + Ff(W.Rng) * 1.0f : 0.35f + Ff(W.Rng) * 1.15f;
	W.Target = E.Kind == 1 ? FMath::Max(W.Base, CrossSpeed) : W.Base; W.bDecided = false;
	const FVector2D Dv = E.U * W.Dir;
	W.S = FMath::Clamp(FVector2D::DotProduct(W.Pos - LinePos(E, W.Dir, 0.f), Dv), 0.f, E.Len);
	W.Node = W.Dir > 0 ? E.B : E.A;
}

void AWHLifeCrowd::PickNextEdge(FWalker& W)
{
	const FEdge& Cur = Edges[W.Edge];
	const FVector2D Dv = Cur.U * W.Dir;
	const int32 Node = W.Node;
	TArray<float, TInlineAllocator<4>> Wt; TArray<int32, TInlineAllocator<4>> Ids;
	float Tot = 0.f;
	for (int32 EI : Adj[Node])
	{
		if (EI == W.Edge) continue;
		const FEdge& E = Edges[EI];
		const FVector2D Out = (E.A == Node ? E.U : -E.U);
		const float Dot = FVector2D::DotProduct(Out, Dv);
		float X;
		if (Dot > 0.7f) X = E.Kind == 0 ? 0.55f : 0.5f;
		else if (Dot < -0.7f) X = 0.02f;
		else X = E.Kind == 0 ? 0.3f : 0.3f;
		Wt.Add(X); Ids.Add(EI); Tot += X;
	}
	if (Ids.Num() == 0) { W.NextEdge = W.Edge; return; } // dead end: turn round on the same edge
	float R = Ff(W.Rng) * Tot;
	for (int32 I = 0; I < Ids.Num(); ++I) { R -= Wt[I]; if (R <= 0.f) { W.NextEdge = Ids[I]; return; } }
	W.NextEdge = Ids.Last();
}

void AWHLifeCrowd::StepWalker(FWalker& W, float Dt)
{
	if (W.Edge < 0) return;
	if (W.State == 1)
	{
		W.WaitT += Dt; W.Speed = 0.f;
		if (MayCross(Edges[W.NextEdge], W.Base)) EnterEdge(W, W.NextEdge, W.Node, true);
		return;
	}
	const FEdge& E = Edges[W.Edge];
	const float ToEnd = E.Len - W.S;
	// decide the next edge early, and brake in time when it is a crosswalk that is not open (people do not stop dead: the gait follows the ground speed)
	if (!W.bDecided && ToEnd < 3.0f) { PickNextEdge(W); W.bDecided = true; }
	float Tgt = W.Target;
	if (W.bDecided && Edges[W.NextEdge].Kind == 1 && !MayCross(Edges[W.NextEdge], W.Base) && ToEnd < W.Speed * W.Speed / (2.f * 2.2f) + 0.6f) Tgt = ToEnd > 0.55f ? 0.3f : 0.f;
	W.Speed = FMath::FInterpConstantTo(W.Speed, Tgt, Dt, Tgt > W.Speed ? 1.6f : 2.2f);
	const FVector2D Dv = E.U * W.Dir, Rt(-Dv.Y, Dv.X);
	const float S2 = FMath::Min(W.S + 1.6f, E.Len);
	const FVector2D Tp = LinePos(E, W.Dir, S2) + Rt * W.Lat;
	const FVector2D To = Tp - W.Pos;
	if (To.SizeSquared() > 1e-4f)
	{
		const float Des = FMath::Atan2(To.Y, To.X);
		const float D = WrapPi(Des - W.Heading);
		const float MaxTurn = 4.5f * Dt;
		W.Heading = WrapPi(W.Heading + FMath::Clamp(D, -MaxTurn, MaxTurn));
	}
	W.Pos += FVector2D(FMath::Cos(W.Heading), FMath::Sin(W.Heading)) * (W.Speed * Dt);
	W.S = FMath::Clamp(FVector2D::DotProduct(W.Pos - LinePos(E, W.Dir, 0.f), Dv), 0.f, E.Len);
	if (W.S >= E.Len - 0.45f)
	{
		if (!W.bDecided) { PickNextEdge(W); W.bDecided = true; }
		const FEdge& N = Edges[W.NextEdge];
		if (N.Kind == 1 && !MayCross(N, W.Base)) { W.State = 1; W.WaitT = 0.f; W.Speed = 0.f; }
		else EnterEdge(W, W.NextEdge, W.Node, true);
	}
}

void AWHLifeCrowd::Assign(int32 WI, int32 Slot)
{
	FWalker& W = Walkers[WI]; USkeletalMeshComponent* C = Pool[Slot];
	W.Comp = Slot; SlotOwner[Slot] = WI;
	C->SetVisibility(true); C->SetComponentTickEnabled(true);
	Apply(W);
	// random gait phase: run the (native, speed-synced) walk cycle forward by 0 .. ~2 s before the first visible frame
	if (UWHCharAnimInstance* AI = Cast<UWHCharAnimInstance>(C->GetAnimInstance()))
	{
		AI->ForcedSpeed = W.State == 0 ? W.Speed * 100.f : 0.f;
		const int32 N = 6 + FMath::FloorToInt(Ff(W.Rng) * 58.f);
		for (int32 I = 0; I < N; ++I) C->TickAnimation(1.f / 30.f, false);
		C->RefreshBoneTransforms();
	}
}

void AWHLifeCrowd::Unassign(int32 WI)
{
	FWalker& W = Walkers[WI]; if (W.Comp < 0) return;
	USkeletalMeshComponent* C = Pool[W.Comp];
	C->SetVisibility(false); C->SetComponentTickEnabled(false);
	FreeSlots[PoolModel[W.Comp]].Add(W.Comp); SlotOwner[W.Comp] = -1; W.Comp = -1;
}

void AWHLifeCrowd::Apply(FWalker& W)
{
	if (W.Comp < 0) return;
	USkeletalMeshComponent* C = Pool[W.Comp];
	const float Z = (W.Edge >= 0 && Edges[W.Edge].Kind == 1) ? 2.f : SidewalkZ;
	// P2: glTF +Z forward -> actor +X is a -90 deg yaw of the mesh
	C->SetWorldLocationAndRotation(FVector(W.Pos.X * 100.f, W.Pos.Y * 100.f, Z), FRotator(0.f, FMath::RadiansToDegrees(W.Heading) - 90.f, 0.f));
	C->SetWorldScale3D(FVector(W.Scale));
	if (UWHCharAnimInstance* AI = Cast<UWHCharAnimInstance>(C->GetAnimInstance())) AI->ForcedSpeed = W.State == 0 ? W.Speed * 100.f : 0.f;
}

void AWHLifeCrowd::RefreshLive(const FVector& Cam)
{
	const FVector2D C2(Cam.X, Cam.Y);
	const float R2 = LiveRadius * LiveRadius, Rd2 = (LiveRadius * 1.08f) * (LiveRadius * 1.08f);
	// release far walkers first so their slots can be reused
	for (int32 I = 0; I < Walkers.Num(); ++I)
		if (Walkers[I].Comp >= 0 && (FVector2D(Walkers[I].Pos.X * 100.f, Walkers[I].Pos.Y * 100.f) - C2).SizeSquared() > Rd2) Unassign(I);
	// nearest-first assignment so a full pool serves the walkers closest to the camera. The model is chosen at assignment time: the model (with a free
	// slot) that has the fewest live walkers within 45 m of this one, so identical twins do not walk side by side; the walker's default model breaks ties.
	TArray<TArray<FVector2D>> LiveByModel; LiveByModel.SetNum(Meshes.Num());
	for (const FWalker& W : Walkers) if (W.Comp >= 0) LiveByModel[W.Model].Add(FVector2D(W.Pos.X * 100.f, W.Pos.Y * 100.f));
	TArray<TPair<float, int32>, TInlineAllocator<256>> Cand;
	for (int32 I = 0; I < Walkers.Num(); ++I)
	{
		if (Walkers[I].Comp >= 0) continue;
		const float D2 = (FVector2D(Walkers[I].Pos.X * 100.f, Walkers[I].Pos.Y * 100.f) - C2).SizeSquared();
		if (D2 < R2) Cand.Add(TPair<float, int32>(D2, I));
	}
	Cand.Sort([](const TPair<float, int32>& A, const TPair<float, int32>& B) { return A.Key < B.Key; });
	constexpr float TwinR2 = 11000.f * 11000.f;
	for (const TPair<float, int32>& P : Cand)
	{
		FWalker& W = Walkers[P.Value];
		const FVector2D Me(W.Pos.X * 100.f, W.Pos.Y * 100.f);
		int32 Best = -1; float BestScore = 1e9f;
		for (int32 M = 0; M < Meshes.Num(); ++M)
		{
			if (FreeSlots[M].Num() == 0) continue;
			int32 Near = 0; for (const FVector2D& Q : LiveByModel[M]) if ((Q - Me).SizeSquared() < TwinR2) ++Near;
			const float Score = Near * 100.f + (M == W.Model ? 0.f : 1.f);
			if (Score < BestScore) { BestScore = Score; Best = M; }
		}
		if (Best < 0) continue;
		W.Model = Best; LiveByModel[Best].Add(Me);
		Assign(P.Value, FreeSlots[Best].Pop());
	}
	// identical twins in the CAMERA'S frame: among the walkers that project inside the viewport, a model may appear once. When two on-screen walkers share a model
	// the farther one (never closer than 30 m, so a swap is a few dozen pixels at most) takes a model that is not on screen; at most 10 swaps per refresh
	if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
	{
		int32 VW = 0, VH = 0; PC->GetViewportSize(VW, VH);
		if (VW > 0 && VH > 0)
		{
			TArray<int32> OnCount; OnCount.Init(0, Meshes.Num());
			TArray<TPair<float, int32>> On;
			for (int32 I = 0; I < Walkers.Num(); ++I)
			{
				const FWalker& W = Walkers[I]; if (W.Comp < 0) continue;
				FVector2D Sc; const FVector P(W.Pos.X * 100.f, W.Pos.Y * 100.f, SidewalkZ + 90.f);
				if (!PC->ProjectWorldLocationToScreen(P, Sc, false) || Sc.X < 0 || Sc.Y < 0 || Sc.X > VW || Sc.Y > VH) continue;
				On.Add(TPair<float, int32>(FVector::Dist(Cam, P), I)); ++OnCount[W.Model];
			}
			On.Sort([](const TPair<float, int32>& A, const TPair<float, int32>& B) { return A.Key > B.Key; }); // farthest first
			int32 Swaps = 0;
			for (const TPair<float, int32>& E : On)
			{
				if (Swaps >= 10) break;
				FWalker& W = Walkers[E.Value];
				if (OnCount[W.Model] <= 1 || E.Key < 3000.f) continue;
				int32 Best = -1;
				for (int32 M = 0; M < Meshes.Num(); ++M) if (M != W.Model && OnCount[M] == 0 && FreeSlots[M].Num() > 0) { Best = M; break; }
				if (Best < 0) continue;
				--OnCount[W.Model]; Unassign(E.Value); W.Model = Best; ++OnCount[Best]; Assign(E.Value, FreeSlots[Best].Pop()); ++Swaps;
			}
		}
	}
	NumLive = 0; NumWaiting = 0;
	for (const FWalker& W : Walkers) { NumLive += W.Comp >= 0; NumWaiting += W.State == 1; }
}

void AWHLifeCrowd::Tick(float Dt)
{
	Super::Tick(Dt);
	if (!bReady) return;
	const double T0 = FPlatformTime::Seconds();
	Dt = FMath::Min(Dt, 0.1f);
	if (!Traffic) Clock += Dt;
	for (FWalker& W : Walkers) StepWalker(W, Dt);
	RefreshT += Dt;
	if (RefreshT > 0.25f) { RefreshT = 0.f; RefreshLive(CameraLocation()); }
	for (FWalker& W : Walkers) if (W.Comp >= 0) Apply(W);
	LastSimMs = (FPlatformTime::Seconds() - T0) * 1000.f;
	if (StatsInterval > 0.f) { StatsT += Dt; if (StatsT >= StatsInterval) { StatsT = 0.f; UE_LOG(LogWHCrowd, Log, TEXT("%s"), *StatsString()); } }
}

FString AWHLifeCrowd::StatsString() const
{
	return FString::Printf(TEXT("[crowd] walkers %d live %d waiting %d models %d sim+apply %.2f ms"), NumWalkers, NumLive, NumWaiting, Meshes.Num(), LastSimMs);
}

void AWHLifeCrowd::GetLive(TArray<FVector>& Pos, TArray<int32>& Model, TArray<USkeletalMeshComponent*>& Comps, TArray<float>& Speed) const
{
	Pos.Reset(); Model.Reset(); Comps.Reset(); Speed.Reset();
	for (const FWalker& W : Walkers)
	{
		if (W.Comp < 0) continue;
		Pos.Add(FVector(W.Pos.X * 100.f, W.Pos.Y * 100.f, SidewalkZ + 90.f)); Model.Add(W.Model); Comps.Add(Pool[W.Comp]); Speed.Add(W.State == 0 ? W.Speed : 0.f);
	}
}

int32 AWHLifeCrowd::CountInCone(FVector Eye, FVector Forward, float HalfAngleDeg, float Range, int32& OutModels) const
{
	int32 N = 0; TSet<int32> Models; const FVector F = Forward.GetSafeNormal(); const float CosA = FMath::Cos(FMath::DegreesToRadians(HalfAngleDeg));
	for (const FWalker& W : Walkers)
	{
		if (W.Comp < 0) continue;
		const FVector P(W.Pos.X * 100.f, W.Pos.Y * 100.f, SidewalkZ + 90.f);
		const FVector D = P - Eye; const float Dist = D.Size();
		if (Dist < Range && Dist > 100.f && FVector::DotProduct(D / Dist, F) > CosA) { ++N; Models.Add(W.Model); }
	}
	OutModels = Models.Num();
	return N;
}
