import sys; sys.path.insert(0,'.')
from ed import Ed
c=Ed('/Users/midir/sm2-n1/combat/unreal/WebHomage/Source/WebHomage/Combat/WHCombatDirector.cpp')
c.rep("""			if (B.bGuard && ((B.bFired && RTime - B.FiredRT < 1.2) || (!B.bFired && B.T - RTime < 0.5 && B.T - RTime > -1.5))) bGuarded = true;""",
"""			if (B.bGuard && ((B.bFired && RTime - B.FiredRT < 0.45) || (!B.bFired && B.T - RTime < 0.25 && B.T - RTime > -1.5))) bGuarded = true;""")
c.rep("""	if (MeleeTokens.Num() < MaxMelee && (GlobalCd <= 0 || bPressure) && !Me->bAirborne)""",
"""	if (MeleeTokens.Num() < MaxMelee && (GlobalCd <= 0 || bPressure) && (!Me->bAirborne || Gap > 0.8))""")
c.rep("""			const double Sc = D + Rng.FRand() * 2 + (E->Cd > 0 ? 2 : 0);
			if (Sc < Bs) { Bs = Sc; Best = E; }
		}
		if (Best) { MeleeTokens.Add(Best); Best->Set(EWHEnemyState::Approach); GlobalCd = Rnd(0.25, 0.5); LogEvent(TEXT("token melee ") + Best->Tag()); }""",
"""			const double Sc = D + Rng.FRand() * 2 + (E->Cd > 0 ? 2 : 0);
			if (Sc < Bs) { Bs = Sc; Best = E; }
		}
		if (Best)
		{
			MeleeTokens.Add(Best); Best->Set(EWHEnemyState::Approach); GlobalCd = Rnd(0.25, 0.5); LogEvent(TEXT("token melee ") + Best->Tag());
			if (Me->bAirborne) Best->StartSwing();   // hero above him: he swings up at once (it misses unless the hero comes down into it)
		}""")
c.rep("""			const FRotator Cr = (Mid + FVector(0, 0, 0.1) - Cp).Rotation();""","""			const FVector LookC = Mid + FVector(0, 0, 0.1);
			const FRotator Cr = (LookC - Cp).Rotation();""")
c.rep("""			CamP = CamP + (Cp - CamP) * K;
			CamR = FQuat::Slerp(CamR.Quaternion(), Cr.Quaternion(), K).Rotator();""","""			// blend position and LOOK TARGET (not the rotation): hero + victim stay centred through the whole ease
			const FVector Look0 = Focus;
			CamP = CamP + (Cp - CamP) * K;
			CamR = (Look0 + (LookC - Look0) * K - CamP).Rotation();""")
c.save(); print('ok')
