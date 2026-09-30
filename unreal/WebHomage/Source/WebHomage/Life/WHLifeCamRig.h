// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
// P6 City life: a camera that walks a straight street-level path (for the 1080p60 street clip and other life captures).
#pragma once

#include "CoreMinimal.h"
#include "Camera/CameraActor.h"
#include "WHLifeCamRig.generated.h"

UCLASS()
class WEBHOMAGE_API AWHLifeCamRig : public ACameraActor
{
	GENERATED_BODY()
public:
	AWHLifeCamRig();
	virtual void BeginPlay() override;
	virtual void Tick(float Dt) override;

	/** Start / end of the path (cm). The camera looks along the path (plus LookOffset) at the given eye height above Start.Z. */
	UPROPERTY(EditAnywhere, Category="Rig") FVector Start = FVector::ZeroVector;
	UPROPERTY(EditAnywhere, Category="Rig") FVector End = FVector(0, -6000, 0);
	UPROPERTY(EditAnywhere, Category="Rig") float Duration = 20.f;
	UPROPERTY(EditAnywhere, Category="Rig") float EyeHeight = 170.f;
	UPROPERTY(EditAnywhere, Category="Rig") float LookAheadCm = 4000.f;
	UPROPERTY(EditAnywhere, Category="Rig") float LookHeightDelta = 250.f;
	UPROPERTY(EditAnywhere, Category="Rig") float YawSwayDeg = 6.f;
	UPROPERTY(EditAnywhere, Category="Rig") bool bLoop = true;
	UPROPERTY(EditAnywhere, Category="Rig") float FovDegrees = 70.f;
private:
	float T = 0.f;
	void Place();
};
