// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Core/WebHomagePlayerController.h"
#include "WebHomage.h"

#include "Framework/Application/SlateApplication.h"
#include "InputCoreTypes.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

AWebHomagePlayerController::AWebHomagePlayerController()
{
	bShowMouseCursor = true;
}

void AWebHomagePlayerController::BeginPlay()
{
	Super::BeginPlay();

	const TCHAR* Cmd = FCommandLine::Get();
	FString Dummy;
	bNeverCapture = FParse::Param(Cmd, TEXT("WHNoMouseCapture"))
		|| FParse::Param(Cmd, TEXT("WHAutoMove"))
		|| FParse::Value(Cmd, TEXT("WHShotAt="), Dummy)
		|| FParse::Value(Cmd, TEXT("WHPerfFrom="), Dummy)
		|| FParse::Value(Cmd, TEXT("WHQuitAt="), Dummy);

	if (IsLocalController())
	{
		ReleaseMouse();
	}
}

void AWebHomagePlayerController::ReleaseMouse()
{
	FInputModeGameAndUI Mode;
	Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
	Mode.SetHideCursorDuringCapture(false);
	SetInputMode(Mode);
	bShowMouseCursor = true;
	bMouseCaptured = false;
	if (FSlateApplication::IsInitialized())
	{
		FSlateApplication::Get().ReleaseAllPointerCapture();
		FSlateApplication::Get().SetAllUserFocusToGameViewport(); // keep keyboard input
	}
}

void AWebHomagePlayerController::CaptureMouse()
{
	if (bNeverCapture)
	{
		return;
	}
	FInputModeGameOnly Mode;
	SetInputMode(Mode);
	bShowMouseCursor = false;
	bMouseCaptured = true;
}

void AWebHomagePlayerController::PlayerTick(float DeltaTime)
{
	Super::PlayerTick(DeltaTime);

	if (WasInputKeyJustPressed(EKeys::Escape))
	{
		ReleaseMouse();
	}
	else if (!bMouseCaptured && !bNeverCapture && WasInputKeyJustPressed(EKeys::LeftMouseButton))
	{
		CaptureMouse();
	}
}
