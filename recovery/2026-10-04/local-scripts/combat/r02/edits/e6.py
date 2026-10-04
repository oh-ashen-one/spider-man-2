import sys; sys.path.insert(0,'.')
from ed import Ed
D='/Users/midir/sm2-n1/combat/unreal/WebHomage/Source/WebHomage/Combat/'
h=Ed(D+'WHEnemy.h')
h.rep("""	bool bMoving = false;
	int32 HitsTaken = 0;""","""	bool bMoving = false;
	int32 HitsTaken = 0;
	FVector Slide = FVector::ZeroVector;   // r02: hit push (m/s, decays): every light hit moves the victim >= 0.3 m
	/** r02: attack warning visible (melee / brute wind-up until the blow, gun aim + burst). */
	bool WarnOn() const;""")
h.rep("""	UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> CocoonMat;""","""	UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> CocoonMat;
	UPROPERTY(Transient) TObjectPtr<UStaticMeshComponent> WarnBar;
	UPROPERTY(Transient) TObjectPtr<UStaticMeshComponent> WarnDot;
	UPROPERTY(Transient) TObjectPtr<UStaticMeshComponent> Laser;
	UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> WarnMat;
	UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> LaserMat;
	double WarnT = 0;
	void UpdateWarn(double Dt);""")
h.save()
c=Ed(D+'WHEnemy.cpp')
c.rep("""	static FWHEnemyType Brute{ 150, 2.4, 1.7, 18, 1.24, { "bruteSlam", "thugPunch1", "bruteSlam" } };""",
"""	static FWHEnemyType Brute{ 150, 2.4, 1.7, 18, 1.3, { "bruteSlam", "thugPunch1", "bruteSlam" } };   // r02: taller + much wider (below)""")
c.rep("""	SetActorScale3D(Type == EWHEnemyType::Brute ? FVector(S * 1.1, S * 1.1, S) : FVector(S));""",
"""	SetActorScale3D(Type == EWHEnemyType::Brute ? FVector(S * 1.4, S * 1.45, S) : FVector(S));   // brute: bulk reads by silhouette""")
c.rep("""	SyncActor();
	Play("thugIdle", 0.25);
}""","""	// r02 attack warning: a glowing "!" over the head (orange = melee, deep red = brute / gun) + the gunman's aim laser
	UStaticMesh* Cyl = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (UMaterialInterface* M = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Combat/Materials/M_CmbFX.M_CmbFX")))
	{
		WarnMat = UMaterialInstanceDynamic::Create(M, this); LaserMat = UMaterialInstanceDynamic::Create(M, this);
		LaserMat->SetVectorParameterValue(TEXT("Color"), FLinearColor(6.f, 0.25f, 0.2f));
	}
	auto Mk = [this](UStaticMesh* SMh, UMaterialInstanceDynamic* Mt)
	{
		UStaticMeshComponent* C = NewObject<UStaticMeshComponent>(this);
		C->SetStaticMesh(SMh); C->SetCollisionEnabled(ECollisionEnabled::NoCollision); C->SetCastShadow(false);
		C->SetUsingAbsoluteLocation(true); C->SetUsingAbsoluteRotation(true); C->SetUsingAbsoluteScale(true);
		C->SetupAttachment(Root); C->RegisterComponent(); if (Mt) C->SetMaterial(0, Mt); C->SetVisibility(false);
		return C;
	};
	WarnBar = Mk(Sph, WarnMat); WarnDot = Mk(Sph, WarnMat); Laser = Mk(Cyl, LaserMat);
	SyncActor();
	Play("thugIdle", 0.25);
}

bool AWHEnemy::WarnOn() const
{
	if (!Alive()) return false;
	return (State == EWHEnemyState::Attack && !bSwung) || State == EWHEnemyState::Aim || (State == EWHEnemyState::Fire && Shots < 3);
}

void AWHEnemy::UpdateWarn(double Dt)
{
	const bool bOn = WarnOn();
	WarnT = bOn ? WarnT + Dt : 0;
	if (WarnBar) WarnBar->SetVisibility(bOn);
	if (WarnDot) WarnDot->SetVisibility(bOn);
	const bool bGun = State == EWHEnemyState::Aim || State == EWHEnemyState::Fire;
	if (Laser) Laser->SetVisibility(bOn && bGun && bHasGun && Dir.IsValid());
	if (!bOn) return;
	const double Pop = FMath::Min(1.0, WarnT / 0.08), Pulse = 1.0 + 0.12 * FMath::Sin(WarnT * 26.0);
	const FVector H = FVector(Pos.X, Pos.Y, Pos.Z + 1.95 * T.Scale + 0.25);
	const double K = 0.9 * Pop * Pulse;
	WarnBar->SetWorldLocationAndRotation((H + FVector(0, 0, 0.2)) * 100.0, FQuat::Identity);
	WarnBar->SetWorldScale3D(FVector(0.085, 0.085, 0.26) * K);
	WarnDot->SetWorldLocationAndRotation(H * 100.0, FQuat::Identity);
	WarnDot->SetWorldScale3D(FVector(0.09) * K);
	if (WarnMat)
	{
		const FLinearColor Cw = bGun || Type == EWHEnemyType::Brute ? FLinearColor(7.f, 0.5f, 0.25f) : FLinearColor(7.f, 2.6f, 0.3f);
		WarnMat->SetVectorParameterValue(TEXT("Color"), Cw); WarnMat->SetScalarParameterValue(TEXT("Opacity"), 1.f);
	}
	if (Laser && Laser->IsVisible())
	{
		const FVector A = Muzzle(), B = Dir->PlayerChest();
		const FVector Dd = B - A; const double L = Dd.Size();
		Laser->SetWorldLocationAndRotation((A + B) * 50.0, FQuat::FindBetweenNormals(FVector::UpVector, Dd / FMath::Max(1e-3, L)));
		Laser->SetWorldScale3D(FVector(0.012, 0.012, L));
		if (LaserMat) LaserMat->SetScalarParameterValue(TEXT("Opacity"), float(State == EWHEnemyState::Aim ? 0.35 + 0.65 * FMath::Min(1.0, St / FMath::Max(0.1, AimDur)) : 1.0));
	}
}""")
# light hit: flinch pose in the contact frame + push
c.rep("""	if (bArmored && !bDead) { Flinch = 1; FlinchDir = Rng.FRand() < 0.5 ? -1 : 1; MoveXZ(H.Dir.X * 0.15, H.Dir.Y * 0.15); R.bArmored = true; return R; }""",
"""	if (bArmored && !bDead) { Flinch = 1; FlinchDir = Rng.FRand() < 0.5 ? -1 : 1; Slide = FlatNorm(H.Dir) * 2.4; R.bArmored = true; return R; }""")
c.rep("""	Set(EWHEnemyState::Stagger); TurnRate = FMath::Abs(Rel) > 2.3 ? 14 : 5;
	const double Ts = 1.15 + Rng.FRand() * 0.15;
	Play(S == "back" ? FName("thugStumbleBack") : S == "left" ? FName("thugStumbleLeft") : FName("thugStumbleRight"), 0.06, Ts, 1);""",
"""	Set(EWHEnemyState::Stagger); TurnRate = FMath::Abs(Rel) > 2.3 ? 14 : 5;
	const double Ts = 1.15 + Rng.FRand() * 0.15;
	// r02: the flinch is already in the contact frame (clip entered at 0.1 s with a 0.02 s fade + procedural head / torso snap),
	// then the hit-stop holds it and the victim is pushed ~0.4 m along the blow
	Play(S == "back" ? FName("thugStumbleBack") : S == "left" ? FName("thugStumbleLeft") : FName("thugStumbleRight"), 0.02, Ts, 1, 0.1);
	Flinch = 1; FlinchDir = S == "left" ? -1 : S == "right" ? 1 : (Rng.FRand() < 0.5 ? -1 : 1);
	Slide = FlatNorm(H.Dir) * 2.6;""")
c.rep("""	Flinch = FMath::Max(0.0, Flinch - Dt * 5);""","""	Flinch = FMath::Max(0.0, Flinch - Dt * 5);
	if (Slide.SizeSquared() > 1e-4 && State != EWHEnemyState::Air && State != EWHEnemyState::Knock && State != EWHEnemyState::Yanked && Stuck == 0)
	{ MoveXZ(Slide.X * Dt, Slide.Y * Dt); Slide *= FMath::Exp(-6.0 * Dt); }
	else if (Slide.SizeSquared() <= 1e-4) Slide = FVector::ZeroVector;""")
c.rep("""		if (Dist <= Reach + 1.0 && FMath::Abs(AngWrap(FaceP - Yaw)) < 0.6) StartSwing();""",
"""		if (Dist <= Reach + 1.6 && FMath::Abs(AngWrap(FaceP - Yaw)) < 0.8) StartSwing();   // r02: wind up earlier, close in during it""")
c.rep("""	SyncActor();
	UpdateCocoon(Dt);
}""","""	SyncActor();
	UpdateCocoon(Dt);
	UpdateWarn(Dt);
}""")
c.save(); print('enemy ok')
