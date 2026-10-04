import sys; sys.path.insert(0,'.')
from ed import Ed
D='/Users/midir/sm2-n1/combat/unreal/WebHomage/Source/WebHomage/Combat/'
h=Ed(D+'WHCombatDirector.h')
h.rep("""	double Window = 3.0;
	FString Label;""","""	double Window = 3.0;
	bool bGuard = false;  // r02: no reflex dodge 0.5 s before / 1.2 s after this beat (launchers, juggles, finishers)
	FString Label;""")
h.save()
c=Ed(D+'WHCombatDirector.cpp')
c.rep("""				B.React = FName(*O.Str_(TEXT("react"))); B.Window = O.Num_(TEXT("window"), 3.0);""","""				B.React = FName(*O.Str_(TEXT("react"))); B.Window = O.Num_(TEXT("window"), 3.0);
				B.bGuard = O.Get(TEXT("guard")) && O.Get(TEXT("guard"))->N > 0;""")
c.rep("""		if (Th && R >= 0.08 && R <= 0.22 && MN != "down" && MN != "finisher" && MN != "hit" && MN != "dodge" && !Me->bAirborne)""","""		bool bGuarded = false;
		for (const FWHBeat& B : Beats)
			if (B.bGuard && ((B.bFired && RTime - B.FiredRT < 1.2) || (!B.bFired && B.T - RTime < 0.5 && B.T - RTime > -1.5))) bGuarded = true;
		if (Th && !bGuarded && R >= 0.08 && R <= 0.22 && MN != "down" && MN != "finisher" && MN != "hit" && MN != "dodge" && !Me->bAirborne)""")
c.rep("""	const int32 MaxGun = Me->bAirborne ? 2 : 1;""","""	if (Gap > 0.8)
	{ // pressure: the nearest attacker still closing in winds up now (the wind-up itself closes up to ~1.5 m)
		AWHEnemy* Best = nullptr; double Bd = 1e9;
		for (const auto& W : MeleeTokens)
			if (W.IsValid() && W->State == EWHEnemyState::Approach) { const double Dd = HDist(W->Pos, Pf); if (Dd < W->T.Reach + 2.6 && Dd < Bd) { Bd = Dd; Best = W.Get(); } }
		if (Best) Best->StartSwing();
	}
	const int32 MaxGun = (Me->bAirborne || Gap > 0.9) ? 2 : 1;""")
c.save(); print('ok')
