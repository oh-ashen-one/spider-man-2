// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Tickable.h"
#include "WebHomageAutomation.generated.h"

/**
 * Command-line driven capture / perf director for unattended runs of the real game
 * (standalone -game or PIE). All times are GAME seconds since the subsystem started
 * (deterministic under -benchmark -fps=60, ~wall clock otherwise).
 *
 *   -WHShotAt=3,8.5        screenshots (true back-buffer size, no UI) at those times
 *   -WHShotDir=<abs dir>   output folder (default <Project>/Saved/WHCaptures)
 *   -WHShotName=<prefix>   file prefix (default "shot")
 *   -WHPerfFrom=3 -WHPerfTo=13   frame-time window: writes <dir>/<prefix>_perf.json and logs
 *                          "WH_PERF ..." (avg/p50/p95/p99 frame ms, GPU ms, render size)
 *   -WHCsv                 also run CsvProfile Start/Stop over the perf window
 *   -WHQuitAt=15           request clean exit at that time
 *   -WHAutoMove            (character) run/turn/jump automatically
 * See unreal/WebHomage/CAPTURE.md.
 */
UCLASS()
class WEBHOMAGE_API UWebHomageAutomation : public UGameInstanceSubsystem, public FTickableGameObject
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;

	// FTickableGameObject
	virtual void Tick(float DeltaTime) override;
	virtual TStatId GetStatId() const override;
	virtual bool IsTickable() const override { return bActive; }
	virtual ETickableTickType GetTickableTickType() const override { return ETickableTickType::Conditional; }
	virtual bool IsTickableWhenPaused() const override { return true; }

private:
	void WritePerf();

	bool bActive = false;
	double Elapsed = 0.0;
	double LastWall = 0.0;

	TArray<double> ShotTimes;
	int32 NextShot = 0;
	FString ShotDir;
	FString ShotName = TEXT("shot");

	double PerfFrom = -1.0;
	double PerfTo = -1.0;
	bool bCsv = false;
	bool bPerfRunning = false;
	bool bPerfDone = false;
	TArray<float> FrameMs;
	TArray<float> GpuMs;

	double QuitAt = -1.0;
	bool bQuitRequested = false;
};
