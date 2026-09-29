// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
// Piece P3: world queries for traversal in METRES (port of the browser's world.raycast / world.groundHeight /
// collide.js BoxIndex + pushOutCapsule), implemented with Unreal line traces and capsule penetration tests.
#pragma once

#include "CoreMinimal.h"
#include "CollisionQueryParams.h"

class UWorld;
class AActor;
class UPrimitiveComponent;

struct FTravHit
{
	double Distance = 0.0;
	FVector Point = FVector::ZeroVector;   // m
	FVector Normal = FVector::UpVector;
	bool bGround = false;                  // hit the bare ground plane (actor tagged WHGround): never holds a web
	int32 Box = -1;                        // building box index, -1 if not a box
	TWeakObjectPtr<UPrimitiveComponent> Comp;
};

struct FTravContact
{
	FVector Normal = FVector::ForwardVector; // horizontal
	FVector Point = FVector::ZeroVector;
	double Depth = 0.0;
	double Top = 0.0;                         // top of the obstacle stack in front (m)
};

struct FTravBox
{
	FVector Min = FVector::ZeroVector; // m
	FVector Max = FVector::ZeroVector;
};

class WEBHOMAGE_API FWebTravWorld
{
public:
	/** Gathers building boxes (blocking static geometry, not tagged WHGround) and sets up query params. */
	void Init(UWorld* InWorld, const AActor* IgnoreActor);

	/** Ray from O along unit D up to MaxDist (m). */
	bool Raycast(const FVector& O, const FVector& D, double MaxDist, FTravHit& Out) const;
	/** Sphere sweep from A to B (m); returns true on a blocking hit (OutDist = distance travelled before the hit). */
	bool SphereSweep(const FVector& A, const FVector& B, double Radius, double& OutDist) const;
	/** Does a sphere at P (m) overlap solid geometry (ground included)? */
	bool SphereOverlaps(const FVector& P, double Radius) const;
	/** Highest surface at (X,Y) at or below FromZ (m). -1000 if nothing. */
	double GroundHeight(double X, double Y, double FromZ) const;
	/** Round 10 (lit city): like GroundHeight but passes through props / trees / street-kit meshes (only ground-tagged actors
	 *  and indexed building boxes count), so a swing's designed low point is measured from the street, not a tree canopy. */
	double StreetHeight(double X, double Y, double FromZ) const;
	/** Pushes a vertical capsule (feet, radius R, height H) horizontally out of solids; only the part above StepH collides. */
	bool PushOutCapsule(FVector& Feet, double R, double H, double StepH, FTravContact& Out) const;
	/** Is the point inside a building box (margin m)? */
	bool Inside(const FVector& P, double Margin = 0.05) const;
	/** Box indices whose XY footprint intersects the square around (X,Y) with half-size R. */
	void Near(double X, double Y, double R, TArray<int32>& Out) const;

	bool Ok() const { return Boxes.Num() > 0; }

	TArray<FTravBox> Boxes;
	/** Terrain (actors tagged WHGround): always a floor, even when a body has sunk below its top (browser terrain). */
	TArray<FTravBox> GroundBoxes;
	mutable int32 TraceCount = 0;

private:
	int64 Key(int32 CX, int32 CY) const { return (int64(CX) << 32) ^ int64(uint32(CY)); }
	TMap<int64, TArray<int32>> Grid;
	TMap<const UPrimitiveComponent*, int32> CompToBox;
	double Cell = 24.0;
	TWeakObjectPtr<UWorld> World;
	FCollisionQueryParams Params;
	FCollisionObjectQueryParams ObjParams;
};
