// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Look/WHLookHeroLight.h"
#include "Components/SpotLightComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Camera/PlayerCameraManager.h"
#include "Kismet/GameplayStatics.h"

static void InitHeroLight(ULocalLightComponent* L, const FLinearColor& C, float Candela, float Radius, bool bInverseExposure)
{
	L->SetMobility(EComponentMobility::Movable);
	L->SetLightColor(C);
	L->SetIntensityUnits(ELightUnits::Candelas);
	L->SetIntensity(Candela);
	L->SetCastShadows(false);
	L->SetVolumetricScatteringIntensity(0.f);
	L->SetIndirectLightingIntensity(0.f); // no GI from the hero lights: they must not light the street
	L->SetLightingChannels(false, true, false); // channel 1 only: the pawn's meshes are on 0 + 1, the world on 0
	L->SetAttenuationRadius(Radius);
	if (UPointLightComponent* PL = Cast<UPointLightComponent>(L)) { PL->SourceRadius = 15.f; PL->SetInverseExposureBlend(bInverseExposure ? 1.f : 0.f); }
}

AWHLookHeroLight::AWHLookHeroLight()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickGroup = TG_PostUpdateWork;
	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	Rim = CreateDefaultSubobject<USpotLightComponent>(TEXT("Rim"));
	Fill = CreateDefaultSubobject<UPointLightComponent>(TEXT("Fill"));
	Top = CreateDefaultSubobject<UPointLightComponent>(TEXT("Top"));
	Rim->SetupAttachment(RootComponent); Fill->SetupAttachment(RootComponent); Top->SetupAttachment(RootComponent);
	Rim->SetOuterConeAngle(50.f); Rim->SetInnerConeAngle(20.f);
}

void AWHLookHeroLight::SetPawnChannels(APawn* P)
{
	TInlineComponentArray<UPrimitiveComponent*> Prims; P->GetComponents(Prims);
	for (UPrimitiveComponent* C : Prims)
	{
		if (Cast<USkeletalMeshComponent>(C) || Cast<UStaticMeshComponent>(C)) C->SetLightingChannels(true, true, false);
	}
	LitPawn = P;
}

void AWHLookHeroLight::Tick(float Dt)
{
	Super::Tick(Dt);
	APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
	APawn* P = PC ? PC->GetPawn() : nullptr;
	if (!P) return;
	if (LitPawn.Get() != P) SetPawnChannels(P);
	if (!bLightsInit)
	{
		bLightsInit = true;
		const float Rel = bInverseExposure ? ExposureRelativeScale : 1.f;
		InitHeroLight(Rim, RimColor, RimIntensity * HourScale * Rel, 1500.f, bInverseExposure); InitHeroLight(Fill, FillColor, FillIntensity * HourScale * Rel, 1200.f, bInverseExposure);
		InitHeroLight(Top, FLinearColor(0.7f, 0.8f, 1.f), TopIntensity * HourScale * Rel, 1000.f, bInverseExposure);
		AppliedScale = HourScale;
	}
	if (!FMath::IsNearlyEqual(AppliedScale, HourScale, 1e-4f))
	{
		AppliedScale = HourScale;
		const float Rel = bInverseExposure ? ExposureRelativeScale : 1.f;
		Rim->SetIntensity(RimIntensity * HourScale * Rel); Fill->SetIntensity(FillIntensity * HourScale * Rel); Top->SetIntensity(TopIntensity * HourScale * Rel);
	}
	const FVector Hero = P->GetActorLocation() + FVector(0, 0, 40.f);
	FVector Cam = PC->PlayerCameraManager ? PC->PlayerCameraManager->GetCameraLocation() : Hero + FVector(-500, 0, 100);
	FVector ToCam = (Cam - Hero); ToCam.Z = 0; ToCam = ToCam.GetSafeNormal();
	if (ToCam.IsNearlyZero()) ToCam = FVector(-1, 0, 0);
	Fill->SetWorldLocation(Hero + ToCam * FillDistance + FVector(0, 0, FillHeight));
	const FVector RimPos = Hero - ToCam * RimDistance + FVector(0, 0, RimHeight);
	Rim->SetWorldLocation(RimPos);
	Rim->SetWorldRotation((Hero - RimPos).Rotation());
	Top->SetWorldLocation(Hero + FVector(0, 0, 320.f));
}
