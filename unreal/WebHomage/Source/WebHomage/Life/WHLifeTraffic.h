// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
// P6 City life: instanced street traffic. Port of the browser sim (src/world/npc/roads.js + traffic.js) reduced to what the
// Midtown block needs: cars follow directed lane links (exported by tools/life/export_lanes.mjs), turn through junction
// connectors, stop at the browser's 40 s signal phases, follow each other with the IDM model, and yield inside the junction box
// through connector conflict reservations. Cars are ISM instances (one component per vehicle type, per-instance custom data =
// linear paint colour + brake-light state); parked cars / curb taxis are static ISM instances placed from ParkedData.
// Frame: browser metres (x east, z south) -> UE cm (X = 100 x, Y = 100 z, Z up), yaw = atan2(dz, dx) in degrees.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WHLifeTraffic.generated.h"

class UStaticMesh;
class UMaterialInterface;
class UInstancedStaticMeshComponent;

namespace WHLife
{
	constexpr int32 NumTypes = 15;
	struct FConn
	{
		int32 Id = 0, FromLink = -1, ToLink = -1, Turn = 0;
		float Len = 0.f;
		TArray<FVector2D> Poly;
		TArray<float> Cum;
		TArray<int32> Conflicts;
		TArray<int32> Cars;         // cars whose FRONT is on this connector
		TArray<int32> Reserved;     // car ids that hold the box for this connector (in the box or committed to enter)
	};
	struct FLink
	{
		int32 Id = 0, From = -1, To = -1, Kind = 0, Lane = 0, Axis = 0;
		FVector2D A = FVector2D::ZeroVector, D = FVector2D::ZeroVector;
		float Len = 0.f;
		bool bSig = false, bNoPark = false, bNarrow = false, bEntry = false;
		TArray<float> ParkSides;
		TArray<int32> Outs, Ins;    // connector indices
		TArray<int32> Cars;         // cars whose FRONT is on this link, ascending S
		float NextSpawn = 0.f;
	};
	struct FCar
	{
		bool bActive = false;
		int32 Type = 0, Inst = -1;
		float Len = 4.8f, Wid = 1.85f, V = 0.f, V0 = 13.f, S = 0.f, Acc = 0.f;
		float DA = 2.0f, DTH = 1.1f, DS0 = 2.0f, Lat = 0.f, WaitT = 0.f, StuckT = 0.f, Age = 0.f;
		int32 L0 = -1, K = -1, L1 = -1;   // incoming link, connector (chosen / current), outgoing link
		uint8 Where = 0;                  // front on: 0 = L0, 1 = K, 2 = L1
		bool bReserved = false;
		bool bRedHold = false;            // was held by a red / amber signal on the previous step
		float GoDelay = 0.f;              // driver reaction time after the light turns green (s)
		float BoxStopT = 0.f;             // seconds stopped with the body inside the junction box
		uint8 Brake = 0;
		FLinearColor Color = FLinearColor::White;
		uint32 Rng = 1;
	};
}

UCLASS()
class WEBHOMAGE_API AWHLifeTraffic : public AActor
{
	GENERATED_BODY()
public:
	AWHLifeTraffic();
	virtual void BeginPlay() override;
	virtual void Tick(float Dt) override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;

	/** Scripts/life_data/lanes.txt (written into the actor by Scripts/build_life.py). */
	UPROPERTY(EditAnywhere, Category="Life|Data", meta=(MultiLine=true)) FString LaneData;
	/** Scripts/life_data/parked.txt: `type x z yawDeg r g b flags` per line (metres, linear colour). */
	UPROPERTY(EditAnywhere, Category="Life|Data", meta=(MultiLine=true)) FString ParkedData;
	/** Static meshes in the order taxi, taxi_hy, taxi_mv, taxi_gr, sedan, hatch, sedan2, cross, suv, suv2, pickup, van, truck, bus, tour. */
	UPROPERTY(EditAnywhere, Category="Life|Data") TArray<TObjectPtr<UStaticMesh>> VehicleMeshes;
	UPROPERTY(EditAnywhere, Category="Life|Data") TObjectPtr<UMaterialInterface> VehicleMaterial;
	/** Scripts/life_data/signals.txt: `M|P x z ry` per line (browser metres; M = mast arm with 2 arm heads + 1 pole head, P = post head), the P1 signal props. */
	UPROPERTY(EditAnywhere, Category="Life|Signals", meta=(MultiLine=true)) FString SignalData;
	/** Lens overlay: a unit cylinder (axis Z, 100 cm) turned into a flat disc facing the road; the material reads custom data (r, g, b, on). */
	UPROPERTY(EditAnywhere, Category="Life|Signals") TObjectPtr<UStaticMesh> SignalMesh;
	UPROPERTY(EditAnywhere, Category="Life|Signals") TObjectPtr<UMaterialInterface> SignalMaterial;
	UPROPERTY(EditAnywhere, Category="Life|Signals") float LensDiameterCm = 27.f;
	/** Drivers wait this long (s, uniform between the two) after their light turns green before they pull away. */
	UPROPERTY(EditAnywhere, Category="Life") float ReactionMin = 0.35f;
	UPROPERTY(EditAnywhere, Category="Life") float ReactionMax = 1.25f;
	/** >= 0: the signal clock reads this phase (s in the 40 s cycle) when the pre-roll ends, i.e. game time 0. Fixed-camera signal clips. */
	UPROPERTY(EditAnywhere, Category="Life") float SignalPhaseAtStart = -1.f;
	/** Bus / tourist bus share of the curb-side through lane of avenues (0..1). */
	UPROPERTY(EditAnywhere, Category="Life") float BusShare = 0.07f;

	UPROPERTY(EditAnywhere, Category="Life") bool bSimulate = true;
	/** 1 = the browser's steady-state density (cars per km of lane by road kind). */
	UPROPERTY(EditAnywhere, Category="Life") float DensityScale = 1.f;
	/** Extra factor for the cross-street lanes (kind 1): they are 10 m wide with curb parking, a dense avenue setting would make a solid queue. */
	UPROPERTY(EditAnywhere, Category="Life") float StreetDensityFactor = 0.6f;
	UPROPERTY(EditAnywhere, Category="Life") int32 Seed = 7;
	/** Seconds simulated at BeginPlay so the first frame already shows platoons and queues at the lights. */
	UPROPERTY(EditAnywhere, Category="Life") float PreRollSeconds = 75.f;
	UPROPERTY(EditAnywhere, Category="Life") int32 MaxCars = 2000;
	/** Cull moving and parked instances beyond this distance (cm). */
	UPROPERTY(EditAnywhere, Category="Life") float CullDistance = 100000.f;
	UPROPERTY(EditAnywhere, Category="Life") bool bCastShadows = true;
	/** Ray tracing (Lumen hardware RT / TLAS) sees the instances. Off by default: moving instances force a TLAS update every frame. */
	UPROPERTY(EditAnywhere, Category="Life") bool bVisibleInRayTracing = false;
	/** Simulated signal clock offset (s). */
	UPROPERTY(EditAnywhere, Category="Life") float SignalOffset = 0.f;
	/** Tick-time budget log every N seconds (0 = off). */
	UPROPERTY(EditAnywhere, Category="Life") float StatsInterval = 0.f;

	UPROPERTY(BlueprintReadOnly, Category="Life|Stats") int32 NumMoving = 0;
	UPROPERTY(BlueprintReadOnly, Category="Life|Stats") int32 NumParked = 0;
	UPROPERTY(BlueprintReadOnly, Category="Life|Stats") int32 NumParkedTaxis = 0;
	UPROPERTY(BlueprintReadOnly, Category="Life|Stats") int32 NumStopped = 0;
	/** Cars stopped (< 0.3 m/s) with any part of the body inside a junction box right now / worst count seen / accumulated car-seconds. */
	UPROPERTY(BlueprintReadOnly, Category="Life|Stats") int32 NumBoxStopped = 0;
	UPROPERTY(BlueprintReadOnly, Category="Life|Stats") int32 MaxBoxStopped = 0;
	UPROPERTY(BlueprintReadOnly, Category="Life|Stats") float BoxStopSeconds = 0.f;
	UPROPERTY(BlueprintReadOnly, Category="Life|Stats") float LastSimMs = 0.f;
	UPROPERTY(BlueprintReadOnly, Category="Life|Stats") float LastPushMs = 0.f;

	UFUNCTION(BlueprintCallable, Category="Life") FString StatsString() const;
	/** Debug: write every active car (world position m, speed, link id, where, type, reserved) to a CSV. */
	void DumpCars(const FString& Path) const;
	/** props.js phase(): 40 s cycle, axis 0 = avenue traffic, 1 = street traffic; returns 2 green, 1 amber, 0 red. */
	static int32 SigPhase(double T, int32 Axis);
	/** Seconds on the shared signal clock (the crowd waits at crosswalks by it). */
	double GetSignalClock() const { return SimClock + SignalOffset; }
	/** Centres of the vehicles (cm, ground level + 0.8 m): moving, then parked, with their type index. */
	void GetPoints(TArray<FVector>& Moving, TArray<int32>& MovingType, TArray<FVector>& Parked, TArray<int32>& ParkedType) const;
	/** Moving cars with their world centre (cm), speed (m/s) and a lane key (kind*100 + lane*10 + travel direction 1 N / 2 S / 3 E / 4 W). */
	void GetMovingInfo(TArray<FVector>& Pos, TArray<float>& Speed, TArray<int32>& LaneKey) const;
	/** Queue on a lane link (file id): cars whose front is on it, how many are stopped, the front car's distance to the stop line (m, -1 none). */
	void GetLinkQueue(int32 LinkFileId, int32& Cars, int32& Stopped, float& FrontToLine) const;
	/** Signal state of an axis (0 avenue, 1 street) now: 2 green, 1 amber, 0 red. */
	int32 CurrentPhase(int32 Axis) const { return SigPhase(GetSignalClock(), Axis); }
	/** Moving-car count whose centre is inside a world-space frustum-ish cone (camera location, forward, half-angle deg, range cm). */
	UFUNCTION(BlueprintCallable, Category="Life") int32 CountInCone(FVector Eye, FVector Forward, float HalfAngleDeg, float Range) const;

private:
	// data
	TArray<WHLife::FLink> Links;
	TArray<WHLife::FConn> Conns;
	TArray<WHLife::FCar> Cars;
	TMap<int32, int32> LinkIdx; // file id -> index
	TArray<int32> FreeCars;
	UPROPERTY(Transient) TArray<TObjectPtr<UInstancedStaticMeshComponent>> MovingISM;
	UPROPERTY(Transient) TArray<TObjectPtr<UInstancedStaticMeshComponent>> ParkedISM;
	UPROPERTY(Transient) TObjectPtr<UInstancedStaticMeshComponent> LensISM;
	struct FLens { int32 Axis = 0, Color = 0, Inst = 0; };
	TArray<FLens> Lenses;
	int32 LastSig[2] = { -1, -1 };
	TArray<TArray<int32>> FreeInst;
	TArray<TArray<FTransform>> Xf;
	TArray<int32> HighWater;
	TArray<bool> Dirty;
	TArray<FVector> ParkedPts;
	TArray<int32> ParkedTypes;
	double SimClock = 0.0;
	float Accum = 0.f, StatsT = 0.f;
	uint32 GlobalRng = 1;
	bool bReady = false;

	float KindDensity(int32 Kind) const;
	void ParseLanes();
	void BuildComponents();
	void PlaceParked();
	void BuildSignals();
	void UpdateSignals();
	void PopulateInitial();
	void StepSim(float Dt);
	void PushInstances();

	// sim helpers
	int32 SpawnCar(int32 LinkI, float Front, float V, bool bRandomType);
	void DespawnCar(int32 CarI);
	int32 PickType(const WHLife::FLink& L, uint32& R) const;
	FLinearColor PickColor(int32 Type, uint32& R) const;
	int32 ChooseNext(WHLife::FCar& C, const WHLife::FLink& L);
	void FindLeader(int32 CarI, float& Gap, float& VLead);
	bool TryReserve(WHLife::FCar& C);
	void Release(WHLife::FCar& C, int32 CarI);
	bool CanClear(const WHLife::FCar& C, const WHLife::FLink& L) const;
	static float Frand(uint32& R);
	FVector2D LinkPos(const WHLife::FLink& L, float S) const { return L.A + L.D * S; }
	FVector2D ConnPos(const WHLife::FConn& K, float S) const;
	FVector2D PathPoint(const WHLife::FCar& C, float Behind) const;
};
