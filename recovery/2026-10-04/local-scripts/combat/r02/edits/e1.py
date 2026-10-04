import sys; sys.path.insert(0,'.')
from ed import Ed
e=Ed('/Users/midir/sm2-n1/combat/unreal/WebHomage/Source/WebHomage/Combat/WHCombatDirector.cpp')
e.rep("""	if (J.Get(TEXT("seed"))) Rng.Initialize(int32(J.Num_(TEXT("seed"), 0)));""","""	if (J.Get(TEXT("seed"))) Rng.Initialize(int32(J.Num_(TEXT("seed"), 0)));
	HeroMinHp = J.Num_(TEXT("hero_min_hp"), 0);
	ReserveSpec = J.Str_(TEXT("reserve")); Reserve = ReserveSpec.Len();
	KeepAlive = int32(J.Num_(TEXT("keep"), 0));""")
e.rep("""	FWHThreat T; T.E = E; T.At = Time + Lead; T.Kind = FName(Kind);
	Threats.Add(T);""","""	FWHThreat T; T.E = E; T.At = Time + Lead; T.Kind = FName(Kind);
	Threats.Add(T);
	// r02: every threat is an attack start (melee wind-up / brute wind-up / gun aim). Longest gap between starts = aggression metric.
	if (LastAttackRT >= 0) MaxAttackGap = FMath::Max(MaxAttackGap, RTime - LastAttackRT);
	LastAttackRT = RTime; ++NAttackStarts;""")
e.rep("""void AWHCombatDirector::ReleaseToken(AWHEnemy* E)
{
	if (MeleeToken.Get() == E) { MeleeToken = nullptr; GlobalCd = Rnd(0.35, 0.9); }
	if (GunToken.Get() == E) { GunToken = nullptr; GunCd = Rnd(1.2, 2.4); }
}""","""bool AWHCombatDirector::HasToken(const AWHEnemy* E) const
{
	for (const auto& W : MeleeTokens) if (W.Get() == E) return true;
	for (const auto& W : GunTokens) if (W.Get() == E) return true;
	return false;
}

void AWHCombatDirector::ReleaseToken(AWHEnemy* E)
{
	if (MeleeTokens.RemoveAll([E](const TWeakObjectPtr<AWHEnemy>& W) { return W.Get() == E; }) > 0) GlobalCd = Rnd(0.15, 0.4);
	if (GunTokens.RemoveAll([E](const TWeakObjectPtr<AWHEnemy>& W) { return W.Get() == E; }) > 0) GunCd = Rnd(0.5, 1.2);
}""")
e.rep("""if (H.Kind == "finisher") HitStop(0.12, 0.05); else if (Heavy > 0.5) HitStop(0.065, 0.08); else HitStop(0.035, 0.15);""",
"""		// r02: a true freeze of hero + victim (3-5 frames at 60 fps); the victim's flinch pose is already in the contact frame
		if (H.Kind == "finisher") HitStop(6); else if (Heavy > 0.5) HitStop(5); else HitStop(4);""")
e.rep("""	CineS = FCine(); CineS.Target = Target; CineS.Dur = Dur; CineS.Kind = Kind; CineS.bOn = true;
	if (Kind == "finisher") Slowmo(1.2, 0.45, 0.4); else Slowmo(0.7, 0.4, 0.3);""","""	if (Kind != "finisher") { Slowmo(0.5, 0.45, 0.25); LogEvent(TEXT("pin beat (slow-mo only, no camera move)")); return; }
	CineS = FCine(); CineS.Target = Target; CineS.Dur = Dur; CineS.Kind = Kind; CineS.bOn = true;
	Slowmo(Dur + 0.25, 0.3, 0.45);""")
e.rep("""	Me->TakeHit(E, Dmg, bHeavy);""","""	Me->TakeHit(E, Dmg, bHeavy);
	if (HeroMinHp > 0) Me->Hp = FMath::Max(Me->Hp, HeroMinHp);""")
e.rep("""	HitStop(bHeavy ? 0.08 : 0.045, bHeavy ? 0.06 : 0.12); Shake(bHeavy ? 0.4 : 0.22); if (bHeavy) Impact(0.3);""",
"""	HitStop(bHeavy ? 5 : 4); Shake(bHeavy ? 0.3 : 0.16); if (bHeavy) Impact(0.25);""")
e.rep("""	Me->Hp = FMath::Max(0.0, Me->Hp - E->T.Dmg);""","""	Me->Hp = FMath::Max(HeroMinHp, Me->Hp - E->T.Dmg);""")
e.rep("""void AWHCombatDirector::HitStop(double Dur, double Scale)
{
	FTimeReq R; R.Until = RTime + Dur; R.Scale = Scale; R.bSlow = false; TimeReq.Add(R); ++NHitStops;
}""","""void AWHCombatDirector::HitStop(int32 Frames, double Scale)
{ // UpdateTime runs at the end of this frame: the next Frames rendered frames advance game time by x Scale only
	FTimeReq R; R.Until = RTime + (Frames - 0.5) / 60.0; R.Scale = Scale; R.bSlow = false; TimeReq.Add(R); ++NHitStops;
}""")
e.rep("""	// P2 armed street people (hero skeleton): variety per type
	static const TCHAR* MeleeMeshes[] = { TEXT("SK_Street_Thug_Bat"), TEXT("SK_Street_Tee_Bat"), TEXT("SK_Street_Beard_Pipe"), TEXT("SK_Street_Hood") };
	static const TCHAR* GunMeshes[] = { TEXT("SK_Street_Thug_Pistol"), TEXT("SK_Street_Hood_Pistol") };
	int32 NM = 0, NG = 0;
	const int32 L = Spec.Len();
	for (int32 i = 0; i < L; ++i)
	{
		const TCHAR Ch = Spec[i];
		const EWHEnemyType Ty = Ch == 'g' ? EWHEnemyType::Gunman : Ch == 'b' ? EWHEnemyType::Brute : EWHEnemyType::Melee;
		const double A = (double(i) / L - 0.5) * 2.2;
		const double R = Ty == EWHEnemyType::Gunman ? Dist + 4 : Dist;
		const FVector D = FQuat(FVector::UpVector, -A).RotateVector(Fwd);   // browser rotates +a about +Y (to his left): mirrored in UE
		FVector P = Pf + D * R; P.Z = GroundHeight(P.X, P.Y, Pf.Z + 2);
		const FString MeshName = Ty == EWHEnemyType::Gunman ? GunMeshes[NG++ % 2] : Ty == EWHEnemyType::Brute ? TEXT("SK_Street_Brute_Pipe") : MeleeMeshes[NM++ % 4];
		FActorSpawnParameters SP; SP.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		AWHEnemy* E = GetWorld()->SpawnActor<AWHEnemy>(AWHEnemy::StaticClass(), FTransform(P * 100.0), SP);
		if (!E) continue;
		E->Setup(this, Ty, i + 1, P, YawTo(P, Pf), MeshName);
		E->Mesh->PrimaryComponentTick.AddPrerequisite(this, PrimaryActorTick);
		Enemies.Add(E);
	}""","""	const int32 L = Spec.Len();
	for (int32 i = 0; i < L; ++i)
	{
		const TCHAR Ch = Spec[i];
		const double A = (double(i) / L - 0.5) * 2.4;
		const double R = Ch == 'g' ? Dist + 4 : Dist + (i % 2) * 1.2;
		const FVector D = FQuat(FVector::UpVector, -A).RotateVector(Fwd);   // browser rotates +a about +Y (to his left): mirrored in UE
		FVector P = Pf + D * R; P.Z = GroundHeight(P.X, P.Y, Pf.Z + 2);
		SpawnEnemy(Ch, P);
	}""")
e.rep("""void AWHCombatDirector::EndFight(bool bWon)""","""void AWHCombatDirector::SpawnEnemy(TCHAR Ch, const FVector& P)
{ // P2 armed street people (hero skeleton): variety per type
	static const TCHAR* MeleeMeshes[] = { TEXT("SK_Street_Thug_Bat"), TEXT("SK_Street_Tee_Bat"), TEXT("SK_Street_Beard_Pipe"), TEXT("SK_Street_Hood") };
	static const TCHAR* GunMeshes[] = { TEXT("SK_Street_Thug_Pistol"), TEXT("SK_Street_Hood_Pistol") };
	const EWHEnemyType Ty = Ch == 'g' ? EWHEnemyType::Gunman : Ch == 'b' ? EWHEnemyType::Brute : EWHEnemyType::Melee;
	int32 NM = 0, NG = 0; for (AWHEnemy* O : Enemies) if (O) { if (O->bHasGun || O->Type == EWHEnemyType::Gunman) ++NG; else if (O->Type != EWHEnemyType::Brute) ++NM; }
	const FString MeshName = Ty == EWHEnemyType::Gunman ? GunMeshes[NG % 2] : Ty == EWHEnemyType::Brute ? TEXT("SK_Street_Brute_Pipe") : MeleeMeshes[NM % 4];
	FActorSpawnParameters SP; SP.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	AWHEnemy* E = GetWorld()->SpawnActor<AWHEnemy>(AWHEnemy::StaticClass(), FTransform(P * 100.0), SP);
	if (!E) return;
	E->Setup(this, Ty, NextIndex++, P, YawTo(P, PlayerFeet), MeshName);
	E->Mesh->PrimaryComponentTick.AddPrerequisite(this, PrimaryActorTick);
	Enemies.Add(E);
}

// r02 reinforcements: keep the ring full (script "keep" standing enemies, "reserve" = spawn spec). They run in from ~13 m in front
// of the combat camera, so the player sees them arrive.
void AWHCombatDirector::Reinforce(double Dt)
{
	SpawnCd -= Dt;
	if (Reserve <= 0 || KeepAlive <= 0 || SpawnCd > 0) return;
	int32 N = 0; for (AWHEnemy* E : Enemies) if (E && E->Alive() && E->State != EWHEnemyState::Down) ++N;
	if (N >= KeepAlive) return;
	const FVector Pf = PlayerFeet;
	for (int32 Try = 0; Try < 8; ++Try)
	{
		const double A = CYaw + (Try % 2 ? 1 : -1) * (0.25 + 0.2 * Try) + Rnd(-0.1, 0.1);
		const FVector D = YawDir(A);
		double R = 13.0;
		FTravHit H; if (Raycast(Pf + FVector(0, 0, 1), D, R + 1, H) && !H.bGround) R = H.Distance - 1.5;
		if (R < 8) continue;
		FVector P = Pf + D * R; P.Z = GroundHeight(P.X, P.Y, Pf.Z + 2);
		const TCHAR Ch = ReserveSpec[ReserveSpec.Len() - Reserve];
		--Reserve; SpawnCd = 0.6;
		SpawnEnemy(Ch, P);
		LogEvent(FString::Printf(TEXT("reinforcement %s %c at %.1f m"), *Enemies.Last()->Tag(), Ch, R));
		return;
	}
}

void AWHCombatDirector::EndFight(bool bWon)""")
e.rep("""	Threats.Reset(); MeleeToken = nullptr; GunToken = nullptr;""","""	Threats.Reset(); MeleeTokens.Reset(); GunTokens.Reset();""")
e.save(); print('e1 ok')
