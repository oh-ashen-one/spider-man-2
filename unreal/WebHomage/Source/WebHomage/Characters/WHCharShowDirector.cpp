// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Characters/WHCharShowDirector.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/PlayerController.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

AWHCharShowDirector::AWHCharShowDirector()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickGroup = TG_PostUpdateWork;
	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
}

void AWHCharShowDirector::BeginPlay()
{
	Super::BeginPlay();
	FActorSpawnParameters P; P.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	Cam = GetWorld()->SpawnActor<ACameraActor>(ACameraActor::StaticClass(), GetActorTransform(), P);
	if (Cam) Cam->GetCameraComponent()->bConstrainAspectRatio = false;
	int32 Start = 0;
	if (FParse::Value(FCommandLine::Get(), TEXT("WHCharShot="), Start))
		for (int32 i = 0; i < FMath::Min(Start, Shots.Num()); ++i) T += Shots[i].Duration;
}

void AWHCharShowDirector::Tick(float Dt)
{
	Super::Tick(Dt);
	if (!Cam || Shots.Num() == 0) return;
	T += Dt;
	float Total = 0.f; for (const FWHShot& S : Shots) Total += S.Duration;
	float Tl = bLoop ? FMath::Fmod(T, FMath::Max(0.1f, Total)) : FMath::Min(T, Total - 1e-3f);
	int32 Idx = 0; for (; Idx < Shots.Num() - 1 && Tl >= Shots[Idx].Duration; ++Idx) Tl -= Shots[Idx].Duration;
	const FWHShot& S = Shots[Idx];
	if (!S.Target) return;
	const FVector Base = S.Target->GetActorLocation();
	const FVector Aim = Base + FVector(0, 0, S.AimHeight);
	const bool bCut = Idx != LastShot; LastShot = Idx;
	SmoothAim = bCut ? Aim : FMath::VInterpTo(SmoothAim, Aim, Dt, 12.f);
	const float Face = S.Target->GetActorRotation().Yaw;
	float Az = S.Azimuth;
	switch (S.Kind)
	{
	case EWHShotKind::Orbit: Az = S.Azimuth + S.OrbitDegPerSec * Tl; break;       // world-fixed orbit
	case EWHShotKind::Side: Az = Face + 90.f + S.Azimuth; break;
	case EWHShotKind::ThreeQuarter: Az = Face + 40.f + S.Azimuth; break;
	case EWHShotKind::Front: Az = Face + S.Azimuth; break;
	case EWHShotKind::Closeup: Az = Face + 25.f + S.Azimuth; break;
	default: break;
	}
	FVector Loc;
	if (S.Kind == EWHShotKind::Wide) Loc = S.WorldLocation;
	else
	{
		const FVector Dir = FRotator(0.f, Az, 0.f).Vector();
		Loc = (S.Kind == EWHShotKind::Orbit ? Aim : SmoothAim) + Dir * S.Distance + FVector(0, 0, S.CamHeight);
	}
	const FVector Look = (S.Kind == EWHShotKind::Orbit ? Aim : SmoothAim);
	Cam->SetActorLocationAndRotation(Loc, (Look - Loc).Rotation());
	Cam->GetCameraComponent()->SetFieldOfView(S.FOV);
	if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
		if (PC->GetViewTarget() != Cam) PC->SetViewTarget(Cam);
}
