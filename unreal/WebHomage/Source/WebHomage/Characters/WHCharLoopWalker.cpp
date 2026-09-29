// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Characters/WHCharLoopWalker.h"
#include "Characters/WHCharAnimInstance.h"
#include "Components/SkeletalMeshComponent.h"

AWHCharLoopWalker::AWHCharLoopWalker()
{
	PrimaryActorTick.bCanEverTick = true;
	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	Mesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Mesh"));
	Mesh->SetupAttachment(RootComponent);
	Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Mesh->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
}

void AWHCharLoopWalker::BeginPlay()
{
	Super::BeginPlay();
	Center = GetActorLocation();
	Theta = FMath::DegreesToRadians(StartAngle);
	Yaw = GetActorRotation().Yaw;
	LineD = LineStart;
	if (Mode == EWHWalkerMode::Loop || Mode == EWHWalkerMode::Line) Tick(0.f);
}

void AWHCharLoopWalker::Tick(float Dt)
{
	Super::Tick(Dt);
	UWHCharAnimInstance* AI = Mesh ? Cast<UWHCharAnimInstance>(Mesh->GetAnimInstance()) : nullptr;
	if (Mode == EWHWalkerMode::Loop)
	{
		const float S = FMath::Sin(Theta), C = FMath::Cos(Theta);
		const float Local = FMath::Max(10.f, FMath::Sqrt(FMath::Square(RadiusX * S) + FMath::Square(RadiusY * C)));
		const float Dir = bClockwise ? -1.f : 1.f;
		Theta += Dir * Speed * Dt / Local;
		const FVector P = Center + FVector(RadiusX * FMath::Cos(Theta), RadiusY * FMath::Sin(Theta), 0.f);
		const FVector T = FVector(-RadiusX * FMath::Sin(Theta), RadiusY * FMath::Cos(Theta), 0.f) * Dir;
		if (HopInterval > 0.f)
		{
			HopT += Dt;
			if (!bAir && HopT >= HopInterval) { HopT = 0.f; bAir = true; Vz = HopVelocity; }
			if (bAir) { Vz -= Gravity * Dt; Z += Vz * Dt; if (Z <= 0.f) { Z = 0.f; bAir = false; } }
		}
		SetActorLocationAndRotation(P + FVector(0, 0, Z), FRotator(0.f, T.Rotation().Yaw, 0.f));
		if (AI) { AI->ForcedSpeed = Speed; AI->bForceAir = bAir; AI->ForcedVerticalSpeed = Vz; }
	}
	else if (Mode == EWHWalkerMode::Line)
	{
		LineD += Speed * Dt;
		const float X = FMath::Fmod(LineD, FMath::Max(100.f, LineLength)) - LineLength * 0.5f;
		SetActorLocationAndRotation(Center + FVector(X, 0.f, 0.f), FRotator(0.f, Yaw, 0.f));
		if (AI) AI->ForcedSpeed = Speed;
	}
	else if (Mode == EWHWalkerMode::Turntable)
	{
		Yaw += TurntableDegPerSec * Dt;
		SetActorRotation(FRotator(0.f, Yaw, 0.f));
		if (AI) AI->ForcedSpeed = Speed;
	}
	else if (AI) AI->ForcedSpeed = 0.f;
}

void AWHCharLoopWalker::RestartLine()
{
	LineD = LineStart;
	if (Mode == EWHWalkerMode::Line) Tick(0.f);
}
