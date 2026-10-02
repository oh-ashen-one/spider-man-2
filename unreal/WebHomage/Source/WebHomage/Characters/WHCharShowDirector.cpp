// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Characters/WHCharShowDirector.h"
#include "Characters/WHCharLoopWalker.h"
#include "Characters/WHCharStage.h"
#include "Characters/WHHeroSuit.h"
#include "Components/SkeletalMeshComponent.h"
#include "AnimationRuntime.h"
#include "EngineUtils.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "UnrealClient.h"
#include "Camera/CameraActor.h"
#include "Engine/PostProcessVolume.h"
#include "Camera/CameraComponent.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/PlayerController.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/App.h"
#include "Engine/Texture2D.h"
#include "Materials/MaterialInterface.h"

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
	{   // round 11: -WHExposure=<EV bias> sets the exposure compensation of every post-process volume of the level (the skins stage runs a MANUAL exposure, so the bias is the only knob)
		float EV = 0.f;
		if (FParse::Value(FCommandLine::Get(), TEXT("WHExposure="), EV))
			for (TActorIterator<APostProcessVolume> It(GetWorld()); It; ++It)
			{
				It->Settings.bOverride_AutoExposureBias = true; It->Settings.AutoExposureBias = EV;
				UE_LOG(LogTemp, Display, TEXT("WH_EXPOSURE bias %.2f on %s"), EV, *It->GetName());
			}
	}
	int32 Start = 0;
	if (FParse::Value(FCommandLine::Get(), TEXT("WHCharShot="), Start))
		for (int32 i = 0; i < FMath::Min(Start, Shots.Num()); ++i) T += Shots[i].Duration;
	WHStage::Offset() = double(T) - GetWorld()->GetTimeSeconds();   // round 09: the stage clock (scripted fights) is this director's shot clock
	{
		FString List;
		if (FParse::Value(FCommandLine::Get(), TEXT("WHStageShot="), List, false) && !List.IsEmpty())
		{
			TArray<FString> Parts; List.ParseIntoArray(Parts, TEXT(","));
			for (const FString& Part : Parts) StageShots.Add(FCString::Atod(*Part));
			StageShots.Sort();
			bStageShotQuit = FParse::Param(FCommandLine::Get(), TEXT("WHStageShotQuit"));
			StageShotDir = FPaths::ProjectSavedDir() / TEXT("WHCaptures"); FParse::Value(FCommandLine::Get(), TEXT("WHShotDir="), StageShotDir);
			StageShotName = TEXT("shot"); FParse::Value(FCommandLine::Get(), TEXT("WHShotName="), StageShotName);
		}
	}
	if (FParse::Value(FCommandLine::Get(), TEXT("WHBoneLog="), BoneLogPath) && !BoneLogPath.IsEmpty())
	{
		IFileManager::Get().Delete(*BoneLogPath);
		BoneLogBuf = TEXT("frame,time,label,x,y,yaw,bone,bx,by,bz\n");
	}
}

void AWHCharShowDirector::EndPlay(const EEndPlayReason::Type Reason)
{
	if (!BoneLogPath.IsEmpty() && !BoneLogBuf.IsEmpty())
		FFileHelper::SaveStringToFile(BoneLogBuf, *BoneLogPath, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), FILEWRITE_Append);
	Super::EndPlay(Reason);
}

// -WHBoneLog=<csv>: per frame and per walker the world position of a few bones (pelvis, spine, head, hands, feet) for the choreography checks
void AWHCharShowDirector::LogBones(float Ts)
{
	// the UE skeleton names the dotted glTF bones with an underscore (hand_L): the csv keeps the glTF names (tools read 'hand.L'); round 09's first log had 0,0,0 for them
	static const TCHAR* Bones[] = {TEXT("hips"), TEXT("spine2"), TEXT("head"), TEXT("hand_L"), TEXT("hand_R"), TEXT("foot_L"), TEXT("foot_R")};
	static const TCHAR* Labels[] = {TEXT("hips"), TEXT("spine2"), TEXT("head"), TEXT("hand.L"), TEXT("hand.R"), TEXT("foot.L"), TEXT("foot.R")};
	for (TActorIterator<AWHCharLoopWalker> It(GetWorld()); It; ++It)
	{
		const AWHCharLoopWalker* W = *It;
		if (!W->Mesh) continue;
#if WITH_EDITOR
		const FString Lbl = W->GetActorLabel();
#else
		const FString Lbl = W->GetName();
#endif
		const FVector P = W->GetActorLocation();
		for (int32 bi = 0; bi < UE_ARRAY_COUNT(Bones); ++bi)
		{
			const FVector L = W->Mesh->GetBoneLocation(FName(Bones[bi]), EBoneSpaces::WorldSpace);
			BoneLogBuf += FString::Printf(TEXT("%llu,%.4f,%s,%.2f,%.2f,%.2f,%s,%.2f,%.2f,%.2f\n"), GFrameCounter, Ts, *Lbl, P.X, P.Y, W->GetActorRotation().Yaw, Labels[bi], L.X, L.Y, L.Z);
		}
	}
	if (BoneLogBuf.Len() > (1 << 20))
	{
		FFileHelper::SaveStringToFile(BoneLogBuf, *BoneLogPath, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), FILEWRITE_Append);
		BoneLogBuf.Reset();
	}
}

void AWHCharShowDirector::Tick(float Dt)
{
	Super::Tick(Dt);
	if (!Cam || Shots.Num() == 0) return;
	// round 16: -WHStageWaitTextures holds the STAGE clock while the target's suit textures are not fully streamed in (r16 hold 2: at 1.4 fps on a contended GPU the first
	// suit's 8192 px maps were still a low mip when its stills were taken), at most 180 s of wall time per shot
	static const bool bWaitTex = FParse::Param(FCommandLine::Get(), TEXT("WHStageWaitTextures"));
	bool bHoldClock = false;
	if (bWaitTex)
	{
		float Tc = bLoop ? T : FMath::Min(T, 1e9f); int32 Ic = 0;
		for (; Ic < Shots.Num() - 1 && Tc >= Shots[Ic].Duration; ++Ic) Tc -= Shots[Ic].Duration;
		AActor* Tg = Shots[Ic].bTargetPlayer ? Cast<AActor>(UGameplayStatics::GetPlayerPawn(this, 0)) : Shots[Ic].Target.Get();
		bool bReady = true;
		if (Tg && Ic != WaitTexDoneShot)
			if (USkeletalMeshComponent* SK = Tg->FindComponentByClass<USkeletalMeshComponent>())
				for (int32 m = 0; m < SK->GetNumMaterials() && bReady; ++m)
					if (UMaterialInterface* MI = SK->GetMaterial(m))
					{
						TArray<UTexture*> Used; MI->GetUsedTextures(Used, EMaterialQualityLevel::Num, true, GMaxRHIFeatureLevel, true);
						for (UTexture* Tx : Used) if (UTexture2D* T2 = Cast<UTexture2D>(Tx)) if (!T2->IsFullyStreamedIn()) { bReady = false; break; }
					}
		if (!bReady && WaitTexWall < 180.0)
		{
			if (WaitTexWall == 0.0) UE_LOG(LogTemp, Display, TEXT("WH_STAGE_WAIT_TEX shot %d: holding the stage clock at T=%.2f until the suit textures are resident"), Ic, T);
			WaitTexWall += FApp::GetDeltaTime();
			bHoldClock = true;      // the rest of the tick still runs (suit, camera); only the stage clock stands still
		}
		else if (Ic != WaitTexDoneShot && WaitTexWall > 0.0) UE_LOG(LogTemp, Display, TEXT("WH_STAGE_WAIT_TEX shot %d: resident=%d after %.1f s wall"), Ic, bReady ? 1 : 0, WaitTexWall);
		if (!bHoldClock && Ic != WaitTexDoneShot) { WaitTexDoneShot = Ic; WaitTexWall = 0.0; }
	}
	if (!bHoldClock) T += Dt;
	if (!BoneLogPath.IsEmpty() && Dt > 0.f) LogBones(T);
	while (NextStageShot < StageShots.Num() && double(T) >= StageShots[NextStageShot])
	{
		const FString File = StageShotDir / FString::Printf(TEXT("%s_%02d_t%05.1f.png"), *StageShotName, NextStageShot, StageShots[NextStageShot]);
		FScreenshotRequest::RequestScreenshot(File, /*bShowUI*/ false, /*bAddFilenameSuffix*/ false);
		UE_LOG(LogTemp, Display, TEXT("WH_STAGE_SHOT %s stage T=%.3f world=%.3f"), *File, T, GetWorld()->GetTimeSeconds());
		++NextStageShot;
		if (bStageShotQuit && NextStageShot >= StageShots.Num()) StageQuitAt = double(T) + 3.0;
	}
	if (StageQuitAt > 0.0 && !bStageQuitDone && double(T) >= StageQuitAt)
	{
		bStageQuitDone = true;
		UE_LOG(LogTemp, Display, TEXT("WH_QUIT stage T=%.2f (director: 3 s after the last of %d stage shots, -WHStageShotQuit)"), T, StageShots.Num());
		if (!GIsEditor && GEngine) GEngine->Exec(GetWorld(), TEXT("quit"));
	}
	float Total = 0.f; for (const FWHShot& S : Shots) Total += S.Duration;
	float Tl = bLoop ? FMath::Fmod(T, FMath::Max(0.1f, Total)) : FMath::Min(T, Total - 1e-3f);
	int32 Idx = 0; for (; Idx < Shots.Num() - 1 && Tl >= Shots[Idx].Duration; ++Idx) Tl -= Shots[Idx].Duration;
	const FWHShot& S = Shots[Idx];
	AActor* Tgt = S.bTargetPlayer ? Cast<AActor>(UGameplayStatics::GetPlayerPawn(this, 0)) : S.Target.Get();
	if (!Tgt) return;
	if (Idx != LastShot && S.Suit >= 0)
		if (UWHHeroSuitSubsystem* Sub = UWHHeroSuitSubsystem::Get(this)) Sub->SetSuit(S.Suit, TEXT("director shot"));
	if (Idx != LastShot)
		for (AActor* W : S.RestartWalkers)
			if (AWHCharLoopWalker* LW = Cast<AWHCharLoopWalker>(W)) LW->RestartLine();
	if (Idx != LastShot && ManagedActors.Num() > 0)
		for (AActor* M : ManagedActors)
			if (M) M->SetActorHiddenInGame(!(M == Tgt || S.ShowActors.Contains(M)));
	const FVector Base = Tgt->GetActorLocation();
	const FVector Aim = Base + FVector(0, 0, S.AimHeight);
	const bool bCut = Idx != LastShot; LastShot = Idx;
	SmoothAim = bCut ? Aim : FMath::VInterpTo(SmoothAim, Aim, Dt, 12.f);
	const float Face = Tgt->GetActorRotation().Yaw;
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
	FRotator CamRot = (Look - Loc).Rotation();
	if (S.bHeadLock)
		if (USkeletalMeshComponent* SK = Tgt->FindComponentByClass<USkeletalMeshComponent>())
			if (SK->GetSkeletalMeshAsset())
			{
				const FReferenceSkeleton& RS = SK->GetSkeletalMeshAsset()->GetRefSkeleton();
				const int32 HB = RS.FindBoneIndex(FName(TEXT("head")));
				if (HB != INDEX_NONE)
				{
					const FTransform RefW = FAnimationRuntime::GetComponentSpaceTransformRefPose(RS, HB) * SK->GetComponentTransform();
					const FTransform NowW = SK->GetBoneTransform(HB);
					const FQuat Dq = NowW.GetRotation() * RefW.GetRotation().Inverse();
					// the camera is moved INTO the head's midsagittal plane (the plane of the face's centre seam: normal = the actor's right axis turned with the head) and its
					// up axis is kept in that plane: the head's yaw and roll are followed, its pitch (a nod, which leaves that plane where it is) is not, so the framing stays the
					// stage framing.  The seam then projects to a straight vertical line.
					const FVector Nrm = Dq.RotateVector(Tgt->GetActorRightVector()).GetSafeNormal();
					const FVector P0 = NowW.GetLocation();
					const FVector LookP = Look - Nrm * FVector::DotProduct(Look - P0, Nrm);
					Loc = Loc - Nrm * FVector::DotProduct(Loc - P0, Nrm);
					FVector Up = FVector::UpVector - Nrm * FVector::DotProduct(FVector::UpVector, Nrm);
					CamRot = FRotationMatrix::MakeFromXZ((LookP - Loc).GetSafeNormal(), Up.GetSafeNormal()).Rotator();
					if (bCut) UE_LOG(LogTemp, Display, TEXT("WH_HEADLOCK shot %d head turn %.2f deg (yaw %.2f pitch %.2f roll %.2f)"), Idx, FMath::RadiansToDegrees(Dq.GetAngle()), Dq.Rotator().Yaw, Dq.Rotator().Pitch, Dq.Rotator().Roll);
				}
			}
	Cam->SetActorLocationAndRotation(Loc, CamRot);
	Cam->GetCameraComponent()->SetFieldOfView(S.FOV);
	if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
		if (PC->GetViewTarget() != Cam) PC->SetViewTarget(Cam);
}
