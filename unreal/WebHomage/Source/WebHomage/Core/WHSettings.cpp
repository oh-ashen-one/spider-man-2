// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Core/WHSettings.h"
#include "WebHomage.h"

#include "GenericPlatform/GenericApplication.h"
#include "HAL/IConsoleManager.h"
#include "Misc/ConfigCacheIni.h"
#include "Scalability.h"
#include "UnrealEngine.h"

namespace
{
	const TCHAR* GSection = TEXT("WebHomage.Settings");
}

FWHSettings& WHSettings()
{
	static FWHSettings S;
	return S;
}

float FWHSettings::FovDefault()
{
	return float(FMath::RadiansToDegrees(2.0 * FMath::Atan(FMath::Tan(FMath::DegreesToRadians(BaseVFovDefault * 0.5)) * 16.0 / 9.0)));
}

FWHSettings::FWHSettings()
{
	FovH = FovDefault();
}

double FWHSettings::BaseVFov() const
{
	if (FMath::Abs(FovH - FovDefault()) < 0.05f)
	{
		return BaseVFovDefault;
	}
	return FMath::RadiansToDegrees(2.0 * FMath::Atan(FMath::Tan(FMath::DegreesToRadians(double(FovH) * 0.5)) * 9.0 / 16.0));
}

void FWHSettings::Clamp()
{
	MouseSens = FMath::Clamp(MouseSens, MouseSensMin, MouseSensMax);
	PadSens = FMath::Clamp(PadSens, PadSensMin, PadSensMax);
	FovH = FMath::Clamp(FovH, FovMin, FovMax);
	Quality = FMath::Clamp(Quality, 0, QualityMax);
	ResScale = FMath::Clamp(ResScale, ResScaleMin, ResScaleMax);
	WindowMode = FMath::Clamp(WindowMode, 0, 2);
}

FText FWHSettings::QualityName(int32 Q)
{
	switch (Q)
	{
	case 0: return NSLOCTEXT("WHSettings", "QLow", "Low");
	case 1: return NSLOCTEXT("WHSettings", "QMedium", "Medium");
	case 2: return NSLOCTEXT("WHSettings", "QHigh", "High");
	case 3: return NSLOCTEXT("WHSettings", "QEpic", "Epic");
	default: return NSLOCTEXT("WHSettings", "QCinematic", "Cinematic");
	}
}

FText FWHSettings::WindowModeName(int32 M)
{
	switch (M)
	{
	case WinWindowed: return NSLOCTEXT("WHSettings", "WWindowed", "Windowed");
	case WinFullscreen: return NSLOCTEXT("WHSettings", "WFullscreen", "Fullscreen");
	default: return NSLOCTEXT("WHSettings", "WBorderless", "Borderless");
	}
}

void FWHSettings::ApplyRender() const
{
	if (!bLive) return; // automated runs keep their command-line render settings
	// Scalability::SetQualityLevels directly: the "scalability" console command would also SaveState() into GameUserSettings.ini
	// [ScalabilityGroups], which the engine re-applies at startup -- that would leak into automated capture / perf runs.
	Scalability::FQualityLevels Q;
	Q.SetFromSingleQualityLevel(Quality);
	Q.ResolutionQuality = float(ResScale);
	Scalability::SetQualityLevels(Q, /*bForce*/ true);
	if (IConsoleVariable* CV = IConsoleManager::Get().FindConsoleVariable(TEXT("r.ScreenPercentage")))
	{
		CV->Set(float(ResScale), ECVF_SetByCode);
	}
	if (IConsoleVariable* CV = IConsoleManager::Get().FindConsoleVariable(TEXT("r.VSync")))
	{
		CV->Set(bVSync ? 1 : 0, ECVF_SetByCode);
	}
}

void FWHSettings::ApplyWindow() const
{
	if (!bLive) return;
	FDisplayMetrics DM;
	FDisplayMetrics::RebuildDisplayMetrics(DM);
	int32 W = FMath::Max(640, DM.PrimaryDisplayWidth), H = FMath::Max(360, DM.PrimaryDisplayHeight);
	// owner playtest 2026-10-01: on macOS the WindowedFullscreen path left mouse clicks unregistered (menu buttons + right-mouse swing dead
	// while keys worked). Borderless = a plain window covering the primary display instead.
	EWindowMode::Type Mode = PLATFORM_MAC ? EWindowMode::Windowed : EWindowMode::WindowedFullscreen;
	if (WindowMode == WinFullscreen)
	{
		Mode = EWindowMode::Fullscreen;
	}
	else if (WindowMode == WinWindowed)
	{
		Mode = EWindowMode::Windowed;
		// a 16:9 window at most 80 % of the desktop (1920x1080 on a 3440x1440 ultrawide)
		const int32 WW = FMath::Min(1920, int32(W * 0.8f));
		W = WW; H = WW * 9 / 16;
	}
	FSystemResolution::RequestResolutionChange(W, H, Mode);
	UE_LOG(LogWebHomage, Display, TEXT("WH_SETTINGS window %s %dx%d"), *WindowModeName(WindowMode).ToString(), W, H);
}

void FWHSettings::ResetToDefaults()
{
	const bool bWasLive = bLive;
	*this = FWHSettings();
	bLive = bWasLive;
	ApplyCVars();
	ApplyRender();
	ApplyWindow();
}

void FWHSettings::ApplyCVars() const
{
	if (IConsoleVariable* CV = IConsoleManager::Get().FindConsoleVariable(TEXT("wh.MouseSensitivity")))
	{
		CV->Set(MouseSens, ECVF_SetByGameSetting);
	}
}

void FWHSettings::SyncFromCVars()
{
	if (IConsoleVariable* CV = IConsoleManager::Get().FindConsoleVariable(TEXT("wh.MouseSensitivity")))
	{
		MouseSens = FMath::Clamp(CV->GetFloat(), MouseSensMin, MouseSensMax);
	}
}

void FWHSettings::Load()
{
	if (!GConfig)
	{
		return;
	}
	GConfig->GetFloat(GSection, TEXT("MouseSensitivity"), MouseSens, GGameUserSettingsIni);
	GConfig->GetFloat(GSection, TEXT("GamepadLookSensitivity"), PadSens, GGameUserSettingsIni);
	GConfig->GetBool(GSection, TEXT("InvertY"), bInvertY, GGameUserSettingsIni);
	GConfig->GetFloat(GSection, TEXT("FieldOfView"), FovH, GGameUserSettingsIni);
	GConfig->GetBool(GSection, TEXT("CameraShake"), bCameraShake, GGameUserSettingsIni);
	GConfig->GetInt(GSection, TEXT("QualityPreset"), Quality, GGameUserSettingsIni);
	GConfig->GetInt(GSection, TEXT("ResolutionScale"), ResScale, GGameUserSettingsIni);
	GConfig->GetInt(GSection, TEXT("WindowMode"), WindowMode, GGameUserSettingsIni);
	GConfig->GetBool(GSection, TEXT("VSync"), bVSync, GGameUserSettingsIni);
	Clamp();
	bLive = true;
	ApplyCVars();
	UE_LOG(LogWebHomage, Display, TEXT("WH_SETTINGS loaded from %s: mouse %.2f pad %.2f invertY %d fov %.1f (vertical %.2f) shake %d quality %d res %d%% window %d vsync %d"),
		*GGameUserSettingsIni, MouseSens, PadSens, bInvertY ? 1 : 0, FovH, BaseVFov(), bCameraShake ? 1 : 0, Quality, ResScale, WindowMode, bVSync ? 1 : 0);
}

void FWHSettings::Save()
{
	if (!GConfig)
	{
		return;
	}
	SyncFromCVars();
	Clamp();
	GConfig->SetFloat(GSection, TEXT("MouseSensitivity"), MouseSens, GGameUserSettingsIni);
	GConfig->SetFloat(GSection, TEXT("GamepadLookSensitivity"), PadSens, GGameUserSettingsIni);
	GConfig->SetBool(GSection, TEXT("InvertY"), bInvertY, GGameUserSettingsIni);
	GConfig->SetFloat(GSection, TEXT("FieldOfView"), FovH, GGameUserSettingsIni);
	GConfig->SetBool(GSection, TEXT("CameraShake"), bCameraShake, GGameUserSettingsIni);
	GConfig->SetInt(GSection, TEXT("QualityPreset"), Quality, GGameUserSettingsIni);
	GConfig->SetInt(GSection, TEXT("ResolutionScale"), ResScale, GGameUserSettingsIni);
	GConfig->SetInt(GSection, TEXT("WindowMode"), WindowMode, GGameUserSettingsIni);
	GConfig->SetBool(GSection, TEXT("VSync"), bVSync, GGameUserSettingsIni);
	GConfig->Flush(false, GGameUserSettingsIni);
	UE_LOG(LogWebHomage, Display, TEXT("WH_SETTINGS saved to %s"), *GGameUserSettingsIni);
}
