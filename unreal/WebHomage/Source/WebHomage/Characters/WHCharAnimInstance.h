// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
// P2 Characters: minimal native locomotion AnimInstance (idle / walk / jog / run / sprint 1D blend by speed with a
// shared, speed-synced phase, plus jump / fall / land). The AnimBP assets (/Game/Characters/*/ABP_*) are Blueprint
// children of this class that only set the clip references; the pose is produced natively in the proxy, so the
// AnimBPs are fully script-built (no hand-edited AnimGraph). Speed comes from the owner's CharacterMovement if it has
// one, otherwise from the component's world motion, or from ForcedSpeed (lineup walkers / turntables).
#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimInstanceProxy.h"
#include "WHCharAnimInstance.generated.h"

class UAnimSequence;

USTRUCT(BlueprintType)
struct WEBHOMAGE_API FWHLocoSample
{
	GENERATED_BODY()
	/** Looping locomotion clip (in place). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Locomotion") TObjectPtr<UAnimSequence> Clip = nullptr;
	/** Ground speed (cm/s) at which this clip plays at rate 1 without foot sliding. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Locomotion") float Speed = 150.f;
};

struct FWHAnimLayer
{
	TObjectPtr<UAnimSequence> Seq = nullptr;
	float Time = 0.f;
	float Weight = 0.f;
	bool bLoop = true;
};

struct FWHCharAnimProxy : public FAnimInstanceProxy
{
	FWHCharAnimProxy() = default;
	explicit FWHCharAnimProxy(UAnimInstance* In) : FAnimInstanceProxy(In) {}
	virtual void PreUpdate(UAnimInstance* InAnimInstance, float DeltaSeconds) override;
	virtual bool Evaluate(FPoseContext& Output) override;
	TArray<FWHAnimLayer> Layers;
};

UCLASS(Blueprintable, Transient)
class WEBHOMAGE_API UWHCharAnimInstance : public UAnimInstance
{
	GENERATED_BODY()
public:
	/** Locomotion samples, any order (sorted by Speed at init). Idle is the implicit speed-0 sample. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category="Locomotion") TArray<FWHLocoSample> Loco;
	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category="Locomotion") TObjectPtr<UAnimSequence> Idle = nullptr;
	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category="Air") TObjectPtr<UAnimSequence> JumpUp = nullptr;
	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category="Air") TObjectPtr<UAnimSequence> Fall = nullptr;
	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category="Air") TObjectPtr<UAnimSequence> Land = nullptr;
	/** Below this speed (cm/s) the idle fully takes over. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category="Locomotion") float IdleSpeed = 20.f;
	/** Cadence/stride split: rate = (v/v_clip)^CadenceExp; the rest of the speed ratio is (visually) stride. 1 = pure rate. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category="Locomotion") float CadenceExp = 1.f;

	/** >= 0 overrides the measured ground speed (cm/s). */
	UPROPERTY(BlueprintReadWrite, Category="State") float ForcedSpeed = -1.f;
	/** Set by non-Character owners (e.g. AWHCharLoopWalker hops). */
	UPROPERTY(BlueprintReadWrite, Category="State") bool bForceAir = false;
	UPROPERTY(BlueprintReadWrite, Category="State") float ForcedVerticalSpeed = 0.f;

	UPROPERTY(BlueprintReadOnly, Category="State") float Speed = 0.f;
	UPROPERTY(BlueprintReadOnly, Category="State") float VerticalSpeed = 0.f;
	UPROPERTY(BlueprintReadOnly, Category="State") bool bInAir = false;

	virtual void NativeInitializeAnimation() override;
	virtual void NativeUpdateAnimation(float DeltaSeconds) override;

	TArray<FWHAnimLayer> GameLayers;

protected:
	virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override { return new FWHCharAnimProxy(this); }
	virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* P) override { delete P; }

private:
	FVector LastPos = FVector::ZeroVector;
	bool bHasLast = false;
	float Phase = 0.f, IdleTime = 0.f, AirAlpha = 0.f, AirTime = 0.f, FallAlpha = 0.f, LandTime = 1e3f, SmoothedSpeed = 0.f;
	bool bWasInAir = false;
};
