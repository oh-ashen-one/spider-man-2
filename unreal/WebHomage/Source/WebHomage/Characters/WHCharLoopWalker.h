// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
// P2 Characters: lineup actor for judging characters while moving. A skeletal mesh that walks/runs an elliptical
// loop at a set ground speed (optionally hopping every N s to exercise jump/fall/land), or turns in place
// (turntable) while its locomotion plays at ForcedSpeed, walks a straight line (Line: for side-tracking clips), or just stands.
// Drives UWHCharAnimInstance.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WHCharLoopWalker.generated.h"

class USkeletalMeshComponent;

UENUM(BlueprintType)
enum class EWHWalkerMode : uint8 { Loop, Turntable, Stand, Line };

UCLASS()
class WEBHOMAGE_API AWHCharLoopWalker : public AActor
{
	GENERATED_BODY()
public:
	AWHCharLoopWalker();
	virtual void BeginPlay() override;
	virtual void Tick(float Dt) override;
	/** Line mode: jump back to LineStart (and reposition now). The director calls this at the start of the shots that list this walker. */
	UFUNCTION(BlueprintCallable, Category="Walker") void RestartLine();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Walker") TObjectPtr<USkeletalMeshComponent> Mesh;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walker") EWHWalkerMode Mode = EWHWalkerMode::Loop;
	/** Ground speed in cm/s (also fed to the AnimInstance as ForcedSpeed). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walker") float Speed = 140.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walker") float RadiusX = 600.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walker") float RadiusY = 300.f;
	/** Start angle on the ellipse, degrees. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walker") float StartAngle = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walker") bool bClockwise = false;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walker") float TurntableDegPerSec = 30.f;
	/** 0 = never; otherwise hop every N seconds (Loop mode). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walker") float HopInterval = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walker") float HopVelocity = 520.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walker") float Gravity = 1470.f;
	/** Line mode: walks +X (actor yaw) from Center - LineLength/2, starting LineStart cm along it, and wraps at LineLength (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walker") float LineLength = 3000.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walker") float LineStart = 0.f;

	/** World-space centre of the loop (set from the actor location at BeginPlay). */
	UPROPERTY(BlueprintReadOnly, Category="Walker") FVector Center = FVector::ZeroVector;

private:
	float Theta = 0.f, HopT = 0.f, Z = 0.f, Vz = 0.f, Yaw = 0.f, LineD = 0.f;
	bool bAir = false;
};
