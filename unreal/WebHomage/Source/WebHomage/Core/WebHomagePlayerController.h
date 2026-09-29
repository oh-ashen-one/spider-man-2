// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "WebHomagePlayerController.generated.h"

/**
 * Mouse-safety player controller (owner rule: the game must never trap the mouse).
 *  - Starts RELEASED: cursor visible, not locked, not captured (look with right-mouse held).
 *  - Left click in the game window captures the mouse for mouse-look.
 *  - Escape ALWAYS releases it again (and shows the cursor).
 *  - Automated runs (-WHNoMouseCapture, or any -WHShotAt/-WHPerfFrom/-WHQuitAt/-WHAutoMove)
 *    never capture at all.
 * Keys are read in PlayerTick via WasInputKeyJustPressed, independent of Enhanced Input
 * mapping, so no pawn/input asset can swallow Escape.
 */
UCLASS()
class WEBHOMAGE_API AWebHomagePlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	AWebHomagePlayerController();

	virtual void PlayerTick(float DeltaTime) override;

	UFUNCTION(BlueprintCallable, Category="WebHomage|Input")
	void ReleaseMouse();

	UFUNCTION(BlueprintCallable, Category="WebHomage|Input")
	void CaptureMouse();

	UFUNCTION(BlueprintPure, Category="WebHomage|Input")
	bool IsMouseCaptured() const { return bMouseCaptured; }

protected:
	virtual void BeginPlay() override;

private:
	bool bMouseCaptured = false;
	bool bNeverCapture = false;
};
