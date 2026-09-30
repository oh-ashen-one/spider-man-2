// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
#include "Life/WHLifeCamRig.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/PlayerController.h"

AWHLifeCamRig::AWHLifeCamRig()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickGroup = TG_PrePhysics;
}

void AWHLifeCamRig::BeginPlay()
{
	Super::BeginPlay();
	if (GetCameraComponent()) { GetCameraComponent()->SetFieldOfView(FovDegrees); GetCameraComponent()->bConstrainAspectRatio = false; }
	T = 0.f; Place();
	if (UWorld* W = GetWorld()) if (APlayerController* PC = W->GetFirstPlayerController()) PC->SetViewTarget(this); // the game mode's pawn is not the view
}

void AWHLifeCamRig::Place()
{
	const float A = Duration > 0.f ? (bLoop ? FMath::Fmod(T, Duration) : FMath::Min(T, Duration)) / Duration : 0.f;
	FVector P = FMath::Lerp(Start, End, A); P.Z = Start.Z + EyeHeight;
	FVector Dir = (End - Start); Dir.Z = 0.f; Dir = Dir.GetSafeNormal();
	const float Sway = FMath::Sin(T * 0.55f) * YawSwayDeg;
	FRotator R = Dir.Rotation(); R.Yaw += Sway; R.Pitch = FMath::RadiansToDegrees(FMath::Atan2(LookHeightDelta, LookAheadCm));
	// gentle head-bob
	P.Z += FMath::Sin(T * 2.0f * PI * 1.7f) * 1.5f;
	SetActorLocationAndRotation(P, R);
}

void AWHLifeCamRig::Tick(float Dt)
{
	Super::Tick(Dt);
	T += Dt; Place();
}
