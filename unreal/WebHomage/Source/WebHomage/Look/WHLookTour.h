// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
// P4 Look: "shot tour" for unattended captures of the REAL game. One game session visits a list of camera poses, waits for exposure / TSR / Lumen to settle at each
// and writes a screenshot per pose, so a whole S1..S8 set of one preset costs one process (shader load, DDC and Lumen warm-up are paid once).
//   -WHLookTour=<abs path of a text file>   one pose per line:  name  x y z  pitch yaw roll  fov  settle_s  [px py pz]      (UE cm / degrees; '#' comments)
//   -WHLookTourDir=<abs dir> (default -WHShotDir)   screenshots go to <dir>/<name>.png (true back-buffer size, no UI)
//   -WHLookTourStart=<s> first pose is entered after this many game seconds (default 8);  -WHLookTourMinFrames=<n> frames to wait per pose at least (default 90)
//   -WHLookTourHidePawn   hide the hero (shots that must not show it)
// px py pz (optional): the pawn is teleported there at every pose (the hero pose of the browser's view definition).  The process quits after the last shot.
// Written by tools/perf_ue/capture_tour.py from Scripts/city_shots.json.
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Tickable.h"
#include "WHLookTour.generated.h"

class ACameraActor;

UCLASS()
class WEBHOMAGE_API UWHLookTour : public UGameInstanceSubsystem, public FTickableGameObject
{
	GENERATED_BODY()
public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Tick(float DeltaTime) override;
	virtual TStatId GetStatId() const override;
	virtual bool IsTickable() const override { return bActive; }
	virtual ETickableTickType GetTickableTickType() const override { return ETickableTickType::Conditional; }
	virtual bool IsTickableWhenPaused() const override { return true; }

private:
	struct FPose { FString Name; FVector Loc; FRotator Rot; float Fov = 70.f; float Settle = 4.f; bool bHasPawn = false; FVector Pawn = FVector::ZeroVector; };
	TArray<FPose> Poses;
	FString OutDir;
	bool bActive = false, bHidePawn = false, bQuit = false;
	double Elapsed = 0.0, StartDelay = 8.0, PoseStart = 0.0;
	int32 MinFrames = 90, Index = -1, FramesInPose = 0;
	enum class EPhase : uint8 { Waiting, Settling, Shot } Phase = EPhase::Waiting;
	int32 ShotFrames = 0;
	TWeakObjectPtr<ACameraActor> Cam;
	void EnterPose(UWorld* World, int32 I);
};
