import sys; sys.path.insert(0,'.')
from ed import Ed
p='/Users/midir/sm2-n1/combat/unreal/WebHomage/Source/WebHomage/Combat/WHCombatDirector.cpp'
e=Ed(p)
s=e.s
a=s.index('	// surround: melee enemies around the player at ~3 m, gunmen at ~10 m')
b=s.index('FVector AWHCombatDirector::SlotFor(')
new='''	// surround: melee enemies around the player at ~3 m, gunmen at ~10 m. r02: the ring stays in the arc the combat camera sees
	// (+-100 deg from its view direction), so nobody stands between the lens and the hero and the whole group is on screen.
	const bool bCamArc = CamW > 0.3;
	for (int32 Gp = 0; Gp < 2; ++Gp)
	{
		TArray<AWHEnemy*> Group;
		for (AWHEnemy* E : Standing) if ((E->Type == EWHEnemyType::Gunman) == (Gp == 1)) Group.Add(E);
		if (!Group.Num()) continue;
		const bool bGun = Gp == 1;
		const double Arc = bGun ? 0.62 : 1.75;
		TArray<double> Ang;
		for (AWHEnemy* E : Group) Ang.Add(FMath::Atan2(E->Pos.Y - Pf.Y, E->Pos.X - Pf.X));
		const double MinSep = bGun ? 0.35 : FMath::Min((bCamArc ? 2 * Arc : 2 * PI) / Group.Num(), 1.1);
		for (int32 It = 0; It < 6; ++It)
		{
			for (int32 i = 0; i < Ang.Num(); ++i)
				for (int32 j = i + 1; j < Ang.Num(); ++j)
				{
					const double D = AngWrap(Ang[j] - Ang[i]);
					if (FMath::Abs(D) < MinSep) { const double Push = (MinSep - FMath::Abs(D)) * 0.5 * (D >= 0 ? 1 : -1); Ang[i] -= Push; Ang[j] += Push; }
				}
			if (bCamArc) for (double& A : Ang) { const double R = AngWrap(A - CYaw); A = CYaw + FMath::Clamp(R, -Arc, Arc); }
		}
		for (int32 i = 0; i < Group.Num(); ++i)
		{
			AWHEnemy* E = Group[i];
			double R = bGun ? 8.5 + (i % 2) * 1.5 : E->Type == EWHEnemyType::Brute ? 3.6 : 2.8 + (i % 2) * 0.9;
			if (Me->bAirborne && !bGun) R += 1.2;
			const FVector D(FMath::Cos(Ang[i]), FMath::Sin(Ang[i]), 0);
			FTravHit H;
			if (Raycast(Pf + FVector(0, 0, 1), D, R + 0.6, H) && !H.bGround) R = FMath::Max(1.8, H.Distance - 0.8);
			Slots.Add(E, FVector(Pf.X + D.X * R, Pf.Y + D.Y * R, Pf.Z));
		}
	}
	// r02 aggression scheduler: several committed attackers, and a new wind-up at least every ~0.6-0.8 s (SM2 street fights keep
	// the pressure on). Melee attackers are not sent while the hero is airborne (they could not reach him): gunmen fill those gaps.
	MeleeTokens.RemoveAll([](const TWeakObjectPtr<AWHEnemy>& W) { return !W.IsValid() || !W->Alive() || (W->State != EWHEnemyState::Approach && W->State != EWHEnemyState::Attack); });
	GunTokens.RemoveAll([](const TWeakObjectPtr<AWHEnemy>& W) { return !W.IsValid() || !W->Alive() || (W->State != EWHEnemyState::Aim && W->State != EWHEnemyState::Fire); });
	const double Gap = LastAttackRT < 0 ? 9 : RTime - LastAttackRT;
	const bool bPressure = Gap > 0.55;
	const int32 MaxMelee = Gap > 0.7 ? 3 : 2;
	if (MeleeTokens.Num() < MaxMelee && (GlobalCd <= 0 || bPressure) && !Me->bAirborne)
	{
		AWHEnemy* Best = nullptr; double Bs = 1e18;
		for (AWHEnemy* E : Standing)
		{
			if ((E->Type == EWHEnemyType::Gunman && E->bHasGun) || E->State != EWHEnemyState::Hold || (E->Cd > 0 && !bPressure)) continue;
			const double D = HDist(E->Pos, Pf); if (D > 9) continue;
			const double Sc = D + Rng.FRand() * 2 + (E->Cd > 0 ? 2 : 0);
			if (Sc < Bs) { Bs = Sc; Best = E; }
		}
		if (Best) { MeleeTokens.Add(Best); Best->Set(EWHEnemyState::Approach); GlobalCd = Rnd(0.25, 0.5); LogEvent(TEXT("token melee ") + Best->Tag()); }
	}
	const int32 MaxGun = (Me->bAirborne || Gap > 0.6) ? 2 : 1;
	if (GunTokens.Num() < MaxGun && (GunCd <= 0 || Gap > 0.6))
	{
		for (AWHEnemy* E : Standing)
		{
			if (!E->bHasGun || E->State != EWHEnemyState::Hold || (E->Cd > 0 && Gap < 0.6)) continue;
			const double D = HDist(E->Pos, Pf); if (D > 24 || D < 2.5) continue;
			const FVector From = E->Pos + FVector(0, 0, 1.4), To = PlayerChest();
			FTravHit H;
			if (Raycast(From, (To - From).GetSafeNormal(), FVector::Dist(From, To) - 0.5, H)) continue;
			GunTokens.Add(E); E->Set(EWHEnemyState::Aim); E->AimDur = 0.8; GunCd = Rnd(0.4, 0.9); Threat(E, 0.8, TEXT("gun"));
			LogEvent(TEXT("token gun ") + E->Tag());
			break;
		}
	}
}

'''
e.s=s[:a]+new+s[b:]
e.save(); print('e2 ok')
