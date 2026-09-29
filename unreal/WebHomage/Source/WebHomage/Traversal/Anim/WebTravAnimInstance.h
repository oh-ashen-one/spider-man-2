// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
// Piece P3 round 04: C++ animation for the traversal hero (port of the essentials of src/player/anim/animator.js).
// No AnimBP graph: a native UAnimInstance picks a node from the C1 traversal anim struct (FWebTravAnim), crossfades
// nodes with the browser's per-transition blend times (TRANS), and its proxy samples + blends the authored clips of the
// hero GLB (/Game/Traversal/HeroDev/<clip>, names unchanged from the browser) and applies procedural layers:
// web-hand arm aim at the anchor, spine bank. Air phases between swings run a per-cycle flavor timeline
// (spread / tuck / rise / reach for the next web) that never repeats the previous cycle's flavor.
#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimInstanceProxy.h"
#include "Traversal/WebTravTypes.h"
#include "WebTravAnimInstance.generated.h"

class UAnimSequence;

struct FWebTravAnimLayer
{
	UAnimSequence* Seq = nullptr;
	float Time = 0.f;
	float Weight = 0.f;
	bool bLoop = true;
};

/** Everything the proxy needs for one evaluation (copied on the game thread). */
struct FWebTravAnimFrame
{
	TArray<FWebTravAnimLayer> Layers;
	bool bArmAim = false;
	bool bArmRight = true;
	float ArmAimWeight = 0.f;
	FVector ArmTargetCS = FVector::ZeroVector;   // component space (cm)
	float SpineBank = 0.f;                        // rad
};

struct FWebTravAnimProxy : public FAnimInstanceProxy
{
	FWebTravAnimProxy() = default;
	explicit FWebTravAnimProxy(UAnimInstance* Inst) : FAnimInstanceProxy(Inst) {}
	virtual void PreUpdate(UAnimInstance* InAnimInstance, float DeltaSeconds) override;
	virtual bool Evaluate(FPoseContext& Output) override;
	FWebTravAnimFrame Frame;
};

UCLASS(Transient, NotBlueprintable)
class WEBHOMAGE_API UWebTravAnimInstance : public UAnimInstance
{
	GENERATED_BODY()

public:
	/** Drive data from the character (game thread, before the mesh ticks). */
	void SetDrive(const FWebTravAnim& InAnim, bool bInWebActive, const FVector& InWebAnchorWorldCm, bool bInWebRight, bool bInSwingHeld);

	/** Name of the node / dominant clip of the last update (telemetry). */
	FName CurrentNode() const { return CurNode; }
	FName DominantClip() const { return Dominant; }
	float TotalClipWeight() const { return TotalWeight; }
	int32 AirFlavor() const { return FlavorIdx; }
	bool InAirCycle() const { return bInAirCycle; }
	float AirCycleTime() const { return AirCycleT; }
	int32 AirCycleCount() const { return CycleCount; }
	/** Round 06: capture pre-roll end — back to the freshly initialised state (no blend from the pre-roll pose). */
	void ResetForSequenceStart()
	{
		CurNode = NAME_None; Dominant = NAME_None; NodeT = 0.f; FadeT = 1.f; FadeDur = 0.2f; PrevLayers.Reset(); Frame.Layers.Reset();
		Frame.ArmAimWeight = 0.f; LocoPhase = 0.f; WallRunPhase = 0.f; bInAirCycle = false; AirCycleT = 0.f; FlavorIdx = -1; CycleCount = 0;
		bReachRight = true; LastMode = EWebTravMode::Ground;
	}

	/** Content folder with the hero clips (dev proxy; P2's hero replaces this path). */
	static FString ClipRoot;

	FWebTravAnimFrame Frame;

protected:
	virtual void NativeInitializeAnimation() override;
	virtual void NativeUpdateAnimation(float DeltaSeconds) override;
	virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override { return new FWebTravAnimProxy(this); }
	virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* InProxy) override { delete InProxy; }

private:
	UAnimSequence* Clip(FName Name);
	FName PickNode(float Dt);
	void BuildNode(FName Node, float NodeT, TArray<FWebTravAnimLayer>& Out);
	static FName Category(FName Node);
	static float BlendTime(FName FromCat, FName ToCat);

	UPROPERTY(Transient) TMap<FName, TObjectPtr<UAnimSequence>> Clips;
	FWebTravAnim A;
	bool bWebActive = false, bWebRight = true, bSwingHeld = false;
	FVector WebAnchorWorld = FVector::ZeroVector;

	FName CurNode, Dominant;
	float NodeT = 0.f, FadeT = 1.f, FadeDur = 0.2f, TotalWeight = 0.f;
	TArray<FWebTravAnimLayer> PrevLayers;
	float LocoPhase = 0.f, WallRunPhase = 0.f;
	// air cycle
	bool bInAirCycle = false;
	float AirCycleT = 0.f;
	int32 FlavorIdx = -1, CycleCount = 0;
	bool bReachRight = true;
	EWebTravMode LastMode = EWebTravMode::Ground;
};
