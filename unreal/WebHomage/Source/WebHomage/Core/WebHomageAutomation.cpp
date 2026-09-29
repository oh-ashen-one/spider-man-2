// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Core/WebHomageAutomation.h"
#include "WebHomage.h"

#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/GameInstance.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/ConfigCacheIni.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "RHI.h"
#include "UnrealClient.h"

void UWebHomageAutomation::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	const TCHAR* Cmd = FCommandLine::Get();

	FString ShotList;
	if (FParse::Value(Cmd, TEXT("WHShotAt="), ShotList, /*bShouldStopOnSeparator*/ false))
	{
		TArray<FString> Parts;
		ShotList.ParseIntoArray(Parts, TEXT(","));
		for (const FString& P : Parts)
		{
			ShotTimes.Add(FCString::Atod(*P));
		}
		ShotTimes.Sort();
	}
	if (!FParse::Value(Cmd, TEXT("WHShotDir="), ShotDir))
	{
		ShotDir = FPaths::ProjectSavedDir() / TEXT("WHCaptures");
	}
	ShotDir = FPaths::ConvertRelativePathToFull(ShotDir);
	FParse::Value(Cmd, TEXT("WHShotName="), ShotName);
	FParse::Value(Cmd, TEXT("WHPerfFrom="), PerfFrom);
	FParse::Value(Cmd, TEXT("WHPerfTo="), PerfTo);
	FParse::Value(Cmd, TEXT("WHQuitAt="), QuitAt);
	bCsv = FParse::Param(Cmd, TEXT("WHCsv"));

	bActive = ShotTimes.Num() > 0 || (PerfFrom >= 0.0 && PerfTo > PerfFrom) || QuitAt > 0.0;
	LastWall = FPlatformTime::Seconds();
	if (bActive)
	{
		IFileManager::Get().MakeDirectory(*ShotDir, true);
		UE_LOG(LogWebHomage, Display, TEXT("WH_AUTOMATION shots=%d perf=[%.2f,%.2f] csv=%d quit=%.2f dir=%s"),
			ShotTimes.Num(), PerfFrom, PerfTo, bCsv ? 1 : 0, QuitAt, *ShotDir);
	}
}

void UWebHomageAutomation::Deinitialize()
{
	if (bPerfRunning)
	{
		WritePerf();
	}
	bActive = false;
	Super::Deinitialize();
}

TStatId UWebHomageAutomation::GetStatId() const
{
	RETURN_QUICK_DECLARE_CYCLE_STAT(UWebHomageAutomation, STATGROUP_Tickables);
}

void UWebHomageAutomation::Tick(float DeltaTime)
{
	// Only drive automation from game worlds (standalone / PIE), not editor preview worlds.
	const UGameInstance* GI = GetGameInstance();
	if (!GI || !GI->GetWorld() || !GI->GetWorld()->IsGameWorld())
	{
		return;
	}

	const double Now = FPlatformTime::Seconds();
	const double WallDelta = Now - LastWall;
	LastWall = Now;
	Elapsed += DeltaTime;

	// Perf window: record real frame-to-frame wall time and the RHI's GPU frame time.
	if (!bPerfDone && PerfFrom >= 0.0 && PerfTo > PerfFrom)
	{
		if (!bPerfRunning && Elapsed >= PerfFrom)
		{
			bPerfRunning = true;
			FrameMs.Reset();
			GpuMs.Reset();
			if (bCsv && GEngine)
			{
				GEngine->Exec(GI->GetWorld(), TEXT("CsvProfile Start"));
			}
			UE_LOG(LogWebHomage, Display, TEXT("WH_PERF_START t=%.2f"), Elapsed);
		}
		else if (bPerfRunning)
		{
			FrameMs.Add(float(WallDelta * 1000.0));
			GpuMs.Add(float(FPlatformTime::ToMilliseconds(RHIGetGPUFrameCycles(0))));
			if (Elapsed >= PerfTo)
			{
				if (bCsv && GEngine)
				{
					GEngine->Exec(GI->GetWorld(), TEXT("CsvProfile Stop"));
				}
				WritePerf();
			}
		}
	}

	while (NextShot < ShotTimes.Num() && Elapsed >= ShotTimes[NextShot])
	{
		const FString File = ShotDir / FString::Printf(TEXT("%s_%02d_t%05.1f.png"), *ShotName, NextShot, ShotTimes[NextShot]);
		FScreenshotRequest::RequestScreenshot(File, /*bShowUI*/ false, /*bAddFilenameSuffix*/ false);
		UE_LOG(LogWebHomage, Display, TEXT("WH_SHOT %s"), *File);
		++NextShot;
	}

	if (QuitAt > 0.0 && !bQuitRequested && Elapsed >= QuitAt)
	{
		bQuitRequested = true;
		if (bPerfRunning)
		{
			WritePerf();
		}
		UE_LOG(LogWebHomage, Display, TEXT("WH_QUIT t=%.2f"), Elapsed);
		if (GIsEditor)
		{
			UE_LOG(LogWebHomage, Display, TEXT("WH_QUIT ignored inside the editor (PIE); stop PIE via MCP StopPIE."));
		}
		else if (GEngine)
		{
			GEngine->Exec(GI->GetWorld(), TEXT("quit"));
		}
	}
}

static float Percentile(TArray<float> V, float P)
{
	if (V.Num() == 0)
	{
		return 0.f;
	}
	V.Sort();
	const int32 Idx = FMath::Clamp(int32(FMath::CeilToInt(P * V.Num())) - 1, 0, V.Num() - 1);
	return V[Idx];
}

void UWebHomageAutomation::WritePerf()
{
	bPerfRunning = false;
	bPerfDone = true;
	const int32 N = FrameMs.Num();
	double Sum = 0.0, GpuSum = 0.0;
	for (float F : FrameMs) { Sum += F; }
	for (float G : GpuMs) { GpuSum += G; }
	const double Avg = N ? Sum / N : 0.0;
	const double GpuAvg = N ? GpuSum / N : 0.0;

	FIntPoint Size(0, 0);
	if (GEngine && GEngine->GameViewport && GEngine->GameViewport->Viewport)
	{
		Size = GEngine->GameViewport->Viewport->GetSizeXY();
	}
	auto CVarF = [](const TCHAR* Name, float Default) -> float
	{
		IConsoleVariable* V = IConsoleManager::Get().FindConsoleVariable(Name);
		return V ? V->GetFloat() : Default;
	};
	const float ScreenPct = CVarF(TEXT("r.ScreenPercentage"), 0.f);
	// Effective internal (pre-TSR) resolution. r.ScreenPercentage<=0 means the engine picks it from
	// r.ScreenPercentage.Default.Desktop.Mode (1 = based on display resolution, table in
	// [Rendering.AutoScreenPercentage]: 2160p display -> 1080p render). Mirrors LegacyScreenPercentageDriver.cpp.
	float Frac = 1.f;
	FString SPMode = TEXT("manual");
	if (ScreenPct > 0.f)
	{
		Frac = ScreenPct / 100.f;
	}
	else if (int32(CVarF(TEXT("r.ScreenPercentage.Default.Desktop.Mode"), 1.f)) == 1 && Size.X > 0)
	{
		SPMode = TEXT("auto_display");
		auto Px = [](float H) { return H * H * 16.f / 9.f; };
		float MinD = 720, MinR = 720, MidD = 2160, MidR = 1080, MaxD = 4320, MaxR = 1440;
		GConfig->GetFloat(TEXT("Rendering.AutoScreenPercentage"), TEXT("MinDisplayResolution"), MinD, GEngineIni);
		GConfig->GetFloat(TEXT("Rendering.AutoScreenPercentage"), TEXT("MinRenderingResolution"), MinR, GEngineIni);
		GConfig->GetFloat(TEXT("Rendering.AutoScreenPercentage"), TEXT("MidDisplayResolution"), MidD, GEngineIni);
		GConfig->GetFloat(TEXT("Rendering.AutoScreenPercentage"), TEXT("MidRenderingResolution"), MidR, GEngineIni);
		GConfig->GetFloat(TEXT("Rendering.AutoScreenPercentage"), TEXT("MaxDisplayResolution"), MaxD, GEngineIni);
		GConfig->GetFloat(TEXT("Rendering.AutoScreenPercentage"), TEXT("MaxRenderingResolution"), MaxR, GEngineIni);
		const float Disp = float(Size.X) * float(Size.Y);
		float Render;
		if (Disp < Px(MinD)) { Render = Disp * Px(MinR) / Px(MinD); }
		else if (Disp > Px(MaxD)) { Render = Disp * Px(MaxR) / Px(MaxD); }
		else if (Disp > Px(MidD)) { Render = FMath::Lerp(Px(MidR), Px(MaxR), (Disp - Px(MidD)) / (Px(MaxD) - Px(MidD))); }
		else { Render = FMath::Lerp(Px(MinR), Px(MidR), FMath::Clamp((Disp - Px(MinD)) / (Px(MidD) - Px(MinD)), 0.f, 1.f)); }
		Frac = FMath::Sqrt(CVarF(TEXT("r.ScreenPercentage.Auto.PixelCountMultiplier"), 1.f) * Render / Disp);
	}
	else
	{
		Frac = CVarF(TEXT("r.ScreenPercentage.Default"), 100.f) / 100.f;
	}
	const int32 InternalW = FMath::RoundToInt(Size.X * Frac);
	const int32 InternalH = FMath::RoundToInt(Size.Y * Frac);
	int32 Under60 = 0;
	for (float F : FrameMs) { if (F > 1000.f / 60.f + 0.5f) { ++Under60; } }

	const FString Json = FString::Printf(TEXT("{\n  \"frames\": %d,\n  \"seconds\": %.3f,\n  \"avg_ms\": %.3f,\n  \"avg_fps\": %.2f,\n  \"p50_ms\": %.3f,\n  \"p95_ms\": %.3f,\n  \"p99_ms\": %.3f,\n  \"max_ms\": %.3f,\n  \"frames_over_16_67ms\": %d,\n  \"gpu_avg_ms\": %.3f,\n  \"gpu_p95_ms\": %.3f,\n  \"output_w\": %d,\n  \"output_h\": %d,\n  \"r_ScreenPercentage\": %.1f,\n  \"screen_percentage_mode\": \"%s\",\n  \"internal_w\": %d,\n  \"internal_h\": %d,\n  \"rhi\": \"%s\"\n}\n"),
		N, Sum / 1000.0, Avg, Avg > 0 ? 1000.0 / Avg : 0.0,
		Percentile(FrameMs, 0.50f), Percentile(FrameMs, 0.95f), Percentile(FrameMs, 0.99f), Percentile(FrameMs, 1.0f), Under60,
		GpuAvg, Percentile(GpuMs, 0.95f), Size.X, Size.Y, ScreenPct, *SPMode, InternalW, InternalH, GDynamicRHI ? GDynamicRHI->GetName() : TEXT("?"));
	const FString Path = ShotDir / (ShotName + TEXT("_perf.json"));
	FFileHelper::SaveStringToFile(Json, *Path);
	UE_LOG(LogWebHomage, Display, TEXT("WH_PERF frames=%d avg_ms=%.2f fps=%.1f p95_ms=%.2f p99_ms=%.2f gpu_avg_ms=%.2f out=%dx%d internal=%dx%d (%s) -> %s"),
		N, Avg, Avg > 0 ? 1000.0 / Avg : 0.0, Percentile(FrameMs, 0.95f), Percentile(FrameMs, 0.99f), GpuAvg, Size.X, Size.Y, InternalW, InternalH, *SPMode, *Path);
}
