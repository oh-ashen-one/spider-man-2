// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
// P6 City life: sidewalk crowd. Walkers are simulated cheaply and analytically on the pedestrian graph exported by
// tools/life/export_lanes.mjs (sidewalk corners, sidewalk edges along the avenue / street sides, crosswalk edges); only the
// walkers near the camera own a skeletal-mesh component (pooled per citizen model), so hundreds of walkers cost as much as the
// ~150 that can be seen. Every live walker plays P2's citizen walk cycle through UWHCharAnimInstance at the exact ground speed
// it moves (ForcedSpeed = actor speed, clip rate = speed / clip speed), so feet stay planted; each walker starts at a random
// gait phase. Walkers wait at crosswalks for the traffic signal (shared clock with AWHLifeTraffic).
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WHLifeCrowd.generated.h"

class USkeletalMesh;
class USkeletalMeshComponent;
class UAnimInstance;
class AWHLifeTraffic;
class UMaterialInterface;

namespace WHLife
{
	struct FWalker
	{
		int32 Model = 0, Edge = -1, Node = -1;   // Node = corner the walker is walking towards
		int8 Dir = 1;
		float S = 0.f;                            // progress along the edge in the travel direction (m)
		FVector2D Pos = FVector2D::ZeroVector;    // metres, browser frame
		float Heading = 0.f, Speed = 1.1f, Base = 1.1f, Lat = 0.8f, Scale = 1.f, WaitT = 0.f;
		uint8 State = 0;                          // 0 walking, 1 waiting at a corner for the walk signal
		int32 NextEdge = -1;
		float Target = 1.1f;                      // desired speed on this edge (m/s); Speed follows it with a limited acceleration
		bool bDecided = false;                    // NextEdge already chosen for the end of this edge
		int32 Comp = -1;                          // pool slot while live
		uint32 Rng = 1;
		float Tint = 1.f;
	};
}

UCLASS()
class WEBHOMAGE_API AWHLifeCrowd : public AActor
{
	GENERATED_BODY()
public:
	AWHLifeCrowd();
	virtual void BeginPlay() override;
	virtual void Tick(float Dt) override;

	/** Scripts/life_data/walk.txt (written by Scripts/build_life.py). */
	UPROPERTY(EditAnywhere, Category="Life|Data", meta=(MultiLine=true)) FString WalkData;
	/** Citizen skeletal meshes (materials are on the meshes). Distinct models: index = model id. */
	UPROPERTY(EditAnywhere, Category="Life|Data") TArray<TObjectPtr<USkeletalMesh>> Meshes;
	/** Optional per-model material override (same length as Meshes, entries may be null): outfit variants share one mesh. */
	UPROPERTY(EditAnywhere, Category="Life|Data") TArray<TObjectPtr<UMaterialInterface>> MaterialOverrides;
	/** Anim blueprint (child of UWHCharAnimInstance) shared by the citizen skeleton. */
	UPROPERTY(EditAnywhere, Category="Life|Data") TSubclassOf<UAnimInstance> AnimClass;
	/** Optional: the traffic actor whose signal clock the crowd obeys. */
	UPROPERTY(EditAnywhere, Category="Life|Data") TObjectPtr<AWHLifeTraffic> Traffic;

	UPROPERTY(EditAnywhere, Category="Life") int32 Seed = 11;
	/** Walkers per km of sidewalk (avenue-side edges get AvenueBoost x). */
	UPROPERTY(EditAnywhere, Category="Life") float PerKmSidewalk = 70.f;
	UPROPERTY(EditAnywhere, Category="Life") float AvenueBoost = 2.6f;
	UPROPERTY(EditAnywhere, Category="Life") int32 MaxWalkers = 2600;
	/** cm: walkers farther than this from the camera are simulated but have no mesh. */
	UPROPERTY(EditAnywhere, Category="Life") float LiveRadius = 19000.f;
	UPROPERTY(EditAnywhere, Category="Life") int32 PoolPerModel = 8;
	/** Clip speed (cm/s) at which the citizen walk cycle plays at rate 1 without foot sliding (P2: stride 1.1543 m / (32/30 s) = 108). */
	UPROPERTY(EditAnywhere, Category="Life") float ClipSpeed = 108.f;
	UPROPERTY(EditAnywhere, Category="Life") float SpeedMin = 100.f;
	UPROPERTY(EditAnywhere, Category="Life") float SpeedMax = 135.f;
	UPROPERTY(EditAnywhere, Category="Life") float SidewalkZ = 15.f;
	UPROPERTY(EditAnywhere, Category="Life") bool bCastShadows = true;
	UPROPERTY(EditAnywhere, Category="Life") float StatsInterval = 0.f;
	/** Fixed camera for the live set (test rigs); ignored if zero. */
	UPROPERTY(EditAnywhere, Category="Life") FVector FocusOverride = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category="Life|Stats") int32 NumWalkers = 0;
	UPROPERTY(BlueprintReadOnly, Category="Life|Stats") int32 NumLive = 0;
	UPROPERTY(BlueprintReadOnly, Category="Life|Stats") int32 NumWaiting = 0;
	UPROPERTY(BlueprintReadOnly, Category="Life|Stats") float LastSimMs = 0.f;

	UFUNCTION(BlueprintCallable, Category="Life") FString StatsString() const;
	/** Live walkers (C++ only): world positions of the feet-level pivot (cm), model ids, and their skeletal components. */
	void GetLive(TArray<FVector>& Pos, TArray<int32>& Model, TArray<USkeletalMeshComponent*>& Comps, TArray<float>& Speed) const;
	/** Live walkers whose position is inside a cone in front of Eye (also returns the number of distinct models via OutModels). */
	UFUNCTION(BlueprintCallable, Category="Life") int32 CountInCone(FVector Eye, FVector Forward, float HalfAngleDeg, float Range, int32& OutModels) const;

private:
	struct FEdge { int32 A = 0, B = 0, Kind = 0, Axis = 0; float Len = 0.f; FVector2D U = FVector2D::ZeroVector; };
	TArray<FVector2D> Pts;
	TArray<FEdge> Edges;
	TArray<TArray<int32>> Adj; // node -> edge indices
	TArray<WHLife::FWalker> Walkers;
	UPROPERTY(Transient) TArray<TObjectPtr<USkeletalMeshComponent>> Pool;
	TArray<int32> PoolModel;                 // model of each pool slot
	TArray<TArray<int32>> FreeSlots;         // per model
	TArray<int32> SlotOwner;                 // pool slot -> walker (-1 free)
	double Clock = 0.0;
	float RefreshT = 0.f, StatsT = 0.f;
	bool bReady = false;

	void ParseWalk();
	void Populate();
	void PickNextEdge(WHLife::FWalker& W);
	FVector2D LinePos(const FEdge& E, int8 Dir, float S) const { return Dir > 0 ? Pts[E.A] + E.U * S : Pts[E.B] - E.U * S; }
	void StepWalker(WHLife::FWalker& W, float Dt);
	void EnterEdge(WHLife::FWalker& W, int32 Edge, int32 FromNode, bool bKeepPos);
	bool MayCross(const FEdge& E, float Speed) const;
	void RefreshLive(const FVector& Cam);
	void Assign(int32 WalkerI, int32 Slot);
	void Unassign(int32 WalkerI);
	void Apply(WHLife::FWalker& W);
	FVector CameraLocation() const;
	double SignalClock() const;
};
