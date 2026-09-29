// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
// Piece P3: the traversal hero pawn. Extends the F1 foundation character with
//  - UWebTraversalComponent (browser traversal state machine, 120 Hz substeps; CharacterMovement switched off),
//  - FWebTravCamera (browser chase camera: springs, FOV kick, speed shake) driving FollowCamera directly,
//  - Enhanced Input bound like the browser (RMB swing, Space jump, Shift sprint / wall-run, E zip, C dive, Q boost + pad),
//  - a placeholder figure (basic shapes, posed procedurally from the C1 anim struct) until P2's hero lands,
//  - web strands drawn as thin cylinder chains from the hand to the anchor (min on-screen width like the browser ribbon),
//  - scripted input playback + per-frame telemetry via UWebTravScript (-WHTravScript / -WHTravCsv).
#pragma once

#include "CoreMinimal.h"
#include "Core/WebHomageCharacter.h"
#include "GameFramework/GameModeBase.h"
#include "Traversal/WebTravTypes.h"
#include "Traversal/WebTravCamera.h"
#include "WebTravCharacter.generated.h"

class UWebTraversalComponent;
class UStaticMeshComponent;
class USceneComponent;
class UMaterialInstanceDynamic;
class UInputAction;

UCLASS(config=Game)
class WEBHOMAGE_API AWebTravCharacter : public AWebHomageCharacter
{
	GENERATED_BODY()

public:
	AWebTravCharacter();

	virtual void Tick(float DeltaSeconds) override;

	UFUNCTION(BlueprintPure, Category="Traversal")
	UWebTraversalComponent* GetTraversal() const { return Traversal; }

	/** C1 animation contract for P2's AnimBP. */
	UFUNCTION(BlueprintPure, Category="Traversal")
	FWebTravAnim GetTravAnim() const;

	/** Live camera state (telemetry / debug). */
	const FWebTravCamera& GetTravCamera() const { return Cam; }

protected:
	virtual void BeginPlay() override;
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
	virtual void NotifyControllerChanged() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Traversal")
	TObjectPtr<UWebTraversalComponent> Traversal;

	/** Root of the placeholder figure (feet, oriented by the traversal body quaternion). */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Placeholder")
	TObjectPtr<USceneComponent> FigureRoot;

	/** Mouse look: radians per Mouse2D unit (browser 0.0023 rad / px; Mouse2D arrives pre-scaled by 0.07). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input")
	float MouseRadPerUnit = 0.033f;

	/** Right stick look rate (rad/s) at full deflection (browser 900 px/s x 0.0023). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input")
	FVector2D PadLookRate = FVector2D(2.07, 1.38);

private:
	void BuildTravInput();
	void BuildFigure();
	bool SetupHeroMesh();
	void PoseFigure(float Dt);
	void UpdateWebs(float Dt, const FVector& CamPosCm);
	FVector HandWorldCm(bool bRight) const;
	void PushTelemetry(double T, const FWebTravInput& I);
	UStaticMeshComponent* AddPart(USceneComponent* Parent, const TCHAR* Name, class UStaticMesh* Mesh, const FVector& Loc, const FVector& Scale, UMaterialInstanceDynamic* Mat);

	// input actions (transient, built at runtime like the F1 foundation)
	UPROPERTY(Transient) TObjectPtr<UInputAction> SwingAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> PadR2Action;
	UPROPERTY(Transient) TObjectPtr<UInputAction> PadL2Action;
	UPROPERTY(Transient) TObjectPtr<UInputAction> SprintAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> ZipAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> DropAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> QuickAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> TrickAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> LookMouseAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> LookPadAction;

	// live input state
	FVector2D LiveMove = FVector2D::ZeroVector, MouseAccum = FVector2D::ZeroVector, PadLook = FVector2D::ZeroVector;
	bool bRMB = false, bR2 = false, bL2 = false, bShift = false, bZipKey = false, bDropKey = false, bQuickKey = false, bJumpKey = false, bTrickKey = false;
	FWebTravInput PrevInput;

	FWebTravCamera Cam;
	double TravTime = 0.0;
	bool bTravStarted = false;
	// autoChain rhythm rule state
	bool bAutoHeld = true, bAutoWasSwinging = false;
	double AutoGapT = 0.0;
	int32 AutoReleases = 0;
	int64 FrameIndex = 0;

	// placeholder figure parts
	UPROPERTY(Transient) TObjectPtr<USceneComponent> ArmPivot[2];   // 0 = left, 1 = right
	UPROPERTY(Transient) TObjectPtr<USceneComponent> LegPivot[2];
	UPROPERTY(Transient) TArray<TObjectPtr<UStaticMeshComponent>> FigureParts;
	UPROPERTY(Transient) TArray<TObjectPtr<UStaticMeshComponent>> WebSegs;
	UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> WebMat;
	UPROPERTY(Transient) TObjectPtr<class USkeletalMeshComponent> LensMesh;
	bool bHeroMesh = false;
	// round 05: pixel measurement of the hero (depth capture that shows only the hero, same camera as the view)
	UPROPERTY(Transient) TObjectPtr<class USceneCaptureComponent2D> MaskCapture;
	UPROPERTY(Transient) TObjectPtr<class UTextureRenderTarget2D> MaskRT;
	float PxTop = -1.f, PxBottom = -1.f, PxLeft = -1.f, PxRight = -1.f;
	void ReadHeroMask();
	double RunPhase = 0.0;
	FVector ReleaseHandCm[2];
	bool bWasReleased[2] = { false, false };
	static constexpr int32 SEGS_PER_STRAND = 12;
};

/** Game mode for traversal test maps: spawns AWebTravCharacter with the mouse-safe controller. */
UCLASS()
class WEBHOMAGE_API AWebTravGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AWebTravGameMode();
};
