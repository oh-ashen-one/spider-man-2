// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
// P4 Look (round 05): continuous time of day in ONE map. Placed in the rig level /Game/Look/Rigs/Look_Rig_tod by Scripts/build_look.py, which bakes the key
// table (Scripts/look_tod.py expansion of look_presets.json "tod") into KeysJson. Every frame the hour / weather / overrides changed, the driver interpolates
// every param (cyclic Catmull-Rom clamped to the neighbouring keys, so nothing overshoots) and applies it to the rig level's actors:
//   sun + moon (directional lights, atmosphere lights 0 / 1) moved on fixed declination circles, horizon fills, SkyLight, SkyAtmosphere (aerial perspective),
//   ExponentialHeightFog (+ second haze layer, volumetric fog), VolumetricCloud (component + a dynamic instance of its material: clouds at every hour),
//   the unbound PostProcessVolume (exposure, grade, bloom), MPC_City (night windows), the star dome and the night street lights level (Look_NightLights).
// Console:
//   wh.TimeOfDay <0..24>       hour (game clock; -1 = the map's default, see DefaultHour)        wh.TimeOfDaySpeed <h per s>   time-lapse rate (0 = frozen)
//   wh.Weather <0..1>          0 clear .. 1 overcast (-1 = keyed)                                  wh.ToDFreeze 1                stop applying (manual tuning)
//   wh.ToDSet <param> <v> [g b a]   pin one param (sweeps)   wh.ToDClear   drop pins   wh.ToDLoad <abs json>   replace the key table   wh.ToDDump   log the values
// Command line: -WHToD=<hour>  -WHToDSpeed=<h/s>  -WHToDKeys=<abs json>  -WHWeather=<0..1>
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WHLookTimeOfDay.generated.h"

class UDirectionalLightComponent;
class USkyLightComponent;
class USkyAtmosphereComponent;
class UExponentialHeightFogComponent;
class UVolumetricCloudComponent;
class UMaterialInstanceDynamic;
class UMaterialParameterCollection;
class APostProcessVolume;
class ULightComponent;
class UPrimitiveComponent;
class AWHLookHeroLight;

UCLASS()
class WEBHOMAGE_API AWHLookTimeOfDay : public AActor
{
	GENERATED_BODY()
public:
	AWHLookTimeOfDay();
	virtual void BeginPlay() override;
	virtual void Tick(float Dt) override;

	/** Key table (JSON, Scripts/look_tod.py format). Baked by Scripts/build_look.py. */
	UPROPERTY(EditAnywhere, Category = "TimeOfDay") FString KeysJson;
	/** Hour used when wh.TimeOfDay is -1 and no -WHToD is given. */
	UPROPERTY(EditAnywhere, Category = "TimeOfDay") float DefaultHour = 18.4f;
	/** Collection whose scalars the mpc.* params drive. */
	UPROPERTY(EditAnywhere, Category = "TimeOfDay") TObjectPtr<UMaterialParameterCollection> CityMpc;

	/** Current hour (read-only mirror for other code / debugging). */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "TimeOfDay") float Hour = 18.4f;

	bool LoadKeys(const FString& Json, const FString& What);
	void Pin(const FString& Name, const FVector4f& V, int32 N) { Pins.Add(FName(*Name), TPair<FVector4f, int32>(V, N)); bDirty = true; }
	void ClearPins() { Pins.Reset(); bDirty = true; }
	void Dump();
	void ForceApply() { bDirty = true; }

private:
	struct FKey { float H = 0.f; TMap<FName, FVector4f> P; };
	struct FBody { double Dec = 0.0, Shift = 0.0; };
	TArray<FKey> Keys;
	TMap<FName, int32> Dims;              // param -> number of components (1 = scalar)
	TMap<FName, FVector4f> Overcast;
	TMap<FName, TPair<FVector4f, int32>> Pins;
	double Lat = 40.7, GridOffset = 29.0;
	FBody Sun, Moon;
	bool bKeysOk = false, bDirty = true, bBound = false;
	float LastCvarHour = -2.f, LastWeather = -2.f, Weather = 0.f;
	double RebindAt = 0.0;
	int32 Rebinds = 0;

	TWeakObjectPtr<UDirectionalLightComponent> SunL, MoonL;
	TMap<FName, TWeakObjectPtr<UDirectionalLightComponent>> Fills;
	TWeakObjectPtr<USkyLightComponent> SkyL;
	TWeakObjectPtr<USkyAtmosphereComponent> Atm;
	TWeakObjectPtr<UExponentialHeightFogComponent> Fog;
	TWeakObjectPtr<UVolumetricCloudComponent> Cloud;
	TWeakObjectPtr<APostProcessVolume> Ppv;
	TWeakObjectPtr<AActor> Stars;
	UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> CloudMid;
	UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> StarsMid;
	struct FNightLight { TWeakObjectPtr<ULightComponent> L; float Base = 0.f; };
	TArray<FNightLight> NightLights;
	TArray<TWeakObjectPtr<AActor>> NightActors;
	TArray<TWeakObjectPtr<AWHLookHeroLight>> HeroLights;   // (round 06) the hero rim / fill lights of the night lights level: scaled by the `hero` key
	float LastLightsK = -1.f;
	bool bNightHidden = false;
	bool bSunLitWorld = true;
	float SunWorldK = -1.f;   // last diffuse/specular scale given to the sun (-1 = never set)

	bool bLapseLumen = false; TMap<FString, FString> LapseOrig; FString LapseSpec;
	void UpdateLapseLumen(bool bWant);
	void Bind();
	TMap<FName, FVector4f> Evaluate(float H, float W, float SunElev) const;
	void Apply(const TMap<FName, FVector4f>& V, float SunElev, float SunAz, float MoonElev, float MoonAz);
	void BodyDir(const FBody& B, float H, float& Elev, float& Az) const;
	static FRotator LightRot(float Elev, float Az);
	bool SetProp(UObject* Obj, UStruct* Struct, void* Container, FName Prop, const FVector4f& V, int32 N);
};
