// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Traversal/WebTravCamera.h"
#include "Traversal/WebTravWorld.h"
#include "WebHomage.h"

namespace
{
	double Damp(double A, double B, double Rate, double Dt) { return A + (B - A) * (1.0 - FMath::Exp(-Rate * Dt)); }
	double WrapA(double A) { return FMath::Atan2(FMath::Sin(A), FMath::Cos(A)); }
	double AngDamp(double A, double B, double Rate, double Dt) { return A + WrapA(B - A) * (1.0 - FMath::Exp(-Rate * Dt)); }
	double Smooth(double X, double E0, double E1) { const double T = FMath::Clamp((X - E0) / (E1 - E0), 0.0, 1.0); return T * T * (3.0 - 2.0 * T); }
	// Critically damped spring (SmoothDamp): frame-rate independent, continuous position AND velocity.
	double SD(double& V, double& Vel, double Target, double St, double Dt)
	{
		const double W = 2.0 / FMath::Max(1e-4, St), X = W * Dt, E = 1.0 / (1.0 + X + 0.48 * X * X + 0.235 * X * X * X);
		const double Ch = V - Target, Tmp = (Vel + W * Ch) * Dt;
		Vel = (Vel - W * Tmp) * E;
		V = Target + (Ch + Tmp) * E;
		return V;
	}
	double SDA(double& V, double& Vel, double Target, double St, double Dt) { return SD(V, Vel, V + WrapA(Target - V), St, Dt); }
	void SDV(FVector& V, FVector& Vel, const FVector& Target, double St, double Dt)
	{
		for (int32 A = 0; A < 3; ++A) { SD(V[A], Vel[A], Target[A], St, Dt); }
	}
	double Noise(double T, double S) { return FMath::Sin(T * 1.7 + S) * 0.5 + FMath::Sin(T * 3.1 + S * 2.3) * 0.3 + FMath::Sin(T * 5.3 + S * 4.1) * 0.2; }
	FName N_vault(TEXT("vault")), N_wallRun(TEXT("wallRun")), N_topOut(TEXT("topOut"));
}

void FWebTravCamera::Reset(const FVector& Pos, double InYaw)
{
	Target = Pos + FVector(0, 0, 0.55);
	Yaw = InYaw; Pitch = 0.14; CollDist = Dist;
	bAutoInit = false;
	LagOff = LagOffV = JumpOff = JumpOffV = FVector::ZeroVector;
	bHasLastGoal = false; AnchorLean = 0.0; AnchorLeanV = 0.0;
	bChaseInit = false; UserPitch = 0.0; OccYawGoal = OccUpGoal = 0.0;
	bOutInit = false; // round 13: a teleport / reset is allowed to move the view at once
	bHaveComposeHero = false;
}

void FWebTravCamera::ApplyLook(const FVector2D& Look)
{
	if (FMath::Abs(Look.X) + FMath::Abs(Look.Y) > 0.001) LastLook = 0.0;
	Yaw += Look.X * Sens;
	Pitch = FMath::Clamp(Pitch + Look.Y * Sens, -0.9, 1.25);
	UserPitch = FMath::Clamp(UserPitch + Look.Y * Sens, -0.6, 0.6);
}

void FWebTravCamera::Update(double Dt, const FTravCamInput& P, const FWebTravWorld& World)
{
	Dt = FMath::Min(Dt, 0.1);
	Time += Dt; LastLook += Dt;
	const FVector& Vel = P.Vel;
	const double Speed = Vel.Size(), HS = FVector2D(Vel.X, Vel.Y).Size();
	const EWebTravMode M = P.Mode;
	const bool bSwinging = M == EWebTravMode::Swing, bAir = M == EWebTravMode::Air || M == EWebTravMode::Zip, bDive = P.bDive;
	const FString SubS = P.Sub.ToString();
	const bool bLandSub = SubS.StartsWith(TEXT("land")), bLedgeSub = SubS.StartsWith(TEXT("ledge"));

	// ---- auto recenter behind the direction of travel
	const double Blend = FMath::Clamp((LastLook - 0.9) * 1.5, 0.0, 1.0);
	if (LastLook < 0.05 || !bAutoInit) { AutoYaw = Yaw; AutoYawV = 0; AutoPitch = Pitch; AutoPitchV = 0; bAutoInit = true; }
	{
		bool bWY = false, bWP = false;
		const double HeightPitch = FMath::Clamp((P.HAbove - HeightPitchRef) * HeightPitchK, -0.1, 0.55);
		double WantYaw = 0, WantPitch = 0, Rate = 0;
		if (M == EWebTravMode::Wall)
		{
			if (P.ModeT > 0.3) { WantYaw = FMath::Atan2(-P.WallNormal.Y, -P.WallNormal.X); Rate = 1.6; bWY = true; }
			WantPitch = P.Sub == N_wallRun ? -0.08 : -0.05; bWP = true;
		}
		else if (M == EWebTravMode::Perch) { WantYaw = P.Facing; Rate = 1.4; WantPitch = 0.3; bWY = bWP = true; }
		else if (bDive && HS <= 2.5) { WantPitch = 0.75 + 0.4 * Smooth(-Vel.Z, 18, 45); bWP = true; }
		else if (bSwinging && P.bHasSwingDir)
		{ // frame the ARC: recenter behind the swing plane direction, not the instantaneous velocity
			WantYaw = FMath::Atan2(P.SwingDir.Y, P.SwingDir.X); Rate = 2.2; bWY = true;
			// round 02: height term (browser: 0.1 - vz*0.006) so the horizon travels with the pendulum
			WantPitch = FMath::Clamp(0.04 + HeightPitch - Vel.Z * 0.0015, -0.15, 0.6); bWP = true;
		}
		else if (HS > 2.5)
		{
			WantYaw = FMath::Atan2(Vel.Y, Vel.X); bWY = true;
			Rate = FMath::Clamp((HS - 2.0) / 10.0, 0.0, 1.0) * (bAir ? 1.8 : 1.3);
			WantPitch = bDive ? 0.62 + 0.5 * Smooth(-Vel.Z, 18, 45) : bAir ? FMath::Clamp(0.08 + HeightPitch - Vel.Z * 0.003, -0.1, 0.6) : 0.14; bWP = true;
		}
		OccHold -= Dt;
		if (OccHold > 0) { bWY = false; bWP = false; }
		if (bWY) SDA(AutoYaw, AutoYawV, WantYaw, 0.5, Dt);
		else if (AutoRate < 0.05) { AutoYaw = Yaw; AutoYawV = 0; }
		if (bWP) SD(AutoPitch, AutoPitchV, WantPitch, (bSwinging || bAir) && !bDive ? 0.18 : 0.5, Dt); // round 02: pitch tracks height closer
		else if (AutoPRate < 0.05) { AutoPitch = Pitch; AutoPitchV = 0; }
		SD(AutoRate, AutoRateV, bWY ? Rate : 0.0, 0.35, Dt);
		SD(AutoPRate, AutoPRateV, bWP ? (bDive ? 2.4 : (bSwinging || bAir) ? 7.0 : 1.1) : 0.0, 0.35, Dt);
		if (Blend > 0)
		{
			Yaw = AngDamp(Yaw, AutoYaw, FMath::Max(0.0, AutoRate) * Blend, Dt);
			Pitch = Damp(Pitch, AutoPitch, FMath::Max(0.0, AutoPRate) * Blend, Dt);
		}
	}
	// ---- follow pivot: soft-clamped velocity lag + unexplained-displacement absorber
	const FVector Goal = P.Pos + FVector(0, 0, 0.55);
	SD(LagK, LagKV, bSwinging || bAir ? 0.03 : M == EWebTravMode::Wall ? 0.02 : 0.012, 0.4, Dt);
	SD(LagMax, LagMaxV, bSwinging || bAir ? 0.8 : 0.5, 0.4, Dt);
	FVector WantLag = Vel * -LagK;
	{ const double L = WantLag.Size(); if (L > 1e-4) WantLag *= LagMax * FMath::Tanh(L / LagMax) / L; }
	SDV(LagOff, LagOffV, WantLag, 0.3, Dt);
	if (bHasLastGoal)
	{
		const FVector Mv = Goal - LastGoal;
		FVector Jump = Mv - Vel * Dt;
		const FVector J2 = Mv - LastVel * Dt;
		if (J2.SizeSquared() < Jump.SizeSquared()) Jump = J2;
		const double JL = Jump.Size();
		if (JL > 0.06 && JL < 3.0) JumpOff -= Jump;
		else if (JL >= 3.0) { JumpOff = FVector::ZeroVector; JumpOffV = FVector::ZeroVector; }
	}
	bHasLastGoal = true; LastGoal = Goal; LastVel = Vel;
	if (JumpOff.Size() > 1.2) JumpOff = JumpOff.GetSafeNormal() * 1.2;
	SDV(JumpOff, JumpOffV, FVector::ZeroVector, 0.3, Dt);
	Target = Goal + LagOff + JumpOff;
	// velocity look-ahead: vertical damped hard while swinging / airborne, capped at 2 m
	{
		const double LW = bSwinging || bAir ? 0.06 : 0.04;
		FVector LeadW(Vel.X * LW, Vel.Y * LW, Vel.Z * (bSwinging || bAir ? 0.015 : LW));
		if (LeadW.Size() > 2.0) LeadW = LeadW.GetSafeNormal() * 2.0;
		SDV(Lead, LeadV, LeadW, 0.45, Dt);
	}
	// ---- distance / height / FOV by context
	double WantDist = 4.0, WantH = 0.0, WantSide = 0.32;
	if (M == EWebTravMode::Ground || M == EWebTravMode::Land) { WantDist = 3.9 + FMath::Clamp((Speed - 8.0) * 0.07, 0.0, 0.7); WantSide = 0.35; }
	else if (bSwinging) { WantDist = 3.6 + FMath::Clamp((Speed - 12.0) * 0.025, 0.0, 0.7); WantH = 0.35 + P.Tension * 0.25; WantSide = 0.15; }
	else if (bAir) { WantDist = bDive ? 3.9 : 3.8 + FMath::Clamp((Speed - 12.0) * 0.025, 0.0, 0.7); WantH = bDive ? 0.9 : 0.15; WantSide = 0.2; }
	else if (M == EWebTravMode::Wall) { WantDist = 4.8; WantH = P.Sub == N_wallRun ? 0.2 : 0.0; WantSide = 0.0; }
	else if (M == EWebTravMode::Perch) { WantDist = 4.3; WantH = 0.25; WantSide = 0.4; }
	if (M == EWebTravMode::Land || bLandSub) WantDist = 4.2;
	if (bLedgeSub) { WantH = 1.4; Pitch = Damp(Pitch, 0.42, 4, Dt); }
	const double WantFov = 58.0 + 13.0 * Smooth(Speed, 12, 44) + (bDive ? 5.0 : 0.0) + WallFovAdd * WallK;
	SD(Dist, DistV, WantDist, 0.55, Dt);
	SD(HeightOff, HeightOffV, WantH, 0.5, Dt);
	SD(SideOff, SideOffV, WantSide, 0.6, Dt);
	// FOV punch / dip springs
	PunchV += (-Punch * 140.0 - PunchV * 16.0) * Dt; Punch += PunchV * Dt;
	DipV += (-Dip * 90.0 - DipV * 13.0) * Dt; Dip += DipV * Dt;
	SD(Fov, FovV, WantFov, 0.5, Dt);
	// launch kick spring
	KickV += (-KickK * 55.0 - KickV * 11.0) * Dt; KickK += KickV * Dt;
	// ---- roll: velocity yaw-rate + swing bank
	const double VelYaw = FMath::Atan2(Vel.Y, Vel.X);
	const double DY = bHasLastVelYaw ? WrapA(VelYaw - LastVelYaw) : 0.0;
	LastVelYaw = VelYaw; bHasLastVelYaw = true;
	SD(YawRate, YawRateV, HS > 3 ? FMath::Clamp(DY / FMath::Max(Dt, 1e-3), -3.0, 3.0) * FMath::Min(1.0, (HS - 3.0) / 17.0) : 0.0, 0.3, Dt);
	SD(BankS, BankSV, bSwinging ? P.Bank : 0.0, 0.35, Dt);
	// round 09 (TRAVERSAL-SPEC T13: roll allowed, |roll| median <= 1.5 deg, p90 <= 10): a lean toward the anchor side only
	// toward the arc ends
	const double ArcRoll = SideK * FMath::DegreesToRadians(AnchorRollMax) * Smooth(FMath::Abs(P.SwingAngle), 0.55, 1.0);
	double WantRoll = FMath::Clamp(-YawRate * 0.03, -0.07, 0.07) - BankS * 0.04 + ArcRoll;
	// round 10 (critic r09 T13 |roll| median 1.6 > 1.5 deg): small leans (< RollDeadDeg) are dropped, larger ones keep their size
	{
		const double Dz = FMath::DegreesToRadians(RollDeadDeg);
		WantRoll *= FMath::Clamp((FMath::Abs(WantRoll) - Dz) / FMath::Max(Dz, 1e-6), 0.0, 1.0); // 0 below Dz, full from 2 Dz
	}
	WantRoll *= 1.0 - Smooth(FlipK, 0.0, 1.0); // round 16 (TC12): no roll with the body while the trick camera is in
	Roll = Damp(Roll, WantRoll, 3, Dt);
	// ---- compose (round 03): lagged chase camera with explicit framing and collision
	const FVector Fwd = Forward();
	ComposeChase(Dt, P, World, Fwd);
	const FVector LookAt = CamPos + CamRot.Vector() * 10.0;
	// shake
	Trauma = FMath::Max(0.0, Trauma - Dt * 1.5);
	const double Sh = Trauma * Trauma;
	FRotator R = CamRot;
	R.Roll = FMath::RadiansToDegrees(Roll + Sh * 0.045 * Noise(Time * 22.0, 3.0));
	R.Pitch += FMath::RadiansToDegrees(Sh * 0.035 * Noise(Time * 25.0, 1.0));
	R.Yaw += FMath::RadiansToDegrees(Sh * 0.035 * Noise(Time * 24.0, 7.0));
	CamRot = R;
	OutVFov = Fov + Punch + 9.0 * FMath::Max(0.0, KickK) + FMath::RadiansToDegrees(AttachFov);
	(void)LookAt;
	// ---- round 13: output slew limit (see the header): never a cut
	SlewFlags = 0;
	if (bOutInit && Dt > 0.0)
	{
		const double K = Dt * 60.0;
		const FVector D = CamPos - LastOutPos;
		const double Lm = MaxStepPosM * K;
		if (D.Size() > Lm)
		{
			const FVector NewPos = LastOutPos + D.GetSafeNormal() * Lm;
			const FRotator A0 = (P.Pos - CamPos).Rotation(), A1 = (P.Pos - NewPos).Rotation();
			CamRot.Yaw += FRotator::NormalizeAxis(A1.Yaw - A0.Yaw);
			CamRot.Pitch += A1.Pitch - A0.Pitch;
			CamPos = NewPos;
			SlewFlags |= 1;
		}
		const double SlP = CamRot.Pitch - LastOutRot.Pitch, SlY = FRotator::NormalizeAxis(CamRot.Yaw - LastOutRot.Yaw);
		const double MP = MaxStepPitchDeg * K, MY = (FlipK > 1e-3 ? FlipMaxStepYawDeg : MaxStepYawDeg) * K; // round 16 (TC-B): <= 150 deg/s while the trick camera is in (blend in / hold / blend out)
		if (FMath::Abs(SlP) > MP) { CamRot.Pitch = LastOutRot.Pitch + FMath::Sign(SlP) * MP; SlewFlags |= 2; }
		if (FMath::Abs(SlY) > MY) { CamRot.Yaw = LastOutRot.Yaw + FMath::Sign(SlY) * MY; SlewFlags |= 4; }
		if (SlewFlags) { HeroDist = FVector::Dist(CamPos, P.Pos); bCamInGeometry = World.SphereOverlaps(CamPos, 0.15); }
		// round 14: the position re-aim above may add pitch -- keep the look-up cap (wall-run camera excepted)
		// (round 15: CapUpDeg = the cap ComposeChase applied this frame -- flip 8, chase 10, wall 30)
		if (CamRot.Pitch > CapUpDeg + 0.5) CamRot.Pitch = CapUpDeg + 0.5;
	}
	bLensTouch = World.SphereOverlaps(CamPos, 0.25);
	LastOutPos = CamPos; LastOutRot = CamRot; bOutInit = true;
	// speed motion blur: none on foot / walls, ramps in over fast swings / dives / zips
	const bool bGroundish = M == EWebTravMode::Ground || M == EWebTravMode::Land || M == EWebTravMode::Wall;
	// round 08: blur only at genuinely high speed (0 below 28 m/s, full at 50), none on foot / walls
	const double MbTarget = (bGroundish ? 0.0 : bDive ? 1.3 : 1.0) * Smooth(Speed, 28, 50);
	MotionBlur = FMath::Max(0.0, SD(MbK, MbKV, MbTarget, MbTarget > MbK ? 0.35 : 0.2, Dt));
}

void FWebTravCamera::ComposeChase(double Dt, const FTravCamInput& P, const FWebTravWorld& World, const FVector& /*Fwd*/)
{
	const FVector Hero = P.Pos;                         // body centre (m)
	const FVector Chest = Hero + FVector(0, 0, 0.4);
	const bool bSwinging = P.Mode == EWebTravMode::Swing, bAir = P.Mode == EWebTravMode::Air || P.Mode == EWebTravMode::Zip;
	const double VFov = FMath::DegreesToRadians(Fov + Punch + 9.0 * FMath::Max(0.0, KickK));
	const double TanHalfV = FMath::Tan(VFov * 0.5);
	// ---- framing target: hero low in frame at the bottom of an arc / near the street, upper centre up high; falling
	// fast pushes him lower (the camera trails above), rising pushes him higher
	double SWant = 0.58;
	if (bSwinging)
	{ // by arc angle: lower third at the bottom of the arc, upper centre at both ends (every swing travels the frame)
		SWant = FMath::Lerp(FrameLowS, FrameHighS, FMath::Clamp(FMath::Abs(P.SwingAngle) / 0.85, 0.0, 1.0));
	}
	else if (bAir)
	{
		SWant = FMath::Lerp(FrameLowS, FrameHighS, FMath::Clamp((P.HAbove - 8.0) / 32.0, 0.0, 1.0)) - P.Vel.Z * 0.0025;
	}
	if (P.Mode == EWebTravMode::Wall || P.Sub == N_topOut) SWant = WallFrameS;
	// round 10: sky launch — the camera sinks under the hero and looks up while he rises / hangs (released at a fast fall)
	SD(SkyK, SkyKV, (P.bSky && P.Vel.Z > -9.0) ? 1.0 : 0.0, P.bSky && P.Vel.Z > -9.0 ? 0.25 : 0.35, Dt);
	SkyK = FMath::Clamp(SkyK, 0.0, 1.0);
	SWant = FMath::Lerp(SWant, SkySFrame, SkyK);
	// round 16 (TRICK_CAMERA_SPEC): the trick camera is chosen ONCE at the release frame (ChooseFlipView) and held on its world
	// azimuth; an obstruction on the held axis dollies in (TC11), under FlipDistMin it blends to the plain chase
	const bool bFlipCam = P.bFlip || P.bFlipSoon;
	if (bFlipCam && !bFlipWas)
	{
		ChooseFlipView(P, World);
		bFlipAbort = FlipTier >= 3;
		FlipDistNow = FlipDistSel; FlipDistV = 0.0;
	}
	if (!bFlipCam) { bFlipAbort = false; FlipTier = -1; FlipObsT = 0.0; }
	bFlipWas = bFlipCam;
	if (bFlipCam && !bFlipAbort && bChaseInit)
	{ // TC11: sweep hero chest -> the held spot; a hit dollies the camera in along the axis, never yaws / re-picks the side
		const double Ec = FMath::Asin(FMath::Clamp(FlipDrop / FMath::Max(1.0, FlipDistSel), 0.0, 0.6));
		const FVector Uc(FMath::Cos(FlipAz) * FMath::Cos(Ec), FMath::Sin(FlipAz) * FMath::Cos(Ec), -FMath::Sin(Ec));
		double HitD = 0.0, Goal = FlipDistSel;
		if (!World.SphereOverlaps(Chest, 0.22) && World.SphereSweep(Chest, Hero + Uc * FlipDistSel, 0.3, HitD)) Goal = FMath::Min(Goal, HitD - 0.25);
		// TC11: no room to keep the trick view (under FlipDistMin for FlipAbortGrace s running -- a trunk or a canopy edge passing the
		// axis for a few frames is dollied through, r16 probe: one tree at a 13 m flip ended the whole trick camera) -> plain chase over FlipOutT
		FlipObsT = Goal < FlipDistMin ? FlipObsT + Dt : 0.0;
		if (FlipObsT > FlipAbortGrace) bFlipAbort = true;
		else SD(FlipDistNow, FlipDistV, FMath::Max(Goal, 2.8), Goal < FlipDistNow ? FlipDollyInT : FlipDollyOutT, Dt);
	}
	{
		const bool bOn = bFlipCam && !bFlipAbort;
		if (bOn)
		{ // blend in: critically damped springs (smooth times FlipInT horizontal, FlipZInT height), continuous with a blend-out still running
			bFlipOutRun = false;
			SD(FlipK, FlipKV, 1.0, FlipInT, Dt);
			SD(FlipZK, FlipZKV, 1.0, FlipZInT, Dt);
		}
		else if (FlipK > 1e-4 || FlipZK > 1e-4)
		{ // blend out (TC10): a smoothstep over FlipOutT seconds from the weights at its start -- finite, so the next trick of a chain never
			// starts on the exponential tail of this one (a critically damped tail left 22 % of the old side in the next flip: a 19 deg jump)
			if (!bFlipOutRun) { bFlipOutRun = true; FlipOutClock = 0.0; FlipOutK0 = FlipK; FlipOutZ0 = FlipZK; }
			FlipOutClock += Dt;
			const double X = FMath::Clamp(FlipOutClock / FMath::Max(0.05, FlipOutT), 0.0, 1.0), S = X * X * (3.0 - 2.0 * X), Dv = 6.0 * X * (1.0 - X) / FMath::Max(0.05, FlipOutT);
			FlipK = FlipOutK0 * (1.0 - S); FlipKV = -FlipOutK0 * Dv;
			// the height weight holds FlipZHold s after the catch before it follows (TC6: the lens stays under the hips through the 0.5 s tail)
			const double Xz = FMath::Clamp((FlipOutClock - FlipZHold) / FMath::Max(0.05, FlipOutT), 0.0, 1.0), Sz = Xz * Xz * (3.0 - 2.0 * Xz);
			FlipZK = FlipOutZ0 * (1.0 - Sz); FlipZKV = Xz > 0.0 && Xz < 1.0 ? -FlipOutZ0 * 6.0 * Xz * (1.0 - Xz) / FMath::Max(0.05, FlipOutT) : 0.0;
		}
		else { bFlipOutRun = false; FlipK = FlipZK = 0.0; FlipKV = FlipZKV = 0.0; }
		FlipK = FMath::Clamp(FlipK, 0.0, 1.0);
		FlipZK = FMath::Clamp(FlipZK, 0.0, 1.0);
	}
	SWant = FMath::Lerp(SWant, FlipSFrame, FlipK);
	SWant = FMath::Clamp(SWant, 0.32, 0.72);
	// round 10 (critic r09: camera pop at b 0.000-0.017 s): the first composed frame starts AT its framing / attach targets
	// (FrameS was reset to 0.55 and sprang to ~0.40 over the first frames: 4 deg of pitch per frame)
	const bool bFirst = !bChaseInit;
	if (bFirst) { FrameS = SWant; FrameSV = 0.0; }
	SD(FrameS, FrameSV, SWant, 0.22, Dt);
	// ---- desired position: behind the (lagged) heading yaw, above the hero
	const FVector Back = -ForwardFlat(), Right = RightFlat();
	// round 07: 0.4 m closer while swinging / airborne (the higher round-07 camera left the hero < 160 px at the arc ends)
	const double AirClose = (bSwinging || bAir) ? SwingCloser : 0.0;
	const double BackDist = ChaseDist - AirClose + 1.3 * FMath::Max(0.0, KickK);
	const double OY = OccYawOff, OU = OccUp; // round 12: the flip orbit is placed below (searched view), not a fixed 40 deg
	const FVector BackR(Back.X * FMath::Cos(OY) - Back.Y * FMath::Sin(OY), Back.X * FMath::Sin(OY) + Back.Y * FMath::Cos(OY), 0);
	// round 09 (TRAVERSAL-SPEC T12/T17/T18): the camera slides AnchorShift m toward the ACTIVE anchor's side (kept through the
	// swing chain's short air phases) while still looking at the hero: the view runs 2-25 deg off the avenue axis and the near
	// facade on that side fills a side third, the hero stays centred
	if (bSwinging && P.bHasAnchor)
	{
		const double Lat = FVector::DotProduct(P.Anchor - Hero, Right);
		if (FMath::Abs(Lat) > 2.0) SideGoal = Lat > 0 ? 1.0 : -1.0;
	}
	if (bSwinging) { bInChain = true; ChainAirT = 0.0; }
	else if (P.Mode != EWebTravMode::Air) bInChain = false; // ground / wall / perch / zip end the chain
	else ChainAirT += Dt;
	if (P.bDive || ChainAirT > 0.8) bInChain = false;       // a long fall / dive is not the chain rhythm: centred again (aiming)
	SD(SideK, SideKV, bInChain ? SideGoal : 0.0, 0.3, Dt);
	FVector Desired = Hero + BackR * BackDist + Right * (0.3 + AnchorShift * SideK);
	double ZWant = Hero.Z + FMath::Lerp(ChaseHeight, -SkyCamBelow, SkyK) + OU;
	// round 16: trick camera spot = FlipDistNow m from the hero on the held world azimuth, FlipDrop m under his body centre
	// (the chase camera state -- Desired / CamXY / CamZ -- keeps running through the trick, so the blend-out has no jump; the trick spot is
	// blended onto its result in POLAR coordinates around the hero: azimuth, radius, height -- a Cartesian lerp of two spots 45 deg apart
	// swings the view ~2x faster than the spring asks for)
	const double FlipKs = Smooth(FlipK, 0.0, 1.0);
	FVector FlipSpot = Hero;
	{
		const double FlipElevNow = FMath::Asin(FMath::Clamp(FlipDrop / FMath::Max(1.0, FlipDistNow), 0.0, 0.6));
		FlipSpot = Hero + FVector(FMath::Cos(FlipAz) * FMath::Cos(FlipElevNow), FMath::Sin(FlipAz) * FMath::Cos(FlipElevNow), -FMath::Sin(FlipElevNow)) * FlipDistNow;
	}
	if (!bChaseInit)
	{
		bChaseInit = true;
		CamXY = FVector(Desired.X, Desired.Y, 0); CamXYV = FVector::ZeroVector; CamZ = ZWant; CamZV = 0;
	}
	// horizontal lag, then hold 4..6.5 m (plus kick) behind; vertical lag, then hold 0.8..4 m (+ occlusion lift) above
	SDV(CamXY, CamXYV, FVector(Desired.X, Desired.Y, 0), 0.07, Dt);
	FVector HD = FVector(CamXY.X - Hero.X, CamXY.Y - Hero.Y, 0);
	const double HL = HD.Size();
	const double MaxH = 5.0 - AirClose + 1.3 * FMath::Max(0.0, KickK), MinH = 3.5 - AirClose;
	if (HL < 1e-3) HD = BackR * MinH; else if (HL < MinH) HD *= MinH / HL; else if (HL > MaxH) HD *= MaxH / HL;
	CamXY = FVector(Hero.X + HD.X, Hero.Y + HD.Y, 0);
	SD(CamZ, CamZV, ZWant, 0.05, Dt);
	CamZ = FMath::Clamp(CamZ, Hero.Z + FMath::Lerp(CamZMin, -SkyCamBelow - 0.3, SkyK) + OU, Hero.Z + CamZMax + OU); // round 07: 0.7..1.8 -> 1.2..2.6
	FVector Cam(CamXY.X, CamXY.Y, CamZ);
	if (FlipK > 1e-4 || FlipZK > 1e-4)
	{ // the trick camera: polar blend (azimuth / radius about the hero by FlipK, height by FlipZK) of the chase camera onto the held spot
		const double DxC = Cam.X - Hero.X, DyC = Cam.Y - Hero.Y, DxF = FlipSpot.X - Hero.X, DyF = FlipSpot.Y - Hero.Y;
		const double AC = FMath::Atan2(DyC, DxC), AF = FMath::Atan2(DyF, DxF);
		const double RC = FMath::Sqrt(DxC * DxC + DyC * DyC), RF = FMath::Sqrt(DxF * DxF + DyF * DyF);
		const double AB = AC + WrapA(AF - AC) * FlipK, RB = FMath::Lerp(RC, RF, FlipK);
		Cam = FVector(Hero.X + RB * FMath::Cos(AB), Hero.Y + RB * FMath::Sin(AB), Hero.Z + FMath::Lerp(Cam.Z - Hero.Z, FlipSpot.Z - Hero.Z, FlipZK));
	}
	// ---- collision: sphere-sweep from the chest; if the clear distance would drop under MinHeroDist, search raised /
	// rotated positions and move there smoothly (held ~1 s so the camera does not flicker)
	bool bNoSweep = false; // round 14: set below when the hero himself is inside geometry
	auto ClearFrom = [&](const FVector& From, const FVector& To, FVector& Out) -> double
	{
		const FVector D = To - From;
		const double L = D.Size();
		double HitD = 0;
		if (!bNoSweep && L > 1e-3 && World.SphereSweep(From, To, 0.22, HitD)) { Out = From + D / L * FMath::Max(0.0, HitD - 0.12); return FMath::Max(0.0, HitD - 0.12); }
		Out = To;
		return L;
	};
	// sweep origin: the chest, or (hero against / clipping a surface) the first clear point 1-2.5 m above it
	FVector From = Chest;
	bool bFromOk = false;
	for (double Lift : { 0.0, 1.0, 1.8, 2.6 })
	{
		From = Chest + FVector(0, 0, Lift);
		if (!World.SphereOverlaps(From, 0.22)) { bFromOk = true; break; }
	}
	// round 14 (probe f3 4.8-5.6 s: the hero swings through a street-tree canopy at a swing bottom; every sweep origin overlaps the
	// canopy): the r13 hold kept the camera's offset AND rotation for 0.8 s (hero slid to 0.90 of the frame, pitch 28 deg down, camera
	// 49 frames inside the foliage). Now the frame composes normally but WITHOUT the collision sweeps (the hero is inside geometry,
	// so a sweep from him cannot tell a clear spot): the chase spot behind him is taken as it is.
	bNoSweep = !bFromOk && bChaseInit && !CamPos.IsZero();
	if (bNoSweep) From = Chest;
	auto ClearTo = [&](const FVector& To, FVector& Out) -> double
	{
		ClearFrom(From, To, Out);
		return FVector::Dist(Out, Hero);
	};
	// orbit candidates relative to the current heading: yaw offset DYw (rad) and extra height Up (m)
	auto Candidate = [&](double DYw, double Up)
	{
		const FVector B2(Back.X * FMath::Cos(DYw) - Back.Y * FMath::Sin(DYw), Back.X * FMath::Sin(DYw) + Back.Y * FMath::Cos(DYw), 0);
		return Hero + B2 * ChaseDist + FVector(0, 0, ChaseHeight + Up);
	};
	FVector Tmp;
	const double DefClear = ClearTo(Candidate(0, 0), Tmp);
	const double DefLen = FVector::Dist(Candidate(0, 0), Hero); // unobstructed distance of the default spot
	if (DefClear >= DefLen - 0.3) { OccYawGoal = 0; OccUpGoal = 0; }
	else if ((OccYawGoal == 0 && OccUpGoal == 0) || ClearTo(Candidate(OccYawGoal, OccUpGoal), Tmp) < DefLen - 0.8)
	{ // default spot blocked and no clear orbit held: search raised / rotated spots
		double BestC = -1e9, BY = 0, BU = 0;
		for (double Up : { 0.0, 2.0, 4.0, 6.0, 9.0 })
		{
			for (double DYw : { 0.0, 0.6, -0.6, 1.1, -1.1, 1.6, -1.6, 2.2, -2.2 })
			{
				const double C2 = ClearTo(Candidate(DYw, Up), Tmp);
				const double Score = FMath::Min(C2, 6.0) - 0.8 * FMath::Abs(DYw) - 0.25 * Up - (FMath::Abs(DYw - OccYawGoal) + FMath::Abs(Up - OccUpGoal) * 0.2) * 0.3;
				if (C2 >= DefLen - 0.8 && Score > BestC) { BestC = Score; BY = DYw; BU = Up; }
			}
		}
		if (BestC > -1e8) { OccYawGoal = BY; OccUpGoal = BU; }
	}
	SD(OccYawOff, OccYawOffV, OccYawGoal, 0.3, Dt);
	SD(OccUp, OccUpV, OccUpGoal, 0.3, Dt);
	FVector Got;
	ClearTo(Cam, Got);
	// round 15 (r14 f3 4.6-5.5 s: 43 frames with the lens inside a street-tree canopy while the hero swung through it): with the hero
	// inside geometry the spot is not swept, so lift it (then pull it toward the hero) until the lens is out of the foliage
	if (bNoSweep && World.SphereOverlaps(Got, 0.25))
	{
		bool bOut = false;
		for (double Up : { 0.8, 1.6, 2.4, 3.2, 4.0, 5.0 })
		{
			const FVector C2 = Got + FVector(0, 0, Up);
			if (!World.SphereOverlaps(C2, 0.25)) { Got = C2; bOut = true; break; }
		}
		if (!bOut)
		{
			for (double K2 : { 0.8, 0.6, 1.3, 1.6 })
			{
				const FVector C2 = Hero + (Got - Hero) * K2;
				if (!World.SphereOverlaps(C2, 0.25)) { Got = C2; break; }
			}
		}
	}
	// (round 12: the flip spot sits FlipDist out by design — the 3 m cut fired every frame and snapped to the chase orbit)
	// round 13 (critic r12: this "too close: cut to the clear orbit" rule re-armed while the flip camera blended out -> one-frame 43 deg /
	// 60 deg / 3.1 m cuts at f1 6.30 s and f4 8.58 s, then oscillated for 15 frames): no cut. The orbit search above already springs the
	// camera to a clear spot (OccYawOff / OccUp, 0.3 s); until it gets there the swept position is used, and MinHeroDist below keeps it
	// off the hero. The output slew limit (Update) bounds every frame.
	Cam = Got;
	// never closer than MinHeroDist: if the geometry forces it, rise straight up over the hero instead
	if (FVector::Dist(Cam, Hero) < MinHeroDist)
	{
		FVector Up2 = Hero + FVector(0, 0, MinHeroDist + 0.5) + BackR * 1.0;
		FVector G3;
		ClearTo(Up2, G3);
		if (FVector::Dist(G3, Hero) > FVector::Dist(Cam, Hero)) Cam = G3;
	}
	// ---- round 08 (critic r07: camera hugging / entering facades): keep the camera off the walls sideways — a spring toward
	// CamWallSoft m of clearance (toward the canyon centre, not along the wall) and a hard CamWallHard m minimum
	{
		const FVector RtC = RightFlat();
		double DR = 1e9, DL = 1e9;
		FTravHit WH;
		if (World.Raycast(Cam, RtC, CamWallSoft + 1.0, WH) && FMath::Abs(WH.Normal.Z) < 0.5) DR = WH.Distance;
		if (World.Raycast(Cam, -RtC, CamWallSoft + 1.0, WH) && FMath::Abs(WH.Normal.Z) < 0.5) DL = WH.Distance;
		double Want = 0.0;
		if (DR < CamWallSoft) Want -= CamWallSoft - DR;
		if (DL < CamWallSoft) Want += CamWallSoft - DL;
		SD(WallPush, WallPushV, Want, 0.15, Dt);
		double Push = WallPush;
		if (DR < CamWallHard) Push = FMath::Min(Push, -(CamWallHard - DR));
		if (DL < CamWallHard) Push = FMath::Max(Push, CamWallHard - DL);
		Push *= 1.0 - FlipKs; // round 16 (TC11): the trick camera never yaws round the hero -- the dolly-in along the held axis replaces the push
		if (FMath::Abs(Push) > 1e-3)
		{
			FVector Moved;
			ClearFrom(Cam, Cam + RtC * Push, Moved);
			Cam = Moved;
			FVector Seen;
			if (ClearTo(Cam, Seen) < FVector::Dist(Cam, Hero) - 0.3) Cam = Seen; // keep the hero in sight
		}
	}
	const double GY = World.GroundHeight(Cam.X, Cam.Y, Cam.Z + 0.3) + 0.4;
	if (Cam.Z < GY) Cam.Z = GY;
	// ---- round 06: wall-run camera, blended in / out with a spring (held through the rising half of the top-out, so the
	// hero clears the roof edge in frame, then handed back to the chase camera which comes up over the edge)
	{
		const bool bOnWall = P.Mode == EWebTravMode::Wall;
		const bool bWant = bOnWall || (P.Sub == N_topOut && P.Vel.Z > 0.0);
		SD(WallK, WallKV, bWant ? 1.0 : 0.0, bWant ? 0.16 : 0.22, Dt);
		WallK = FMath::Clamp(WallK, 0.0, 1.0);
		if (bOnWall) { WallHeroXY = FVector(Hero.X, Hero.Y, 0); bWallXY = true; }
		if (WallK > 0.001)
		{
			FVector N(P.WallNormal.X, P.WallNormal.Y, 0.0);
			N = N.SizeSquared() > 0.01 ? N.GetSafeNormal() : -ForwardFlat();
			const FVector Base = (bOnWall || !bWallXY) ? Hero : FVector(WallHeroXY.X, WallHeroXY.Y, Hero.Z);
			const double Floor = World.GroundHeight(Base.X + N.X * WallCamOut, Base.Y + N.Y * WallCamOut, Hero.Z + 0.5);
			const double WZ = FMath::Max(Hero.Z - WallCamBelow, Floor + 0.6);
			const double Dz = Hero.Z - WZ;
			const double Out = FMath::Max(WallCamOut, FMath::Sqrt(FMath::Max(0.0, WallCamDist * WallCamDist - Dz * Dz)));
			FVector WallCam(Base.X + N.X * Out, Base.Y + N.Y * Out, WZ), WallClear;
			ClearFrom(From, WallCam, WallClear);
			Cam = FMath::Lerp(Cam, WallClear, Smooth(WallK, 0.0, 1.0));
		}
	}
	CamPos = Cam;
	LastComposeHero = Hero; bHaveComposeHero = true;
	HeroDist = FVector::Dist(CamPos, Hero);
	bCamInGeometry = World.SphereOverlaps(CamPos, 0.15);
	// ---- orientation: yaw toward the hero; pitch puts the hero's centre at FrameS on screen (user look adds an offset)
	const FVector ToHero = Hero - CamPos;
	const double HLen = FMath::Max(0.1, FVector2D(ToHero.X, ToHero.Y).Size());
	const double DownToHero = FMath::Atan2(-ToHero.Z, HLen);
	UserPitch = Damp(UserPitch, 0.0, LastLook > 1.5 ? 1.5 : 0.0, Dt);
	const double Delta = FMath::Atan((FrameS - 0.5) * 2.0 * TanHalfV);
	// (round 06: on the wall the lower clamp opens up to an 80 deg look UP the facade)
	// (round 12: during a flip the look-up limit follows the searched elevation: + 20 deg of framing, <= 75)
	// (round 14: capped at FlipPitchUpMax -- the r13 look-up reached 53 deg)
	const double FlipUpDeg = FlipPitchUpMax;
	double PitchDown = FMath::Clamp(DownToHero - Delta + UserPitch, FMath::DegreesToRadians(FMath::Lerp(FMath::Lerp(FMath::Lerp(PitchDownMin, -SkyPitchUp, SkyK), -FlipUpDeg, FlipK), -WallMaxUpDeg, Smooth(WallK, 0.0, 1.0))),
		// round 06: when collision lifts the camera high over the hero (roof edges), look down far enough that his centre
		// stays at or above 0.62 of the frame height (the fixed 22 deg limit dropped him off the bottom edge)
		FMath::Max(FMath::DegreesToRadians(22.0), DownToHero - FMath::Atan((0.62 - 0.5) * 2.0 * TanHalfV)));
	// round 05: at each web attach, look up enough that the anchor on the facade (and a band of sky) is on screen for
	// ~0.7 s, then settle back (spring); the hero stays in frame below
	double LookWant = 0.0, FovWant = 0.0;
	if (bSwinging && P.bHasAnchor && P.SwingT < 0.5)
	{
		const FVector ToA = P.Anchor - CamPos;
		const double UpToAnchor = FMath::Atan2(ToA.Z, FMath::Max(0.1, FVector2D(ToA.X, ToA.Y).Size()));
		const double TopM = FMath::DegreesToRadians(4.0), BotM = FMath::DegreesToRadians(12.0); // round 07: 8 -> 12
		// if anchor (top) and hero (bottom) cannot both fit, widen the view for the attach beat (<= 20 deg)
		const double Span = UpToAnchor + DownToHero + TopM + BotM;
		FovWant = FMath::Clamp(Span - VFov, 0.0, FMath::DegreesToRadians(AttachFovMax)); // round 08: 26 -> 10 deg (92-95 deg fish-eye shrank the hero)
		const double Half = (VFov + FovWant) * 0.5;
		const double Need = UpToAnchor - (Half - TopM);             // pitch-up that puts it TopM inside the top
		// round 10 (TRAVERSAL-SPEC T5 voids anchor-in-frame; T10 hero centre y <= 0.70, critic r09 cy p95 .72): the look-up stops
		// where the hero centre reaches AttachMaxS of the frame height (was: hero 12 deg inside the bottom edge -> cy up to .87)
		(void)BotM;
		const double HeroLimit = FMath::Atan((AttachMaxS - 0.5) * 2.0 * FMath::Tan(Half)) - DownToHero;
		LookWant = FMath::Max(0.0, FMath::Min(Need + PitchDown, HeroLimit + PitchDown));
		// round 07: the new swings open with a steep swoop (up to 40 m/s down) — the look-up fades out as he falls faster so
		// the hero does not drop off the bottom edge
		LookWant *= FMath::Clamp(1.0 - (-P.Vel.Z - 8.0) / 14.0, 0.0, 1.0);
	}
	// horizontal: turn toward an anchor that is outside the sides (hero kept 10 deg inside the opposite edge)
	double YawWant = 0.0;
	const double ToHeroYaw = FMath::Atan2(ToHero.Y, ToHero.X);
	if (bSwinging && P.bHasAnchor && P.SwingT < 0.5)
	{
		const FVector ToA = P.Anchor - CamPos;
		const double HalfH = FMath::Atan(FMath::Tan((VFov + FovWant) * 0.5) * 16.0 / 9.0);
		const double DA = FMath::Atan2(FMath::Sin(FMath::Atan2(ToA.Y, ToA.X) - ToHeroYaw), FMath::Cos(FMath::Atan2(ToA.Y, ToA.X) - ToHeroYaw));
		const double Over = FMath::Abs(DA) - (HalfH - FMath::DegreesToRadians(5.0));
		if (Over > 0) YawWant = FMath::Sign(DA) * FMath::Min(Over, HalfH - FMath::DegreesToRadians(10.0));
	}
	// round 07: gentler, capped turn toward an off-screen anchor (the 0.035 s spring whipped the view ~45 deg in 0.1 s)
	YawWant = FMath::Clamp(YawWant, -FMath::DegreesToRadians(25.0), FMath::DegreesToRadians(25.0));
	YawWant *= 1.0 - FlipKs; // round 16 (TC3): no attach yaw beat while the trick camera is in -- the view turns only with the blend-out
	if (bFirst) { AttachYaw = YawWant; AttachLook = LookWant; AttachFov = FovWant; AttachYawV = AttachLookV = AttachFovV = 0.0; }
	// round 13: a web caught out of a flip (flip camera still blending out) turns the view more gently (per-frame yaw budget)
	const double AttachSt = P.SwingT < 0.5 ? (FlipK > 0.05 ? 0.25 : 0.12) : 0.3;
	SD(AttachYaw, AttachYawV, YawWant, AttachSt, Dt);
	// round 10 (critic r09: camera pop at b 0.000-0.017 s, a web attached on the first frame): 0.035 s -> 0.12 s springs
	SD(AttachLook, AttachLookV, LookWant, AttachSt, Dt);
	SD(AttachFov, AttachFovV, FovWant, AttachSt, Dt);
	PitchDown -= AttachLook;
	// ---- round 14 (critic r13: "within 0.5 s of attach return the pitch to 4-12 deg down"; r13 f4 medians -1..+9 deg UP 0.5-1.0 s after
	// the attaches: the attach look-up beat + the arc-bottom framing looked up): from SettleT0 to SettleT1 s after a web attaches the
	// pitch is pulled into the settle band, as long as the hero stays inside 0.18..0.82 of the frame height
	{
		const double WallW = Smooth(WallK, 0.0, 1.0);
		if (bSwinging && P.SwingT < 90.0)
		{
			const double Sk = Smooth(P.SwingT, SettleT0, SettleT1) * (1.0 - WallW);
			if (Sk > 0.0)
			{
				const double Keep = FMath::Atan(0.64 * TanHalfV);
				const double Lo = FMath::Min(FMath::DegreesToRadians(SettleDownMin), DownToHero + Keep);
				const double Hi = FMath::Max(FMath::DegreesToRadians(SettleDownMax), DownToHero - Keep);
				PitchDown = FMath::Lerp(PitchDown, FMath::Clamp(PitchDown, Lo, Hi), Sk);
			}
		}
		// hard look-up cap for every view but the wall-run camera (critic r13 test: pitch never > 30 deg up)
		// (round 15: the flip view is capped at FlipPitchUpMax from FlipK 0.3 on -- also while it blends out -- the wall camera at WallMaxUpDeg)
		CapUpDeg = FMath::Lerp(FMath::Lerp(MaxLookUpDeg, FlipPitchUpMax, Smooth(FlipK, 0.0, 0.3)), WallMaxUpDeg, WallW);
		PitchDown = FMath::Max(PitchDown, -FMath::DegreesToRadians(CapUpDeg));
	}
	Pitch = PitchDown; // keep the orbit state coherent for Forward()
	// (round 09: the hero stays centred horizontally — TRAVERSAL-SPEC T9; the off-axis look comes from the sideways slide)
	// (round 16, TC7: a small lead-room yaw bias toward the hero's travel -- the hero sits on the trailing side of the frame, x ~ .45-.55)
	CamRot = FRotator(FMath::RadiansToDegrees(-PitchDown), FMath::RadiansToDegrees(ToHeroYaw + AttachYaw - FlipSide * FMath::DegreesToRadians(FlipLeadDeg) * FlipKs), 0);
}

// round 16 (TRICK_CAMERA_SPEC TC1 / TC2): choose the trick camera's view ONCE, at the release frame; it is never re-searched.
// Candidates: yaw offsets FlipYawMin..FlipYawMax deg from the travel-behind direction on both sides, FlipDist m out, FlipDrop m under the
// hero. Order: (1) obstruction -- the spot must be sweep-reachable from the hero with FlipWallMargin m free beyond it and a clear path
// FlipAheadT s along the travel; (2) sun -- the view at least SunMinDeg from the sun; (3) open space (lateral free distance, background
// sky share, a graded clear-path time, no glare facade). A side that passes (1) wins over one that fails it, even if it fails (2). If
// nothing passes at FlipDist the same yaws are tried pulled in (TC11) down to FlipDistMin, and if that fails too the plain chase is used
// (Tier 3) -- never a side-on orbit.
void FWebTravCamera::ChooseFlipView(const FTravCamInput& P, const FWebTravWorld& World)
{
	const FVector Hero = P.Pos;
	const FVector VF(P.Vel.X, P.Vel.Y, 0.0);
	const double HS = VF.Size();
	const double Head = HS > 1.5 ? FMath::Atan2(VF.Y, VF.X) : Yaw;   // travel heading (rad)
	const double BackAz = Head + PI;
	double CurOff = 0.0; // the side the chase camera is on at the release (a tie-break: the blend-in moves the least)
	{
		const FVector Off = CamPos - Hero;
		if (bChaseInit && FVector2D(Off.X, Off.Y).Size() > 0.2) CurOff = WrapA(FMath::Atan2(Off.Y, Off.X) - BackAz);
	}
	static const double RingDeg[][2] = { {0, 11}, {0, -11}, {8, 0}, {-8, 0}, {8, 11}, {-8, 11}, {8, -11}, {-8, -11},
		{8, 5}, {-8, 5}, {8, -5}, {-8, -5}, {4, 11}, {-4, 11}, {4, -11}, {-4, -11} };
	struct FCand { double Az = 0, Off = 0, Rad = 0, Open = 0, Sky = 0, Glare = 0, Sun = 180, ClearT = 0, Cost = 0; int32 Side = 1, Tier = 3, Why = 0; };
	auto Eval = [&](double OffDeg, int32 Side, double Rad, FCand& C) -> bool // true = passes (1) obstruction
	{
		C.Side = Side; C.Off = OffDeg; C.Rad = Rad;
		C.Az = BackAz + Side * FMath::DegreesToRadians(OffDeg);
		const double E = FMath::Asin(FMath::Clamp(FlipDrop / FMath::Max(1.0, Rad), 0.0, 0.6));
		const FVector ToCam(FMath::Cos(C.Az) * FMath::Cos(E), FMath::Sin(C.Az) * FMath::Cos(E), -FMath::Sin(E));
		const FVector CamP = Hero + ToCam * Rad;
		double HitD = 0.0;
		if (World.SphereSweep(Hero, CamP, 0.3, HitD)) { C.Why = 1; return false; }
		if (World.SphereSweep(CamP, CamP + ToCam * FlipWallMargin, 0.3, HitD)) { C.Why = 2; return false; }
		if (HS > 1.0 && World.SphereSweep(CamP, CamP + VF * FlipAheadT, 0.3, HitD)) { C.Why = 3; return false; }
		if (CamP.Z < World.GroundHeight(CamP.X, CamP.Y, CamP.Z + 0.5) + 0.5) { C.Why = 4; return false; }
		// graded clearance: how far along the predicted travel (ballistic, 0.25 s steps) the camera spot stays clear
		{
			FVector Prev = CamP;
			C.ClearT = 1.5;
			for (int32 K = 1; K <= 6; ++K)
			{
				const double Tt = 0.25 * K;
				const FVector Nx = CamP + VF * Tt + FVector(0, 0, P.Vel.Z * Tt - 3.0 * Tt * Tt);
				if (World.SphereSweep(Prev, Nx, 0.3, HitD) || World.SphereOverlaps(Nx, 0.3)) { C.ClearT = 0.25 * (K - 1); break; }
				Prev = Nx;
			}
		}
		// open space: lateral free distance from the hero toward the camera side, background sky share, glare facades
		{
			FTravHit H;
			const FVector HDir(ToCam.X, ToCam.Y, 0.0);
			C.Open = World.Raycast(Hero, HDir.GetSafeNormal(), 30.0, H) ? FMath::Min(30.0, H.Distance) / 30.0 : 1.0;
			const FVector D = -ToCam;
			const FVector Rt = FVector::CrossProduct(FVector::UpVector, D).GetSafeNormal();
			const FVector Up = FVector::CrossProduct(D, Rt).GetSafeNormal();
			int32 Free = 0, N = 0, Glr = 0;
			for (const auto& RD : RingDeg)
			{
				const FVector Dir = (D + Rt * FMath::Tan(FMath::DegreesToRadians(RD[0])) + Up * FMath::Tan(FMath::DegreesToRadians(RD[1]))).GetSafeNormal();
				FTravHit Hh;
				++N;
				if (!World.Raycast(CamP + Dir * (Rad + 0.6), Dir, 900.0, Hh)) ++Free;
				else if (bHaveSun && FMath::Abs(Hh.Normal.Z) < 0.5)
				{ // a background facade whose mirror direction lies within GlareDeg of the sun mirrors it into the lens (rendered r14 f4 9.85 s)
					const FVector Rf = Dir - 2.0 * FVector::DotProduct(Dir, Hh.Normal) * Hh.Normal;
					if (FVector::DotProduct(Rf.GetSafeNormal(), SunDir) > FMath::Cos(FMath::DegreesToRadians(GlareDeg))) ++Glr;
				}
			}
			C.Sky = double(Free) / double(FMath::Max(1, N));
			C.Glare = double(Glr) / double(FMath::Max(1, N));
			C.Sun = bHaveSun ? FMath::RadiansToDegrees(FMath::Acos(FMath::Clamp(FVector::DotProduct(D, SunDir), -1.0, 1.0))) : 180.0;
		}
		C.Tier = C.Sun >= SunMinDeg ? 0 : 1;
		C.Cost = 2.0 * (1.0 - C.Open) + 1.5 * (1.0 - C.Sky) + 4.0 * (1.0 - C.ClearT / 1.5) + GlareW * C.Glare
			+ 2.0 * FMath::Max(0.0, SunPrefDeg - C.Sun) / 40.0
			+ 0.6 * FMath::Abs(OffDeg - FlipPrefYaw) / 5.0 + (FMath::Sign(CurOff) != double(Side) ? 0.25 : 0.0);
		return true;
	};
	static const double OffsDeg[] = { 40.0, 45.0, 50.0, 55.0 };
	FCand Best; bool bHave = false;
	FString Log;
	int32 BestTier = 99;
	for (int32 Stage = 0; Stage < 4 && !bHave; ++Stage)
	{
		const double Rd = Stage == 0 ? FlipDist : FMath::Lerp(FlipDist, FlipDistMin, double(Stage) / 3.0);
		for (double O : OffsDeg)
		{
			if (O < FlipYawMin - 1e-3 || O > FlipYawMax + 1e-3) continue;
			for (int32 Side : { 1, -1 })
			{
				FCand C;
				if (!Eval(O, Side, Rd, C)) { Log += FString::Printf(TEXT(" [%+.0f@%.1f fail%d]"), Side * O, Rd, C.Why); continue; }
				Log += FString::Printf(TEXT(" [%+.0f@%.1f sun%.0f open%.2f sky%.2f clr%.2f cost%.2f]"), Side * O, Rd, C.Sun, C.Open, C.Sky, C.ClearT, C.Cost);
				if (Stage > 0) { C.Cost += C.Sun >= SunMinDeg ? 0.0 : 100.0; C.Tier = 2; } // pulled in along the same yaw (TC11): tier 2, sun-ok first
				if (!bHave || C.Tier < BestTier || (C.Tier == BestTier && C.Cost < Best.Cost)) { Best = C; BestTier = C.Tier; bHave = true; }
			}
		}
	}
	UE_LOG(LogWebHomage, Display, TEXT("WH_TRAV trick camera choice at hero (%.1f, %.1f, %.1f) heading %.0f:%s"), Hero.X, Hero.Y, Hero.Z, FMath::RadiansToDegrees(Head), *Log);
	if (!bHave) { FlipTier = 3; FlipDistSel = FlipDist; FlipSkyShare = -1.0; return; }
	FlipAz = Best.Az; FlipSide = double(Best.Side); FlipOffDeg = Best.Side * Best.Off; FlipDistSel = Best.Rad; FlipTier = Best.Tier;
	FlipSkyShare = Best.Sky; FlipSunDeg = Best.Sun; FlipGlare = Best.Glare;
}

bool FWebTravCamera::SetTune(const FString& Name, double V)
{
	struct FT { const TCHAR* N; double* P; };
	const FT Tab[] = { {TEXT("SunMinDeg"), &SunMinDeg}, {TEXT("SunPrefDeg"), &SunPrefDeg}, {TEXT("FlipDist"), &FlipDist}, {TEXT("FlipDistMin"), &FlipDistMin},
		{TEXT("FlipDrop"), &FlipDrop}, {TEXT("FlipYawMin"), &FlipYawMin}, {TEXT("FlipYawMax"), &FlipYawMax}, {TEXT("FlipPrefYaw"), &FlipPrefYaw},
		{TEXT("FlipLeadDeg"), &FlipLeadDeg}, {TEXT("FlipSFrame"), &FlipSFrame}, {TEXT("FlipPitchUpMax"), &FlipPitchUpMax}, {TEXT("MaxLookUpDeg"), &MaxLookUpDeg},
		{TEXT("FlipInT"), &FlipInT}, {TEXT("FlipOutT"), &FlipOutT}, {TEXT("FlipZInT"), &FlipZInT}, {TEXT("FlipDollyInT"), &FlipDollyInT}, {TEXT("FlipDollyOutT"), &FlipDollyOutT},
		{TEXT("FlipWallMargin"), &FlipWallMargin}, {TEXT("FlipAheadT"), &FlipAheadT},
		{TEXT("WallCamBelow"), &WallCamBelow}, {TEXT("WallCamOut"), &WallCamOut}, {TEXT("WallCamDist"), &WallCamDist},
		{TEXT("WallFrameS"), &WallFrameS}, {TEXT("WallMaxUpDeg"), &WallMaxUpDeg}, {TEXT("SettleDownMin"), &SettleDownMin},
		{TEXT("SettleDownMax"), &SettleDownMax}, {TEXT("GlareDeg"), &GlareDeg}, {TEXT("GlareW"), &GlareW} };
	for (const FT& T : Tab) if (Name == T.N) { *T.P = V; return true; }
	return false;
}
