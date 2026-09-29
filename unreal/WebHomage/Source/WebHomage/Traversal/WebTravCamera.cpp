// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Traversal/WebTravCamera.h"
#include "Traversal/WebTravWorld.h"

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
	const double WantRoll = FMath::Clamp(-YawRate * 0.04, -0.09, 0.09) - BankS * 0.05;
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
	// speed motion blur: none on foot / walls, ramps in over fast swings / dives / zips
	const bool bGroundish = M == EWebTravMode::Ground || M == EWebTravMode::Land || M == EWebTravMode::Wall;
	const double MbTarget = (bGroundish ? 0.45 : bDive ? 1.6 : 1.0) * Smooth(Speed, 6, 36) * 1.1;
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
	SWant = FMath::Clamp(SWant, 0.32, 0.72);
	SD(FrameS, FrameSV, SWant, 0.22, Dt);
	// ---- desired position: behind the (lagged) heading yaw, above the hero
	const FVector Back = -ForwardFlat(), Right = RightFlat();
	const double BackDist = ChaseDist + 1.3 * FMath::Max(0.0, KickK);
	const double OY = OccYawOff, OU = OccUp;
	const FVector BackR(Back.X * FMath::Cos(OY) - Back.Y * FMath::Sin(OY), Back.X * FMath::Sin(OY) + Back.Y * FMath::Cos(OY), 0);
	FVector Desired = Hero + BackR * BackDist + Right * 0.3;
	const double ZWant = Hero.Z + ChaseHeight + OU;
	if (!bChaseInit)
	{
		bChaseInit = true;
		CamXY = FVector(Desired.X, Desired.Y, 0); CamXYV = FVector::ZeroVector; CamZ = ZWant; CamZV = 0;
	}
	// horizontal lag, then hold 4..6.5 m (plus kick) behind; vertical lag, then hold 0.8..4 m (+ occlusion lift) above
	SDV(CamXY, CamXYV, FVector(Desired.X, Desired.Y, 0), 0.07, Dt);
	FVector HD = FVector(CamXY.X - Hero.X, CamXY.Y - Hero.Y, 0);
	const double HL = HD.Size();
	const double MaxH = 5.0 + 1.3 * FMath::Max(0.0, KickK);
	if (HL < 1e-3) HD = BackR * 3.5; else if (HL < 3.5) HD *= 3.5 / HL; else if (HL > MaxH) HD *= MaxH / HL;
	CamXY = FVector(Hero.X + HD.X, Hero.Y + HD.Y, 0);
	SD(CamZ, CamZV, ZWant, 0.05, Dt);
	CamZ = FMath::Clamp(CamZ, Hero.Z + 0.7 + OU, Hero.Z + 1.8 + OU);
	FVector Cam(CamXY.X, CamXY.Y, CamZ);
	// ---- collision: sphere-sweep from the chest; if the clear distance would drop under MinHeroDist, search raised /
	// rotated positions and move there smoothly (held ~1 s so the camera does not flicker)
	auto ClearFrom = [&](const FVector& From, const FVector& To, FVector& Out) -> double
	{
		const FVector D = To - From;
		const double L = D.Size();
		double HitD = 0;
		if (L > 1e-3 && World.SphereSweep(From, To, 0.22, HitD)) { Out = From + D / L * FMath::Max(0.0, HitD - 0.12); return FMath::Max(0.0, HitD - 0.12); }
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
	if (!bFromOk && bChaseInit && !CamPos.IsZero())
	{ // the hero himself is inside geometry this frame (e.g. clipping a facade at a zip arrival): hold the last view
		HeroDist = FVector::Dist(CamPos, Hero);
		bCamInGeometry = World.SphereOverlaps(CamPos, 0.15);
		return;
	}
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
	if (FVector::Dist(Got, Hero) < 3.0)
	{ // too close even after easing: cut to the chosen clear orbit instead of passing through the hero
		OccYawOff = OccYawGoal; OccUp = OccUpGoal; OccYawOffV = OccUpV = 0;
		ClearTo(Candidate(OccYawGoal, OccUpGoal), Got);
		CamXY = FVector(Got.X, Got.Y, 0); CamXYV = FVector::ZeroVector; CamZ = Got.Z; CamZV = 0;
	}
	Cam = Got;
	// never closer than MinHeroDist: if the geometry forces it, rise straight up over the hero instead
	if (FVector::Dist(Cam, Hero) < MinHeroDist)
	{
		FVector Up2 = Hero + FVector(0, 0, MinHeroDist + 0.5) + BackR * 1.0;
		FVector G3;
		ClearTo(Up2, G3);
		if (FVector::Dist(G3, Hero) > FVector::Dist(Cam, Hero)) Cam = G3;
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
	HeroDist = FVector::Dist(CamPos, Hero);
	bCamInGeometry = World.SphereOverlaps(CamPos, 0.15);
	// ---- orientation: yaw toward the hero; pitch puts the hero's centre at FrameS on screen (user look adds an offset)
	const FVector ToHero = Hero - CamPos;
	const double HLen = FMath::Max(0.1, FVector2D(ToHero.X, ToHero.Y).Size());
	const double DownToHero = FMath::Atan2(-ToHero.Z, HLen);
	UserPitch = Damp(UserPitch, 0.0, LastLook > 1.5 ? 1.5 : 0.0, Dt);
	const double Delta = FMath::Atan((FrameS - 0.5) * 2.0 * TanHalfV);
	// (round 06: on the wall the lower clamp opens up to an 80 deg look UP the facade)
	double PitchDown = FMath::Clamp(DownToHero - Delta + UserPitch, FMath::DegreesToRadians(FMath::Lerp(5.0, -80.0, Smooth(WallK, 0.0, 1.0))),
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
		const double TopM = FMath::DegreesToRadians(4.0), BotM = FMath::DegreesToRadians(8.0);
		// if anchor (top) and hero (bottom) cannot both fit, widen the view for the attach beat (<= 20 deg)
		const double Span = UpToAnchor + DownToHero + TopM + BotM;
		FovWant = FMath::Clamp(Span - VFov, 0.0, FMath::DegreesToRadians(26.0));
		const double Half = (VFov + FovWant) * 0.5;
		const double Need = UpToAnchor - (Half - TopM);             // pitch-up that puts it TopM inside the top
		const double HeroLimit = (Half - BotM) - DownToHero;        // keep the hero BotM inside the bottom
		LookWant = FMath::Max(0.0, FMath::Min(Need + PitchDown, HeroLimit + PitchDown));
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
	SD(AttachYaw, AttachYawV, YawWant, P.SwingT < 0.5 ? 0.035 : 0.3, Dt);
	SD(AttachLook, AttachLookV, LookWant, P.SwingT < 0.5 ? 0.035 : 0.3, Dt);
	SD(AttachFov, AttachFovV, FovWant, P.SwingT < 0.5 ? 0.035 : 0.3, Dt);
	PitchDown -= AttachLook;
	Pitch = PitchDown; // keep the orbit state coherent for Forward()
	CamRot = FRotator(FMath::RadiansToDegrees(-PitchDown), FMath::RadiansToDegrees(ToHeroYaw + AttachYaw), 0);
}
