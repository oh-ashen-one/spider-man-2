import sys; sys.path.insert(0,'.')
from ed import Ed
D='/Users/midir/sm2-n1/combat/unreal/WebHomage/Source/WebHomage/Combat/'
h=Ed(D+'WHCombatDirector.h')
h.rep("""	bool Frozen() const { return TimeScale < 0.05 && SlowK < 0.5; }""","""	bool Frozen() const { return bHitStop; }
	bool bHitStop = false;""")
h.save()
c=Ed(D+'WHCombatDirector.cpp')
c.rep("""	double Sc = 1, Slow = 0;""","""	double Sc = 1, Slow = 0; bool bHS = false;""")
c.rep("""		if (R.bSlow) { const double Left = R.Until - RTime; const double K = Smooth(Left / R.Ease); S = 1 - (1 - R.Scale) * K; Slow = FMath::Max(Slow, 1 - S); }""",
"""		if (R.bSlow) { const double Left = R.Until - RTime; const double K = Smooth(Left / R.Ease); S = 1 - (1 - R.Scale) * K; Slow = FMath::Max(Slow, 1 - S); }
		else bHS = true;""")
c.rep("""	TimeScale = Sc; SlowK = Slow;""","""	TimeScale = Sc; SlowK = Slow; bHitStop = bHS;""")
c.rep("""	if (TimeScale < 0.05) ++NFrozenFrames;""","""	if (bHitStop) ++NFrozenFrames;""")
c.rep("""		Frame, RTime, TimeScale, TimeScale < 0.05 ? 1 : 0, CineK,""","""		Frame, RTime, TimeScale, bHitStop ? 1 : 0, CineK,""")
c.save(); print('ok')
