// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
// P2 Characters: in-game capture director for the character lineup map. Owns a camera, takes over player 0's view
// target and cycles through shots (orbit / side / three-quarter / close-up / wide) around target actors, so
// Scripts/run_game.sh -movie / -shots capture the RUNNING game. -WHCharShot=N starts at shot N.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WHCharShowDirector.generated.h"

class ACameraActor;

UENUM(BlueprintType)
enum class EWHShotKind : uint8 { Orbit, Side, ThreeQuarter, Closeup, Wide, Front };

USTRUCT(BlueprintType)
struct WEBHOMAGE_API FWHShot
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shot") TObjectPtr<AActor> Target = nullptr;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shot") EWHShotKind Kind = EWHShotKind::Orbit;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shot") float Duration = 5.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shot") float Distance = 350.f;
	/** Height of the aim point above the target origin (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shot") float AimHeight = 100.f;
	/** Camera height relative to the aim point (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shot") float CamHeight = 10.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shot") float FOV = 40.f;
	/** Orbit speed (deg/s) for Orbit shots; start azimuth for all target-relative shots. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shot") float OrbitDegPerSec = 40.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shot") float Azimuth = 0.f;
	/** Wide shots: fixed camera location. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shot") FVector WorldLocation = FVector::ZeroVector;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shot") FString Label;
	/** Line-mode walkers restarted when this shot begins (so a side-tracking clip always starts with the walkers at the same place). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shot") TArray<TObjectPtr<AActor>> RestartWalkers;
	/** Round 05: with a non-empty Director.ManagedActors list, only these (plus the shot's target) are visible during the shot; every other managed actor is hidden. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shot") TArray<TObjectPtr<AActor>> ShowActors;
};

UCLASS()
class WEBHOMAGE_API AWHCharShowDirector : public AActor
{
	GENERATED_BODY()
public:
	AWHCharShowDirector();
	virtual void BeginPlay() override;
	virtual void Tick(float Dt) override;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Director") TArray<FWHShot> Shots;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Director") bool bLoop = true;
	/** Round 05: actors whose visibility the director controls per shot (see FWHShot::ShowActors): a hero shot never shows another hero or a thug in the background. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Director") TArray<TObjectPtr<AActor>> ManagedActors;
private:
	UPROPERTY() TObjectPtr<ACameraActor> Cam;
	float T = 0.f;
	int32 LastShot = -1;
	FVector SmoothAim = FVector::ZeroVector;
};
