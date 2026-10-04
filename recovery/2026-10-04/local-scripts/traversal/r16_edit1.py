p='WebTravCamera.cpp'
s=open(p).read()
def rep(old,new,cnt=1):
    global s
    assert s.count(old)==cnt, (s.count(old), old[:80])
    s=s.replace(old,new)

rep("""	Roll = Damp(Roll, WantRoll, 3, Dt);""","""	WantRoll *= 1.0 - Smooth(FlipK, 0.0, 1.0); // round 16 (TC12): no roll with the body while the trick camera is in
	Roll = Damp(Roll, WantRoll, 3, Dt);""")

a=s.index("	// round 11: flip camera weight (0.3 s in, 0.45 s out).")
b=s.index("	// round 10 (critic r09: camera pop at b 0.000-0.017 s)")
new_block='''	// round 16 (TRICK_CAMERA_SPEC): the trick camera is chosen ONCE at the release frame (ChooseFlipView) and held on its world
	// azimuth; an obstruction on the held axis dollies in (TC11), under FlipDistMin it blends to the plain chase
	const bool bFlipCam = P.bFlip || P.bFlipSoon;
	if (bFlipCam && !bFlipWas)
	{
		ChooseFlipView(P, World);
		bFlipAbort = FlipTier >= 3;
		FlipDistNow = FlipDistSel; FlipDistV = 0.0;
	}
	if (!bFlipCam) { bFlipAbort = false; FlipTier = -1; }
	bFlipWas = bFlipCam;
	if (bFlipCam && !bFlipAbort && bChaseInit)
	{ // TC11: sweep hero chest -> the held spot; a hit dollies the camera in along the axis, never yaws / re-picks the side
		const double Ec = FMath::Asin(FMath::Clamp(FlipDrop / FMath::Max(1.0, FlipDistSel), 0.0, 0.6));
		const FVector Uc(FMath::Cos(FlipAz) * FMath::Cos(Ec), FMath::Sin(FlipAz) * FMath::Cos(Ec), -FMath::Sin(Ec));
		double HitD = 0.0, Goal = FlipDistSel;
		if (!World.SphereOverlaps(Chest, 0.22) && World.SphereSweep(Chest, Hero + Uc * FlipDistSel, 0.3, HitD)) Goal = FMath::Min(Goal, HitD - 0.25);
		if (Goal < FlipDistMin) bFlipAbort = true; // TC11: no room to keep the trick view -> plain chase over FlipOutT
		else SD(FlipDistNow, FlipDistV, Goal, Goal < FlipDistNow ? FlipDollyInT : FlipDollyOutT, Dt);
	}
	{
		const bool bOn = bFlipCam && !bFlipAbort;
		SD(FlipK, FlipKV, bOn ? 1.0 : 0.0, bOn ? FlipInT : FlipOutT, Dt);
		FlipK = FMath::Clamp(FlipK, 0.0, 1.0);
		SD(FlipZK, FlipZKV, bOn ? 1.0 : 0.0, bOn ? FlipZInT : FlipOutT, Dt);
		FlipZK = FMath::Clamp(FlipZK, 0.0, 1.0);
	}
	SWant = FMath::Lerp(SWant, FlipSFrame, FlipK);
	SWant = FMath::Clamp(SWant, 0.32, 0.72);
'''
s=s[:a]+new_block+s[b:]

rep("const double BackDist = ChaseDist - AirClose - FlipCloser * FlipK + 1.3 * FMath::Max(0.0, KickK);","const double BackDist = ChaseDist - AirClose + 1.3 * FMath::Max(0.0, KickK);")

a=s.index("	// round 12: flip camera spot = FlipDist m from the hero along the searched line")
b=s.index("	if (!bChaseInit)\n	{\n		bChaseInit = true;")
new_spot='''	// round 16: trick camera spot = FlipDistNow m from the hero on the held world azimuth, FlipDrop m under his body centre
	const double FlipKs = Smooth(FlipK, 0.0, 1.0), FlipZs = Smooth(FlipZK, 0.0, 1.0);
	FVector FlipSpot = Hero;
	{
		const double FlipElevNow = FMath::Asin(FMath::Clamp(FlipDrop / FMath::Max(1.0, FlipDistNow), 0.0, 0.6));
		FlipSpot = Hero + FVector(FMath::Cos(FlipAz) * FMath::Cos(FlipElevNow), FMath::Sin(FlipAz) * FMath::Cos(FlipElevNow), -FMath::Sin(FlipElevNow)) * FlipDistNow;
		Desired = FMath::Lerp(Desired, FlipSpot, FlipKs);
		ZWant = FMath::Lerp(ZWant, FlipSpot.Z, FlipZs);
	}
'''
s=s[:a]+new_spot+s[b:]

rep("""	const double MaxH = 5.0 - AirClose + 1.3 * FMath::Max(0.0, KickK), MinH = FMath::Lerp(3.5 - AirClose, FMath::Min(3.5 - AirClose, FlipDist * FMath::Cos(FlipElev) - 0.2), FlipKs);""",
"""	const double MaxH = 5.0 - AirClose + 1.3 * FMath::Max(0.0, KickK), MinH = 3.5 - AirClose;""")

rep("""	// round 12: the flip spot is taken exactly (the 0.07 s chase spring trails ~3 m at 25 m/s), blended in / out by FlipK
	if (FlipKs > 0.0) CamXY = FMath::Lerp(CamXY, FVector(FlipSpot.X, FlipSpot.Y, 0), FlipKs);
	SD(CamZ, CamZV, ZWant, 0.05, Dt);
	if (FlipKs > 0.0) CamZ = FMath::Lerp(CamZ, FlipSpot.Z, FlipKs);
	CamZ = FMath::Clamp(CamZ, FMath::Lerp(Hero.Z + FMath::Lerp(CamZMin, -SkyCamBelow - 0.3, SkyK) + OU, FlipSpot.Z - 0.3, FlipKs), Hero.Z + CamZMax + OU); // round 07: 0.7..1.8 -> 1.2..2.6""",
"""	// the trick spot is taken exactly (the 0.07 s chase spring trails ~3 m at 25 m/s), blended in / out by FlipK (horizontal) / FlipZK (height)
	if (FlipKs > 0.0) CamXY = FMath::Lerp(CamXY, FVector(FlipSpot.X, FlipSpot.Y, 0), FlipKs);
	SD(CamZ, CamZV, ZWant, 0.05, Dt);
	if (FlipZs > 0.0) CamZ = FMath::Lerp(CamZ, FlipSpot.Z, FlipZs);
	CamZ = FMath::Clamp(CamZ, FMath::Lerp(Hero.Z + FMath::Lerp(CamZMin, -SkyCamBelow - 0.3, SkyK) + OU, FlipSpot.Z - 0.3, FlipZs),
		FMath::Lerp(Hero.Z + CamZMax + OU, FMath::Max(Hero.Z + CamZMax + OU, FlipSpot.Z + 0.3), FlipZs)); // round 07: 0.7..1.8 -> 1.2..2.6""")

rep("""		double Push = WallPush;
		if (DR < CamWallHard) Push = FMath::Min(Push, -(CamWallHard - DR));
		if (DL < CamWallHard) Push = FMath::Max(Push, CamWallHard - DL);""",
"""		double Push = WallPush;
		if (DR < CamWallHard) Push = FMath::Min(Push, -(CamWallHard - DR));
		if (DL < CamWallHard) Push = FMath::Max(Push, CamWallHard - DL);
		Push *= 1.0 - FlipKs; // round 16 (TC11): the trick camera never yaws round the hero -- the dolly-in along the held axis replaces the push""")

rep("""	const double FlipUpDeg = FMath::Min(FlipPitchUpMax, FMath::Max(FlipPitchUp, FMath::RadiansToDegrees(FlipElev) + 20.0));""","""	const double FlipUpDeg = FlipPitchUpMax;""")
open(p,'w').write(s)
print("ok")
