import sys; sys.path.insert(0,'.')
from ed import Ed
p='/Users/midir/sm2-n1/combat/unreal/WebHomage/Source/WebHomage/Combat/WHCombatDirector.cpp'
e=Ed(p); s=e.s
a=s.index('// ------------------------------------------------------------------------------------------------ combat camera layer')
b=s.index('// ------------------------------------------------------------------------------------------------ per frame')
new=r'''// ------------------------------------------------------------------------------------------------ combat camera (r02)
bool AWHCombatDirector::Project(const FVector& CamP, const FRotator& CamR, double FovDeg, const FVector& P, double& Sx, double& Sy)
{
	const FVector L = CamR.UnrotateVector(P - CamP);
	if (L.X < 0.05) { Sx = Sy = -1; return false; }
	const double Th = FMath::Tan(FMath::DegreesToRadians(FovDeg) * 0.5);
	Sx = 0.5 + 0.5 * (L.Y / L.X) / Th;
	Sy = 0.5 - 0.5 * (L.Z / L.X) / Th * (16.0 / 9.0);
	return true;
}

// SM2-style group framing (refs group-fight-nm, street-fight-cars): mid-high, 4-6 m back, pitched 15-25 deg down, framing the hero
// plus his 3 nearest enemies. Each frame it scores candidate orbit yaws (hero / group on screen, no body within 2.6 m of the lens
// or on the lens-hero line, no wall in between, reward for every standing enemy in view, cost for turning) and turns toward the
// best at <= 55 deg/s: no cuts, no snaps. During a hit-stop freeze the camera holds its last transform exactly.
void AWHCombatDirector::CombatCamera(double RDt)
{
	UCameraComponent* Cam = Hero->Camera(); if (!Cam) return;
	const FVector Pc = Me->Pos;
	const FVector P3Pos = Cam->GetComponentLocation() / 100.0;
	const FRotator P3Rot = Cam->GetComponentRotation();
	const double P3Fov = Cam->FieldOfView;
	double NearD = 1e9;
	for (AWHEnemy* E : Enemies) if (E && E->Alive()) NearD = FMath::Min(NearD, HDist(E->Pos, Pc));
	const double Want = bFight && bEngaged && NearD < 16 ? 1 : 0;
	if (Frozen() && bCamLast && CamW > 0.5)
	{
		Cam->SetWorldLocationAndRotation(LastCamPos * 100.0, LastCamRot); Cam->SetFieldOfView(LastFov);
		CamPosM = LastCamPos; CamRotF = LastCamRot; CamFovF = LastFov;
		return;
	}
	CamW = Damp(CamW, Want, Want > 0 ? 2.0 : 1.3, RDt);
	const double W = Smooth(CamW);
	CamPunchT += RDt;
	CamPunch = CamPunchT < 0.12 ? Smooth(CamPunchT / 0.12) : 1 - Smooth((CamPunchT - 0.12) / 0.4);
	if (!bCamInit) { CYaw = CYawGoal = FMath::DegreesToRadians(P3Rot.Yaw); CHero = Pc; bCamInit = true; }
	// hero anchor: tight follow, lag capped at 0.7 m (the hero never drifts toward the frame edge during a dash)
	CHero.X = Damp(CHero.X, Pc.X, 12, RDt); CHero.Y = Damp(CHero.Y, Pc.Y, 12, RDt); CHero.Z = Damp(CHero.Z, Pc.Z, 7, RDt);
	{ const FVector Lg = CHero - Pc; if (Lg.Size() > 0.7) CHero = Pc + Lg.GetSafeNormal() * 0.7; }
	// framing set: the 3 nearest standing enemies
	TArray<AWHEnemy*> Near, Stand;
	for (AWHEnemy* E : Enemies)
		if (E && E->Alive() && E->State != EWHEnemyState::Down && E->State != EWHEnemyState::Knock) Stand.Add(E);
	Stand.Sort([&Pc](const AWHEnemy& A, const AWHEnemy& B) { return HDist(A.Pos, Pc) < HDist(B.Pos, Pc); });
	for (AWHEnemy* E : Stand) if (Near.Num() < 3 && HDist(E->Pos, Pc) < 11) Near.Add(E);
	FVector OffT = FVector::ZeroVector;
	if (Near.Num()) { FVector Cn = FVector::ZeroVector; for (AWHEnemy* E : Near) Cn += E->Pos; OffT = Flat(Cn / Near.Num() - Pc) * 0.4; if (OffT.Size() > 1.4) OffT = OffT.GetSafeNormal() * 1.4; }
	COff.X = Damp(COff.X, OffT.X, 2.5, RDt); COff.Y = Damp(COff.Y, OffT.Y, 2.5, RDt); COff.Z = 0;
	const double Gz = GroundHeight(Pc.X, Pc.Y, Pc.Z + 0.5);
	const double Air = FMath::Clamp((Pc.Z - HH) - Gz, 0.0, 4.0);
	const double Pitch = FMath::Lerp(21.0, 15.5, FMath::Clamp(Air / 2.5, 0.0, 1.0));
	CPitch = Damp(CPitch, Pitch, 3, RDt);
	auto FocusNow = [&]() { FVector F = CHero + COff; F.Z = FMath::Max(Gz + 1.0, CHero.Z + 0.05); return F; };
	FVector Focus = FocusNow();
	auto RotFor = [&](double Yaw) { return FRotator(-CPitch, FMath::RadiansToDegrees(Yaw), 0); };
	auto CamFor = [&](double Yaw, double Dist) { return Focus - RotFor(Yaw).Vector() * Dist; };
	auto OutBy = [&](const FVector& Cp, const FRotator& R, const FVector& P, double M) -> double
	{
		double Sx, Sy; if (!Project(Cp, R, CFov, P, Sx, Sy)) return 1.0;
		return FMath::Max(0.0, FMath::Max(M - Sx, Sx - (1 - M))) + FMath::Max(0.0, FMath::Max(M - Sy, Sy - (1 - M)));
	};
	const FVector HeroTop = Pc + FVector(0, 0, 0.95), HeroFeet = Pc - FVector(0, 0, HH);
	auto FramePen = [&](const FVector& Cp, const FRotator& R)
	{
		double C = 20 * (OutBy(Cp, R, HeroTop, 0.1) + OutBy(Cp, R, HeroFeet, 0.1));
		for (AWHEnemy* E : Near) C += 6 * (OutBy(Cp, R, E->Pos + FVector(0, 0, 1.75 * E->T.Scale), 0.04) + OutBy(Cp, R, E->Pos, 0.04));
		return C;
	};
	auto Score = [&](double Yaw, double Dist)
	{
		const FVector Cp = CamFor(Yaw, Dist); const FRotator R = RotFor(Yaw);
		double C = FramePen(Cp, R) + 0.9 * FMath::Abs(AngWrap(Yaw - CYaw));
		const FVector Dv = Cp - Focus; FTravHit H;
		if (Raycast(Focus, Dv.GetSafeNormal(), Dv.Size() + 0.3, H)) C += 8 + (Dv.Size() + 0.3 - H.Distance);
		for (AWHEnemy* E : Enemies)
		{
			if (!E || E->State == EWHEnemyState::Out || E->Stuck) continue;
			const double Dh = HDist(E->Pos, Cp); if (Dh < 2.6) C += (2.6 - Dh) * 4;
			const FVector Ec = E->Pos + FVector(0, 0, 1.0 * E->T.Scale);
			const FVector Q = FMath::ClosestPointOnSegment(Ec, Cp, Pc);
			if (FVector::Dist(Q, Ec) < 0.6 && FVector::Dist(Q, Pc) > 0.5) C += 3;
		}
		for (AWHEnemy* E : Stand)
			if (OutBy(Cp, R, E->Pos + FVector(0, 0, 1.7 * E->T.Scale), 0.02) + OutBy(Cp, R, E->Pos, 0.02) <= 0) C -= 0.35;
		return C;
	};
	if (W > 0.002)
	{
		double BestY = CYawGoal, BestS = Score(CYawGoal, CDist);
		for (int32 k = -7; k <= 7; ++k)
		{
			const double Y = CYaw + k * 0.17; const double S = Score(Y, CDist);
			if (S < BestS - 0.4) { BestS = S; BestY = Y; }
		}
		CYawGoal = BestY;
		const double Step = AngWrap(CYawGoal - CYaw) * (1 - FMath::Exp(-2.2 * RDt));
		CYaw = AngWrap(CYaw + FMath::Clamp(Step, -0.95 * RDt, 0.95 * RDt));
		double WantD = 6.0;
		for (double D : { 4.4, 5.0, 5.6 }) if (FramePen(CamFor(CYaw, D), RotFor(CYaw)) <= 0) { WantD = D; break; }
		CDist = Damp(CDist, WantD, 1.5, RDt);
	}
	else { CYaw = CYawGoal = FMath::DegreesToRadians(P3Rot.Yaw); CHero = Pc; COff = FVector::ZeroVector; }
	// hard hero margin: pull the framing offset back toward the hero until his head and feet sit inside a 7 % border
	for (int32 It = 0; It < 4; ++It)
	{
		if (OutBy(CamFor(CYaw, CDist), RotFor(CYaw), HeroTop, 0.07) + OutBy(CamFor(CYaw, CDist), RotFor(CYaw), HeroFeet, 0.07) <= 0) break;
		COff *= 0.5; CHero = CHero + (Pc - CHero) * 0.5; Focus = FocusNow();
	}
	FVector CamP = CamFor(CYaw, CDist); FRotator CamR = RotFor(CYaw);
	{ // walls between focus and lens: pull in (never closer than 2.2 m)
		const FVector Dv = CamP - Focus; FTravHit H;
		if (Raycast(Focus, Dv.GetSafeNormal(), Dv.Size() + 0.3, H)) CamP = Focus + Dv.GetSafeNormal() * FMath::Max(2.2, H.Distance - 0.3);
		const double Gy = GroundHeight(CamP.X, CamP.Y, CamP.Z + 0.3) + 0.4; if (CamP.Z < Gy) CamP.Z = Gy;
	}
	if (CamPunch > 0) CamP += CamR.Vector() * 0.22 * CamPunch;
	double Fov = CFov;
	// finisher beat: a low 3/4 close-up of hero + victim, eased in over 0.35 s (slow-mo x0.3 runs with it), eased out over 0.5 s
	if (CineS.bOn)
	{
		CineS.T += RDt;
		AWHEnemy* T = CineS.Target.Get();
		if (CineS.T > CineS.Dur || !T) { CineS.bOn = false; CineK = 0; }
		else
		{
			CineK = Smooth(CineS.T / 0.35) * (1 - Smooth((CineS.T - (CineS.Dur - 0.5)) / 0.5));
			const FVector A = Pc, Tp = T->Chest();
			const FVector Mid = (A + Tp) * 0.5;
			const FVector Ax = FlatNorm(Tp - A);
			if (!CineS.bSide)
			{
				const FVector Perp(-Ax.Y, Ax.X, 0);
				const double Sg = FVector::DotProduct(Perp, CamP - Mid) >= 0 ? 1 : -1;
				CineS.Side = (Perp * Sg * 0.9 - Ax * 0.45).GetSafeNormal(); CineS.Dist = 2.4 + FVector::Dist(A, Tp) * 0.6; CineS.bSide = true;
			}
			FVector Cp = Mid + CineS.Side * (CineS.Dist + CineS.T * 0.3); Cp.Z = Mid.Z + 0.3;
			FTravHit Hh; const FVector Dm = (Cp - Mid).GetSafeNormal();
			if (Raycast(Mid, Dm, FVector::Dist(Mid, Cp), Hh)) Cp = Mid + Dm * FMath::Max(1.2, Hh.Distance - 0.3);
			const FRotator Cr = (Mid + FVector(0, 0, 0.1) - Cp).Rotation();
			const double K = CineK;
			CamP = CamP + (Cp - CamP) * K;
			CamR = FQuat::Slerp(CamR.Quaternion(), Cr.Quaternion(), K).Rotator();
			Fov = FMath::Lerp(Fov, 58.0, K);
		}
	}
	// blend from / to the P3 chase camera
	FVector OutP = P3Pos + (CamP - P3Pos) * W;
	FRotator OutR = FQuat::Slerp(P3Rot.Quaternion(), CamR.Quaternion(), W).Rotator();
	const double OutFov = FMath::Lerp(P3Fov, Fov, W);
	// shake / impact (trauma decays and the shake phase advances in real time, but not during a hit-stop freeze)
	CamTrauma = FMath::Max(0.0, CamTrauma - RDt * 1.8);
	CamImpact = FMath::Max(0.0, CamImpact - RDt * 3.0);
	ShakePh += RDt * 47.0;
	if (CamTrauma > 0.001 || CamImpact > 0.001)
	{
		const double Tr = CamTrauma * CamTrauma;
		OutR.Pitch += Tr * 1.6 * FMath::Sin(ShakePh * 1.3) - CamImpact * 0.9;
		OutR.Yaw += Tr * 1.3 * FMath::Sin(ShakePh * 0.9 + 1.7);
		OutR.Roll += Tr * 1.0 * FMath::Sin(ShakePh * 1.1 + 0.4);
	}
	Cam->SetWorldLocationAndRotation(OutP * 100.0, OutR);
	Cam->SetFieldOfView(float(OutFov));
	LastCamPos = OutP; LastCamRot = OutR; LastFov = float(OutFov); bCamLast = true;
	CamPosM = OutP; CamRotF = OutR; CamFovF = OutFov;
}

'''
e.s=s[:a]+new+s[b:]
e.rep("""	else Want = YawDir(Hero->GetTravCamera().Yaw + CamYawOff * Smooth(CamW));""","""	else Want = CamW > 0.5 ? YawDir(CYaw) : YawDir(Hero->GetTravCamera().Yaw);""")
e.save(); print('e3 ok')
