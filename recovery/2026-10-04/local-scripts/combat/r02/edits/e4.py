import sys; sys.path.insert(0,'.')
from ed import Ed
p='/Users/midir/sm2-n1/combat/unreal/WebHomage/Source/WebHomage/Combat/WHCombatDirector.cpp'
e=Ed(p)
e.rep("""			if (bEngaged) DirectorStep(Dt);""","""			if (bEngaged) { DirectorStep(Dt); Reinforce(Dt); }""")
e.rep("""	Fx.Sense(SenseLvl, bRed, Hero->HeadM() + FVector(0, 0, 0.08), RDt);
	Fx.Update(Dt);""","""	Fx.Sense(SenseLvl, bRed, Hero->HeadM() + FVector(0, 0, 0.08), Dt);
	Fx.Update(Dt, Frozen() ? 0.0 : RDt);""")
e.rep("""	UpdateTime();
	CombatCamera(RDt);""","""	if (TimeScale < 0.05) ++NFrozenFrames;
	UpdateTime();
	CombatCamera(RDt);
	FrameRecord();""")
e.rep("""FString AWHCombatDirector::StateString() const""","""// r02 per-frame record for the pixel measurements: camera, and each character's screen-space box (all skeleton bones projected with
// the final camera of this frame; head top padded). The rendered frame shows this simulation state (movie frames lag by the render
// pipeline; docs/night1/combat/measure_r02.py calibrates the offset from the hit-stop freezes).
void AWHCombatDirector::FrameRecord()
{
	if (!bFight && Enemies.Num() == 0) return;
	auto Box = [this](const USkeletalMeshComponent* M, double& X0, double& Y0, double& X1, double& Y1, double& Dist) -> bool
	{
		X0 = Y0 = 9; X1 = Y1 = -9; Dist = 1e9; bool bAny = false;
		if (!M) return false;
		const TArray<FTransform>& Cs = M->GetComponentSpaceTransforms();
		const FTransform Ct = M->GetComponentTransform();
		double Top = -1e9, Bot = 1e9;
		for (const FTransform& B : Cs) { const FVector Wp = Ct.TransformPosition(B.GetLocation()) / 100.0; Top = FMath::Max(Top, Wp.Z); Bot = FMath::Min(Bot, Wp.Z); }
		for (int32 i = 0; i < Cs.Num(); ++i)
		{
			FVector Wp = Ct.TransformPosition(Cs[i].GetLocation()) / 100.0;
			if (Wp.Z >= Top - 1e-3) Wp.Z += 0.12;   // head top above the head bone
			double Sx, Sy;
			if (!Project(CamPosM, CamRotF, CamFovF, Wp, Sx, Sy)) continue;
			X0 = FMath::Min(X0, Sx); X1 = FMath::Max(X1, Sx); Y0 = FMath::Min(Y0, Sy); Y1 = FMath::Max(Y1, Sy); bAny = true;
			Dist = FMath::Min(Dist, FVector::Dist(Wp, CamPosM));
		}
		return bAny;
	};
	double X0, Y0, X1, Y1, D;
	FString Row = FString::Printf(TEXT("{\\"f\\":%lld,\\"rt\\":%.4f,\\"ts\\":%.3f,\\"frz\\":%d,\\"cine\\":%.2f,\\"cam\\":[%.3f,%.3f,%.3f,%.2f,%.2f,%.2f,%.2f],\\"move\\":\\"%s\\","),
		Frame, RTime, TimeScale, TimeScale < 0.05 ? 1 : 0, CineK, CamPosM.X, CamPosM.Y, CamPosM.Z, CamRotF.Pitch, CamRotF.Yaw, CamRotF.Roll, CamFovF, *Me->MoveName().ToString());
	Box(Hero->GetMesh(), X0, Y0, X1, Y1, D);
	Row += FString::Printf(TEXT("\\"hero\\":[%.3f,%.3f,%.3f,%.4f,%.4f,%.4f,%.4f,%.2f],\\"e\\":["), Me->Pos.X, Me->Pos.Y, Me->Pos.Z - HH, X0, Y0, X1, Y1, D);
	bool bFirst = true;
	for (AWHEnemy* E : Enemies)
	{
		if (!E) continue;
		const bool bOk = Box(E->Mesh, X0, Y0, X1, Y1, D);
		const bool bWarn = E->WarnOn();
		Row += FString::Printf(TEXT("%s[\\"%s\\",\\"%s\\",\\"%s\\",%.3f,%.3f,%.3f,%.4f,%.4f,%.4f,%.4f,%.2f,%d,%d]"), bFirst ? TEXT("") : TEXT(","), *E->Tag(), E->TypeName(), E->StateName(),
			E->Pos.X, E->Pos.Y, E->Pos.Z, bOk ? X0 : -1.0, bOk ? Y0 : -1.0, bOk ? X1 : -1.0, bOk ? Y1 : -1.0, D, bWarn ? 1 : 0, E->Alive() ? 1 : 0);
		bFirst = false;
	}
	Row += TEXT("]}");
	FrameRows.Add(Row);
}

FString AWHCombatDirector::StateString() const""")
e.rep("""	FFileHelper::SaveStringToFile(FString::Join(BeatRows, TEXT("\\n")) + TEXT("\\n"), *(OutDir / (ShotName + TEXT("_beats.jsonl"))));""",
"""	FFileHelper::SaveStringToFile(FString::Join(BeatRows, TEXT("\\n")) + TEXT("\\n"), *(OutDir / (ShotName + TEXT("_beats.jsonl"))));
	FFileHelper::SaveStringToFile(FString::Join(FrameRows, TEXT("\\n")) + TEXT("\\n"), *(OutDir / (ShotName + TEXT("_frames.jsonl"))));""")
e.rep("""		TEXT(" \\"hitstops\\": %d, \\"slowmos\\": %d, \\"min_timescale\\": %.3f, \\"slowmo_game_s\\": %.3f, \\"slowmo_real_s\\": %.3f,\\n \\"beats\\": %d, \\"beats_fired\\": %d, \\"fx_spawned\\": %d\\n}\\n"),""",
"""		TEXT(" \\"hitstops\\": %d, \\"frozen_frames\\": %d, \\"slowmos\\": %d, \\"min_timescale\\": %.3f, \\"slowmo_game_s\\": %.3f, \\"slowmo_real_s\\": %.3f,\\n")
		TEXT(" \\"attack_starts\\": %d, \\"max_attack_gap_s\\": %.3f, \\"spawned\\": %d, \\"reserve_left\\": %d,\\n \\"beats\\": %d, \\"beats_fired\\": %d, \\"fx_spawned\\": %d\\n}\\n"),""")
e.rep("""		NDodges, NPerfect, NWebHits, NEnemyHits, NShots, NShotHits, NHitStops, NSlowmo, MinTimeScale, SlowmoGameT, SlowmoRealT,""",
"""		NDodges, NPerfect, NWebHits, NEnemyHits, NShots, NShotHits, NHitStops, NFrozenFrames, NSlowmo, MinTimeScale, SlowmoGameT, SlowmoRealT,
		NAttackStarts, MaxAttackGap, Enemies.Num(), Reserve,""")
e.save(); print('e4 ok')
