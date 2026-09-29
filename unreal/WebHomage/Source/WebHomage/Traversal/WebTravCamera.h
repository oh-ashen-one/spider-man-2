// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
// Piece P3: port of src/player/camera.js — Insomniac-feel chase camera. Metres, UE axes.
// SMOOTHNESS CONTRACT (browser): every framing value that depends on mode / sub / anchor / velocity goes through a
// critically damped spring (SmoothDamp, Game Programming Gems 4), so mode changes never step the camera position, its
// velocity or the view direction. Only user look writes yaw / pitch directly.
// Conventions: Yaw = UE yaw in radians (0 = +X, + = turning right). Pitch in radians, + = looking DOWN (browser).
// Fov = VERTICAL field of view in degrees (browser three.js convention, 58 base); convert with the viewport aspect.
#pragma once

#include "CoreMinimal.h"
#include "Traversal/WebTravTypes.h"

class FWebTravWorld;

struct FTravCamInput
{
	FVector Pos = FVector::ZeroVector;   // body centre (m)
	FVector Vel = FVector::ZeroVector;   // m/s
	EWebTravMode Mode = EWebTravMode::Ground;
	FName Sub;
	double ModeT = 0.0;
	bool bHasAnchor = false;
	FVector Anchor = FVector::ZeroVector;
	bool bHasSwingDir = false;
	FVector SwingDir = FVector::ForwardVector;
	FVector WallNormal = FVector::ForwardVector;
	double Facing = 0.0;
	bool bDive = false;
	double Tension = 0.0;
	double Bank = 0.0;
};

class WEBHOMAGE_API FWebTravCamera
{
public:
	// ---- live state (public for telemetry)
	double Yaw = 0.0, Pitch = 0.14, Dist = 4.2, Fov = 58.0, Roll = 0.0;
	double Sens = 1.0;     // look input already in radians
	double Trauma = 0.0, Time = 0.0, HeightOff = 0.0, CollDist = 4.2, SideOff = 0.32;
	double Punch = 0.0, PunchV = 0.0, Dip = 0.0, DipV = 0.0, AnchorLean = 0.0, AnchorLeanV = 0.0, LastLook = 10.0;
	double KickV = 0.0, KickK = 0.0, MbK = 0.0, MbKV = 0.0;

	// ---- outputs
	FVector CamPos = FVector::ZeroVector;   // m
	FRotator CamRot = FRotator::ZeroRotator;
	double OutVFov = 58.0;                  // deg (vertical)
	double MotionBlur = 0.0;                // 0..~1.8 (browser mbK)

	void Reset(const FVector& Pos, double InYaw);
	void Shake(double Amt) { Trauma = FMath::Min(1.0, Trauma + Amt); }
	/** launch kick (zip slingshot / point launch): pull back + FOV widen, springs back */
	void Kick(double Amt) { KickV += 9.0 * Amt; Trauma = FMath::Min(1.0, Trauma + 0.08 * Amt); }
	void Impact(double Sev) { Trauma = FMath::Min(1.0, Trauma + 0.12 + 0.55 * Sev); PunchV -= 40.0 * Sev; DipV -= 5.0 * Sev; }
	/** Camera-relative directions (browser cam.forward / forwardFlat / rightFlat). */
	FVector Forward() const { const double CP = FMath::Cos(Pitch); return FVector(FMath::Cos(Yaw) * CP, FMath::Sin(Yaw) * CP, -FMath::Sin(Pitch)); }
	FVector ForwardFlat() const { return FVector(FMath::Cos(Yaw), FMath::Sin(Yaw), 0.0); }
	FVector RightFlat() const { return FVector(-FMath::Sin(Yaw), FMath::Cos(Yaw), 0.0); }

	/** Mouse / stick orbit, applied before traversal. Look.X = yaw right (rad), Look.Y = pitch down (rad). */
	void ApplyLook(const FVector2D& Look);
	/** Per-frame update after traversal. */
	void Update(double Dt, const FTravCamInput& P, const FWebTravWorld& World);

private:
	// SmoothDamp state (value + velocity pairs)
	bool bAutoInit = false;
	double AutoYaw = 0.0, AutoYawV = 0.0, AutoPitch = 0.0, AutoPitchV = 0.0, AutoRate = 0.0, AutoRateV = 0.0, AutoPRate = 0.0, AutoPRateV = 0.0;
	double LagK = 0.012, LagKV = 0.0, LagMax = 0.5, LagMaxV = 0.0;
	FVector LagOff = FVector::ZeroVector, LagOffV = FVector::ZeroVector, JumpOff = FVector::ZeroVector, JumpOffV = FVector::ZeroVector;
	FVector Lead = FVector::ZeroVector, LeadV = FVector::ZeroVector, LeanOff = FVector::ZeroVector, LeanOffV = FVector::ZeroVector;
	FVector Target = FVector::ZeroVector, LastGoal = FVector::ZeroVector, LastVel = FVector::ZeroVector;
	bool bHasLastGoal = false;
	double DistV = 0.0, HeightOffV = 0.0, SideOffV = 0.0, FovV = 0.0, CollDistV = 0.0;
	double YawRate = 0.0, YawRateV = 0.0, BankS = 0.0, BankSV = 0.0, LastVelYaw = 0.0;
	bool bHasLastVelYaw = false;
	double PivCap = -1.0, OccHold = 0.0, OccT = 0.0;
	bool bOccGoal = false;
	double OccGoalYaw = 0.0, OccGoalPitch = 0.0;
};
