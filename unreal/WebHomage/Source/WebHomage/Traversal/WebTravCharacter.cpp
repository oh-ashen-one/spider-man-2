// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Traversal/WebTravCharacter.h"
#include "Traversal/WebTraversalComponent.h"
#include "Traversal/WebTravScript.h"
#include "Traversal/Anim/WebTravAnimInstance.h"
#include "Traversal/WebTravFlips.h"
#include "HAL/IConsoleManager.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "ReferenceSkeleton.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Engine/TextureRenderTarget2D.h"
#include "TextureResource.h"
#include "Core/WebHomagePlayerController.h"
#include "WebHomage.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"

#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PointLightComponent.h"
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

// round 11 (owner: mouse look far too fast): MouseRadPerUnit 0.033 -> 0.011 and a sensitivity multiplier console variable
static TAutoConsoleVariable<float> CVarWHMouseSensitivity(TEXT("wh.MouseSensitivity"), 1.0f,
	TEXT("Mouse look sensitivity multiplier for the traversal hero (1 = default, radians per mouse unit = MouseRadPerUnit x this)."), ECVF_Default);

namespace
{
	const FName N_swingLow(TEXT("swingLow")), N_trick(TEXT("trick")), N_tuckFlip(TEXT("tuckFlip")), N_layout(TEXT("layout")),
		N_corkscrew(TEXT("corkscrew")), N_scissor(TEXT("scissor")), N_rise(TEXT("rise")), N_dive(TEXT("dive")), N_zipPull(TEXT("zipPull")),
		N_release(TEXT("release")), N_jumpLaunch(TEXT("jumpLaunch")), N_wallRun(TEXT("wallRun")), N_wallRunSide(TEXT("wallRunSide")),
		N_topOut(TEXT("topOut"));
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
	WebMat = Mat(FLinearColor(0.09f, 0.09f, 0.11f), 0.0f); // round 09: dark line (r08 pale grey vanished on the pale facades; r07 emissive bloomed)

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
	// round 04: the real hero; round 10: paths are properties (HeroMeshPath / HeroLensMeshPath / HeroClipRoot / HeroClipPrefix)
	{
		FString V;
		if (FParse::Value(FCommandLine::Get(), TEXT("-WHHeroMesh="), V)) HeroMeshPath = V;
		if (FParse::Value(FCommandLine::Get(), TEXT("-WHHeroLens="), V)) HeroLensMeshPath = V.Equals(TEXT("none"), ESearchCase::IgnoreCase) ? FString() : V;
		if (FParse::Value(FCommandLine::Get(), TEXT("-WHHeroClips="), V)) HeroClipRoot = V;
		if (FParse::Value(FCommandLine::Get(), TEXT("-WHHeroClipPrefix="), V)) HeroClipPrefix = V;
	}
	USkeletalMesh* Body = HeroMeshPath.IsEmpty() ? nullptr : LoadObject<USkeletalMesh>(nullptr, *HeroMeshPath);
	if (!Body)
	{
		UE_LOG(LogWebHomage, Warning, TEXT("WH_TRAV hero mesh missing (%s): placeholder figure stays"), *HeroMeshPath);
		return false;
	}
	UE_LOG(LogWebHomage, Display, TEXT("WH_TRAV hero: mesh %s, lens %s, clips %s/%s<clip>"), *HeroMeshPath,
		HeroLensMeshPath.IsEmpty() ? TEXT("(none)") : *HeroLensMeshPath, *HeroClipRoot, *HeroClipPrefix);
	UWebTravAnimInstance::ClipRoot = HeroClipRoot;
	UWebTravAnimInstance::ClipPrefix = HeroClipPrefix;
	USkeletalMeshComponent* M = GetMesh();
	M->SetAnimationMode(EAnimationMode::AnimationBlueprint);
	M->SetAnimInstanceClass(UWebTravAnimInstance::StaticClass());
	M->SetSkeletalMesh(Body);
	M->SetCastShadow(true);
	// round 06: the suit rendered white / unshaded for the first frames of a capture (textures streaming in late):
	// keep the hero's textures resident at full mip from the first frame
	M->SetTextureForceResidentFlag(true);
	M->bPerBoneMotionBlur = false; // round 09: limbs never smear (the city blurs, the hero stays crisp)
	M->PrestreamTextures(30.f, true);
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
	if (USkeletalMesh* Lens = HeroLensMeshPath.IsEmpty() ? nullptr : LoadObject<USkeletalMesh>(nullptr, *HeroLensMeshPath))
	{
		LensMesh = NewObject<USkeletalMeshComponent>(this, TEXT("HeroLenses"));
		LensMesh->SetupAttachment(M);
		LensMesh->SetSkeletalMesh(Lens);
		LensMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		LensMesh->RegisterComponent();
		LensMesh->SetLeaderPoseComponent(M);
		LensMesh->SetTextureForceResidentFlag(true);
	}
	for (UStaticMeshComponent* C : FigureParts) { if (C) C->SetVisibility(false); }
	for (USceneComponent* P : ArmPivot) { if (P) P->SetVisibility(false, true); }
	for (USceneComponent* P : LegPivot) { if (P) P->SetVisibility(false, true); }
	return true;
}

void AWebTravCharacter::BeginPlay()
{
	Super::BeginPlay();
	{ // round 07: -WHTravTune=Name=Value,... sets float tuning properties of the traversal component (tuning scans)
		FString Tune;
		if (FParse::Value(FCommandLine::Get(), TEXT("-WHTravTune="), Tune, false))
		{
			TArray<FString> Parts;
			Tune.ParseIntoArray(Parts, TEXT(","));
			for (const FString& Pr : Parts)
			{
				FString K, V;
				if (!Pr.Split(TEXT("="), &K, &V)) continue;
				if (FFloatProperty* FP = FindFProperty<FFloatProperty>(Traversal->GetClass(), FName(*K)))
				{
					FP->SetPropertyValue_InContainer(Traversal, FCString::Atof(*V));
					UE_LOG(LogWebHomage, Display, TEXT("WH_TRAV tune %s = %s"), *K, *V);
				}
				else UE_LOG(LogWebHomage, Warning, TEXT("WH_TRAV tune: no float property %s"), *K);
			}
		}
	}
	float Pre = 0.f;
	if (FParse::Value(FCommandLine::Get(), TEXT("-WHTravPreroll="), Pre) && Pre > 0.f) { PrerollLeft = Pre; bHadPreroll = true; }
	if (ProxyBody) ProxyBody->SetVisibility(false);
	GetCharacterMovement()->SetMovementMode(MOVE_None);
	GetCharacterMovement()->SetComponentTickEnabled(false);
	BuildFigure();
	bHeroMesh = SetupHeroMesh();
	{ // round 13: hero-only fill light (see HeroFillCd)
		FString FillArg;
		if (FParse::Value(FCommandLine::Get(), TEXT("-WHHeroFill="), FillArg))
		{
			FString A, B;
			if (FillArg.Split(TEXT(","), &A, &B)) { HeroFillCd = FCString::Atof(*A); HeroFillFlipCd = FCString::Atof(*B); }
			else HeroFillCd = HeroFillFlipCd = FCString::Atof(*FillArg);
		}
		if (bHeroMesh && (HeroFillCd > 0.f || HeroFillFlipCd > 0.f))
		{
			HeroFill = NewObject<UPointLightComponent>(this, TEXT("HeroFill"));
			HeroFill->SetupAttachment(RootComponent);
			HeroFill->SetUsingAbsoluteLocation(true);
			HeroFill->SetMobility(EComponentMobility::Movable);
			HeroFill->RegisterComponent();
			HeroFill->SetIntensityUnits(ELightUnits::Candelas);
			HeroFill->SetIntensity(HeroFillCd);
			HeroFill->SetLightColor(FLinearColor(1.0f, 0.93f, 0.84f));
			HeroFill->SetCastShadows(false);
			HeroFill->SetVolumetricScatteringIntensity(0.f);
			HeroFill->SetIndirectLightingIntensity(0.f);
			HeroFill->SetAttenuationRadius(600.f);
			HeroFill->SourceRadius = 20.f;
			HeroFill->SetLightingChannels(false, true, false); // channel 1 only
			GetMesh()->SetLightingChannels(true, true, false);
			if (LensMesh) LensMesh->SetLightingChannels(true, true, false);
			UE_LOG(LogWebHomage, Display, TEXT("WH_TRAV hero fill light: %.0f cd (flip %.0f cd), %.1f m toward the camera"), HeroFillCd, HeroFillFlipCd, HeroFillDist);
		}
	}

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
	if (bHeroMesh && Script && Script->WantsTelemetry())
	{ // pixel mask of the hero for telemetry: scene depth of the hero meshes only, 480x270, from the view camera
		MaskRT = NewObject<UTextureRenderTarget2D>(this, TEXT("HeroMaskRT"));
		MaskRT->RenderTargetFormat = ETextureRenderTargetFormat::RTF_RGBA16f;
		MaskRT->ClearColor = FLinearColor(65000.f, 65000.f, 65000.f, 1.f);
		MaskRT->InitAutoFormat(480, 270);
		MaskRT->UpdateResourceImmediate(true);
		MaskCapture = NewObject<USceneCaptureComponent2D>(this, TEXT("HeroMaskCapture"));
		MaskCapture->SetupAttachment(RootComponent);
		MaskCapture->SetUsingAbsoluteLocation(true);
		MaskCapture->SetUsingAbsoluteRotation(true);
		MaskCapture->CaptureSource = ESceneCaptureSource::SCS_SceneDepth;
		MaskCapture->PrimitiveRenderMode = ESceneCapturePrimitiveRenderMode::PRM_UseShowOnlyList;
		MaskCapture->ShowOnlyComponents.Add(GetMesh());
		if (LensMesh) MaskCapture->ShowOnlyComponents.Add(LensMesh);
		MaskCapture->bCaptureEveryFrame = true;
		MaskCapture->bCaptureOnMovement = false;
		MaskCapture->TextureTarget = MaskRT;
		MaskCapture->RegisterComponent();
		// round 08: the whole scene's depth from the same camera (web strands hidden) for wall_frac / hero_occl
		SceneRT = NewObject<UTextureRenderTarget2D>(this, TEXT("SceneDepthRT"));
		SceneRT->RenderTargetFormat = ETextureRenderTargetFormat::RTF_RGBA16f;
		SceneRT->ClearColor = FLinearColor(65000.f, 65000.f, 65000.f, 1.f);
		SceneRT->InitAutoFormat(480, 270);
		SceneRT->UpdateResourceImmediate(true);
		SceneCapture = NewObject<USceneCaptureComponent2D>(this, TEXT("SceneDepthCapture"));
		SceneCapture->SetupAttachment(RootComponent);
		SceneCapture->SetUsingAbsoluteLocation(true);
		SceneCapture->SetUsingAbsoluteRotation(true);
		SceneCapture->CaptureSource = ESceneCaptureSource::SCS_SceneDepth;
		SceneCapture->PrimitiveRenderMode = ESceneCapturePrimitiveRenderMode::PRM_RenderScenePrimitives;
		for (UStaticMeshComponent* W : WebSegs) { if (W) SceneCapture->HiddenComponents.Add(W); }
		SceneCapture->bCaptureEveryFrame = true;
		SceneCapture->bCaptureOnMovement = false;
		SceneCapture->TextureTarget = SceneRT;
		SceneCapture->RegisterComponent();
	}
	UE_LOG(LogWebHomage, Display, TEXT("WH_TRAV ready: %d building boxes, spawn %s m yaw %.1f"), Traversal->BuildingCount(), *PosM.ToString(), YawDeg);
}

// ------------------------------------------------------------------ per frame
void AWebTravCharacter::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	const double Dt = FMath::Clamp(double(DeltaSeconds), 1e-4, 0.1);
	// round 12 (planning tool): -WHTravHeightmap=<csv> writes the traversal world's height field once (5 m grid, down-rays from
	// 600 m; x, y, top z, ground flag) — the roofs the sky-launch solver and the web search actually see (the exported
	// collision.json misses geometry the lit map has)
	{
		static bool bHmDone = false;
		FString HmPath;
		if (!bHmDone && Traversal && FParse::Value(FCommandLine::Get(), TEXT("-WHTravHeightmap="), HmPath))
		{
			bHmDone = true;
			FString Out = TEXT("x,y,z,ground\n");
			double HX0 = -320.0, HY0 = -620.0, HX1 = 680.0, HY1 = 380.0;
			FString Ext;
			if (FParse::Value(FCommandLine::Get(), TEXT("-WHTravHmExt="), Ext))
			{
				TArray<FString> E; Ext.ParseIntoArray(E, TEXT(","));
				if (E.Num() == 4) { HX0 = FCString::Atod(*E[0]); HY0 = FCString::Atod(*E[1]); HX1 = FCString::Atod(*E[2]); HY1 = FCString::Atod(*E[3]); }
			}
			for (double Y = HY0; Y <= HY1; Y += 5.0)
				for (double X = HX0; X <= HX1; X += 5.0)
				{
					FTravHit Hh;
					if (Traversal->TravWorld.Raycast(FVector(X, Y, 600.0), FVector(0, 0, -1), 700.0, Hh))
						Out += FString::Printf(TEXT("%.0f,%.0f,%.1f,%d\n"), X, Y, Hh.Point.Z, Hh.bGround ? 1 : 0);
				}
			FFileHelper::SaveStringToFile(Out, *HmPath);
			UE_LOG(LogWebHomage, Display, TEXT("WH_TRAV heightmap written: %s"), *HmPath);
		}
	}
	// round 06: capture pre-roll (-WHTravPreroll=<s>): the start pose is rendered for a while (camera, exposure, Lumen settle)
	// with the traversal frozen and no input / telemetry; capture_round.sh trims these frames. Auto-exposure lag at the start
	// is what rendered the suit white / blown out in the first ~0.6 s of earlier captures.
	const bool bPre = PrerollLeft > 0.0;
	if (bPre) PrerollLeft -= Dt;
	else if (!bTravStarted)
	{
		bTravStarted = true; TravTime = 0.0;
		if (bHadPreroll)
		{
			if (UWebTravAnimInstance* AI = Cast<UWebTravAnimInstance>(GetMesh()->GetAnimInstance())) AI->ResetForSequenceStart();
			UE_LOG(LogWebHomage, Display, TEXT("WH_TRAV preroll done: %d frames"), PrerollFrames);
		}
	}
	else TravTime += Dt;
	if (bPre) ++PrerollFrames;

	ReadHeroMask(); // previous frame's hero pixel mask (telemetry)
	// ---- input: live (keyboard / mouse / pad) or scripted playback
	FWebTravInput I;
	UWebTravScript* Script = GetGameInstance() ? GetGameInstance()->GetSubsystem<UWebTravScript>() : nullptr;
	if (bPre) {} // pre-roll: no input
	else if (Script && Script->IsActive())
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
			// round 07: a player lets go after the swoop — only once this swing has come down (vz < -3 m/s)
			if (!bSwinging) bAutoSawDescent = false;
			else if (Traversal->VelM().Z < -3.0) bAutoSawDescent = true;
			double SkyRepressH = 18.0, SkyMax = 3.0, SkyPhase = 0.8;
			int32 SkyTricks = 2;
			const int32 SkyEvery = Script->SkyEveryAt(TravTime, SkyRepressH, SkyTricks, SkyMax, SkyPhase);
			bool bKeepSwingThisFrame = false;
			// round 10: the sky release lets the arc climb further (skyPhase) before the launch
			// round 10 (T7 "peak at roofline height, then 1-4 storeys over the street"): the next release is a sky launch when it is
			// >= skyEvery releases after the previous one AND the lower street wall ahead is within reach (its roofline <=
			// SkyPeakMax + 8 m over the street; a player launches where he can top the block), or 5.5 s after the previous one anyway
			bool bSkyNext = false;
			if (SkyEvery > 0 && AutoReleases + 1 - LastSkyRelease >= SkyEvery && bSwinging)
			{
				// round 12: reachable = the apex that clears the tallest roof near the flip (SkyPeakNeeded) is within SkyPeakMax
				bool bReach = false;
				Traversal->SkyPeakNeeded(bReach);
				bSkyNext = bReach; // round 12: no forced launch any more (r10: "or 5.5 s after the last one anyway" flipped under the roofline)
			}
			const double RelPhaseEff = bSkyNext ? SkyPhase : RelPhase;
			// round 10 (Manhattan integration: releasePhase 0.85 left him hanging at 49 m for 14 s — a swing that never came down
			// fast or never reached the release phase): a player lets go of a stale swing after 2.4 s whatever its phase
			const bool bStale = bSwinging && A.ModeT > 2.4f;
			// round 10 (T1 rope held 0.5-1.6 s): past the low point and 1.45 s into the swing he lets go (the long web after a sky
			// launch held 2.1-2.2 s)
			// (the cut varies 1.25-1.55 s by release count so consecutive swings differ in length)
			// round 13 (T2 attach -> attach <= 3.3 s): a swing that ends in a flip program is let go at 1.05-1.2 s
			const int32 EveryNext = Script->TrickEveryAt(TravTime);
			const bool bTrickNext = EveryNext > 0 && (AutoReleases + 1) % EveryNext == 0 && !Traversal->bTrickLaunch;
			// (round 14: 1.05-1.2 -> 0.98-1.12 s: the eased backDouble catches 0.07 s later, T2 kept <= 2.65 s)
			const float LongCut = bTrickNext ? 0.98f + 0.14f * float((AutoReleases * 37) % 7) / 6.f : 1.25f + 0.3f * float((AutoReleases * 37) % 7) / 6.f;
			const bool bLong = bSwinging && bAutoSawDescent && A.ModeT > LongCut && Traversal->VelM().Z > 0;
			if (bAutoHeld && bSwinging && ((bAutoSawDescent && ((A.Swing.Phase > RelPhaseEff && Traversal->VelM().Z > 0 && A.T > 0.25f) || bFrontApex)) || bStale || bLong))
			{
				bAutoHeld = false; AutoGapT = 0.0; ++AutoReleases;
				const int32 Every = Script->TrickEveryAt(TravTime);
				if (bSkyNext)
				{
					LastSkyRelease = AutoReleases; LastSkyT = TravTime; SkyPeakH = 0.0; // round 10: sky launch = jump pressed while the web is still held (jump-release) + trick pressed with it
					I.bJump = true; I.bTrick = true; bKeepSwingThisFrame = true;
					bSkyAuto = true; bSkyWasTrick = false; SkyTricksLeft = FMath::Max(0, SkyTricks - 1); SkyAutoT = 0.0;
				}
				else if (Every > 0 && AutoReleases % Every == 0)
				{ // trick pressed together with this release (round 12: with bTrickLaunch that release is a sky launch: same bookkeeping)
					I.bTrick = true;
					if (Traversal->bTrickLaunch)
					{
						LastSkyRelease = AutoReleases; LastSkyT = TravTime; SkyPeakH = 0.0; bKeepSwingThisFrame = true;
						bSkyAuto = true; bSkyWasTrick = false; SkyTricksLeft = FMath::Max(0, SkyTricks - 1); SkyAutoT = 0.0;
					}
				}
			}
			else if (!bAutoHeld && bSkyAuto)
			{ // sky phase: chain the next trick the moment one ends, then re-press once falling through skyRepressH
				AutoGapT += Dt;
				const bool bTrickNow = A.Sub == FName(TEXT("trick"));
				// round 12: the flip now plays at the apex (armed on the climb): the skyMax clock runs only outside the climb / program,
				// and the web is re-pressed in the program's final reach so the catch comes out of the reach (FLIPS_SPEC F8)
				if (!Traversal->IsFlipArmed() && !bTrickNow) SkyAutoT += Dt;
				bool bInReach = false;
				{
					float Ft = 0.f;
					if (const FWebFlipProgram* FP = bTrickNow ? FlipProgramNow(Ft) : nullptr)
						bInReach = FP->Segs.Num() > 0 && Ft >= FP->CatchT() - 0.1f; // round 13: the program's catch window
				}
				if (bSkyWasTrick && !bTrickNow && SkyTricksLeft > 0 && Traversal->VelM().Z > -12.0) { I.bTrick = true; --SkyTricksLeft; }
				bSkyWasTrick = bTrickNow;
				// round 10: re-press once he has fallen 12 m from the peak (or through skyRepressH): the long web after a sky launch
				// then carries him down to the street (StartSwing: SkyRopeMax) instead of a web-less fall
				const double HS = Traversal->HeightAboveStreet();
				SkyPeakH = FMath::Max(SkyPeakH, HS);
				if ((Traversal->VelM().Z < 0 && (HS <= SkyRepressH || HS <= SkyPeakH - 12.0) && !bTrickNow) || SkyAutoT >= SkyMax || bInReach)
				{
					bAutoHeld = true; bSkyAuto = false;
				}
			}
			else if (!bAutoHeld) { AutoGapT += Dt; if (AutoGapT >= Gap && Traversal->VelM().Z <= RepressVz) bAutoHeld = true; }
			bAutoWasSwinging = bSwinging;
			I.bSwing = bAutoHeld || bKeepSwingThisFrame;
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
		const float MSens = MouseRadPerUnit * FMath::Max(0.f, CVarWHMouseSensitivity.GetValueOnGameThread());
		I.Look = FVector2D(MouseAccum.X * MSens, -MouseAccum.Y * MSens)
			+ FVector2D(PadLook.X * PadLookRate.X, -PadLook.Y * PadLookRate.Y) * Dt;
	}
	MouseAccum = FVector2D::ZeroVector;
	I.ComputeEdges(PrevInput);
	PrevInput = I;

	// ---- camera look, traversal, camera
	Cam.ApplyLook(I.Look);
	// pre-roll: the camera state is restored after the frame is set up and the traversal is only posed (not stepped), so the
	// sequence that follows is bit-identical to a run without pre-roll
	const FWebTravCamera PreCam = Cam;
	if (bPre) Traversal->PosePreview(); else Traversal->UpdateTraversal(Dt, I);
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
	CI.SwingT = Traversal->SwingTime();
	CI.bSky = Traversal->IsSkyLaunch();
	// round 12: the flip camera starts searching for a sky background ~0.35 s before an armed apex flip begins
	CI.bFlipSoon = Traversal->IsFlipArmed() && Traversal->VelM().Z < double(Traversal->SkyTrickVz) + 5.0;
	{ float Ft = 0.f; CI.bFlip = Traversal->Anim.Sub == N_trick && FlipProgramNow(Ft) != nullptr; } // round 11: flip camera
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
	// round 08 (critic r07: blur smeared the whole frame and the hero at all times): no base amount, only at real speed
	FollowCamera->PostProcessSettings.MotionBlurAmount = float(FMath::Clamp(0.35 * Cam.MotionBlur, 0.0, 0.5));
	FollowCamera->PostProcessSettings.MotionBlurMax = float(1.0 + 2.0 * Cam.MotionBlur);
	if (MaskCapture) { MaskCapture->SetWorldLocationAndRotation(CamCm, Cam.CamRot); MaskCapture->FOVAngle = FollowCamera->FieldOfView; }
	if (SceneCapture) { SceneCapture->SetWorldLocationAndRotation(CamCm, Cam.CamRot); SceneCapture->FOVAngle = FollowCamera->FieldOfView; }
	UpdateHeroFill();

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
	if (bPre) { Cam = PreCam; return; }
	if (Script && Script->WantsTelemetry()) PushTelemetry(TravTime, I);
	++FrameIndex;
}

void AWebTravCharacter::UpdateHeroFill()
{
	if (!HeroFill) return;
	const FVector Hero = Traversal->PosM() * 100.0 + FVector(0, 0, 20.0);
	const FVector CamCm = Cam.CamPos * 100.0;
	FVector To = CamCm - Hero;
	To = To.SizeSquared() > 1.0 ? To.GetSafeNormal() : FVector(-1, 0, 0);
	HeroFill->SetWorldLocation(Hero + To * (HeroFillDist * 100.0) + FVector(0, 0, HeroFillUp * 100.0));
	const double K = FMath::Clamp(Cam.FlipK, 0.0, 1.0);
	HeroFill->SetIntensity(float(FMath::Lerp(double(HeroFillCd), double(HeroFillFlipCd), K)));
}

const FWebFlipProgram* AWebTravCharacter::FlipProgramNow(float& OutT) const
{
	const FWebTravAnim& A = Traversal->Anim;
	OutT = A.T;
	if (A.Mode != EWebTravMode::Air) return nullptr;
	if (A.Sub == N_trick && !A.Trick.IsNone()) return WebFlips::Find(A.Trick);
	if (A.Sub == N_topOut && bHeroMesh)
	{ // round 11: the wall-run top-out flip is a program too (only with the flip shape clips: the old releaseFlip clip spins by itself)
		const UWebTravAnimInstance* AI = Cast<UWebTravAnimInstance>(GetMesh()->GetAnimInstance());
		if (AI && AI->HasFlipClips()) return WebFlips::Find(FName(TEXT("wallFront")));
	}
	return nullptr;
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
	// round 11 (FLIPS_BRIEF): gymnast flip programs rotate the whole body about its centre — pitch about the lateral axis, twist
	// about the long axis — on the program's momentum timeline (WebTravFlips); a cut program (web catch / landing) hands its last
	// rotation to a 0.07 s spring back to the body frame, so a catch never pops
	float FlipT = 0.f;
	const FWebFlipProgram* FP = FlipProgramNow(FlipT);
	if (FP)
	{
		const FWebFlipPose FPo = WebFlips::Sample(*FP, FlipT);
		// round 14: minus the shape's own hips->head lean (ramped in over the first 0.15 s while the anim crossfades into the first
		// shape), so the visible body axis turns at the program's eased rate instead of spiking at every shape change
		const double AxisOff = FPo.AxisOffDeg * Smooth01(FlipT / 0.15);
		FlipOffQ = FQuat(FVector(0, 1, 0), FMath::DegreesToRadians(FPo.PitchDeg - AxisOff)) * FQuat(FVector(0, 0, 1), FMath::DegreesToRadians(FPo.TwistDeg) * A.TrickSide);
		LastFlip = FPo; LastFlipName = FP->Name;
	}
	else
	{
		FlipOffQ = FQuat::Slerp(FlipOffQ, FQuat::Identity, 1.0 - FMath::Exp(-Dt / 0.07));
		LastFlip = FWebFlipPose(); LastFlipName = NAME_None;
	}
	if (FP || FlipOffQ.GetAngle() > FMath::DegreesToRadians(0.2))
	{
		Q = Body * FlipOffQ;
		const FVector Centre = Traversal->PosM() * 100.0;
		Root = Centre - Q.RotateVector(FVector(0, 0, 95));
	}
	else if (A.Sub == N_trick && !A.Trick.IsNone() && A.TrickDur > 0)
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
	// round 06: its weight is a spring (was switched on at full amplitude when a trick ended: one-frame body pop)
	const bool bSwayOn = bHeroMesh && A.Mode == EWebTravMode::Air && A.Sub != N_trick && A.Sub != N_topOut; // round 09: dives sway too
	SwayW = FMath::Clamp(SwayW + (bSwayOn ? Dt / 0.2f : -Dt / 0.2f), 0.f, 1.f);
	if (bHeroMesh && A.Mode == EWebTravMode::Air && SwayW > 0.001f)
	{
		if (const UWebTravAnimInstance* AI = Cast<UWebTravAnimInstance>(GetMesh()->GetAnimInstance()))
		{
			if (AI->InAirCycle())
			{
				const double Tc = AI->AirCycleTime(), Ph = AI->AirCycleCount() * 1.7;
				const double Ramp = FMath::Clamp(Tc / 0.3, 0.0, 1.0) * Smooth01(SwayW); // round 09: dives sway too
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
			// round 08 (critic r07: thick blooming beam): world width 1.2 cm, never thinner than ~1.2 px at 1080p
			const double CamD = FVector::Dist(Mid, CamPosCm);
			if (CamD < 300.0) { C->SetVisibility(false); continue; } // never draw a strand segment on the lens
			const double W = FMath::Max(1.6, 0.0025 * CamD) * Fade; // round 09: 1.6 cm, >= ~2 px at 1080p (TRAVERSAL-SPEC T6: 2-4 px)
			C->SetWorldLocationAndRotation(Mid, FRotationMatrix::MakeFromZ((P1 - P0).GetSafeNormal()).ToQuat());
			C->SetWorldScale3D(FVector(W / 100.0, W / 100.0, Len / 100.0));
			C->SetVisibility(true);
		}
	}
}

void AWebTravCharacter::ReadHeroMask()
{
	PxTop = PxBottom = PxLeft = PxRight = -1.f; WallFrac = HeroOccl = -1.f;
	if (!MaskRT) return;
	FTextureRenderTargetResource* Res = MaskRT->GameThread_GetRenderTargetResource();
	if (!Res) return;
	TArray<FLinearColor> Px;
	if (!Res->ReadLinearColorPixels(Px) || Px.Num() != 480 * 270) return;
	// round 08: near-wall share (non-hero pixels whose scene depth < 6 m) and hero occlusion (hero pixels with something
	// > 0.3 m in front of the hero surface)
	if (SceneRT)
	{
		if (FTextureRenderTargetResource* SR = SceneRT->GameThread_GetRenderTargetResource())
		{
			TArray<FLinearColor> Sc;
			if (SR->ReadLinearColorPixels(Sc) && Sc.Num() == Px.Num())
			{
				int32 Near = 0, NonHero = 0, Hero = 0, Occ = 0;
				// view rays of the capture camera: a near pixel whose world point lies on the street (z < 0.4 m) is floor, not
				// a facade, and is not counted
				const FRotationMatrix RM(Cam.CamRot);
				const FVector CF = RM.GetUnitAxis(EAxis::X), CR = RM.GetUnitAxis(EAxis::Y), CU = RM.GetUnitAxis(EAxis::Z);
				const double TV = FMath::Tan(FMath::DegreesToRadians(Cam.OutVFov * 0.5)), TH = TV * 480.0 / 270.0;
				for (int32 K = 0; K < Px.Num(); ++K)
				{
					const float HD = Px[K].R, SD = Sc[K].R;
					if (HD < 20000.f) { ++Hero; if (SD < HD - 30.f) ++Occ; continue; }
					++NonHero;
					if (SD >= 600.f) continue;
					const double U = ((K % 480) + 0.5) / 480.0 * 2.0 - 1.0, V = 1.0 - ((K / 480) + 0.5) / 270.0 * 2.0;
					const double WZ = Cam.CamPos.Z + (CF.Z + CR.Z * U * TH + CU.Z * V * TV) * SD / 100.0;
					if (WZ > 0.4) ++Near;
				}
				WallFrac = float(Near) / float(FMath::Max(1, Px.Num()));
				HeroOccl = Hero > 0 ? float(Occ) / float(Hero) : 1.f;
			}
		}
	}
	int32 Y0 = 9999, Y1 = -1, X0 = 9999, X1 = -1;
	for (int32 Y = 0; Y < 270; ++Y)
	{
		for (int32 X = 0; X < 480; ++X)
		{
			if (Px[Y * 480 + X].R < 20000.f) { Y0 = FMath::Min(Y0, Y); Y1 = FMath::Max(Y1, Y); X0 = FMath::Min(X0, X); X1 = FMath::Max(X1, X); }
		}
	}
	if (Y1 >= 0) { PxTop = Y0 * 4.f; PxBottom = (Y1 + 1) * 4.f; PxLeft = X0 * 4.f; PxRight = (X1 + 1) * 4.f; } // 1920x1080 pixels
}

void AWebTravCharacter::PushTelemetry(double T, const FWebTravInput& I)
{
	UWebTravScript* Script = GetGameInstance()->GetSubsystem<UWebTravScript>();
	Script->SetTelemetryHeader(TEXT("frame,t,mode,sub,x_m,y_m,z_m,vx,vy,vz,speed_mps,hspeed_mps,height_above_floor_m,anchor_x,anchor_y,anchor_z,")
		TEXT("rope_m,tension,chain,trick,zip_target,zt_x,zt_y,zt_z,cam_x,cam_y,cam_z,cam_yaw_deg,cam_pitch_deg,cam_vfov_deg,cam_dist_m,motion_blur,")
		TEXT("in_move_x,in_move_y,in_swing,in_jump,in_sprint,in_zip,in_drop,in_quick,cam_orbit_pitch_deg,cam_auto_pitch_deg,cam_occ_hold,")
		TEXT("hero_bbox_h,hero_bbox_w,hero_cy,hero_in_frame,cam_hero_dist_m,cam_in_geometry,frame_s_target,in_trick,")
		TEXT("anim_node,anim_clip,anim_weight,air_flavor,pose_sig,pcm_x,pcm_y,pcm_z,pcm_pitch,pcm_yaw,pcm_fov,px_top,px_bottom,px_left,px_right,head_hip_dz,limb_z,body_rope_deg,web_on,wall_frac,hero_occl,hero_cx,pcm_roll,")
		TEXT("flip_prog,flip_t,flip_pitch_deg,flip_twist_deg,flip_rate_dps,flip_shape,flip_shape_legs,body_axis_deg,body_pitch_deg,body_roll_deg,flip_armed,flipcam_k,flipcam_yaw_deg,flipcam_elev_deg,flipcam_sky,sky_tall_m,sky_peak_want_m,cam_slew,hero_fill_cd"));
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
	FString Node = TEXT("none"), ClipN = TEXT("none"), Sig, LimbZ;
	double HeadHipDz = 0.0, BodyRope = -1.0;
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
		// round 06: world-up offsets from the hips (m): head, and hands / feet (limb phase on a wall = their order up the wall)
		HeadHipDz = (M->GetBoneLocation(TEXT("head")).Z - Hip.Z) / 100.0;
		// round 07: body axis (hips -> head) vs the web (hips -> anchor), degrees, while swinging
		if (bSw)
		{
			const FVector BodyAx = (M->GetBoneLocation(TEXT("head")) - Hip).GetSafeNormal(), RopeAx = (An * 100.0 - Hip).GetSafeNormal();
			BodyRope = FMath::RadiansToDegrees(FMath::Acos(FMath::Clamp(FVector::DotProduct(BodyAx, RopeAx), -1.0, 1.0)));
		}
		for (const TCHAR* Bn : { TEXT("hand_L"), TEXT("hand_R"), TEXT("foot_L"), TEXT("foot_R") })
		{
			LimbZ += FString::Printf(TEXT("%s%.3f"), LimbZ.IsEmpty() ? TEXT("") : TEXT(" "), (M->GetBoneLocation(FName(Bn)).Z - Hip.Z) / 100.0);
		}
	}
	// round 11: flip program state + the RENDERED body axis from the bones (hips -> head): angle from world up (0..180), and the
	// signed pitch of that axis in the facing plane (+ = head forward) and roll in the lateral plane
	double BodyAxis = -1.0, BodyPitch = 0.0, BodyRoll = 0.0;
	if (bHeroMesh)
	{
		const USkeletalMeshComponent* M = GetMesh();
		const FVector Ax = (M->GetBoneLocation(TEXT("head")) - M->GetBoneLocation(TEXT("hips"))).GetSafeNormal();
		const double Fy = FMath::DegreesToRadians(A.FacingDeg);
		const FVector Fw(FMath::Cos(Fy), FMath::Sin(Fy), 0.0), Rt(-FMath::Sin(Fy), FMath::Cos(Fy), 0.0);
		BodyAxis = FMath::RadiansToDegrees(FMath::Acos(FMath::Clamp(Ax.Z, -1.0, 1.0)));
		BodyPitch = FMath::RadiansToDegrees(FMath::Atan2(FVector::DotProduct(Ax, Fw), Ax.Z));
		BodyRoll = FMath::RadiansToDegrees(FMath::Atan2(FVector::DotProduct(Ax, Rt), Ax.Z));
	}
	float FlipTNow = 0.f;
	const bool bFlipNow = FlipProgramNow(FlipTNow) != nullptr && LastFlip.bValid;
	const FString FlipCols = FString::Printf(TEXT("%s,%.3f,%.1f,%.1f,%.1f,%s,%s,%.1f,%.1f,%.1f"),
		bFlipNow ? *LastFlipName.ToString() : TEXT(""), bFlipNow ? FlipTNow : -1.f, bFlipNow ? LastFlip.PitchDeg : 0.f, bFlipNow ? LastFlip.TwistDeg : 0.f,
		bFlipNow ? LastFlip.PitchRate : 0.f,
		bFlipNow ? (LastFlip.W < 0.5f ? WebFlips::ShapeName(LastFlip.A) : WebFlips::ShapeName(LastFlip.B)) : TEXT(""),
		bFlipNow ? (LastFlip.LW < 0.5f ? WebFlips::ShapeName(LastFlip.LA) : WebFlips::ShapeName(LastFlip.LB)) : TEXT(""),
		BodyAxis, BodyPitch, BodyRoll);
	// the camera the engine actually rendered with (player camera manager cache)
	FVector PcmLoc = FVector::ZeroVector; FRotator PcmRot = FRotator::ZeroRotator; float PcmFov = 0.f;
	if (const APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (PC->PlayerCameraManager) { PcmLoc = PC->PlayerCameraManager->GetCameraLocation(); PcmRot = PC->PlayerCameraManager->GetCameraRotation(); PcmFov = PC->PlayerCameraManager->GetFOVAngle(); }
	}
	const FString Row = FString::Printf(
		TEXT("%lld,%.4f,%s,%s,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.2f,%.2f,%.2f,%.2f,%.3f,%d,%s,%d,%.2f,%.2f,%.2f,%.3f,%.3f,%.3f,%.2f,%.2f,%.2f,%.3f,%.3f,%.2f,%.2f,%d,%d,%d,%d,%d,%d,%.2f,%.2f,%.2f,%.4f,%.4f,%.4f,%d,%.3f,%d,%.3f,%d,%s,%s,%.3f,%d,%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.0f,%.0f,%.0f,%.0f,%.3f,%s,%.1f,%d,%.3f,%.3f,%.4f,%.2f"),
		FrameIndex, T, ModeName(A.Mode), *A.Sub.ToString(), P.X, P.Y, P.Z, V.X, V.Y, V.Z, V.Size(), FVector2D(V.X, V.Y).Size(),
		P.Z - UWebTraversalComponent::H - Traversal->FloorBelow(), An.X, An.Y, An.Z, bSw ? Traversal->SwingRope() : 0.0, bSw ? Traversal->SwingTension() : 0.0,
		Traversal->Chain(), A.Trick.IsNone() ? TEXT("") : *A.Trick.ToString(), Traversal->HasZipTarget() ? 1 : 0,
		Traversal->ZipTargetPos().X, Traversal->ZipTargetPos().Y, Traversal->ZipTargetPos().Z,
		Cam.CamPos.X, Cam.CamPos.Y, Cam.CamPos.Z, Cam.CamRot.Yaw, Cam.CamRot.Pitch, Cam.OutVFov, FVector::Dist(Cam.CamPos, P), Cam.MotionBlur,
		I.Move.X, I.Move.Y, I.bSwing ? 1 : 0, I.bJump ? 1 : 0, I.bSprint ? 1 : 0, I.bZip ? 1 : 0, I.bDrop ? 1 : 0, I.bQuick ? 1 : 0,
		-FMath::RadiansToDegrees(Cam.Pitch), -FMath::RadiansToDegrees(Cam.DebugAutoPitch()), Cam.DebugOccHold(),
		bBehind ? 1.0 : MaxY - MinY, bBehind ? 1.0 : MaxX - MinX, bBehind ? -1.0 : 0.5 * (MinY + MaxY), bInFrame ? 1 : 0, Cam.HeroDist,
		Cam.bCamInGeometry ? 1 : 0, Cam.FrameS, I.bTrick ? 1 : 0, *Node, *ClipN, AW, Flav, *Sig,
		PcmLoc.X / 100.0, PcmLoc.Y / 100.0, PcmLoc.Z / 100.0, PcmRot.Pitch, PcmRot.Yaw, PcmFov, PxTop, PxBottom, PxLeft, PxRight,
		HeadHipDz, LimbZ.IsEmpty() ? TEXT("-") : *LimbZ, BodyRope,
		(Traversal->Strands[0].bActive && Traversal->Strands[0].ReleaseT < 0.f) || (Traversal->Strands[1].bActive && Traversal->Strands[1].ReleaseT < 0.f) ? 1 : 0, WallFrac, HeroOccl, bBehind ? -1.0 : 0.5 * (MinX + MaxX), PcmRot.Roll);
	// round 12: armed apex flip, flip camera view search (yaw offset from behind, elevation below the hero, ring sky share of the
	// chosen view), tallest roof near the last sky launch's flip and its solved peak (m over the street)
	// round 13: camera output slew-limit flags (1 position, 2 pitch, 4 yaw) and the hero fill light (cd)
	const FString Flip12 = FString::Printf(TEXT(",%s,%.3f,%.1f,%.1f,%.2f,%.1f,%.1f,%d,%.0f"),
		Traversal->IsFlipArmed() ? *Traversal->ArmedFlipName().ToString() : TEXT(""), Cam.FlipK,
		FMath::RadiansToDegrees(Cam.FlipYawOff), FMath::RadiansToDegrees(Cam.FlipElev), Cam.FlipSkyShare,
		Traversal->SkyTallUsed, Traversal->SkyPeakWant, Cam.SlewFlags, HeroFill ? HeroFill->Intensity : 0.f);
	Script->AddTelemetryRow(Row + TEXT(",") + FlipCols + Flip12);
}

// ------------------------------------------------------------------ game mode
AWebTravGameMode::AWebTravGameMode()
{
	DefaultPawnClass = AWebTravCharacter::StaticClass();
	PlayerControllerClass = AWebHomagePlayerController::StaticClass();
}
