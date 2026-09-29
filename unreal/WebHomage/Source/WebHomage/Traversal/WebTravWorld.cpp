// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Traversal/WebTravWorld.h"
#include "WebHomage.h"

#include "Components/PrimitiveComponent.h"
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
			const FBox B = P->Bounds.GetBox();
			FTravBox TB{ B.Min / 100.0, B.Max / 100.0 };
			const FVector S = TB.Max - TB.Min;
			if (S.Z < 1.0 || (S.X < 0.8 && S.Y < 0.8))
			{
				continue;
			}
			const int32 Idx = Boxes.Add(TB);
			CompToBox.Add(P, Idx);
			const int32 X0 = FMath::FloorToInt(TB.Min.X / Cell), X1 = FMath::FloorToInt(TB.Max.X / Cell);
			const int32 Y0 = FMath::FloorToInt(TB.Min.Y / Cell), Y1 = FMath::FloorToInt(TB.Max.Y / Cell);
			for (int32 X = X0; X <= X1; ++X)
			{
				for (int32 Y = Y0; Y <= Y1; ++Y)
				{
					Grid.FindOrAdd(Key(X, Y)).Add(Idx);
				}
			}
		}
	}
	UE_LOG(LogWebHomage, Display, TEXT("WebTravWorld: %d building boxes indexed"), Boxes.Num());
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
	return true;
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
