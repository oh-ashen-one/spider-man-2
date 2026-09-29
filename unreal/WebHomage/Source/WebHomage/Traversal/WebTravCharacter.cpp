// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Traversal/WebTravCharacter.h"
#include "Traversal/WebTraversalComponent.h"
#include "Traversal/WebTravScript.h"
#include "Traversal/Anim/WebTravAnimInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "ReferenceSkeleton.h"
#include "Core/WebHomagePlayerController.h"
#include "WebHomage.h"

#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/GameViewportClient.h"
#include "Engine/LocalPlayer.h"
#include "Engine/StaticMesh.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UnrealClient.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	const FName N_swingLow(TEXT("swingLow")), N_trick(TEXT("trick")), N_tuckFlip(TEXT("tuckFlip")), N_layout(TEXT("layout")),
		N_corkscrew(TEXT("corkscrew")), N_scissor(TEXT("scissor")), N_rise(TEXT("rise")), N_dive(TEXT("dive")), N_zipPull(TEXT("zipPull")),
		N_release(TEXT("release")), N_jumpLaunch(TEXT("jumpLaunch")), N_wallRun(TEXT("wallRun")), N_wallRunSide(TEXT("wallRunSide"));
	const TCHAR* ModeName(EWebTravMode M)
	{
		switch (M)
		{
		case EWebTravMode::Ground: return TEXT("ground");
		case EWebTravMode::Air: return TEXT("air");
		case EWebTravMode::Swing: return TEXT("swing");
		case EWebTravMode::Zip: return TEXT("zip");
		case EWebTravMode::Perch: return TEXT("perch");
		case EWebTravMode::Wall: return TEXT("wall");
		case EWebTravMode::Land: return TEXT("land");
		}
		return TEXT("?");
	}
	double Smooth01(double X) { X = FMath::Clamp(X, 0.0, 1.0); return X * X * (3 - 2 * X); }
}

AWebTravCharacter::AWebTravCharacter()
{
	Traversal = CreateDefaultSubobject<UWebTraversalComponent>(TEXT("Traversal"));

	FigureRoot = CreateDefaultSubobject<USceneComponent>(TEXT("FigureRoot"));
	FigureRoot->SetupAttachment(RootComponent);
	FigureRoot->SetUsingAbsoluteLocation(true);
	FigureRoot->SetUsingAbsoluteRotation(true);
	GetMesh()->SetupAttachment(FigureRoot);
	GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	// the chase camera is driven directly (browser camera.js port), not by the spring arm
	CameraBoom->bDoCollisionTest = false;
	CameraBoom->bEnableCameraLag = false;
	FollowCamera->SetUsingAbsoluteLocation(true);
	FollowCamera->SetUsingAbsoluteRotation(true);
	FollowCamera->PostProcessBlendWeight = 1.f;
	FollowCamera->PostProcessSettings.bOverride_MotionBlurAmount = true;
	FollowCamera->PostProcessSettings.bOverride_MotionBlurMax = true;

	for (FVector& V : ReleaseHandCm) V = FVector::ZeroVector;
}

FWebTravAnim AWebTravCharacter::GetTravAnim() const
{
	return Traversal ? Traversal->Anim : FWebTravAnim();
}

// ------------------------------------------------------------------ input (browser input.js bindings)
void AWebTravCharacter::BuildTravInput()
{
	if (SwingAction)
	{
		return;
	}
	auto MakeAction = [this](const TCHAR* Name, EInputActionValueType Type)
	{
		UInputAction* A = NewObject<UInputAction>(this, Name);
		A->ValueType = Type;
		return A;
	};
	MoveAction = MakeAction(TEXT("IA_TravMove"), EInputActionValueType::Axis2D);
	LookAction = MakeAction(TEXT("IA_TravLook"), EInputActionValueType::Axis2D); // unused (kept non-null for the base class)
	JumpAction = MakeAction(TEXT("IA_TravJump"), EInputActionValueType::Boolean);
	SwingAction = MakeAction(TEXT("IA_TravSwing"), EInputActionValueType::Boolean);
	PadR2Action = MakeAction(TEXT("IA_TravPadR2"), EInputActionValueType::Boolean);
	PadL2Action = MakeAction(TEXT("IA_TravPadL2"), EInputActionValueType::Boolean);
	SprintAction = MakeAction(TEXT("IA_TravSprint"), EInputActionValueType::Boolean);
	ZipAction = MakeAction(TEXT("IA_TravZip"), EInputActionValueType::Boolean);
	DropAction = MakeAction(TEXT("IA_TravDrop"), EInputActionValueType::Boolean);
	QuickAction = MakeAction(TEXT("IA_TravQuick"), EInputActionValueType::Boolean);
	TrickAction = MakeAction(TEXT("IA_TravTrick"), EInputActionValueType::Boolean);
	LookMouseAction = MakeAction(TEXT("IA_TravLookMouse"), EInputActionValueType::Axis2D);
	LookPadAction = MakeAction(TEXT("IA_TravLookPad"), EInputActionValueType::Axis2D);

	MappingContext = NewObject<UInputMappingContext>(this, TEXT("IMC_Trav"));
	UInputMappingContext* IMC = MappingContext;
	auto MapMove = [IMC, this](const FKey& Key, bool bSwizzle, bool bNegate)
	{
		FEnhancedActionKeyMapping& M = IMC->MapKey(MoveAction, Key);
		if (bSwizzle)
		{
			UInputModifierSwizzleAxis* Swz = NewObject<UInputModifierSwizzleAxis>(IMC);
			Swz->Order = EInputAxisSwizzle::YXZ;
			M.Modifiers.Add(Swz);
		}
		if (bNegate) M.Modifiers.Add(NewObject<UInputModifierNegate>(IMC));
	};
	// Move: X = right, Y = forward (WASD + arrows + left stick)
	MapMove(EKeys::W, true, false); MapMove(EKeys::Up, true, false);
	MapMove(EKeys::S, true, true); MapMove(EKeys::Down, true, true);
	MapMove(EKeys::D, false, false); MapMove(EKeys::Right, false, false);
	MapMove(EKeys::A, false, true); MapMove(EKeys::Left, false, true);
	IMC->MapKey(MoveAction, EKeys::Gamepad_Left2D);
	IMC->MapKey(LookMouseAction, EKeys::Mouse2D);
	IMC->MapKey(LookPadAction, EKeys::Gamepad_Right2D);
	// RIGHT MOUSE = web swing (hold); R2 = swing in air / parkour on ground (L2+R2 = zip)
	IMC->MapKey(SwingAction, EKeys::RightMouseButton);
	IMC->MapKey(PadR2Action, EKeys::Gamepad_RightTrigger);
	IMC->MapKey(PadL2Action, EKeys::Gamepad_LeftTrigger);
	// Space = jump (hold = charge) / A
	IMC->MapKey(JumpAction, EKeys::SpaceBar);
	IMC->MapKey(JumpAction, EKeys::Gamepad_FaceButton_Bottom);
	// Shift = wall run + ground parkour
	IMC->MapKey(SprintAction, EKeys::LeftShift);
	IMC->MapKey(SprintAction, EKeys::RightShift);
	// E / MIDDLE MOUSE = web-zip / point-launch; Y / Triangle
	IMC->MapKey(ZipAction, EKeys::E);
	IMC->MapKey(ZipAction, EKeys::MiddleMouseButton);
	IMC->MapKey(ZipAction, EKeys::Gamepad_FaceButton_Top);
	// C / Ctrl = drop / dive; B / Circle
	IMC->MapKey(DropAction, EKeys::C);
	IMC->MapKey(DropAction, EKeys::LeftControl);
	IMC->MapKey(DropAction, EKeys::Gamepad_FaceButton_Right);
	// Q = quick web boost; L1
	IMC->MapKey(QuickAction, EKeys::Q);
	IMC->MapKey(QuickAction, EKeys::Gamepad_LeftShoulder);
	// F / X (Square) = air trick (round 04: tricks only on input; double-tap Space still works in the air)
	IMC->MapKey(TrickAction, EKeys::F);
	IMC->MapKey(TrickAction, EKeys::Gamepad_FaceButton_Left);
}

void AWebTravCharacter::NotifyControllerChanged()
{
	BuildTravInput(); // before the base, so its EnsureDefaultInput keeps our mapping context
	Super::NotifyControllerChanged();
}

void AWebTravCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	BuildTravInput();
	UEnhancedInputComponent* EIC = Cast<UEnhancedInputComponent>(PlayerInputComponent);
	if (!EIC)
	{
		UE_LOG(LogWebHomage, Error, TEXT("AWebTravCharacter needs an EnhancedInputComponent"));
		return;
	}
	auto BindHeld = [this, EIC](UInputAction* A, bool AWebTravCharacter::*Flag)
	{
		EIC->BindActionValueLambda(A, ETriggerEvent::Started, [this, Flag](const FInputActionValue&) { this->*Flag = true; });
		EIC->BindActionValueLambda(A, ETriggerEvent::Triggered, [this, Flag](const FInputActionValue&) { this->*Flag = true; });
		EIC->BindActionValueLambda(A, ETriggerEvent::Completed, [this, Flag](const FInputActionValue&) { this->*Flag = false; });
		EIC->BindActionValueLambda(A, ETriggerEvent::Canceled, [this, Flag](const FInputActionValue&) { this->*Flag = false; });
	};
	BindHeld(SwingAction, &AWebTravCharacter::bRMB);
	BindHeld(PadR2Action, &AWebTravCharacter::bR2);
	BindHeld(PadL2Action, &AWebTravCharacter::bL2);
	BindHeld(SprintAction, &AWebTravCharacter::bShift);
	BindHeld(ZipAction, &AWebTravCharacter::bZipKey);
	BindHeld(DropAction, &AWebTravCharacter::bDropKey);
	BindHeld(QuickAction, &AWebTravCharacter::bQuickKey);
	BindHeld(JumpAction, &AWebTravCharacter::bJumpKey);
	BindHeld(TrickAction, &AWebTravCharacter::bTrickKey);
	EIC->BindActionValueLambda(MoveAction, ETriggerEvent::Triggered, [this](const FInputActionValue& V) { LiveMove = V.Get<FVector2D>(); });
	EIC->BindActionValueLambda(MoveAction, ETriggerEvent::Completed, [this](const FInputActionValue&) { LiveMove = FVector2D::ZeroVector; });
	EIC->BindActionValueLambda(LookMouseAction, ETriggerEvent::Triggered, [this](const FInputActionValue& V) { MouseAccum += V.Get<FVector2D>(); });
	EIC->BindActionValueLambda(LookPadAction, ETriggerEvent::Triggered, [this](const FInputActionValue& V) { PadLook = V.Get<FVector2D>(); });
	EIC->BindActionValueLambda(LookPadAction, ETriggerEvent::Completed, [this](const FInputActionValue&) { PadLook = FVector2D::ZeroVector; });
}

// ------------------------------------------------------------------ setup
UStaticMeshComponent* AWebTravCharacter::AddPart(USceneComponent* Parent, const TCHAR* Name, UStaticMesh* Mesh, const FVector& Loc, const FVector& Scale,
	UMaterialInstanceDynamic* Mat)
{
	UStaticMeshComponent* C = NewObject<UStaticMeshComponent>(this, Name);
	C->SetupAttachment(Parent);
	C->SetStaticMesh(Mesh);
	C->SetRelativeLocation(Loc);
	C->SetRelativeScale3D(Scale);
	C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	C->SetGenerateOverlapEvents(false);
	if (Mat) C->SetMaterial(0, Mat);
	C->RegisterComponent();
	FigureParts.Add(C);
	return C;
}

void AWebTravCharacter::BuildFigure()
{
	UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	UStaticMesh* Sphere = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	UStaticMesh* Cyl = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	UMaterialInterface* Base = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Traversal/Materials/M_TravColor.M_TravColor"));
	if (!Base) Base = LoadObject<UMaterialInterface>(nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
	auto Mat = [this, Base](const FLinearColor& C, float Emissive)
	{
		UMaterialInstanceDynamic* M = UMaterialInstanceDynamic::Create(Base, this);
		M->SetVectorParameterValue(TEXT("Color"), C);
		M->SetScalarParameterValue(TEXT("Emissive"), Emissive);
		return M;
	};
	UMaterialInstanceDynamic* Red = Mat(FLinearColor(0.55f, 0.02f, 0.03f), 0.f);
	UMaterialInstanceDynamic* Blue = Mat(FLinearColor(0.02f, 0.05f, 0.30f), 0.f);
	UMaterialInstanceDynamic* White = Mat(FLinearColor(0.9f, 0.9f, 0.95f), 0.6f);
	WebMat = Mat(FLinearColor(0.92f, 0.92f, 0.96f), 0.35f);

	// placeholder hero, 1.8 m: X forward, Y right, Z up, origin at the feet
	AddPart(FigureRoot, TEXT("Fig_Pelvis"), Cube, FVector(0, 0, 95), FVector(0.22, 0.32, 0.18), Blue);
	AddPart(FigureRoot, TEXT("Fig_Torso"), Cube, FVector(0, 0, 128), FVector(0.24, 0.40, 0.48), Red);
	AddPart(FigureRoot, TEXT("Fig_Head"), Sphere, FVector(0, 0, 166), FVector(0.24, 0.23, 0.26), Red);
	AddPart(FigureRoot, TEXT("Fig_EyeL"), Sphere, FVector(10, -5, 168), FVector(0.05, 0.07, 0.05), White);
	AddPart(FigureRoot, TEXT("Fig_EyeR"), Sphere, FVector(10, 5, 168), FVector(0.05, 0.07, 0.05), White);
	for (int32 S = 0; S < 2; ++S)
	{
		const double Side = S == 0 ? -1.0 : 1.0;
		USceneComponent* AP = NewObject<USceneComponent>(this, S == 0 ? TEXT("Fig_ArmL") : TEXT("Fig_ArmR"));
		AP->SetupAttachment(FigureRoot);
		AP->SetRelativeLocation(FVector(0, 23 * Side, 146));
		AP->RegisterComponent();
		ArmPivot[S] = AP;
		AddPart(AP, S == 0 ? TEXT("Fig_ArmL_M") : TEXT("Fig_ArmR_M"), Cyl, FVector(0, 0, -29), FVector(0.09, 0.09, 0.58), Red);
		AddPart(AP, S == 0 ? TEXT("Fig_HandL") : TEXT("Fig_HandR"), Sphere, FVector(0, 0, -60), FVector(0.1, 0.1, 0.1), Red);
		USceneComponent* LP = NewObject<USceneComponent>(this, S == 0 ? TEXT("Fig_LegL") : TEXT("Fig_LegR"));
		LP->SetupAttachment(FigureRoot);
		LP->SetRelativeLocation(FVector(0, 10 * Side, 88));
		LP->RegisterComponent();
		LegPivot[S] = LP;
		AddPart(LP, S == 0 ? TEXT("Fig_LegL_M") : TEXT("Fig_LegR_M"), Cyl, FVector(0, 0, -44), FVector(0.13, 0.13, 0.88), Blue);
	}
	// web strands: chains of thin cylinders (absolute transforms), 2 strands
	for (int32 I = 0; I < 2 * SEGS_PER_STRAND; ++I)
	{
		UStaticMeshComponent* C = NewObject<UStaticMeshComponent>(this, *FString::Printf(TEXT("WebSeg_%02d"), I));
		C->SetupAttachment(RootComponent);
		C->SetUsingAbsoluteLocation(true);
		C->SetUsingAbsoluteRotation(true);
		C->SetUsingAbsoluteScale(true);
		C->SetStaticMesh(Cyl);
		C->SetMaterial(0, WebMat);
		C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		C->SetCastShadow(false);
		C->SetVisibility(false);
		C->RegisterComponent();
		WebSegs.Add(C);
	}
}

bool AWebTravCharacter::SetupHeroMesh()
{
	// round 04: the real hero (browser GLB, dev proxy in /Game/Traversal/HeroDev; P2's hero replaces the path)
	USkeletalMesh* Body = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/Traversal/HeroDev/HeroDev/SkeletalMeshes/SpiderMan.SpiderMan"));
	if (!Body)
	{
		UE_LOG(LogWebHomage, Warning, TEXT("WH_TRAV hero mesh missing: placeholder figure stays"));
		return false;
	}
	USkeletalMeshComponent* M = GetMesh();
	M->SetAnimationMode(EAnimationMode::AnimationBlueprint);
	M->SetAnimInstanceClass(UWebTravAnimInstance::StaticClass());
	M->SetSkeletalMesh(Body);
	M->SetCastShadow(true);
	M->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
	M->PrimaryComponentTick.AddPrerequisite(this, PrimaryActorTick);
	// the asset's own forward / up axes (from its reference pose) -> figure root +X forward, +Z up
	const FReferenceSkeleton& RS = Body->GetRefSkeleton();
	auto RefCS = [&RS](const TCHAR* Name)
	{
		int32 I = RS.FindBoneIndex(FName(Name));
		FTransform T = FTransform::Identity;
		while (I != INDEX_NONE) { T = T * RS.GetRefBonePose()[I]; I = RS.GetParentIndex(I); }
		return T.GetLocation();
	};
	FVector Fwd = RefCS(TEXT("toe_L")) - RefCS(TEXT("foot_L")) + RefCS(TEXT("toe_R")) - RefCS(TEXT("foot_R"));
	const FVector Up = (RefCS(TEXT("head")) - RefCS(TEXT("hips"))).GetSafeNormal();
	Fwd = (Fwd - Up * FVector::DotProduct(Fwd, Up)).GetSafeNormal();
	const FQuat Basis = FRotationMatrix::MakeFromXZ(Fwd, Up).ToQuat();
	const FQuat Corr = Basis.Inverse();
	const FVector LeftDir = Corr.RotateVector(RefCS(TEXT("hand_L")) - RefCS(TEXT("hand_R")));
	const double FootZ = FMath::Min(Corr.RotateVector(RefCS(TEXT("toe_L"))).Z, Corr.RotateVector(RefCS(TEXT("foot_L"))).Z);
	const double HeadZ = Corr.RotateVector(RefCS(TEXT("head"))).Z;
	M->SetRelativeRotation(Corr);
	M->SetRelativeLocation(FVector(0, 0, 0));
	UE_LOG(LogWebHomage, Display, TEXT("WH_TRAV hero mesh: fwd(asset)=%s up(asset)=%s left-after-corr=%s footZ=%.1f headZ=%.1f cm"),
		*Fwd.ToString(), *Up.ToString(), *LeftDir.GetSafeNormal().ToString(), FootZ, HeadZ);
	if (USkeletalMesh* Lens = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/Traversal/HeroDev/HeroDev/SkeletalMeshes/Lenses.Lenses")))
	{
		LensMesh = NewObject<USkeletalMeshComponent>(this, TEXT("HeroLenses"));
		LensMesh->SetupAttachment(M);
		LensMesh->SetSkeletalMesh(Lens);
		LensMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		LensMesh->RegisterComponent();
		LensMesh->SetLeaderPoseComponent(M);
	}
	for (UStaticMeshComponent* C : FigureParts) { if (C) C->SetVisibility(false); }
	for (USceneComponent* P : ArmPivot) { if (P) P->SetVisibility(false, true); }
	for (USceneComponent* P : LegPivot) { if (P) P->SetVisibility(false, true); }
	return true;
}

void AWebTravCharacter::BeginPlay()
{
	Super::BeginPlay();
	if (ProxyBody) ProxyBody->SetVisibility(false);
	GetCharacterMovement()->SetMovementMode(MOVE_None);
	GetCharacterMovement()->SetComponentTickEnabled(false);
	BuildFigure();
	bHeroMesh = SetupHeroMesh();

	const UWebTravScript* Script = GetGameInstance() ? GetGameInstance()->GetSubsystem<UWebTravScript>() : nullptr;
	if (Script) Traversal->RandomSeed = Script->Seed();
	Traversal->Cam = &Cam;
	Traversal->InitWorld(GetWorld(), this);

	// capsule centre (96 cm over the feet) -> traversal body centre (0.95 m over the feet)
	FVector PosM = (GetActorLocation() - FVector(0, 0, GetCapsuleComponent()->GetScaledCapsuleHalfHeight())) / 100.0 + FVector(0, 0, UWebTraversalComponent::H);
	double YawDeg = GetActorRotation().Yaw;
	double CamPitch = 0.14;
	if (Script && Script->IsActive() && Script->HasSpawn())
	{
		PosM = Script->SpawnPosM(); YawDeg = Script->SpawnYawDeg(); CamPitch = Script->SpawnCamPitch();
	}
	Traversal->Teleport(PosM, FMath::DegreesToRadians(YawDeg));
	if (Script && Script->IsActive()) Traversal->SetVelocityM(Script->SpawnVelM());
	Cam.Reset(Traversal->PosM(), FMath::DegreesToRadians(YawDeg));
	Cam.Pitch = CamPitch;
	UE_LOG(LogWebHomage, Display, TEXT("WH_TRAV ready: %d building boxes, spawn %s m yaw %.1f"), Traversal->BuildingCount(), *PosM.ToString(), YawDeg);
}

// ------------------------------------------------------------------ per frame
void AWebTravCharacter::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	const double Dt = FMath::Clamp(double(DeltaSeconds), 1e-4, 0.1);
	if (!bTravStarted) { bTravStarted = true; TravTime = 0.0; }
	else TravTime += Dt;

	// ---- input: live (keyboard / mouse / pad) or scripted playback
	FWebTravInput I;
	UWebTravScript* Script = GetGameInstance() ? GetGameInstance()->GetSubsystem<UWebTravScript>() : nullptr;
	if (Script && Script->IsActive())
	{
		FVector2D LookRate;
		I = Script->Sample(TravTime, LookRate);
		I.Look = LookRate * Dt;
		double HeadingDeg = 0;
		if (Script->HeadingAt(TravTime, HeadingDeg))
		{ // steer toward a world direction: express it in camera-relative stick terms (what a player's stick would do)
			const double Mag = FMath::Max(I.Move.Size(), 0.0);
			const FVector W = FVector(FMath::Cos(FMath::DegreesToRadians(HeadingDeg)), FMath::Sin(FMath::DegreesToRadians(HeadingDeg)), 0);
			I.Move = FVector2D(FVector::DotProduct(W, Cam.RightFlat()), FVector::DotProduct(W, Cam.ForwardFlat())) * Mag;
		}
		double RelPhase = 0.45, Gap = 0.3, RepressVz = 1e9;
		if (Script->AutoChainAt(TravTime, RelPhase, Gap, RepressVz))
		{ // deterministic swing rhythm: hold through the arc, let go on the rising front, re-press after the gap
			const bool bSwinging = Traversal->IsSwinging();
			const FWebTravAnim& A = Traversal->Anim;
			// release on the rising front of the arc, or at the forward apex if the arc never gets that far
			const bool bFrontApex = A.Swing.Phase > 0.15f && Traversal->VelM().Z <= 0 && A.T > 0.6f;
			if (bAutoHeld && bSwinging && ((A.Swing.Phase > RelPhase && Traversal->VelM().Z > 0 && A.T > 0.25f) || bFrontApex))
			{
				bAutoHeld = false; AutoGapT = 0.0; ++AutoReleases;
				const int32 Every = Script->TrickEveryAt(TravTime);
				if (Every > 0 && AutoReleases % Every == 0) I.bTrick = true; // trick pressed together with this release
			}
			else if (!bAutoHeld) { AutoGapT += Dt; if (AutoGapT >= Gap && Traversal->VelM().Z <= RepressVz) bAutoHeld = true; }
			bAutoWasSwinging = bSwinging;
			I.bSwing = bAutoHeld;
		}
	}
	else
	{
		I.Move = LiveMove.Size() > 1 ? LiveMove.GetSafeNormal() : LiveMove;
		I.bSwing = bRMB || (bR2 && !bL2);
		I.bSprint = bShift || (bR2 && !bL2);
		I.bZip = bZipKey || (bL2 && bR2);
		I.bJump = bJumpKey; I.bDrop = bDropKey; I.bQuick = bQuickKey; I.bTrick = bTrickKey;
		// look: mouse (yaw right +, pitch down +) and right stick rate
		I.Look = FVector2D(MouseAccum.X * MouseRadPerUnit, -MouseAccum.Y * MouseRadPerUnit)
			+ FVector2D(PadLook.X * PadLookRate.X, -PadLook.Y * PadLookRate.Y) * Dt;
	}
	MouseAccum = FVector2D::ZeroVector;
	I.ComputeEdges(PrevInput);
	PrevInput = I;

	// ---- camera look, traversal, camera
	Cam.ApplyLook(I.Look);
	Traversal->UpdateTraversal(Dt, I);
	for (const FWebTravEvent& E : Traversal->Events)
	{ // player.js event -> camera mapping
		const FString T = E.Type.ToString();
		if (T == TEXT("land") && E.Severity > 0.02f) Cam.Impact(E.Severity);
		else if (T == TEXT("perch")) Cam.Impact(E.Severity * 0.6);
		else if (T == TEXT("pointLaunch")) { Cam.Impact(0.18); Cam.Kick(0.7); }
		else if (T == TEXT("zipLaunch")) Cam.Kick(FMath::Min(1.0, 0.45 + E.Dist / 60.0));
		else if (T == TEXT("quickBoost")) { Cam.Kick(0.22 + 0.18 * E.K); Cam.Shake(0.04); }
		else if (T == TEXT("wall") && E.bRun) Cam.Shake(0.08);
		else if (T == TEXT("swingWallKick")) Cam.Shake(0.1 + 0.3 * E.Severity);
	}
	FTravCamInput CI;
	CI.Pos = Traversal->PosM(); CI.Vel = Traversal->VelM(); CI.Mode = Traversal->Anim.Mode; CI.Sub = Traversal->Sub(); CI.ModeT = Traversal->ModeT();
	CI.bHasAnchor = Traversal->IsSwinging(); CI.Anchor = Traversal->SwingAnchor();
	CI.bHasSwingDir = Traversal->IsSwinging(); CI.SwingDir = Traversal->SwingDir();
	CI.WallNormal = Traversal->WallNormal(); CI.Facing = Traversal->Facing(); CI.bDive = Traversal->IsDiving();
	CI.Tension = Traversal->SwingTension(); CI.Bank = Traversal->SwingBank();
	CI.HAbove = Traversal->PosM().Z - UWebTraversalComponent::H - Traversal->FloorBelow();
	CI.SwingAngle = Traversal->Anim.Swing.Angle;
	Cam.Update(Dt, CI, Traversal->TravWorld);

	// ---- move the actor (capsule) with the simulated body
	const FVector BodyCm = Traversal->PosM() * 100.0;
	SetActorLocationAndRotation(BodyCm - FVector(0, 0, UWebTraversalComponent::H * 100.0) + FVector(0, 0, GetCapsuleComponent()->GetScaledCapsuleHalfHeight()),
		FRotator(0, FMath::RadiansToDegrees(Traversal->Facing()), 0), false, nullptr, ETeleportType::TeleportPhysics);

	// ---- camera component
	const FVector CamCm = Cam.CamPos * 100.0;
	FollowCamera->SetWorldLocationAndRotation(CamCm, Cam.CamRot);
	double Aspect = 16.0 / 9.0;
	if (GEngine && GEngine->GameViewport && GEngine->GameViewport->Viewport)
	{
		const FIntPoint Sz = GEngine->GameViewport->Viewport->GetSizeXY();
		if (Sz.X > 0 && Sz.Y > 0) Aspect = double(Sz.X) / double(Sz.Y);
	}
	const double HFov = 2.0 * FMath::Atan(FMath::Tan(FMath::DegreesToRadians(Cam.OutVFov * 0.5)) * Aspect);
	FollowCamera->SetFieldOfView(float(FMath::RadiansToDegrees(HFov)));
	FollowCamera->PostProcessSettings.MotionBlurAmount = float(FMath::Clamp(0.15 + 0.5 * Cam.MotionBlur, 0.0, 1.0));
	FollowCamera->PostProcessSettings.MotionBlurMax = float(3.0 + 4.0 * Cam.MotionBlur);

	// ---- figure + webs
	PoseFigure(float(Dt));
	if (bHeroMesh)
	{
		if (UWebTravAnimInstance* AI = Cast<UWebTravAnimInstance>(GetMesh()->GetAnimInstance()))
		{
			const FWebTravStrand& St = Traversal->Strands[0];
			const bool bWeb = St.bActive && St.ReleaseT < 0.f;
			AI->SetDrive(Traversal->Anim, bWeb, St.Anchor * 100.0, St.bRightHand, I.bSwing);
		}
		for (UStaticMeshComponent* C : FigureParts) { if (C) C->SetVisibility(false); }
	}
	FigureRoot->SetVisibility(FVector::Dist(CamCm, BodyCm) > 85.0, true);
	if (bHeroMesh) { for (UStaticMeshComponent* C : FigureParts) { if (C) C->SetVisibility(false); } }
	UpdateWebs(float(Dt), CamCm);

	// ---- telemetry
	if (Script && Script->WantsTelemetry()) PushTelemetry(TravTime, I);
	++FrameIndex;
}

FVector AWebTravCharacter::HandWorldCm(bool bRight) const
{
	if (bHeroMesh && GetMesh()) return GetMesh()->GetBoneLocation(bRight ? FName(TEXT("hand_R")) : FName(TEXT("hand_L")));
	const USceneComponent* P = ArmPivot[bRight ? 1 : 0];
	if (!P) return Traversal->PosM() * 100.0;
	return P->GetComponentTransform().TransformPosition(FVector(0, 0, -60));
}

void AWebTravCharacter::PoseFigure(float Dt)
{
	const FWebTravAnim& A = Traversal->Anim;
	const FQuat Body = A.BodyQ;
	FVector Root = A.RootPos;
	FQuat Q = Body;
	// release / air tricks: the whole body flips / rolls around its centre (placeholder for P2's trick clips)
	if (A.Sub == N_trick && !A.Trick.IsNone() && A.TrickDur > 0)
	{
		const double E = Smooth01(A.T / A.TrickDur);
		double Ang = 0;
		FVector Axis(0, 1, 0);
		if (A.Trick == N_tuckFlip) Ang = 2 * PI * E;
		else if (A.Trick == N_layout) Ang = 2 * PI * E * A.TrickSide;
		else if (A.Trick == N_corkscrew) { Ang = 2 * PI * E * A.TrickSide; Axis = FVector(1, 0, 0); }
		if (Ang != 0)
		{
			Q = Body * FQuat(Axis, Ang);
			const FVector Centre = Traversal->PosM() * 100.0;
			Root = Centre - Q.RotateVector(FVector(0, 0, 95));
		}
	}
	// round 04: air cycles keep the whole body moving — a slow barrel roll and pitch sway, phased per cycle
	if (bHeroMesh && A.Mode == EWebTravMode::Air && A.Sub != N_trick && !A.bDive)
	{
		if (const UWebTravAnimInstance* AI = Cast<UWebTravAnimInstance>(GetMesh()->GetAnimInstance()))
		{
			if (AI->InAirCycle())
			{
				const double Tc = AI->AirCycleTime(), Ph = AI->AirCycleCount() * 1.7;
				const double Ramp = FMath::Clamp(Tc / 0.3, 0.0, 1.0);
				const double RollA = 0.6 * Ramp * FMath::Sin(2 * PI * 1.05 * Tc + Ph) * (AI->AirCycleCount() % 2 ? 1.0 : -1.0);
				const double PitchA = 0.35 * Ramp * FMath::Sin(2 * PI * 0.8 * Tc + Ph * 0.5);
				const FQuat Q2 = Q * FQuat(FVector(1, 0, 0), RollA) * FQuat(FVector(0, 1, 0), PitchA);
				const FVector Centre = Traversal->PosM() * 100.0;
				Root = Centre - Q2.RotateVector(FVector(0, 0, 95));
				Q = Q2;
			}
		}
	}
	FigureRoot->SetWorldLocationAndRotation(Root, Q);

	// limb directions in figure space (X forward, Y right, Z up); pivots hang along -Z by default
	auto ToLocal = [this](const FVector& WorldDir) { return FigureRoot->GetComponentQuat().UnrotateVector(WorldDir).GetSafeNormal(); };
	FVector Arm[2], Leg[2];
	const double Sp = A.Speed;
	const EWebTravMode M = A.Mode;
	for (int32 S = 0; S < 2; ++S)
	{
		const double Sd = S == 0 ? -1.0 : 1.0;
		Arm[S] = FVector(0.05, 0.18 * Sd, -1);
		Leg[S] = FVector(0, 0.05 * Sd, -1);
	}
	if (M == EWebTravMode::Ground)
	{
		RunPhase += Dt * Sp * 0.95;
		const double AA = FMath::Min(1.0, Sp / 8.0) * 0.9, LA = FMath::Min(1.0, Sp / 8.0) * 0.8;
		for (int32 S = 0; S < 2; ++S)
		{
			const double Sd = S == 0 ? -1.0 : 1.0;
			Arm[S] = FVector(FMath::Sin(RunPhase + (S ? PI : 0)) * AA, 0.15 * Sd, -1);
			Leg[S] = FVector(FMath::Sin(RunPhase + (S ? 0 : PI)) * LA, 0.05 * Sd, -1);
		}
	}
	else if (M == EWebTravMode::Land)
	{
		for (int32 S = 0; S < 2; ++S) { const double Sd = S == 0 ? -1.0 : 1.0; Arm[S] = FVector(0.5, 0.5 * Sd, -0.6); Leg[S] = FVector(0.6, 0.2 * Sd, -1); }
	}
	else if (M == EWebTravMode::Air)
	{
		const bool bDive = A.bDive || A.Sub == N_dive;
		for (int32 S = 0; S < 2; ++S)
		{
			const double Sd = S == 0 ? -1.0 : 1.0;
			if (bDive) { Arm[S] = FVector(-1, 0.25 * Sd, 0.15); Leg[S] = FVector(-0.25, 0.08 * Sd, -1); }
			else if (A.Sub == N_rise || A.Sub == N_jumpLaunch) { Arm[S] = FVector(0.3, 0.6 * Sd, 0.5); Leg[S] = FVector(S ? -0.3 : 0.5, 0.1 * Sd, -1); }
			else if (A.Sub == N_trick || A.Sub == N_release)
			{
				Arm[S] = FVector(0.1, 1.0 * Sd, 0.25);
				Leg[S] = A.Trick == N_tuckFlip ? FVector(1.0, 0.15 * Sd, -0.3) : A.Trick == N_scissor ? FVector(S ? 0.8 : -0.6, 0.1 * Sd, -1) : FVector(0.3, 0.2 * Sd, -1);
			}
			else if (A.Sub == N_zipPull) { Arm[S] = S ? FVector(1, 0.1, 0.25) : FVector(-0.2, -0.8, -0.2); Leg[S] = FVector(-0.3, 0.1 * Sd, -1); }
			else { Arm[S] = FVector(0.1, 0.9 * Sd, 0.3); Leg[S] = FVector(0.3, 0.2 * Sd, -1); }
		}
	}
	else if (M == EWebTravMode::Swing)
	{
		const int32 WebHand = A.Swing.bRightHand ? 1 : 0;
		const double Fwd = -A.Swing.Phase * 0.55 + 0.2;
		for (int32 S = 0; S < 2; ++S)
		{
			const double Sd = S == 0 ? -1.0 : 1.0;
			const FVector Shoulder = ArmPivot[S]->GetComponentLocation();
			Arm[S] = S == WebHand ? ToLocal(A.Swing.Anchor - Shoulder) : FVector(0.2, 0.9 * Sd, -0.2);
			Leg[S] = FVector(Fwd + (S ? 0.15 : -0.1), 0.1 * Sd, -1);
		}
	}
	else if (M == EWebTravMode::Zip)
	{
		for (int32 S = 0; S < 2; ++S)
		{
			const double Sd = S == 0 ? -1.0 : 1.0;
			Arm[S] = ToLocal(A.Zip.Target - ArmPivot[S]->GetComponentLocation());
			Leg[S] = FVector(-0.4, 0.1 * Sd, -1);
		}
	}
	else if (M == EWebTravMode::Wall)
	{
		const double Ph = A.Wall.Phase * 2 * PI;
		for (int32 S = 0; S < 2; ++S)
		{
			const double Sd = S == 0 ? -1.0 : 1.0;
			const double Sw = A.Wall.bFast ? FMath::Sin(Ph + (S ? PI : 0)) : 0;
			Arm[S] = FVector(0.6 + 0.3 * Sw, 0.45 * Sd, 0.5);
			Leg[S] = FVector(0.4 - 0.4 * Sw, 0.3 * Sd, -0.7);
		}
	}
	else if (M == EWebTravMode::Perch)
	{
		for (int32 S = 0; S < 2; ++S) { const double Sd = S == 0 ? -1.0 : 1.0; Arm[S] = FVector(0.7, 0.3 * Sd, -0.6); Leg[S] = FVector(0.9, 0.3 * Sd, -0.35); }
	}
	// quick web boost: the web hand reaches for its anchor
	if (A.bQuickActive && A.QuickT < 0.4f)
	{
		const int32 H = A.bQuickRightHand ? 1 : 0;
		const FWebTravStrand& St = Traversal->Strands[0];
		if (St.bActive) Arm[H] = ToLocal(St.Anchor * 100.0 - ArmPivot[H]->GetComponentLocation());
	}
	const double K = 1.0 - FMath::Exp(-18.0 * Dt);
	for (int32 S = 0; S < 2; ++S)
	{
		const FQuat WA = FQuat::FindBetweenNormals(FVector(0, 0, -1), Arm[S].GetSafeNormal());
		const FQuat WL = FQuat::FindBetweenNormals(FVector(0, 0, -1), Leg[S].GetSafeNormal());
		ArmPivot[S]->SetRelativeRotation(FQuat::Slerp(ArmPivot[S]->GetRelativeRotation().Quaternion(), WA, K));
		LegPivot[S]->SetRelativeRotation(FQuat::Slerp(LegPivot[S]->GetRelativeRotation().Quaternion(), WL, K));
	}
}

void AWebTravCharacter::UpdateWebs(float Dt, const FVector& CamPosCm)
{
	for (int32 SI = 0; SI < 2; ++SI)
	{
		const FWebTravStrand& St = Traversal->Strands[SI];
		const bool bReleased = St.bActive && St.ReleaseT >= 0.f;
		const FVector Hand = HandWorldCm(St.bRightHand);
		if (bReleased && !bWasReleased[SI]) ReleaseHandCm[SI] = Hand;
		bWasReleased[SI] = bReleased;
		FVector A = Hand, B = St.Anchor * 100.0;
		double Fade = 1.0, Wave = 0.0;
		if (St.bActive)
		{
			// shot: cubic ease-out extension, a decaying sine wave along the strand while it flies (web.js)
			const double U = FMath::Clamp(St.Age / FMath::Max(St.ShootDur, 0.01f), 0.0, 1.0);
			const double Ext = 1 - FMath::Pow(1 - U, 3);
			B = A + (B - A) * Ext;
			Wave = 30.0 * FMath::Exp(-9.0 * St.Age) * (1 - St.Taut);
			if (bReleased)
			{ // round 02: the released strand retracts from the hand toward its anchor and thins out (never sweeps the lens)
				const double R = St.ReleaseT;
				const double E = 1.0 - FMath::Pow(1.0 - FMath::Min(1.0, R / 0.18), 2);
				A = FMath::Lerp(Hand, B, E); // from the moving hand (stays in front of the lens), not the world point of release
				Fade = FMath::Clamp(1.0 - R / 0.25, 0.0, 1.0);
			}
		}
		const FVector D = B - A;
		const FVector Perp = FVector::CrossProduct(D.GetSafeNormal(), FVector::UpVector).GetSafeNormal();
		for (int32 K = 0; K < SEGS_PER_STRAND; ++K)
		{
			UStaticMeshComponent* C = WebSegs[SI * SEGS_PER_STRAND + K];
			if (!St.bActive || Fade <= 0.01 || D.Size() < 5.0) { C->SetVisibility(false); continue; }
			auto P = [&](double U)
			{
				return A + D * U + Perp * (Wave * FMath::Sin(U * PI * 3 + St.Age * 40.0) * FMath::Sin(U * PI));
			};
			const double U0 = double(K) / SEGS_PER_STRAND, U1 = double(K + 1) / SEGS_PER_STRAND;
			const FVector P0 = P(U0), P1 = P(U1);
			const FVector Mid = (P0 + P1) * 0.5;
			const double Len = FVector::Dist(P0, P1);
			// world width 2.2 cm, never thinner than ~1.6 px at 1080p (the browser ribbon's minimum-pixel rule)
			const double CamD = FVector::Dist(Mid, CamPosCm);
			if (CamD < 300.0) { C->SetVisibility(false); continue; } // never draw a strand segment on the lens
			const double W = FMath::Max(2.2, 0.0019 * CamD) * Fade;
			C->SetWorldLocationAndRotation(Mid, FRotationMatrix::MakeFromZ((P1 - P0).GetSafeNormal()).ToQuat());
			C->SetWorldScale3D(FVector(W / 100.0, W / 100.0, Len / 100.0));
			C->SetVisibility(true);
		}
	}
}

void AWebTravCharacter::PushTelemetry(double T, const FWebTravInput& I)
{
	UWebTravScript* Script = GetGameInstance()->GetSubsystem<UWebTravScript>();
	Script->SetTelemetryHeader(TEXT("frame,t,mode,sub,x_m,y_m,z_m,vx,vy,vz,speed_mps,hspeed_mps,height_above_floor_m,anchor_x,anchor_y,anchor_z,")
		TEXT("rope_m,tension,chain,trick,zip_target,zt_x,zt_y,zt_z,cam_x,cam_y,cam_z,cam_yaw_deg,cam_pitch_deg,cam_vfov_deg,cam_dist_m,motion_blur,")
		TEXT("in_move_x,in_move_y,in_swing,in_jump,in_sprint,in_zip,in_drop,in_quick,cam_orbit_pitch_deg,cam_auto_pitch_deg,cam_occ_hold,")
		TEXT("hero_bbox_h,hero_bbox_w,hero_cy,hero_in_frame,cam_hero_dist_m,cam_in_geometry,frame_s_target,in_trick,")
		TEXT("anim_node,anim_clip,anim_weight,air_flavor,pose_sig"));
	const FVector P = Traversal->PosM(), V = Traversal->VelM();
	const bool bSw = Traversal->IsSwinging();
	const FVector An = bSw ? Traversal->SwingAnchor() : FVector::ZeroVector;
	const FWebTravAnim& A = Traversal->Anim;
	// hero screen-space box: corners of every placeholder part's bounds projected through the final camera
	double MinX = 1e9, MaxX = -1e9, MinY = 1e9, MaxY = -1e9;
	bool bBehind = false;
	{
		const FRotationMatrix RM(Cam.CamRot);
		const FVector CF = RM.GetUnitAxis(EAxis::X), CR = RM.GetUnitAxis(EAxis::Y), CU = RM.GetUnitAxis(EAxis::Z);
		const double TV = FMath::Tan(FMath::DegreesToRadians(Cam.OutVFov * 0.5));
		double Aspect = 16.0 / 9.0;
		if (GEngine && GEngine->GameViewport && GEngine->GameViewport->Viewport)
		{
			const FIntPoint Sz = GEngine->GameViewport->Viewport->GetSizeXY();
			if (Sz.X > 0 && Sz.Y > 0) Aspect = double(Sz.X) / double(Sz.Y);
		}
		const FVector CP = Cam.CamPos;
		TArray<FBox> Boxes;
		if (bHeroMesh)
		{ // bone positions padded by 10 cm (limb thickness)
			const USkeletalMeshComponent* M = GetMesh();
			for (int32 Bi = 0; Bi < M->GetNumBones(); ++Bi)
			{
				const FVector BP = M->GetBoneLocation(M->GetBoneName(Bi));
				Boxes.Add(FBox(BP - FVector(10), BP + FVector(10)));
			}
		}
		else { for (const UStaticMeshComponent* C : FigureParts) { if (C) Boxes.Add(C->Bounds.GetBox()); } }
		for (const FBox& B : Boxes)
		{
			for (int32 K = 0; K < 8; ++K)
			{
				const FVector Corner((K & 1) ? B.Max.X : B.Min.X, (K & 2) ? B.Max.Y : B.Min.Y, (K & 4) ? B.Max.Z : B.Min.Z);
				const FVector Rel = Corner / 100.0 - CP;
				const double Z = FVector::DotProduct(Rel, CF);
				if (Z < 0.05) { bBehind = true; continue; }
				const double SX = 0.5 + 0.5 * FVector::DotProduct(Rel, CR) / (Z * TV * Aspect);
				const double SY = 0.5 - 0.5 * FVector::DotProduct(Rel, CU) / (Z * TV);
				MinX = FMath::Min(MinX, SX); MaxX = FMath::Max(MaxX, SX); MinY = FMath::Min(MinY, SY); MaxY = FMath::Max(MaxY, SY);
			}
		}
	}
	const bool bInFrame = !bBehind && MinX >= 0 && MaxX <= 1 && MinY >= 0 && MaxY <= 1;
	// pose signature: head / hands / feet relative to the hips, in camera right / up (m) — screen silhouette proxy
	FString Node = TEXT("none"), ClipN = TEXT("none"), Sig;
	float AW = 0.f; int32 Flav = -1;
	if (bHeroMesh)
	{
		const USkeletalMeshComponent* M = GetMesh();
		if (const UWebTravAnimInstance* AI = Cast<UWebTravAnimInstance>(M->GetAnimInstance()))
		{
			Node = AI->CurrentNode().ToString(); ClipN = AI->DominantClip().ToString(); AW = AI->TotalClipWeight(); Flav = AI->AirFlavor();
		}
		const FRotationMatrix RM(Cam.CamRot);
		const FVector CR = RM.GetUnitAxis(EAxis::Y), CU = RM.GetUnitAxis(EAxis::Z);
		const FVector Hip = M->GetBoneLocation(TEXT("hips"));
		for (const TCHAR* Bn : { TEXT("head"), TEXT("hand_L"), TEXT("hand_R"), TEXT("foot_L"), TEXT("foot_R") })
		{
			const FVector D = (M->GetBoneLocation(FName(Bn)) - Hip) / 100.0;
			Sig += FString::Printf(TEXT("%s%.3f %.3f"), Sig.IsEmpty() ? TEXT("") : TEXT(" "), FVector::DotProduct(D, CR), FVector::DotProduct(D, CU));
		}
	}
	const FString Row = FString::Printf(
		TEXT("%lld,%.4f,%s,%s,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.2f,%.2f,%.2f,%.2f,%.3f,%d,%s,%d,%.2f,%.2f,%.2f,%.3f,%.3f,%.3f,%.2f,%.2f,%.2f,%.3f,%.3f,%.2f,%.2f,%d,%d,%d,%d,%d,%d,%.2f,%.2f,%.2f,%.4f,%.4f,%.4f,%d,%.3f,%d,%.3f,%d,%s,%s,%.3f,%d,%s"),
		FrameIndex, T, ModeName(A.Mode), *A.Sub.ToString(), P.X, P.Y, P.Z, V.X, V.Y, V.Z, V.Size(), FVector2D(V.X, V.Y).Size(),
		P.Z - UWebTraversalComponent::H - Traversal->FloorBelow(), An.X, An.Y, An.Z, bSw ? Traversal->SwingRope() : 0.0, bSw ? Traversal->SwingTension() : 0.0,
		Traversal->Chain(), A.Trick.IsNone() ? TEXT("") : *A.Trick.ToString(), Traversal->HasZipTarget() ? 1 : 0,
		Traversal->ZipTargetPos().X, Traversal->ZipTargetPos().Y, Traversal->ZipTargetPos().Z,
		Cam.CamPos.X, Cam.CamPos.Y, Cam.CamPos.Z, Cam.CamRot.Yaw, Cam.CamRot.Pitch, Cam.OutVFov, FVector::Dist(Cam.CamPos, P), Cam.MotionBlur,
		I.Move.X, I.Move.Y, I.bSwing ? 1 : 0, I.bJump ? 1 : 0, I.bSprint ? 1 : 0, I.bZip ? 1 : 0, I.bDrop ? 1 : 0, I.bQuick ? 1 : 0,
		-FMath::RadiansToDegrees(Cam.Pitch), -FMath::RadiansToDegrees(Cam.DebugAutoPitch()), Cam.DebugOccHold(),
		bBehind ? 1.0 : MaxY - MinY, bBehind ? 1.0 : MaxX - MinX, bBehind ? -1.0 : 0.5 * (MinY + MaxY), bInFrame ? 1 : 0, Cam.HeroDist,
		Cam.bCamInGeometry ? 1 : 0, Cam.FrameS, I.bTrick ? 1 : 0, *Node, *ClipN, AW, Flav, *Sig);
	Script->AddTelemetryRow(Row);
}

// ------------------------------------------------------------------ game mode
AWebTravGameMode::AWebTravGameMode()
{
	DefaultPawnClass = AWebTravCharacter::StaticClass();
	PlayerControllerClass = AWebHomagePlayerController::StaticClass();
}
