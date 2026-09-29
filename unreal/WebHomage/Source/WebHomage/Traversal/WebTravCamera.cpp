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
	FName N_vault(TEXT("vault")), N_wallRun(TEXT("wallRun"));
}

void FWebTravCamera::Reset(const FVector& Pos, double InYaw)
{
	Target = Pos + FVector(0, 0, 0.55);
	Yaw = InYaw; Pitch = 0.14; CollDist = Dist;
	bAutoInit = false;
	LagOff = LagOffV = JumpOff = JumpOffV = FVector::ZeroVector;
	bHasLastGoal = false; AnchorLean = 0.0; AnchorLeanV = 0.0;
}

void FWebTravCamera::ApplyLook(const FVector2D& Look)
{
	if (FMath::Abs(Look.X) + FMath::Abs(Look.Y) > 0.001) LastLook = 0.0;
	Yaw += Look.X * Sens;
	Pitch = FMath::Clamp(Pitch + Look.Y * Sens, -0.9, 1.25);
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
	const double WantFov = 58.0 + 13.0 * Smooth(Speed, 12, 44) + (bDive ? 5.0 : 0.0);
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
	// ---- compose
	const FVector Fwd = Forward();
	FVector Pivot = Target + FVector(0, 0, HeightOff + Dip);
	const FVector Right = RightFlat();
	Pivot += Right * SideOff;
	{ // the pivot itself must never sit behind a wall relative to the character
		const FVector Eye = P.Pos + FVector(0, 0, 0.55);
		FVector D = Pivot - Eye;
		const double L = D.Size();
		if (L > 1e-3)
		{
			D /= L;
			FTravHit H;
			const double Cap = World.Raycast(Eye, D, L + 0.25, H) ? FMath::Max(0.0, H.Distance - 0.3) : L + 0.25;
			PivCap = PivCap < 0 ? Cap : Cap < PivCap ? Cap : Damp(PivCap, Cap, 4, Dt);
			if (PivCap < L) Pivot = Eye + D * PivCap;
		}
	}
	FVector Back = -Fwd;
	double Allowed = Dist;
	auto ProbeAt = [&](double OX, double OZ)
	{
		const FVector O = Pivot + Right * OX + FVector(0, 0, OZ);
		FTravHit H;
		if (World.Raycast(O, Back, Dist + 0.4, H)) Allowed = FMath::Min(Allowed, FMath::Max(0.5, H.Distance - 0.35));
	};
	ProbeAt(0, 0); ProbeAt(0.3, 0); ProbeAt(-0.3, 0); ProbeAt(0, 0.25); ProbeAt(0, -0.25);
	// occluded: search nearby orbit directions for one with >= ~3 m of clearance, move there smoothly
	const double MinD = FMath::Min(3.0, Dist * 0.75);
	OccT -= Dt;
	if ((P.Sub == N_vault || bLedgeSub) && OccT > 0.03) OccT = 0.03;
	if (Allowed < MinD && OccT <= 0)
	{
		OccT = 0.12;
		auto Clear = [&](double Y, double Pt)
		{
			const double CP = FMath::Cos(Pt);
			const FVector D(-FMath::Cos(Y) * CP, -FMath::Sin(Y) * CP, FMath::Sin(Pt));
			double A = Dist;
			for (double OX : { 0.0, 0.3, -0.3 })
			{
				FTravHit H;
				if (World.Raycast(Pivot + Right * OX, D, Dist + 0.4, H)) A = FMath::Min(A, H.Distance - 0.35);
			}
			return A;
		};
		bool bBest = false;
		double BS = -1e9, BY = 0, BP = 0;
		const double Base = M == EWebTravMode::Perch ? P.Facing : Yaw;
		for (double DP : { 0.0, 0.35, 0.7, 1.0 })
		{
			for (double DYW : { 0.0, 0.5, -0.5, 1.0, -1.0, 1.5, -1.5 })
			{
				const double Y = Base + DYW, Pt = FMath::Clamp(Pitch + DP, -0.3, 1.15);
				const double A = Clear(Y, Pt);
				const double SC = FMath::Min(A, Dist) - 0.9 * FMath::Abs(DYW) - 0.6 * DP;
				if (A >= MinD && SC > BS) { BS = SC; BY = Y; BP = Pt; bBest = true; }
			}
		}
		bOccGoal = bBest;
		if (bBest) { OccGoalYaw = BY; OccGoalPitch = BP; OccHold = 2.0; }
	}
	if (Allowed >= MinD + 0.5 && OccT <= -1) bOccGoal = false;
	if (bOccGoal)
	{
		const bool bFast = P.Sub == N_vault || bLedgeSub || (P.ModeT < 0.8 && !bSwinging && !bAir);
		const double R = LastLook < 0.4 ? 1.5 : bFast ? 11 : (bSwinging || bAir) ? 3 : 5;
		Yaw = AngDamp(Yaw, OccGoalYaw, R, Dt); Pitch = Damp(Pitch, OccGoalPitch, R, Dt);
		const double CP = FMath::Cos(Pitch);
		Back = FVector(-FMath::Cos(Yaw) * CP, -FMath::Sin(Yaw) * CP, FMath::Sin(Pitch));
		if (FMath::Abs(WrapA(Yaw - OccGoalYaw)) < 0.05 && FMath::Abs(Pitch - OccGoalPitch) < 0.05) bOccGoal = false;
	}
	// collision distance: fast pull-in, critically damped ease back out
	if (Allowed < CollDist) { CollDist = Damp(CollDist, Allowed, 30, Dt); CollDistV = 0; }
	else SD(CollDist, CollDistV, Allowed, 0.45, Dt);
	CamPos = Pivot + Back * FMath::Min(CollDist + 1.3 * FMath::Max(0.0, KickK), FMath::Max(CollDist, Allowed));
	const double GY = World.GroundHeight(CamPos.X, CamPos.Y, CamPos.Z + 0.3) + 0.3;
	if (CamPos.Z < GY) CamPos.Z = GY;
	// look target: ahead of the pivot; while swinging lean slightly toward the anchor (held after release, weight eases)
	if (bSwinging && P.bHasAnchor)
	{
		FVector Want = P.Anchor - Pivot;
		Want.Z *= 0.15; // round 02: lean toward the anchor sideways, not up (a 25 m-high anchor cancelled the height pitch)
		if (AnchorLean < 0.005) LeanOff = Want;
		SDV(LeanOff, LeanOffV, Want, 0.4, Dt);
	}
	SD(AnchorLean, AnchorLeanV, bSwinging && P.bHasAnchor ? 0.1 : 0.0, bSwinging ? 0.5 : 0.7, Dt);
	FVector LookAt = Pivot + Fwd * 10.0 + Lead;
	if (AnchorLean > 0.0005) LookAt = FMath::Lerp(LookAt, Pivot + LeanOff, AnchorLean);
	// shake
	Trauma = FMath::Max(0.0, Trauma - Dt * 1.5);
	const double Sh = Trauma * Trauma;
	FRotator R = (LookAt - CamPos).Rotation();
	R.Roll = FMath::RadiansToDegrees(Roll + Sh * 0.045 * Noise(Time * 22.0, 3.0));
	R.Pitch += FMath::RadiansToDegrees(Sh * 0.035 * Noise(Time * 25.0, 1.0));
	R.Yaw += FMath::RadiansToDegrees(Sh * 0.035 * Noise(Time * 24.0, 7.0));
	CamRot = R;
	OutVFov = Fov + Punch + 9.0 * FMath::Max(0.0, KickK);
	// speed motion blur: none on foot / walls, ramps in over fast swings / dives / zips
	const bool bGroundish = M == EWebTravMode::Ground || M == EWebTravMode::Land || M == EWebTravMode::Wall;
	const double MbTarget = (bGroundish ? 0.45 : bDive ? 1.6 : 1.0) * Smooth(Speed, 6, 36) * 1.1;
	MotionBlur = FMath::Max(0.0, SD(MbK, MbKV, MbTarget, MbTarget > MbK ? 0.35 : 0.2, Dt));
}
