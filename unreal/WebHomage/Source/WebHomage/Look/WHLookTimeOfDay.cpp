// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Look/WHLookTimeOfDay.h"
#include "WebHomage.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/SkyAtmosphereComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Components/VolumetricCloudComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/LightComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/PostProcessVolume.h"
#include "Engine/Level.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "HAL/IConsoleManager.h"
#include "Kismet/KismetMaterialLibrary.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialParameterCollection.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "UObject/UnrealType.h"
#include "Look/WHLookHeroLight.h"

static TAutoConsoleVariable<float> CVarToD(TEXT("wh.TimeOfDay"), -1.f, TEXT("P4 time of day, game-clock hour 0..24 (-1 = the map's default hour)"), ECVF_Default);
static TAutoConsoleVariable<float> CVarToDSpeed(TEXT("wh.TimeOfDaySpeed"), 0.f, TEXT("P4 time-lapse rate in game hours per game second (0 = frozen)"), ECVF_Default);
static TAutoConsoleVariable<float> CVarWeather(TEXT("wh.Weather"), -1.f, TEXT("P4 weather: 0 clear .. 1 overcast (-1 = keyed by the time of day)"), ECVF_Default);
static TAutoConsoleVariable<int32> CVarToDLapseLumen(TEXT("wh.ToDLapseLumen"), 1, TEXT("P4 (round 06): 1 = while the clock runs faster than 0.3 h/s (a time-lapse / time skip) Lumen's surface-cache lighting is told to refresh within a few frames "
	"(r.LumenScene.DirectLighting.UpdateFactor 32 -> 4, r.LumenScene.Radiosity.UpdateFactor 64 -> 4, Radiosity.Temporal.MaxFramesAccumulated 4 -> 1) and restored afterwards; "
	"0 = engine defaults (the lighting then lags the clock by 32-64 frames = 0.5-1 game hour at 2 h/s)"), ECVF_Default);
static TAutoConsoleVariable<int32> CVarToDFreeze(TEXT("wh.ToDFreeze"), 0, TEXT("P4: 1 = the time-of-day driver stops applying (manual look tuning)"), ECVF_Default);

static AWHLookTimeOfDay* FindDriver(UWorld* W)
{
	if (!W) return nullptr;
	TActorIterator<AWHLookTimeOfDay> It(W);
	return It ? *It : nullptr;
}

static FAutoConsoleCommandWithWorldAndArgs GCmdToDSet(TEXT("wh.ToDSet"), TEXT("wh.ToDSet <param> <v> [g b a]: pin a time-of-day param (sweeps)"),
	FConsoleCommandWithWorldAndArgsDelegate::CreateLambda([](const TArray<FString>& A, UWorld* W)
	{
		AWHLookTimeOfDay* D = FindDriver(W);
		if (!D || A.Num() < 2) return;
		FVector4f V(0.f, 0.f, 0.f, 1.f);
		const int32 N = FMath::Min(4, A.Num() - 1);
		for (int32 i = 0; i < N; ++i) V[i] = FCString::Atof(*A[i + 1]);
		D->Pin(A[0], V, N);
		UE_LOG(LogWebHomage, Display, TEXT("WH_TOD pin %s (%d values)"), *A[0], N);
	}));
static FAutoConsoleCommandWithWorldAndArgs GCmdToDClear(TEXT("wh.ToDClear"), TEXT("wh.ToDClear: drop every pinned param"),
	FConsoleCommandWithWorldAndArgsDelegate::CreateLambda([](const TArray<FString>&, UWorld* W) { if (AWHLookTimeOfDay* D = FindDriver(W)) D->ClearPins(); }));
static FAutoConsoleCommandWithWorldAndArgs GCmdToDLoad(TEXT("wh.ToDLoad"), TEXT("wh.ToDLoad <abs file>: replace the key table (Scripts/look_tod.py text format)"),
	FConsoleCommandWithWorldAndArgsDelegate::CreateLambda([](const TArray<FString>& A, UWorld* W)
	{
		AWHLookTimeOfDay* D = FindDriver(W);
		FString Text;
		if (D && A.Num() >= 1 && FFileHelper::LoadFileToString(Text, *A[0])) D->LoadKeys(Text, A[0]);
		else UE_LOG(LogWebHomage, Warning, TEXT("WH_TOD load failed (%s)"), A.Num() ? *A[0] : TEXT("no file"));
	}));
static FAutoConsoleCommandWithWorldAndArgs GCmdToDDump(TEXT("wh.ToDDump"), TEXT("wh.ToDDump: log the current time-of-day values"),
	FConsoleCommandWithWorldAndArgsDelegate::CreateLambda([](const TArray<FString>&, UWorld* W) { if (AWHLookTimeOfDay* D = FindDriver(W)) D->Dump(); }));

AWHLookTimeOfDay::AWHLookTimeOfDay()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickGroup = TG_PrePhysics;
	PrimaryActorTick.bTickEvenWhenPaused = true;
	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
}

bool AWHLookTimeOfDay::LoadKeys(const FString& Text, const FString& What)
{
	TArray<FKey> NewKeys; TMap<FName, FVector4f> NewOc; TMap<FName, int32> NewDims;
	TArray<FString> Lines; Text.ParseIntoArrayLines(Lines);
	for (const FString& Raw : Lines)
	{
		const FString L = Raw.TrimStartAndEnd();
		if (L.IsEmpty() || L.StartsWith(TEXT("#"))) continue;
		TArray<FString> T; L.ParseIntoArrayWS(T);
		if (T.Num() < 2) continue;
		if (T[0] == TEXT("sun") && T.Num() >= 5) { Lat = FCString::Atod(*T[1]); Sun.Dec = FCString::Atod(*T[2]); GridOffset = FCString::Atod(*T[3]); Sun.Shift = FCString::Atod(*T[4]); }
		else if (T[0] == TEXT("moon") && T.Num() >= 3) { Moon.Dec = FCString::Atod(*T[1]); Moon.Shift = FCString::Atod(*T[2]); }
		else if (T[0] == TEXT("default")) DefaultHour = FCString::Atof(*T[1]);
		else if (T[0] == TEXT("key")) { FKey K; K.H = FCString::Atof(*T[1]); NewKeys.Add(K); }
		else if ((T[0] == TEXT("p") || T[0] == TEXT("oc")) && T.Num() >= 3)
		{
			FVector4f V(0.f, 0.f, 0.f, 1.f);
			const int32 N = FMath::Min(4, T.Num() - 2);
			for (int32 i = 0; i < N; ++i) V[i] = FCString::Atof(*T[i + 2]);
			const FName Nm(*T[1]);
			NewDims.Add(Nm, N);
			if (T[0] == TEXT("oc")) NewOc.Add(Nm, V);
			else if (NewKeys.Num()) NewKeys.Last().P.Add(Nm, V);
		}
	}
	if (NewKeys.Num() < 2) { UE_LOG(LogWebHomage, Error, TEXT("WH_TOD %s: %d keys, need >= 2"), *What, NewKeys.Num()); return false; }
	NewKeys.Sort([](const FKey& A, const FKey& B) { return A.H < B.H; });
	Keys = MoveTemp(NewKeys); Overcast = MoveTemp(NewOc); Dims = MoveTemp(NewDims);
	bKeysOk = true; bDirty = true;
	UE_LOG(LogWebHomage, Display, TEXT("WH_TOD keys %s: %d keys, %d params, %d overcast, sun dec %.1f shift %.2f, moon dec %.1f shift %.2f"), *What, Keys.Num(), Keys[0].P.Num(), Overcast.Num(), Sun.Dec, Sun.Shift, Moon.Dec, Moon.Shift);
	return true;
}

void AWHLookTimeOfDay::BeginPlay()
{
	Super::BeginPlay();
	const TCHAR* Cmd = FCommandLine::Get();
	FString File, Text;
	if (FParse::Value(Cmd, TEXT("WHToDKeys="), File) && FFileHelper::LoadFileToString(Text, *File)) LoadKeys(Text, File);
	else LoadKeys(KeysJson, TEXT("baked"));
	float F;
	if (FParse::Value(Cmd, TEXT("WHToD="), F)) CVarToD->Set(F, ECVF_SetByCommandline);
	if (FParse::Value(Cmd, TEXT("WHToDSpeed="), F)) CVarToDSpeed->Set(F, ECVF_SetByCommandline);
	if (FParse::Value(Cmd, TEXT("WHWeather="), F)) CVarWeather->Set(F, ECVF_SetByCommandline);
	Hour = DefaultHour;
	Bind();
}

void AWHLookTimeOfDay::Bind()
{
	UWorld* W = GetWorld();
	if (!W) return;
	ULevel* Mine = GetLevel();
	auto InMine = [Mine](const AActor* A) { return A && A->GetLevel() == Mine; };
	Fills.Reset(); NightLights.Reset(); NightActors.Reset(); HeroLights.Reset();
	int32 NNight = 0;
	for (TActorIterator<AActor> It(W); It; ++It)
	{
		AActor* A = *It;
		const FString Pkg = A->GetLevel() ? A->GetLevel()->GetOutermost()->GetName() : FString();
		if (Pkg.Contains(TEXT("Look_NightLights")))
		{
			NightActors.Add(A); ++NNight;
			if (AWHLookHeroLight* Hl = Cast<AWHLookHeroLight>(A)) { HeroLights.Add(Hl); continue; }   // initialises its own intensities on its first tick; hidden by day with its level; scaled by the `hero` key
			TInlineComponentArray<ULightComponent*> Ls; A->GetComponents(Ls);
			for (ULightComponent* L : Ls) NightLights.Add({ L, L->Intensity });
			continue;
		}
		if (!InMine(A)) continue;
		if (ADirectionalLight* D = Cast<ADirectionalLight>(A))
		{
			UDirectionalLightComponent* C = Cast<UDirectionalLightComponent>(D->GetLightComponent());
			if (A->ActorHasTag(TEXT("WHSun"))) SunL = C;
			else if (A->ActorHasTag(TEXT("WHMoon"))) MoonL = C;
			else for (const TCHAR* Dn : { TEXT("N"), TEXT("E"), TEXT("S"), TEXT("W") })
				if (A->ActorHasTag(FName(*(FString(TEXT("WHFill_")) + Dn)))) Fills.Add(FName(Dn), C);
			continue;
		}
		if (APostProcessVolume* P = Cast<APostProcessVolume>(A)) { if (P->bUnbound) Ppv = P; continue; }
		if (A->ActorHasTag(TEXT("WHStars"))) { Stars = A; continue; }
		if (USkyLightComponent* C = A->FindComponentByClass<USkyLightComponent>()) SkyL = C;
		if (USkyAtmosphereComponent* C = A->FindComponentByClass<USkyAtmosphereComponent>()) Atm = C;
		if (UExponentialHeightFogComponent* C = A->FindComponentByClass<UExponentialHeightFogComponent>()) Fog = C;
		if (UVolumetricCloudComponent* C = A->FindComponentByClass<UVolumetricCloudComponent>()) Cloud = C;
	}
	if (Cloud.IsValid() && !CloudMid && Cloud->GetMaterial())
	{
		CloudMid = UMaterialInstanceDynamic::Create(Cloud->GetMaterial(), this);
		Cloud->SetMaterial(CloudMid);
	}
	if (Stars.IsValid() && !StarsMid)
		if (UStaticMeshComponent* S = Stars->FindComponentByClass<UStaticMeshComponent>())
			if (S->GetMaterial(0)) { StarsMid = UMaterialInstanceDynamic::Create(S->GetMaterial(0), this); S->SetMaterial(0, StarsMid); }
	if (!CityMpc) CityMpc = LoadObject<UMaterialParameterCollection>(nullptr, TEXT("/Game/City/Materials/MPC_City.MPC_City"));
	bBound = SunL.IsValid() && Ppv.IsValid();
	LastLightsK = -1.f; bNightHidden = false; bDirty = true;
	UE_LOG(LogWebHomage, Display, TEXT("WH_TOD bind: sun %d moon %d fills %d sky %d atm %d fog %d cloud %d (mid %d) ppv %d stars %d mpc %d night actors %d lights %d"),
		SunL.IsValid(), MoonL.IsValid(), Fills.Num(), SkyL.IsValid(), Atm.IsValid(), Fog.IsValid(), Cloud.IsValid(), CloudMid != nullptr, Ppv.IsValid(), Stars.IsValid(),
		CityMpc != nullptr, NNight, NightLights.Num());
}

void AWHLookTimeOfDay::BodyDir(const FBody& B, float H, float& Elev, float& Az) const
{
	// same maths as Scripts/look_tod.py body_dir: a body on a fixed declination circle, hour angle 15 deg / h from the meridian
	const double Ha = FMath::DegreesToRadians(15.0 * (H - 12.0 - B.Shift)), La = FMath::DegreesToRadians(Lat), D = FMath::DegreesToRadians(B.Dec);
	const double E = FMath::Asin(FMath::Sin(La) * FMath::Sin(D) + FMath::Cos(La) * FMath::Cos(D) * FMath::Cos(Ha));
	const double A = FMath::Atan2(FMath::Sin(Ha), FMath::Cos(Ha) * FMath::Sin(La) - FMath::Tan(D) * FMath::Cos(La));
	Elev = (float)FMath::RadiansToDegrees(E);
	Az = (float)FMath::Fmod(FMath::RadiansToDegrees(A) + 180.0 - GridOffset + 720.0, 360.0);
}

FRotator AWHLookTimeOfDay::LightRot(float Elev, float Az)
{
	// build_look.py sun_rotator: compass azimuth (east = 90) in the city export frame, UE X east, Y south (north = -Y), Z up; the light travels away from the body
	const double E = FMath::DegreesToRadians(Elev), A = FMath::DegreesToRadians(Az);
	const FVector ToBody(FMath::Sin(A) * FMath::Cos(E), -FMath::Cos(A) * FMath::Cos(E), FMath::Sin(E));
	return (-ToBody).Rotation();
}

TMap<FName, FVector4f> AWHLookTimeOfDay::Evaluate(float H, float Wx, float SunElev) const
{
	static const FName CutoffName(TEXT("fog.FogCutoffDistance"));
	TMap<FName, FVector4f> Out;
	const int32 N = Keys.Num();
	// segment i -> i+1 (cyclic) containing H
	int32 I = N - 1;
	for (int32 k = 0; k < N; ++k) if (Keys[k].H <= H) I = k;
	auto KH = [&](int32 k) { const int32 m = ((k % N) + N) % N; const float Wrap = 24.f * (float)((k - m) / N); return Keys[m].H + Wrap; };
	auto KP = [&](int32 k) -> const TMap<FName, FVector4f>& { return Keys[((k % N) + N) % N].P; };
	float h0 = KH(I - 1), h1 = KH(I), h2 = KH(I + 1), h3 = KH(I + 2);
	float Hx = H;
	if (Hx < h1) Hx += 24.f;
	if (h2 <= h1) { h2 += 24.f; h3 += 24.f; }
	const float Seg = FMath::Max(1e-3f, h2 - h1);
	const float t = FMath::Clamp((Hx - h1) / Seg, 0.f, 1.f);
	const float t2 = t * t, t3 = t2 * t;
	const float b0 = 2 * t3 - 3 * t2 + 1, b1 = t3 - 2 * t2 + t, b2 = -2 * t3 + 3 * t2, b3 = t3 - t2;
	const TMap<FName, FVector4f>& P0 = KP(I - 1); const TMap<FName, FVector4f>& P1 = KP(I); const TMap<FName, FVector4f>& P2 = KP(I + 1); const TMap<FName, FVector4f>& P3 = KP(I + 2);
	for (const auto& It : P1)
	{
		const FVector4f& V1 = It.Value;
		const FVector4f* pV2 = P2.Find(It.Key); const FVector4f V2 = pV2 ? *pV2 : V1;
		const FVector4f* pV0 = P0.Find(It.Key); const FVector4f V0 = pV0 ? *pV0 : V1;
		const FVector4f* pV3 = P3.Find(It.Key); const FVector4f V3 = pV3 ? *pV3 : V2;
		FVector4f R;
		for (int32 c = 0; c < 4; ++c)
		{
			const float m1 = (V2[c] - V0[c]) / FMath::Max(1e-3f, h2 - h0) * Seg;
			const float m2 = (V3[c] - V1[c]) / FMath::Max(1e-3f, h3 - h1) * Seg;
			const float v = b0 * V1[c] + b1 * m1 + b2 * V2[c] + b3 * m2;
			R[c] = FMath::Clamp(v, FMath::Min(V1[c], V2[c]), FMath::Max(V1[c], V2[c]));
		}
		// (round 05) the fog cutoff is a switch, not a blend: 0 = fog everywhere incl. the sky, > 0 = no height fog past that distance (the night sky stays clear
		// above a fogged far shore). An in-between value would un-fog the near city, so it steps at the middle of the segment (a dark hour at night).
		if (It.Key == CutoffName) R = t < 0.5f ? V1 : V2;
		Out.Add(It.Key, R);
	}
	// weather: daylight params blend toward the overcast set (night is untouched)
	const float DayK = FMath::SmoothStep(-6.f, 4.f, SunElev) * FMath::Clamp(Wx, 0.f, 1.f);
	if (DayK > 0.f)
		for (const auto& It : Overcast)
			if (FVector4f* V = Out.Find(It.Key)) *V = *V + (It.Value - *V) * DayK;
	for (const auto& It : Pins)
	{
		FVector4f& V = Out.FindOrAdd(It.Key);
		for (int32 c = 0; c < It.Value.Value; ++c) V[c] = It.Value.Key[c];
	}
	return Out;
}

bool AWHLookTimeOfDay::SetProp(UObject* Obj, UStruct* Struct, void* Container, FName Prop, const FVector4f& V, int32 N)
{
	FProperty* P = Struct ? Struct->FindPropertyByName(Prop) : nullptr;
	if (!P) return false;
	void* Addr = P->ContainerPtrToValuePtr<void>(Container);
	auto Near = [](double a, double b) { return FMath::Abs(a - b) <= 1e-6 * FMath::Max(1.0, FMath::Abs(b)); };
	if (FFloatProperty* F = CastField<FFloatProperty>(P)) { if (Near(F->GetPropertyValue(Addr), V.X)) return false; F->SetPropertyValue(Addr, V.X); return true; }
	if (FDoubleProperty* D = CastField<FDoubleProperty>(P)) { if (Near(D->GetPropertyValue(Addr), V.X)) return false; D->SetPropertyValue(Addr, V.X); return true; }
	if (FIntProperty* I = CastField<FIntProperty>(P)) { const int32 x = FMath::RoundToInt(V.X); if (I->GetPropertyValue(Addr) == x) return false; I->SetPropertyValue(Addr, x); return true; }
	if (FStructProperty* S = CastField<FStructProperty>(P))
	{
		if (S->Struct == TBaseStructure<FLinearColor>::Get())
		{
			FLinearColor* C = (FLinearColor*)Addr; const FLinearColor New(V.X, V.Y, V.Z, N >= 4 ? V.W : C->A);
			if (*C == New) return false; *C = New; return true;
		}
		if (S->Struct == TBaseStructure<FColor>::Get())
		{
			FColor* C = (FColor*)Addr;
			const FColor New((uint8)FMath::Clamp(FMath::RoundToInt(255.f * V.X), 0, 255), (uint8)FMath::Clamp(FMath::RoundToInt(255.f * V.Y), 0, 255),
				(uint8)FMath::Clamp(FMath::RoundToInt(255.f * V.Z), 0, 255), C->A);
			if (*C == New) return false; *C = New; return true;
		}
		if (S->Struct == TBaseStructure<FVector4>::Get())
		{
			FVector4* C = (FVector4*)Addr; const FVector4 New(V.X, V.Y, V.Z, N >= 4 ? V.W : C->W);
			if (*C == New) return false; *C = New; return true;
		}
		if (S->Struct == TBaseStructure<FVector>::Get())
		{
			FVector* C = (FVector*)Addr; const FVector New(V.X, V.Y, V.Z);
			if (*C == New) return false; *C = New; return true;
		}
	}
	return false;
}

void AWHLookTimeOfDay::Apply(const TMap<FName, FVector4f>& V, float SunElev, float SunAz, float MoonElev, float MoonAz)
{
	auto G = [&](const TCHAR* N, float Def) { const FVector4f* p = V.Find(FName(N)); return p ? p->X : Def; };
	auto GC = [&](const TCHAR* N, const FLinearColor& Def) { const FVector4f* p = V.Find(FName(N)); return p ? FLinearColor(p->X, p->Y, p->Z, p->W) : Def; };
	auto Dim = [&](const FName& N) { const int32* d = Dims.Find(N); return d ? *d : 1; };
	// --- sun / moon / fills
	if (UDirectionalLightComponent* S = SunL.Get())
	{
		S->GetOwner()->SetActorRotation(LightRot(SunElev, SunAz));
		// (round 06) the sun's twilight light fades out between -16 and -26 deg (it was cut to 0 at -20 deg, a step in the sky at 21:00 / 05:00)
		S->SetIntensity(G(TEXT("sun.Intensity"), 40000.f) * FMath::SmoothStep(-26.f, -16.f, SunElev));
		S->SetTemperature(G(TEXT("sun.Temperature"), 5500.f));
		S->SetLightSourceAngle(G(TEXT("sun.LightSourceAngle"), 0.53f));
		const float Dk = G(TEXT("sun.DiskScale"), 1.f); S->SetAtmosphereSunDiskColorScale(FLinearColor(Dk, Dk, Dk, 1.f));
		// UE's per-pixel transmittance still lights meshes from a sun a few degrees under the horizon (round 05 tours: a sunlit city with cast shadows at 19:48,
		// sun -6.7 deg; switching the light off lighting channel 0 did NOT stop it). Under the horizon the sun keeps its intensity for the sky, the aerial
		// perspective and the clouds (twilight glow), but its diffuse / specular contribution to surfaces ramps to 0 between +3.5 and -2.5 deg.
		// (round 06) the ramp was +0.5..-2.5 deg = 16 game minutes (the lapse's 19:12 dip); the sun moves ~11.3 deg / h there, 6 deg = 32 min at 2 h/s = 64 frames.
		const float WorldK = FMath::SmoothStep(-2.5f, 3.5f, SunElev);
		if (FMath::Abs(WorldK - SunWorldK) > 1e-3f || (WorldK == 0.f) != (SunWorldK == 0.f))
		{
			S->SetDiffuseScale(WorldK); S->SetSpecularScale(WorldK); SunWorldK = WorldK;
			if (!bSunLitWorld) { S->SetLightingChannels(true, false, false); bSunLitWorld = true; }   // undo the round-05 channel switch if a map still carries it
		}
		S->SetCastShadows(WorldK > 0.02f);
	}
	if (UDirectionalLightComponent* M = MoonL.Get())
	{
		M->GetOwner()->SetActorRotation(LightRot(MoonElev, MoonAz));
		const float K = FMath::SmoothStep(-1.f, 6.f, MoonElev) * G(TEXT("moon.Intensity"), 0.f);
		M->SetIntensity(K);
		M->SetTemperature(G(TEXT("moon.Temperature"), 5600.f));
		// (round 06) one shadowing directional light at a time, and the switch must not show: the moon takes over once the sun's surface light is gone (SunWorldK 0) and its own
		// lux is still tiny (the keys bring moon.Intensity in from 0 over >= 40 game minutes after 20:00), so turning its shadows on changes under 5 % of a moonlit surface.
		M->SetCastShadows(K > 0.4f && SunWorldK < 0.01f);
		M->SetVisibility(K > 0.001f);
	}
	for (const auto& F : Fills)
		if (UDirectionalLightComponent* C = F.Value.Get())
		{
			const float Lux = G(*(FString(TEXT("fill.")) + F.Key.ToString()), 0.f);
			C->SetIntensity(Lux); C->SetVisibility(Lux > 1e-4f);
			C->SetTemperature(G(*(FString(TEXT("fillT.")) + F.Key.ToString()), 6500.f));
		}
	if (USkyLightComponent* S = SkyL.Get())
	{
		S->SetIntensity(G(TEXT("sky.Intensity"), 1.f));
		S->SetLightColor(GC(TEXT("sky.LightColor"), FLinearColor::White));
	}
	// --- reflection-driven components
	bool bAtm = false, bFog = false, bCloud = false, bPp = false;
	for (const auto& It : V)
	{
		const FString K = It.Key.ToString();
		int32 Dot; if (!K.FindChar(TEXT('.'), Dot)) continue;
		const FString T = K.Left(Dot); const FName Pn(*K.Mid(Dot + 1));
		const int32 N = Dim(It.Key);
		if (T == TEXT("atm") && Atm.IsValid()) bAtm |= SetProp(Atm.Get(), Atm->GetClass(), Atm.Get(), Pn, It.Value, N);
		else if (T == TEXT("fog") && Fog.IsValid()) bFog |= SetProp(Fog.Get(), Fog->GetClass(), Fog.Get(), Pn, It.Value, N);
		else if (T == TEXT("fog2") && Fog.IsValid())
		{
			if (FStructProperty* SP = CastField<FStructProperty>(Fog->GetClass()->FindPropertyByName(TEXT("SecondFogData"))))
				bFog |= SetProp(Fog.Get(), SP->Struct, SP->ContainerPtrToValuePtr<void>(Fog.Get()), Pn, It.Value, N);
		}
		else if (T == TEXT("moonc") && MoonL.IsValid()) { if (SetProp(MoonL.Get(), MoonL->GetClass(), MoonL.Get(), Pn, It.Value, N)) MoonL->MarkRenderStateDirty(); }   // (round 06) e.g. moonc.LightSourceAngle (disk size), moonc.AtmosphereSunDiskColorScale, moonc.CloudScatteredLuminanceScale
		else if (T == TEXT("sunc") && SunL.IsValid()) { if (SetProp(SunL.Get(), SunL->GetClass(), SunL.Get(), Pn, It.Value, N)) SunL->MarkRenderStateDirty(); }
		else if (T == TEXT("cloudc") && Cloud.IsValid()) bCloud |= SetProp(Cloud.Get(), Cloud->GetClass(), Cloud.Get(), Pn, It.Value, N);
		else if (T == TEXT("cloud") && CloudMid) CloudMid->SetScalarParameterValue(Pn, It.Value.X);
		else if (T == TEXT("cloudv") && CloudMid) CloudMid->SetVectorParameterValue(Pn, FLinearColor(It.Value.X, It.Value.Y, It.Value.Z, It.Value.W));
		else if (T == TEXT("pp") && Ppv.IsValid())
		{
			UScriptStruct* PS = FPostProcessSettings::StaticStruct();
			bPp |= SetProp(Ppv.Get(), PS, &Ppv->Settings, Pn, It.Value, N);
			if (FBoolProperty* Ov = CastField<FBoolProperty>(PS->FindPropertyByName(FName(*(TEXT("bOverride_") + Pn.ToString())))))
				Ov->SetPropertyValue(Ov->ContainerPtrToValuePtr<void>(&Ppv->Settings), true);
		}
		else if (T == TEXT("mpc") && CityMpc) UKismetMaterialLibrary::SetScalarParameterValue(this, CityMpc, Pn, It.Value.X);
	}
	if (bAtm) Atm->MarkRenderStateDirty();
	if (bFog) Fog->MarkRenderStateDirty();
	if (bCloud) Cloud->MarkRenderStateDirty();
	// --- hero lights follow the `hero` key (round 06)
	{
		const float Hs = G(TEXT("hero"), 1.f), Fs = G(TEXT("herofill"), 1.f);
		for (const auto& H : HeroLights) if (AWHLookHeroLight* Hl = H.Get()) { Hl->HourScale = Hs; Hl->ExternalFillScale = Fs; }
	}
	// --- stars + night street lights
	const float StarK = G(TEXT("stars"), 0.f);
	if (Stars.IsValid())
	{
		Stars->SetActorHiddenInGame(StarK < 0.01f);
		if (StarsMid) StarsMid->SetScalarParameterValue(TEXT("Gain"), StarK);
	}
	const float LK = FMath::Clamp(G(TEXT("lights"), 0.f), 0.f, 4.f);
	if (FMath::Abs(LK - LastLightsK) > 0.004f)
	{
		LastLightsK = LK;
		const bool bHide = LK < 0.02f;
		if (bHide != bNightHidden)
			for (const auto& A : NightActors) if (A.IsValid()) A->SetActorHiddenInGame(bHide);
		bNightHidden = bHide;
		if (!bHide) for (const FNightLight& L : NightLights) if (L.L.IsValid()) L.L->SetIntensity(L.Base * LK);
	}
}

void AWHLookTimeOfDay::UpdateLapseLumen(bool bWant)
{
	// (round 06) Lumen refreshes its surface-cache lighting over SurfaceCacheTexels / UpdateFactor texels per FRAME (direct 32, radiosity 64, radiosity history 4 frames): at 2 h/s that is
	// 0.5-1 game hour of stale bounce light after the sun is gone (hold 1: lapse mean 211 at 20:30 against 43 for a settled still). While the clock runs fast the refresh is made fast.
	static const TCHAR* Names[3] = { TEXT("r.LumenScene.DirectLighting.UpdateFactor"), TEXT("r.LumenScene.Radiosity.UpdateFactor"), TEXT("r.LumenScene.Radiosity.Temporal.MaxFramesAccumulated") };
	static const int32 Fast[3] = { 4, 4, 1 };
	if (bWant == bLapseLumen) return;
	for (int32 i = 0; i < 3; ++i)
	{
		IConsoleVariable* V = IConsoleManager::Get().FindConsoleVariable(Names[i]);
		if (!V) continue;
		if (bWant) { LapseOrig[i] = V->GetInt(); V->Set(Fast[i], ECVF_SetByCode); }
		else V->Set(LapseOrig[i], ECVF_SetByCode);
	}
	bLapseLumen = bWant;
	UE_LOG(LogWebHomage, Display, TEXT("WH_TOD lapse lumen %s (clock %.2f h/s)"), bWant ? TEXT("fast refresh ON") : TEXT("defaults restored"), CVarToDSpeed.GetValueOnGameThread());
}

void AWHLookTimeOfDay::Dump()
{
	float Se, Sa, Me, Ma; BodyDir(Sun, Hour, Se, Sa); BodyDir(Moon, Hour, Me, Ma);
	UE_LOG(LogWebHomage, Display, TEXT("WH_TOD dump hour %.3f weather %.2f sun %.1f/%.1f moon %.1f/%.1f pins %d"), Hour, Weather, Se, Sa, Me, Ma, Pins.Num());
	if (!bKeysOk) return;
	TMap<FName, FVector4f> V = Evaluate(Hour, Weather, Se);
	V.KeySort([](const FName& A, const FName& B) { return A.LexicalLess(B); });
	for (const auto& It : V) UE_LOG(LogWebHomage, Display, TEXT("WH_TOD   %s = %g %g %g %g"), *It.Key.ToString(), It.Value.X, It.Value.Y, It.Value.Z, It.Value.W);
}

void AWHLookTimeOfDay::Tick(float Dt)
{
	Super::Tick(Dt);
	if (!bKeysOk) return;
	UWorld* W = GetWorld();
	// sublevels (the night street lights level) can become visible after this actor's BeginPlay: bind again a few times early on, and until the rig is found
	if (W && (!bBound || Rebinds < 3) && W->GetTimeSeconds() >= RebindAt) { ++Rebinds; RebindAt = W->GetTimeSeconds() + (Rebinds < 3 ? 1.5 : 1.0); Bind(); }
	if (!bBound) return;
	const float Cv = CVarToD.GetValueOnGameThread();
	if (Cv != LastCvarHour) { LastCvarHour = Cv; Hour = Cv >= 0.f ? FMath::Fmod(Cv, 24.f) : DefaultHour; bDirty = true; }
	const float Speed = CVarToDSpeed.GetValueOnGameThread();
	if (Speed != 0.f) { Hour = FMath::Fmod(Hour + Speed * Dt + 48.f, 24.f); bDirty = true; }
	UpdateLapseLumen(FMath::Abs(Speed) >= 0.3f && CVarToDLapseLumen.GetValueOnGameThread() != 0);
	const float Wc = CVarWeather.GetValueOnGameThread();
	if (Wc != LastWeather) { LastWeather = Wc; bDirty = true; }
	if (CVarToDFreeze.GetValueOnGameThread() != 0 || !bDirty) return;
	bDirty = false;
	float Se, Sa, Me, Ma; BodyDir(Sun, Hour, Se, Sa); BodyDir(Moon, Hour, Me, Ma);
	if (Wc >= 0.f) Weather = Wc;
	else { const TMap<FName, FVector4f> K = Evaluate(Hour, 0.f, Se); const FVector4f* w = K.Find(TEXT("weather")); Weather = w ? w->X : 0.f; }
	Apply(Evaluate(Hour, Weather, Se), Se, Sa, Me, Ma);
	static double LastLog = -100.0;
	if (W && W->GetTimeSeconds() - LastLog > 2.0) { LastLog = W->GetTimeSeconds(); UE_LOG(LogWebHomage, Display, TEXT("WH_TOD hour %.3f weather %.2f sun %.1f/%.1f moon %.1f/%.1f"), Hour, Weather, Se, Sa, Me, Ma); }
}
