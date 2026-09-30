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
	double HAbove = 0.0;   // feet height above the floor below (m)
	double SwingAngle = 0.0; // rope angle from straight down (rad), swinging only
	double SwingT = 99.0;    // s since the current web attached
	bool bSky = false;       // round 10: sky launch (jump-release + trick) in progress
};

class WEBHOMAGE_API FWebTravCamera
{
public:
	// ---- live state (public for telemetry)
	double Yaw = 0.0, Pitch = 0.14, Dist = 4.2, Fov = 58.0, Roll = 0.0;
	double Sens = 1.0;     // look input already in radians
	/** Round 02: swing / air pitch follows height (looks down over the street when high, levels out at the arc bottom). */
	double HeightPitchK = 0.024, HeightPitchRef = 10.0;
	double Trauma = 0.0, Time = 0.0, HeightOff = 0.0, CollDist = 4.2, SideOff = 0.32;
	double Punch = 0.0, PunchV = 0.0, Dip = 0.0, DipV = 0.0, AnchorLean = 0.0, AnchorLeanV = 0.0, LastLook = 10.0;
	double KickV = 0.0, KickK = 0.0, MbK = 0.0, MbKV = 0.0;

	// ---- round 03 chase-camera tuning
	double ChaseDist = 3.8;        // horizontal distance behind the hero (m) — round 05
	double ChaseHeight = 0.6;      // camera height over the hero centre (m) — r05 1.1, r07 1.8, r09 0.6 (TRAVERSAL-SPEC T11: pitch median 4-12 deg down)
	double CamZMin = 0.2, CamZMax = 1.8;   // held band over the hero centre (m) — r07 1.2..2.6, r09 0.2..1.8
	// round 09: anchor-side composition — yaw (deg) and sideways shift (m) toward the active anchor, roll (deg) with the arc
	double AnchorShift = 1.3, AnchorRollMax = 6.0; // round 09: sideways slide (m) toward the active anchor, roll at the arc ends (deg)
	double AttachMaxS = 0.64;     // round 10: attach look-up keeps the hero centre at or above this share of the frame height
	double RollDeadDeg = 1.0;     // round 10: roll leans under this are dropped (T13 median)
	double AttachFovMax = 10.0;   // deg of extra vertical FOV at a web attach — round 08 (was 26)
	double CamWallSoft = 3.0, CamWallHard = 1.5;   // m sideways clearance from facades — round 08
	double SwingCloser = 0.4;      // m closer while swinging / airborne — round 07
	double PitchDownMin = -8.0;    // deg, lowest look-down of the chase camera — r07 10, r09 -8 (T11 p5: 10 deg up .. 3 deg down)
	double MinHeroDist = 2.2;      // never closer to the hero (m)
	double FrameLowS = 0.50, FrameHighS = 0.37; // hero screen centre (0 top .. 1 bottom): arc bottom .. top — r10 low 0.44 -> 0.50 (T10 spread .187 < .20); r09 (was 0.48 / 0.40; T10 range <= 0.70)
	// ---- round 06 wall-run camera (critic r05 / ref wall-run): below and out from the hero, looking UP the facade at a
	// grazing angle (view 20-35 deg off the wall plane) so the wall converges to the roof edge; hero in the lower third
	double WallCamBelow = 2.2;     // m under the hero centre
	double WallCamOut = 2.2;       // m out from the wall (min; more when the street floor pushes the camera up)
	double WallCamDist = 3.2;      // m camera -> hero kept while the floor clamps the camera height
	double WallFrameS = 0.68;      // hero screen centre on the wall
	double WallFovAdd = 4.0;       // deg vertical FOV added on the wall
	double WallK = 0.0;            // 0 chase .. 1 wall camera (spring)
	// round 10 (TRAVERSAL-SPEC T23: release trick silhouetted against the sky, with a rise): during a sky launch the camera sinks
	// SkyCamBelow m under the hero centre and frames him at SkySFrame (upper centre), look-up limited to SkyPitchUp deg (T11 p5)
	double SkyCamBelow = 1.2, SkySFrame = 0.40, SkyPitchUp = 10.0;
	double SkyK = 0.0, SkyKV = 0.0;

	// ---- outputs
	bool bCamInGeometry = false;            // camera sphere (0.25 m) overlaps solid geometry this frame
	double HeroDist = 0.0;                  // camera -> hero centre (m)
	double FrameS = 0.55;                   // current framing target (hero screen centre Y, 0 top .. 1 bottom)
	FVector CamPos = FVector::ZeroVector;   // m
	FRotator CamRot = FRotator::ZeroRotator;
	double OutVFov = 58.0;                  // deg (vertical)
	double MotionBlur = 0.0;                // 0..~1.8 (browser mbK)

	void Reset(const FVector& Pos, double InYaw);
	/** Round 03 chase composition: position, collision, framing, orientation (called by Update). */
	void ComposeChase(double Dt, const FTravCamInput& P, const FWebTravWorld& World, const FVector& Fwd);
	double DebugOccHold() const { return OccHold; }
	double DebugAutoPitch() const { return AutoPitch; }
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
	bool bChaseInit = false;
	FVector CamXY = FVector::ZeroVector, CamXYV = FVector::ZeroVector;
	double CamZ = 0.0, CamZV = 0.0, FrameSV = 0.0, OccYawOff = 0.0, OccYawOffV = 0.0, OccUp = 0.0, OccUpV = 0.0;
	double OccYawGoal = 0.0, OccUpGoal = 0.0, UserPitch = 0.0, AttachLook = 0.0, AttachLookV = 0.0, AttachFov = 0.0, AttachFovV = 0.0, AttachYaw = 0.0, AttachYawV = 0.0;
	bool bOccGoal = false;
	double WallKV = 0.0;
	double WallPush = 0.0, WallPushV = 0.0;
	double SideGoal = 1.0, SideK = 0.0, SideKV = 0.0;
	bool bInChain = false;
	double ChainAirT = 0.0;
	FVector WallHeroXY = FVector::ZeroVector;
	bool bWallXY = false;
	double OccGoalYaw = 0.0, OccGoalPitch = 0.0;
};
