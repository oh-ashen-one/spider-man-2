import sys; sys.path.insert(0,'.')
from ed import Ed
d=Ed('/Users/midir/sm2-n1/combat/unreal/WebHomage/Source/WebHomage/Combat/WHCombatDirector.cpp')
d.rep("""	Slowmo(Dur + 0.25, 0.3, 0.45);""","""	Slowmo(0.45, 0.55, 0.25);   // a light pre-slow on the wind-up; the takedown blow itself gets the deep slow-mo (PlayerHit)""")
d.rep("""		if (H.Kind == "finisher") HitStop(6); else if (Heavy > 0.5) HitStop(5); else HitStop(4);""",
"""		if (H.Kind == "finisher") HitStop(6); else if (Heavy > 0.5) HitStop(5); else HitStop(4);
		if (H.Kind == "finisher")
		{ // finisher beat: freeze, then x0.25 slow-mo while the victim flies, the close-up camera holds 1.4 s past the blow
			Slowmo(1.1, 0.25, 0.5); Shake(0.35); Impact(0.4);
			if (CineS.bOn) CineS.Dur = FMath::Max(CineS.Dur, CineS.T + 1.4);
		}""")
d.save(); print('ok')
