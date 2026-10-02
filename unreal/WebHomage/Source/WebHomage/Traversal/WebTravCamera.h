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
	bool bFlip = false;      // round 11: a gymnast flip program is playing
	bool bFlipSoon = false;  // round 12: an apex flip is armed and about to start (the flip camera moves into place first)
	float FlipCompact = 0.f; // round 16: how compact the flip's upper-body shape is right now (tuck 1, pike 0.6, every open shape 0)
	// round 18: the hero's vertical extent (m: joints + 0.2 m pad, max of the posed body now and the program's shape table 0.1-0.25 s ahead);
	// 0 = unknown. The trick camera's distance follows it (FlipExtK x extent within FlipDist..FlipDistMax) so TC-C holds at TC4 distances.
	float FlipExtent = 0.f;
	bool bFlipPre = false;   // round 18: a flow flip release is predicted (autoChain rule / trick held while swinging): the trick camera pre-blends
};

class WEBHOMAGE_API FWebTravCamera
{
public:
	// ---- live state (public for telemetry)
	double Yaw = 0.0, Pitch = 0.14, Dist = 4.2, Fov = 58.0, Roll = 0.0;
	double Sens = 1.0;     // look input already in radians
	/** 2026-10-01 settings menu: base vertical FOV (deg; browser 58) and the camera-shake switch. Set from WHSettings() every frame
	 *  by the pawn; at the defaults (58.0, true) the camera is bit-identical to before the menu existed. */
	double BaseVFov = 58.0;
	bool bJolts = true;
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
	// (round 15, orchestrator: "wall-run camera c must not look 56 deg up" -- 2.2 m below / 2.2 m out / hero at 0.68 made the view
	// ~57 deg up): 1.3 m below, 3.1 m out, hero at 0.60, look-up capped at WallMaxUpDeg)
	double WallCamBelow = 1.3;     // m under the hero centre
	double WallCamOut = 3.1;       // m out from the wall (min; more when the street floor pushes the camera up)
	double WallCamDist = 3.4;      // m camera -> hero kept while the floor clamps the camera height
	double WallFrameS = 0.60;      // hero screen centre on the wall
	double WallMaxUpDeg = 30.0;    // round 15: wall camera look-up cap (was 80)
	double WallFovAdd = 4.0;       // deg vertical FOV added on the wall
	double WallK = 0.0;            // 0 chase .. 1 wall camera (spring)
	// round 10 (TRAVERSAL-SPEC T23: release trick silhouetted against the sky, with a rise): during a sky launch the camera sinks
	// SkyCamBelow m under the hero centre and frames him at SkySFrame (upper centre), look-up limited to SkyPitchUp deg (T11 p5)
	double SkyCamBelow = 1.2, SkySFrame = 0.40, SkyPitchUp = 10.0;
	double SkyK = 0.0, SkyKV = 0.0;
	// ---- round 16: TRICK_CAMERA_SPEC (director, Fable 5.1, after r15; supersedes the r11-r15 sky search / side-on orbit / tilt demands)
	// While a flip program plays the camera is a HELD 3/4-behind chase: ONE yaw offset of FlipYawMin..FlipYawMax deg from the
	// travel-behind direction, chosen once at the release frame (ChooseFlipView) and never re-searched (TC1); side order = obstruction
	// (the spot at FlipDist must be sweep-reachable with FlipWallMargin m free beyond it and a clear path FlipAheadT s along the travel),
	// then sun (view >= SunMinDeg from the sun), then open space (TC2). The camera sits FlipDist m from the hero (5.0-6.5, TC4) on that
	// WORLD azimuth (drift is the hero's own motion only, TC3), FlipDrop m under his body centre (TC6), hero framed at FlipSFrame
	// (TC7) with a FlipLeadDeg lead-room yaw bias toward his travel, pitch within +-8 deg (TC5). An obstruction on the held axis dollies the
	// camera IN along it (to FlipDistMin; TC11), never yaws or re-picks the side; under FlipDistMin (or with no clear spot at all) the
	// camera blends to the plain chase over FlipOutT. Blend in FlipInT (vertical FlipZInT), out FlipOutT (spring smooth times, TC10).
	double FlipK = 0.0, FlipKV = 0.0, FlipZK = 0.0, FlipZKV = 0.0;   // weights: 0 chase .. 1 trick camera (FlipK = telemetry flipcam_k)
	bool bFlipWas = false, bFlipAbort = false, bFlipOutRun = false, bFlipInRun = false;
	double FlipInClock = 0.0, FlipInK0 = 0.0, FlipInS = 0.0, FlipInR = 0.0, FlipInD0 = 30.0;
	double FlipInRate = 140.0, FlipInAcc = 2400.0, FlipInDec = 380.0;   // round 17 v2 blend-in profile (deg/s, deg/s^2)   // round 17: blend-in state (smoothstep over FlipInT from the weight at its start: k >= .9 by 0.8 x FlipInT)
	double FlipSkyW = 4.0;   // round 17: weight of the ring sky share in the side choice (r16 1.5: the open-space term picked the street side)
	double FlipObsT = 0.0, FlipSinceObs = 9.0, FlipAbortGrace = 0.20;   // seconds the held axis has been blocked under FlipDistMin / grace before the plain-chase fallback
	double FlipOutClock = 0.0, FlipOutK0 = 0.0, FlipOutZ0 = 0.0;   // blend-out state (smoothstep over FlipOutT from the weights at its start)
	// round 18 (critic r17 TC-C "distance 4.1-4.4 m, h p90 .37-.46"): FlipDist 4.4 -> 5.0 (TC4 5.0-6.5) and the distance follows the hero's
	// extent (FlipExtK m per m, up to FlipDistMax) instead of the r16 tuck pull-in; FlipAzHold: the held azimuth stays FlipAzHold s past the
	// catch before it blends out (critic r17 TC-A "offset p5 20-29, range up to 34": the window runs to the catch + 0.5 s); FlipAzRate: a
	// re-chosen view while the previous one is still blended moves its azimuth at <= this rate (deg/s) instead of jumping
	double FlipDistMax = 6.4, FlipDistCompact = 4.5, FlipExtK = 2.6, FlipExtS = 0.0, FlipExtV = 0.0, FlipAzHold = 0.25, FlipAzRate = 50.0, FlipAzNow = 0.0;
	double FlipDist = 5.0, FlipDistMin = 4.0, FlipTuckPull = 0.0, FlipCompactS = 0.0, FlipCompactV = 0.0, FlipCompactT = 0.2, FlipDrop = 1.0, FlipYawMin = 35.0, FlipYawMax = 55.0, FlipPrefYaw = 47.0, FlipLeadDeg = 3.0;
	double FlipSFrame = 0.38, FlipPitchUpMax = 7.5, MaxLookUpDeg = 10.0;
	double FlipInT = 0.34, FlipOutT = 0.90, FlipZInT = 0.15, FlipZHold = 0.30, FlipDollyInT = 0.08, FlipDollyOutT = 0.6;
	double FlipWallMargin = 1.5, FlipAheadT = 0.5;
	double FlipAz = 0.0;        // rad, world azimuth hero -> camera (held for the trick)
	double FlipOffDeg = 0.0;    // signed offset of that azimuth from the travel-behind direction at the release (deg, + = right of behind)
	double FlipSide = 1.0;      // sign of FlipOffDeg
	double FlipDistSel = 5.0, FlipDistNow = 5.0, FlipDistV = 0.0;   // chosen / current (dollied) distance
	int32 FlipTier = -1;        // selection: 0 obstruction + sun ok, 1 sun rule failed (only side clear), 2 pulled in, 3 plain chase (no clear spot)
	double FlipSkyShare = -1.0, FlipGlare = 0.0, FlipSunDeg = -1.0;   // telemetry: ring sky share / glare share / sun angle of the chosen view
	// the sun: SunDir = unit vector TO the sun, set by the character from the level's atmosphere sun light (bHaveSun false = no sun term)
	FVector SunDir = FVector::UpVector;
	bool bHaveSun = false;
	double SunMinDeg = 100.0, SunPrefDeg = 140.0, GlareDeg = 25.0, GlareW = 8.0;
	double CapUpDeg = 29.0;    // the look-up cap applied this frame (also after the output slew re-aim)
	/** Round 15: -WHCamTune=Name=Value,... for the named tuning doubles (probes without a rebuild). Returns false if unknown. */
	bool SetTune(const FString& Name, double V);
	// round 14: after a web attach (SwingT) the pitch settles into SettleDownMin..SettleDownMax deg DOWN, blended in over
	// SettleT0..SettleT1 s (the hero is kept inside 0.18..0.82 of the frame height; the band widens if it has to)
	double SettleDownMin = 5.5, SettleDownMax = 11.5, SettleT0 = 0.25, SettleT1 = 0.5;
	// round 13 (critic r12: one-frame cuts): no cut -- the camera OUTPUT is slew-limited per 1/60 s (position first, the view re-aimed at
	// the hero by the same correction, then pitch / yaw). SlewFlags (telemetry): 1 = position limited, 2 = pitch, 4 = yaw this frame.
	// round 20: hero visibility lift (m, spring) + telemetry: visible probe points (0-4) and the camera enclosed by geometry
	double VisUp = 0.0, VisUpV = 0.0, VisUpGoal = 0.0, VisHold = 0.0;
	int32 VisPts = 4;
	// round 24 (critic r23 camera hard gate, c 7.7-8.5 s: a user camera turn on a roof swung the lens into a tower wall -- cam 1.6 m, hero out
	// of frame, yaw -88 -> -46 -> -99): on foot / perched (Ground / Perch / Land) the blocked-spot orbit search only takes offsets in the
	// direction the user is turning (LookYawDir, within GndLookHold s of the last look input), the found orbit offset is absorbed into the
	// look yaw (GndAbsorb 1: no spring back = no reversal), and a lens pushed under GndMinDist m cranes up over the hero (GndCrane, spring
	// GndCraneT s) until it is GndMinDist + 0.2 m away. GndMinDist 0 = r23.
	double GndMinDist = 3.0, GndLookHold = 0.8, GndAbsorb = 1.0, GndCraneT = 0.10, GndCraneMax = 6.0;
	double GndCrane = 0.0, GndCraneV = 0.0, GndCraneGoal = 0.0, GndClearT = 0.0;
	int32 LookYawDir = 0;
	double GndStop = 1.0, GndStopExtra = 1.2, GndStopR = 0.5, GndYawOk = 0.0;
	bool bGndYawOk = false; int32 GndStopped = 0;
	bool bCamEnclosed = false;
	double MaxStepPosM = 1.1, MaxStepPitchDeg = 2.7, MaxStepYawDeg = 3.6, FlipMaxStepYawDeg = 2.4;
	int32 SlewFlags = 0;
	/** Round 16: pick the held trick view at the release frame (TC1/TC2). Sets FlipAz / FlipOffDeg / FlipDistSel / FlipTier. */
	void ChooseFlipView(const FTravCamInput& P, const FWebTravWorld& World);

	// ---- outputs
	bool bCamInGeometry = false;            // camera sphere (0.25 m) overlaps solid geometry this frame
	bool bLensTouch = false;               // round 16 (T19 / TC11): the 0.25 m lens sphere at the FINAL camera position touches geometry / foliage
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
	// 2026-10-01 settings menu: bJolts = "Camera shake" (default on). Off = no trauma shake, no landing punch / dip, no launch kick.
	void Shake(double Amt) { if (!bJolts) return; Trauma = FMath::Min(1.0, Trauma + Amt); }
	/** launch kick (zip slingshot / point launch): pull back + FOV widen, springs back */
	void Kick(double Amt) { if (!bJolts) return; KickV += 9.0 * Amt; Trauma = FMath::Min(1.0, Trauma + 0.08 * Amt); }
	void Impact(double Sev) { if (!bJolts) return; Trauma = FMath::Min(1.0, Trauma + 0.12 + 0.55 * Sev); PunchV -= 40.0 * Sev; DipV -= 5.0 * Sev; }
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
	bool bOutInit = false;
	FVector LastOutPos = FVector::ZeroVector;
	FRotator LastOutRot = FRotator::ZeroRotator;
	// round 13: the hero position of the last composed frame (the "hero inside geometry" hold follows the hero instead of freezing)
	FVector LastComposeHero = FVector::ZeroVector;
	bool bHaveComposeHero = false;
};
