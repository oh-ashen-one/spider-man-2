// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
// Night city lights: the original author's night mode (night_lights.json -> Content/Night/CityLights.bin, tools/night/prep_night.py)
// as a streamed, budgeted pool of real movable lights around the camera, plus the author's area ambient (citylights.js AMB) that drives
// AWHLookHeroLight. Tuning: Content/Night/CityLights.json (Scripts/night_city.json). Dark below MPC_City NightK 0.01.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "WHCityLights.generated.h"

class ULocalLightComponent;
class UMaterialParameterCollection;
class AWHLookHeroLight;

struct FWHCLRecord
{
	float Pos[3], Dir[3], U[3], Col[3];
	float Intensity, Range, W, H;       // cm
	uint8 Cat, Type, Flags, Vol;
	float CosO, CosI, Radius, Spec;     // radius cm
	float AreaM2 = 1.f;
	int32 Parent = -1;                  // board tile -> its whole board
	bool bHasTiles = false;             // board whole: has tiles
	int32 Group = -1;
	FVector Location() const { return FVector(Pos[0], Pos[1], Pos[2]); }
	bool bDay() const { return (Flags & 1) != 0; }
};

struct FWHCLGroupCfg
{
	FString Name;
	TArray<int32> Cats;
	int32 Budget = 0;          // 0 = every record of the group
	float RadiusCm = 10000.f, MinRadiusCm = 0.f, TileRadiusCm = 0.f, Gain = 1.f;
	bool bShadow = false;
};

struct FWHCLConfig
{
	float K = 200.f, EmissiveK = 1.f, FadeS = 0.35f, RebuildMoveCm = 250.f, RebuildIntervalS = 0.2f, VolumetricGain = 1.f, ShadowRadiusCm = 2500.f, NightOffBelow = 0.01f, PoolHeadroom = 1.25f;
	int32 ShadowSlots = 4;
	float AmbR = 70.f, AmbSoft = 6.f, AmbGain = 0.16f, LayerYm = 14.f, HeroFillBase = 0.35f, HeroIrradianceScale = 1.f;
	TArray<FWHCLGroupCfg> Groups;
	bool Load(const FString& Path, FString& Err);
};

struct FWHCLData
{
	TArray<FWHCLRecord> Recs;
	FString Commit;
	int32 CatCounts[16] = {};
	bool bAnyDay = false;
	TArray<TMap<int64, TArray<int32>>> GroupGrid;   // per config group: 32 m XY cell -> record indices
	TMap<int64, TArray<int32>> AmbGrid;             // every record, for the ambient
	bool Load(const FString& Path, FString& Err);
	void Index(const FWHCLConfig& Cfg);
	static int64 CellKey(int32 CX, int32 CY) { return (int64(CX) << 32) ^ int64(uint32(CY)); }
};

struct FWHCLView
{
	FVector Loc = FVector::ZeroVector;
	FVector Fwd = FVector::ForwardVector, Right = FVector::RightVector, Up = FVector::UpVector;
	float HalfH = 0.f, HalfV = 0.f;    // radians; 0 = no frustum bonus
	bool bFrustum = false;
	bool SphereIn(const FVector& C, float R) const;
};

/** One selection pass: per group, the chosen record indices (top Budget by score, with a bonus for `Assigned`). */
struct FWHCLSelection
{
	TArray<TArray<int32>> Chosen;         // [group]
	TArray<int32> Candidates;             // [group] records inside the radius
};
void WHCLSelect(const FWHCLData& D, const FWHCLConfig& C, const FWHCLView& V, float BudgetScale, const TArray<TSet<int32>>* Assigned, FWHCLSelection& Out);

UCLASS()
class WEBHOMAGE_API AWHCityLights : public AActor
{
	GENERATED_BODY()
public:
	AWHCityLights();
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
	virtual void Tick(float Dt) override;

	/** Re-reads Content/Night/CityLights.json (tuning without a rebuild). */
	void ReloadConfig();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="CityLights") bool bActive = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="CityLights") int32 ActiveLights = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="CityLights") FLinearColor AmbientLower = FLinearColor::Black;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="CityLights") FLinearColor AmbientUpper = FLinearColor::Black;

private:
	struct FSlot { ULocalLightComponent* Comp = nullptr; int32 Rec = -1; float Fade = 0.f; bool bTarget = false; float AppliedIntensity = -1.f; bool bShadowOn = false; };
	struct FPool { int32 Group = 0; int32 Type = 0; TArray<FSlot> Slots; };

	FWHCLConfig Cfg;
	FWHCLData Data;
	TArray<FPool> Pools;                    // group * 3 + type
	TArray<TMap<int32, int32>> RecToSlot;   // [group] rec -> slot index within its pool
	FVector LastRebuildPos = FVector(1e18);
	float SinceRebuild = 1e9f;
	float NightK = 0.f, LastNightK = -1.f, LastGain = -1.f;
	FVector AmbLo = FVector::ZeroVector, AmbHi = FVector::ZeroVector;
	FVector AmbTargetLo = FVector::ZeroVector, AmbTargetHi = FVector::ZeroVector;   // last ambient sum (recomputed every rebuild interval)
	float AmbAcc = 0.f;
	float DebugT = 0.f;
	TObjectPtr<UMaterialParameterCollection> MPC;
	TWeakObjectPtr<AWHLookHeroLight> HeroLight;
	FString LoadError;

	void BuildPools();
	void DestroyPools();
	bool GetView(FWHCLView& V) const;
	void Rebuild(const FWHCLView& V);
	void AssignSlot(FPool& P, int32 SlotIdx, int32 RecIdx);
	void ApplyIntensity(FSlot& S, float Gain);
	void UpdateShadows(const FVector& HeroLoc);
	void UpdateAmbient(const FWHCLView& V, float Dt);
	void DriveHero();
	float ReadNightK() const;
	void DebugReport() const;
	FString CountsString() const;
};

UCLASS()
class WEBHOMAGE_API UWHCityLightsLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()
public:
	/** Loads the data, runs one selection at CamPos without spawning any component; returns JSON with per-group candidate / selected counts and K-scaled intensity. */
	UFUNCTION(BlueprintCallable, Category="CityLights")
	static FString SelfTest(FVector CamPos);
};
