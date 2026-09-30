// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Look/WHLookTour.h"
#include "WebHomage.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "HAL/FileManager.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "UnrealClient.h"

void UWHLookTour::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	const TCHAR* Cmd = FCommandLine::Get();
	FString File;
	if (!FParse::Value(Cmd, TEXT("WHLookTour="), File, false)) return;
	if (!FParse::Value(Cmd, TEXT("WHLookTourDir="), OutDir)) FParse::Value(Cmd, TEXT("WHShotDir="), OutDir);
	OutDir = FPaths::ConvertRelativePathToFull(OutDir);
	FParse::Value(Cmd, TEXT("WHLookTourStart="), StartDelay);
	FParse::Value(Cmd, TEXT("WHLookTourMinFrames="), MinFrames);
	bHidePawn = FParse::Param(Cmd, TEXT("WHLookTourHidePawn"));
	TArray<FString> Lines;
	if (!FFileHelper::LoadFileToStringArray(Lines, *File)) { UE_LOG(LogWebHomage, Error, TEXT("WH_TOUR cannot read %s"), *File); return; }
	for (const FString& L : Lines)
	{
		FString T = L.TrimStartAndEnd();
		if (T.IsEmpty() || T.StartsWith(TEXT("#"))) continue;
		TArray<FString> P; T.ParseIntoArrayWS(P);
		if (P.Num() < 10) continue;
		FPose Ps;
		Ps.Name = P[0];
		Ps.Loc = FVector(FCString::Atod(*P[1]), FCString::Atod(*P[2]), FCString::Atod(*P[3]));
		Ps.Rot = FRotator(FCString::Atod(*P[4]), FCString::Atod(*P[5]), FCString::Atod(*P[6]));
		Ps.Fov = (float)FCString::Atod(*P[7]); Ps.Settle = (float)FCString::Atod(*P[8]);
		// P[9] is reserved (kept so the format can grow); pawn position is P[10..12]
		if (P.Num() >= 13) { Ps.bHasPawn = true; Ps.Pawn = FVector(FCString::Atod(*P[10]), FCString::Atod(*P[11]), FCString::Atod(*P[12])); }
		Poses.Add(Ps);
	}
	bActive = Poses.Num() > 0;
	if (bActive) { IFileManager::Get().MakeDirectory(*OutDir, true); UE_LOG(LogWebHomage, Display, TEXT("WH_TOUR poses=%d dir=%s start=%.1f minframes=%d"), Poses.Num(), *OutDir, StartDelay, MinFrames); }
}

TStatId UWHLookTour::GetStatId() const { RETURN_QUICK_DECLARE_CYCLE_STAT(UWHLookTour, STATGROUP_Tickables); }

void UWHLookTour::EnterPose(UWorld* World, int32 I)
{
	const FPose& P = Poses[I];
	APlayerController* PC = UGameplayStatics::GetPlayerController(World, 0);
	if (!PC) return;
	if (!Cam.IsValid())
	{
		FActorSpawnParameters SP; SP.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		Cam = World->SpawnActor<ACameraActor>(P.Loc, P.Rot, SP);
		if (Cam.IsValid()) Cam->GetCameraComponent()->bConstrainAspectRatio = false;
	}
	if (!Cam.IsValid()) return;
	Cam->SetActorLocationAndRotation(P.Loc, P.Rot, false, nullptr, ETeleportType::TeleportPhysics);
	Cam->GetCameraComponent()->SetFieldOfView(P.Fov);
	if (APawn* Pawn = PC->GetPawn())
	{
		if (P.bHasPawn) Pawn->SetActorLocation(P.Pawn, false, nullptr, ETeleportType::TeleportPhysics);
		if (bHidePawn) Pawn->SetActorHiddenInGame(true);
	}
	PC->SetViewTarget(Cam.Get());
	if (PC->PlayerCameraManager) PC->PlayerCameraManager->SetGameCameraCutThisFrame();
	PoseStart = Elapsed; FramesInPose = 0; Phase = EPhase::Settling; Index = I;
	UE_LOG(LogWebHomage, Display, TEXT("WH_TOUR pose %d %s t=%.1f"), I, *P.Name, Elapsed);
}

void UWHLookTour::Tick(float DeltaTime)
{
	const UGameInstance* GI = GetGameInstance();
	UWorld* World = GI ? GI->GetWorld() : nullptr;
	if (!World || !World->IsGameWorld() || bQuit) return;
	Elapsed += DeltaTime;
	if (Phase == EPhase::Waiting)
	{
		if (Elapsed >= StartDelay && UGameplayStatics::GetPlayerController(World, 0)) EnterPose(World, 0);
		return;
	}
	if (Phase == EPhase::Settling)
	{
		++FramesInPose;
		if (Elapsed - PoseStart >= Poses[Index].Settle && FramesInPose >= MinFrames)
		{
			const FString File = OutDir / (Poses[Index].Name + TEXT(".png"));
			FScreenshotRequest::RequestScreenshot(File, /*bShowUI*/ false, /*bAddFilenameSuffix*/ false);
			UE_LOG(LogWebHomage, Display, TEXT("WH_SHOT %s (frames %d, %.1f s)"), *File, FramesInPose, Elapsed - PoseStart);
			Phase = EPhase::Shot; ShotFrames = 0;
		}
		return;
	}
	if (Phase == EPhase::Shot)
	{
		if (++ShotFrames < 6) return;   // the screenshot is written at the end of the frame after the request; give it a few frames
		if (Index + 1 < Poses.Num()) EnterPose(World, Index + 1);
		else { bQuit = true; UE_LOG(LogWebHomage, Display, TEXT("WH_TOUR_DONE %d"), Poses.Num()); if (GEngine) GEngine->Exec(World, TEXT("quit")); }
	}
}
