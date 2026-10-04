import sys; sys.path.insert(0,'.')
from ed import Ed
D='/Users/midir/sm2-n1/combat/unreal/WebHomage/Source/WebHomage/Combat/'
h=Ed(D+'WHCombatDirector.h')
h.rep("""	double HeroMinHp = 0;""","""	double HeroMinHp = 0;
	double ReflexCd = 0, LastReflexRT = -9, LastPerfectSlowRT = -9;   // script "reflex": scripted player dodges telegraphed blows (min interval s)""")
h.save()
c=Ed(D+'WHCombatDirector.cpp')
c.rep("""	KeepAlive = int32(J.Num_(TEXT("keep"), 0));""","""	KeepAlive = int32(J.Num_(TEXT("keep"), 0));
	ReflexCd = J.Num_(TEXT("reflex"), 0);""")
c.rep("""	if (RTime > StickUntil) StickDir = FVector::ZeroVector;""","""	if (RTime > StickUntil) StickDir = FVector::ZeroVector;
	if (ReflexCd > 0 && bEngaged && RTime - LastReflexRT > ReflexCd)
	{ // record runs: a skilled player reacts to the telegraph (the freeze step turns every reflex into a fixed-time beat)
		const FWHThreat* Th = NearestThreat();
		const double R = Th ? Th->At - Time : 9;
		const FName MN = Me->MoveName();
		if (Th && R >= 0.08 && R <= 0.22 && MN != "down" && MN != "finisher" && MN != "hit" && MN != "dodge" && !Me->bAirborne)
		{
			LastReflexRT = RTime; KeyPress("dodge");
			const FString Row = FString::Printf(TEXT("{\\"t\\":%.3f,\\"rt\\":%.3f,\\"gt\\":%.3f,\\"key\\":\\"dodge\\",\\"hold\\":0.00,\\"toward\\":\\"\\",\\"label\\":\\"reflex dodge %.2f\\",\\"move_before\\":\\"%s\\",\\"react\\":\\"reflex %s in %.3f\\"}"),
				RTime, RTime, Time, RTime, *MN.ToString(), Th->E.IsValid() ? *Th->E->Tag() : TEXT("?"), R);
			BeatRows.Add(Row);
			UE_LOG(LogWebHomage, Display, TEXT("WH_CMB_BEAT %s"), *Row);
		}
	}""")
c.rep("""		Slowmo(0.85, 0.22, 0.35); Banner(TEXT("PERFECT DODGE")); Me->Focus = FMath::Min(3.0, Me->Focus + 0.35);""",
"""		// r02: short slow-mo, at most every 3 s (r01's 0.85 s x0.22 on every perfect dodge made the fight float)
		if (RTime - LastPerfectSlowRT > 3.0) { Slowmo(0.45, 0.35, 0.25); LastPerfectSlowRT = RTime; }
		Banner(TEXT("PERFECT DODGE")); Me->Focus = FMath::Min(3.0, Me->Focus + 0.35);""")
c.rep("""	const bool bMiss = Me->Invuln() || bBlocked || (Me->bAirborne && Rng.FRand() < 0.6);""",
"""	const bool bMiss = Me->Invuln() || bBlocked || (Me->bAirborne && Rng.FRand() < 0.6) || (Me->Busy() && Rng.FRand() < 0.75);""")
c.rep("""	const int32 MaxGun = (Me->bAirborne || Gap > 0.6) ? 2 : 1;
	if (GunTokens.Num() < MaxGun && (GunCd <= 0 || Gap > 0.6))""","""	const int32 MaxGun = Me->bAirborne ? 2 : 1;
	if (GunTokens.Num() < MaxGun && (GunCd <= 0 || Gap > 0.8))""")
c.rep("""			if (!E->bHasGun || E->State != EWHEnemyState::Hold || (E->Cd > 0 && Gap < 0.6)) continue;""",
"""			if (!E->bHasGun || E->State != EWHEnemyState::Hold || (E->Cd > 0 && Gap < 0.8)) continue;""")
c.rep("""			GunTokens.Add(E); E->Set(EWHEnemyState::Aim); E->AimDur = 0.8; GunCd = Rnd(0.4, 0.9); Threat(E, 0.8, TEXT("gun"));""",
"""			GunTokens.Add(E); E->Set(EWHEnemyState::Aim); E->AimDur = 0.8; GunCd = Rnd(1.0, 1.8); Threat(E, 0.8, TEXT("gun"));""")
c.rep("""	if (GunTokens.RemoveAll([E](const TWeakObjectPtr<AWHEnemy>& W) { return W.Get() == E; }) > 0) GunCd = Rnd(0.5, 1.2);""",
"""	if (GunTokens.RemoveAll([E](const TWeakObjectPtr<AWHEnemy>& W) { return W.Get() == E; }) > 0) GunCd = FMath::Max(GunCd, Rnd(0.8, 1.6));""")
c.save(); print('ok')
