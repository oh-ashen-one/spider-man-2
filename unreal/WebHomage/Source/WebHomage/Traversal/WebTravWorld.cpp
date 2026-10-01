// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Traversal/WebTravWorld.h"
#include "WebHomage.h"

#include "Components/PrimitiveComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/OverlapResult.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Actor.h"
#include "GameFramework/Pawn.h"

static const FName NAME_WHGround(TEXT("WHGround"));

void FWebTravWorld::Init(UWorld* InWorld, const AActor* IgnoreActor)
{
	World = InWorld;
	Params = FCollisionQueryParams(SCENE_QUERY_STAT(WebTrav), /*bTraceComplex*/ false);
	if (IgnoreActor)
	{
		Params.AddIgnoredActor(IgnoreActor);
	}
	ObjParams = FCollisionObjectQueryParams();
	ObjParams.AddObjectTypesToQuery(ECC_WorldStatic);
	ObjParams.AddObjectTypesToQuery(ECC_WorldDynamic);

	Boxes.Reset();
	GroundBoxes.Reset();
	Grid.Reset();
	CompToBox.Reset();
	InstToBox.Reset();
	int32 NInstComps = 0, NInstBoxes = 0, NInstSkipped = 0, NFarSkipped = 0;
	if (!InWorld)
	{
		return;
	}
	for (TActorIterator<AActor> It(InWorld); It; ++It)
	{
		AActor* A = *It;
		if (!A || A == IgnoreActor || A->IsA<APawn>())
		{
			continue;
		}
		if (A->ActorHasTag(NAME_WHGround))
		{
			FVector Origin, Extent;
			A->GetActorBounds(false, Origin, Extent);
			GroundBoxes.Add({ (Origin - Extent) / 100.0, (Origin + Extent) / 100.0 });
			continue;
		}
		TInlineComponentArray<UPrimitiveComponent*> Prims(A);
		for (UPrimitiveComponent* P : Prims)
		{
			if (!P || !P->IsCollisionEnabled() || P->GetCollisionObjectType() != ECC_WorldStatic)
			{
				continue;
			}
			{
				// owner playtest 2026-10-01 ("landed in mid-air", "ran up the air"): the far-skyline LOD meshes (SM_farCityMass / SM_farCity /
				// SM_farCityRoofs, one merged mesh per 2 km tile) carried collision, so each became one 2 km x 2 km, 80-290 m tall invisible block.
				// They are scenery only: switch their collision off (also for web traces) and never index anything wider than 400 m above street level.
				const UStaticMeshComponent* SMC = Cast<UStaticMeshComponent>(P);
				const UStaticMesh* SMesh = SMC ? SMC->GetStaticMesh() : nullptr;
				const bool bFarMesh = SMesh && SMesh->GetName().StartsWith(TEXT("SM_far"));
				const FBox PB = P->Bounds.GetBox();
				const bool bGiant = FMath::Max(PB.GetSize().X, PB.GetSize().Y) > 40000.0 && PB.Max.Z > 2000.0;
				if (bFarMesh || bGiant)
				{
					P->SetCollisionEnabled(ECollisionEnabled::NoCollision);
					++NFarSkipped;
					continue;
				}
			}
			auto AddBox = [this](const FBox& B) -> int32
			{
				FTravBox TB{ B.Min / 100.0, B.Max / 100.0 };
				const FVector S = TB.Max - TB.Min;
				if (S.Z < 1.0 || (S.X < 0.8 && S.Y < 0.8))
				{
					return -1;
				}
				const int32 Idx = Boxes.Add(TB);
				const int32 X0 = FMath::FloorToInt(TB.Min.X / Cell), X1 = FMath::FloorToInt(TB.Max.X / Cell);
				const int32 Y0 = FMath::FloorToInt(TB.Min.Y / Cell), Y1 = FMath::FloorToInt(TB.Max.Y / Cell);
				for (int32 X = X0; X <= X1; ++X)
				{
					for (int32 Y = Y0; Y <= Y1; ++Y)
					{
						Grid.FindOrAdd(Key(X, Y)).Add(Idx);
					}
				}
				return Idx;
			};
			if (const UInstancedStaticMeshComponent* ISM = Cast<UInstancedStaticMeshComponent>(P))
			{
				// per-instance boxes; foliage / tree / moving-traffic instances are not perchable building boxes
				const UStaticMesh* SM = ISM->GetStaticMesh();
				const FString MeshName = SM ? SM->GetName().ToLower() : FString();
				const FString CompName = (A->GetName() + TEXT("/") + ISM->GetName()).ToLower();
				static const TCHAR* Skip[] = { TEXT("tree"), TEXT("crown"), TEXT("clump"), TEXT("leaf"), TEXT("leaves"), TEXT("foliage"), TEXT("canopy"), TEXT("bush"), TEXT("traffic") };
				bool bSkip = !SM;
				for (const TCHAR* K : Skip) { if (MeshName.Contains(K) || CompName.Contains(K)) { bSkip = true; break; } }
				++NInstComps;
				TArray<int32>& Map = InstToBox.FindOrAdd(P);
				const int32 N = ISM->GetInstanceCount();
				Map.Init(-1, N);
				if (bSkip) { NInstSkipped += N; continue; }
				const FBox MB = SM->GetBoundingBox();
				for (int32 I = 0; I < N; ++I)
				{
					FTransform T;
					if (!ISM->GetInstanceTransform(I, T, /*bWorldSpace*/ true)) continue;
					const int32 Idx = AddBox(MB.TransformBy(T));
					Map[I] = Idx;
					if (Idx >= 0) ++NInstBoxes;
				}
				continue;
			}
			const int32 Idx = AddBox(P->Bounds.GetBox());
			if (Idx >= 0)
			{
				CompToBox.Add(P, Idx);
			}
		}
	}
	UE_LOG(LogWebHomage, Display, TEXT("WebTravWorld: %d building boxes indexed (%d instanced components -> %d instance boxes, %d foliage/traffic instances skipped, %d far-skyline/giant components de-collided)"), Boxes.Num(), NInstComps, NInstBoxes, NInstSkipped, NFarSkipped);
}

void FWebTravWorld::Near(double X, double Y, double R, TArray<int32>& Out) const
{
	Out.Reset();
	const int32 X0 = FMath::FloorToInt((X - R) / Cell), X1 = FMath::FloorToInt((X + R) / Cell);
	const int32 Y0 = FMath::FloorToInt((Y - R) / Cell), Y1 = FMath::FloorToInt((Y + R) / Cell);
	for (int32 CX = X0; CX <= X1; ++CX)
	{
		for (int32 CY = Y0; CY <= Y1; ++CY)
		{
			if (const TArray<int32>* L = Grid.Find(Key(CX, CY)))
			{
				for (int32 I : *L)
				{
					const FTravBox& B = Boxes[I];
					if (B.Max.X < X - R || B.Min.X > X + R || B.Max.Y < Y - R || B.Min.Y > Y + R)
					{
						continue;
					}
					Out.AddUnique(I);
				}
			}
		}
	}
}

bool FWebTravWorld::Inside(const FVector& P, double M) const
{
	TArray<int32> L;
	Near(P.X, P.Y, 0.01, L);
	for (int32 I : L)
	{
		const FTravBox& B = Boxes[I];
		if (P.X > B.Min.X + M && P.X < B.Max.X - M && P.Y > B.Min.Y + M && P.Y < B.Max.Y - M && P.Z > B.Min.Z + M && P.Z < B.Max.Z - M)
		{
			return true;
		}
	}
	return false;
}

bool FWebTravWorld::Raycast(const FVector& O, const FVector& D, double MaxDist, FTravHit& Out) const
{
	UWorld* W = World.Get();
	if (!W || MaxDist <= 0.0)
	{
		return false;
	}
	++TraceCount;
	FHitResult H;
	const FVector Start = O * 100.0, End = (O + D * MaxDist) * 100.0;
	if (!W->LineTraceSingleByObjectType(H, Start, End, ObjParams, Params) || H.bStartPenetrating)
	{
		return false;
	}
	Out.Distance = H.Distance / 100.0;
	Out.Point = H.ImpactPoint / 100.0;
	Out.Normal = H.ImpactNormal.GetSafeNormal();
	Out.Comp = H.GetComponent();
	const AActor* A = H.GetActor();
	Out.bGround = A && A->ActorHasTag(NAME_WHGround);
	const int32* Bi = H.GetComponent() ? CompToBox.Find(H.GetComponent()) : nullptr;
	Out.Box = Bi ? *Bi : -1;
	if (!Bi && H.GetComponent())
	{
		if (const TArray<int32>* M = InstToBox.Find(H.GetComponent()))
		{
			Out.Box = M->IsValidIndex(H.Item) ? (*M)[H.Item] : -1;
		}
	}
	return true;
}

bool FWebTravWorld::SphereSweep(const FVector& A, const FVector& B, double Radius, double& OutDist) const
{
	UWorld* W = World.Get();
	if (!W) return false;
	++TraceCount;
	FHitResult H;
	if (!W->SweepSingleByObjectType(H, A * 100.0, B * 100.0, FQuat::Identity, ObjParams, FCollisionShape::MakeSphere(float(Radius * 100.0)), Params))
	{
		return false;
	}
	OutDist = H.bStartPenetrating ? 0.0 : H.Distance / 100.0;
	return true;
}

bool FWebTravWorld::SphereOverlaps(const FVector& P, double Radius) const
{
	UWorld* W = World.Get();
	if (!W) return false;
	++TraceCount;
	return W->OverlapAnyTestByObjectType(P * 100.0, FQuat::Identity, ObjParams, FCollisionShape::MakeSphere(float(Radius * 100.0)), Params);
}

double FWebTravWorld::GroundHeight(double X, double Y, double FromZ) const
{
	double Best = -1000.0;
	for (const FTravBox& G : GroundBoxes)
	{
		if (X >= G.Min.X && X <= G.Max.X && Y >= G.Min.Y && Y <= G.Max.Y) Best = FMath::Max(Best, G.Max.Z);
	}
	FTravHit H;
	if (Raycast(FVector(X, Y, FromZ), FVector(0, 0, -1), 2000.0, H))
	{
		Best = FMath::Max(Best, H.Point.Z);
	}
	return Best;
}

double FWebTravWorld::StreetHeight(double X, double Y, double FromZ) const
{
	double Best = -1000.0;
	for (const FTravBox& G : GroundBoxes)
	{
		if (X >= G.Min.X && X <= G.Max.X && Y >= G.Min.Y && Y <= G.Max.Y) Best = FMath::Max(Best, G.Max.Z);
	}
	double Z = FromZ;
	for (int32 K = 0; K < 6; ++K)
	{
		FTravHit H;
		if (!Raycast(FVector(X, Y, Z), FVector(0, 0, -1), 2000.0, H)) break;
		// a building mass counts (a box > 4 m tall); awnings / canopies / fire escapes / ledges (thin boxes), props, trees and
		// street-kit meshes do not: keep looking below them
		const bool bMass = H.Box >= 0 && Boxes.IsValidIndex(H.Box) && Boxes[H.Box].Max.Z - Boxes[H.Box].Min.Z > 4.0;
		if (H.bGround || bMass) { Best = FMath::Max(Best, H.Point.Z); break; }
		Z = H.Point.Z - 0.05;
	}
	return Best;
}

bool FWebTravWorld::PushOutCapsule(FVector& Feet, double R, double H, double StepH, FTravContact& Out) const
{
	UWorld* W = World.Get();
	if (!W)
	{
		return false;
	}
	const double Lo = StepH, Hi = H;
	const double HalfH = FMath::Max((Hi - Lo) * 0.5, R + 0.01);
	const FCollisionShape Shape = FCollisionShape::MakeCapsule(float(R * 100.0), float(HalfH * 100.0));
	bool bAny = false;
	double BestDepth = -1.0;
	TWeakObjectPtr<UPrimitiveComponent> BestComp;
	for (int32 Iter = 0; Iter < 3; ++Iter)
	{
		const FVector Centre = FVector(Feet.X, Feet.Y, Feet.Z + Lo + HalfH) * 100.0;
		TArray<FOverlapResult> Overlaps;
		++TraceCount;
		if (!W->OverlapMultiByObjectType(Overlaps, Centre, FQuat::Identity, ObjParams, Shape, Params))
		{
			break;
		}
		bool bMoved = false;
		for (const FOverlapResult& O : Overlaps)
		{
			UPrimitiveComponent* C = O.GetComponent();
			if (!C)
			{
				continue;
			}
			FMTDResult MTD;
			const FVector CNow = FVector(Feet.X, Feet.Y, Feet.Z + Lo + HalfH) * 100.0;
			if (!C->ComputePenetration(MTD, Shape, CNow, FQuat::Identity) || MTD.Distance <= KINDA_SMALL_NUMBER)
			{
				continue;
			}
			FVector N(MTD.Direction.X, MTD.Direction.Y, 0.0);
			const double HL = N.Size();
			if (HL < 0.3)
			{
				continue; // vertical push-out: floor / ceiling, handled by ground snapping
			}
			N /= HL;
			const double Depth = FMath::Min(double(MTD.Distance) / 100.0 / HL, 1.0);
			if (FMath::Abs(N.X) > 0.999) { N = FVector(FMath::Sign(N.X), 0, 0); }
			else if (FMath::Abs(N.Y) > 0.999) { N = FVector(0, FMath::Sign(N.Y), 0); }
			Feet.X += N.X * (Depth + 1e-4);
			Feet.Y += N.Y * (Depth + 1e-4);
			bMoved = true;
			if (Depth > BestDepth)
			{
				BestDepth = Depth;
				bAny = true;
				Out.Normal = N;
				Out.Point = FVector(Feet.X - N.X * R, Feet.Y - N.Y * R, Feet.Z + H * 0.5);
				Out.Depth = Depth;
				BestComp = C;
			}
		}
		if (!bMoved)
		{
			break;
		}
	}
	if (bAny)
	{
		// top of the obstacle stack in front of the contact (wall + parapet + coping): highest surface right behind the
		// contact point. A trace from high above finds the roof; the obstacle bounds are the fallback.
		const FVector P = Out.Point - Out.Normal * 0.05;
		FTravHit TH;
		double Top = BestComp.IsValid() ? BestComp->Bounds.GetBox().Max.Z / 100.0 : Feet.Z + H;
		const double From = Feet.Z + 400.0;
		if (Raycast(FVector(P.X, P.Y, From), FVector(0, 0, -1), 400.0 + 1.0, TH) && TH.Point.Z > Feet.Z + StepH)
		{
			Top = TH.Point.Z;
		}
		Out.Top = Top;
	}
	return bAny;
}
