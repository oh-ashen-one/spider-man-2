import sys; sys.path.insert(0,'.')
from ed import Ed
D='/Users/midir/sm2-n1/combat/unreal/WebHomage/Source/WebHomage/Combat/'
h=Ed(D+'WHCombatFx.h')
h.rep("""	double Width = 0.012, Sag = 0;
	int32 Tag = 0;""","""	double Width = 0.012, Sag = 0;
	int32 Tag = 0;
	bool bReal = false;                   // r02 impact sparks: REAL-time life (hold static for Hold s, then fly + fade); others: game time
	double Hold = 0;""")
h.rep("""	void Update(double Dt);""","""	void Update(double Dt, double RealDt);""")
h.save()
c=Ed(D+'WHCombatFx.cpp')
c.rep("""void FWHCombatFx::Update(double Dt)
{
	for (FWHFxItem& It : Items)
	{
		if (!It.bLive) continue;
		It.T += Dt;
		if (It.T >= It.Life) { It.bLive = false; It.A = nullptr; It.B = nullptr; It.Comp->SetVisibility(false); continue; }
		It.Vel += It.Gravity * Dt;
		if (It.Drag > 0) It.Vel *= FMath::Exp(-It.Drag * Dt);
		It.Pos += It.Vel * Dt;
		Place(It, It.T / It.Life);
	}
}""","""void FWHCombatFx::Update(double GameDt, double RealDt)
{
	for (FWHFxItem& It : Items)
	{
		if (!It.bLive) continue;
		const double Dt = It.bReal ? RealDt : GameDt;
		It.T += Dt;
		if (It.T >= It.Life) { It.bLive = false; It.A = nullptr; It.B = nullptr; It.Comp->SetVisibility(false); continue; }
		if (It.bReal && It.T < It.Hold) { Place(It, 0); continue; }   // static while the hit-stop holds the frame
		It.Vel += It.Gravity * Dt;
		if (It.Drag > 0) It.Vel *= FMath::Exp(-It.Drag * Dt);
		It.Pos += It.Vel * Dt;
		Place(It, It.bReal ? (It.T - It.Hold) / FMath::Max(1e-3, It.Life - It.Hold) : It.T / It.Life);
	}
}""")
a=c.s.index('void FWHCombatFx::Hit('); b=c.s.index('void FWHCombatFx::Dust(')
c.s=c.s[:a]+'''void FWHCombatFx::Hit(const FVector& P, const FVector& Dir, double Heavy, const FLinearColor* Color)
{
	// r02: a small additive spark burst (critic r01: the opaque white disc covered the contact). Real-time life of 6 frames at 60 fps:
	// static for the first 4 (the hit-stop freeze), then the streaks fly out and everything is gone by frame 6. Core <= ~0.2 m.
	const FLinearColor C = Color ? *Color * 0.8f : FLinearColor(4.0f, 2.8f, 1.3f);
	const double Life = 0.1, Hold = 0.066;
	{
		FWHFxItem& F = Alloc(EWHFxMat::Glow, Sphere);
		F.bReal = true; F.Hold = Hold; F.Pos = P; F.Life = Life;
		F.Size0 = FVector(0.1 + 0.08 * Heavy); F.Size1 = FVector(0.05);
		F.Color = C; F.Op0 = 0.9; F.Op1 = 0.0;
		Place(F, 0);
	}
	const int32 N = 6 + int32(6 * Heavy);
	const FVector D = Dir.GetSafeNormal();
	for (int32 i = 0; i < N; ++i)
	{
		FWHFxItem& S = Alloc(EWHFxMat::Glow, Cyl);
		const FVector R = (D * 0.9 + Rng.GetUnitVector()).GetSafeNormal();
		const double Len = Rng.FRandRange(0.1, 0.22 + 0.12 * Heavy);
		S.bReal = true; S.Hold = Hold; S.Life = Life;
		S.Dir = R; S.Pos = P + R * (0.06 + Len * 0.5); S.Vel = R * Rng.FRandRange(4.0, 7.0); S.Drag = 4.0;
		S.Size0 = FVector(0.012 + 0.006 * Heavy, 0.012 + 0.006 * Heavy, Len); S.Size1 = FVector(0.004, 0.004, Len * 0.6);
		S.Color = FLinearColor(C.R * 1.1f, C.G, C.B * 0.7f); S.Op0 = 1.0; S.Op1 = 0.0;
		Place(S, 0);
	}
}

'''+c.s[b:]
c.save()
d=Ed(D+'WHCombatDirector.cpp')
d.rep("""	Fx.Update(Dt, Frozen() ? 0.0 : RDt);""","""	Fx.Update(Dt, RDt);""")
d.save()
print('fx ok')
