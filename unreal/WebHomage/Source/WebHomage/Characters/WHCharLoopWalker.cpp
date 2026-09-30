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
	HopT = FirstHopDelay >= 0.f ? HopInterval - FirstHopDelay : 0.f;
	if (Mode == EWHWalkerMode::Loop || Mode == EWHWalkerMode::Line) Tick(0.f);
}

void AWHCharLoopWalker::Tick(float Dt)
{
	Super::Tick(Dt);
	UWHCharAnimInstance* AI = Mesh ? Cast<UWHCharAnimInstance>(Mesh->GetAnimInstance()) : nullptr;
	if (AI) AI->IdleOffset = AnimOffset;
	if (Mode == EWHWalkerMode::Loop)
	{
		const float S = FMath::Sin(Theta), C = FMath::Cos(Theta);
		const float Local = FMath::Max(10.f, FMath::Sqrt(FMath::Square(RadiusX * S) + FMath::Square(RadiusY * C)));
		const float Dir = bClockwise ? -1.f : 1.f;
		Theta += Dir * Speed * Dt / Local;
		const FVector P = Center + FVector(RadiusX * FMath::Cos(Theta), RadiusY * FMath::Sin(Theta), 0.f);
		const FVector T = FVector(-RadiusX * FMath::Sin(Theta), RadiusY * FMath::Cos(Theta), 0.f) * Dir;
		TickHop(Dt);
		SetActorLocationAndRotation(P + FVector(0, 0, Z), FRotator(0.f, T.Rotation().Yaw, 0.f));
		if (AI) { AI->ForcedSpeed = Speed; AI->bForceAir = bAir; AI->ForcedVerticalSpeed = Vz; AI->TakeoffTime = TakeoffT; }
	}
	else if (Mode == EWHWalkerMode::Line)
	{
		LineD += Speed * Dt;
		const float X = FMath::Fmod(LineD, FMath::Max(100.f, LineLength)) - LineLength * 0.5f;
		TickHop(Dt);
		SetActorLocationAndRotation(Center + FRotator(0.f, Yaw, 0.f).Vector() * X + FVector(0, 0, Z), FRotator(0.f, Yaw, 0.f));
		if (AI) { AI->ForcedSpeed = Speed; AI->bForceAir = bAir; AI->ForcedVerticalSpeed = Vz; AI->TakeoffTime = TakeoffT; }
	}
	else if (Mode == EWHWalkerMode::Turntable)
	{
		Yaw += TurntableDegPerSec * Dt;
		SetActorRotation(FRotator(0.f, Yaw, 0.f));
		if (AI) AI->ForcedSpeed = Speed;
	}
	else if (AI) AI->ForcedSpeed = 0.f;
}

void AWHCharLoopWalker::TickHop(float Dt)
{
	if (HopInterval <= 0.f) return;
	HopT += Dt;
	if (!bAir && TakeoffT < 0.f && HopT >= HopInterval) { HopT = 0.f; TakeoffT = 0.f; }
	if (TakeoffT >= 0.f)
	{
		// grounded anticipation (the crouch is animated by UWHCharAnimInstance::Takeoff), then leave the ground
		TakeoffT += Dt;
		if (TakeoffT >= TakeoffTime) { TakeoffT = -1.f; bAir = true; Vz = HopVelocity; }
	}
	if (bAir) { Vz -= Gravity * Dt; Z += Vz * Dt; if (Z <= 0.f) { Z = 0.f; bAir = false; Vz = 0.f; } }
}

void AWHCharLoopWalker::RestartLine()
{
	LineD = LineStart;
	HopT = FirstHopDelay >= 0.f ? HopInterval - FirstHopDelay : 0.f; TakeoffT = -1.f; bAir = false; Z = 0.f; Vz = 0.f;
	if (Mode == EWHWalkerMode::Line) Tick(0.f);
}
