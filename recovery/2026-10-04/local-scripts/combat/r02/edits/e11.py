import sys; sys.path.insert(0,'.')
from ed import Ed
D='/Users/midir/sm2-n1/combat/unreal/WebHomage/Source/WebHomage/Combat/'
h=Ed(D+'WHCombatDirector.h')
h.rep("""	double CYaw = 0, CYawGoal = 0, CDist = 5.2, CPitch = 20, CFov = 75, CineK = 0;""","""	double CYaw = 0, CYawGoal = 0, CDist = 5.2, CPitch = 20, CFov = 75, CineK = 0, CineExtra = 0;""")
h.save()
c=Ed(D+'WHCombatDirector.cpp')
c.rep("""			if (!CineS.bSide)
			{
				const FVector Perp(-Ax.Y, Ax.X, 0);
				const double Sg = FVector::DotProduct(Perp, CamP - Mid) >= 0 ? 1 : -1;
				CineS.Side = (Perp * Sg * 0.9 - Ax * 0.45).GetSafeNormal(); CineS.Dist = 2.4 + FVector::Dist(A, Tp) * 0.6; CineS.bSide = true;
			}
			FVector Cp = Mid + CineS.Side * (CineS.Dist + CineS.T * 0.3); Cp.Z = Mid.Z + 0.3;""","""			if (!CineS.bSide)
			{ // 3/4 side candidates; no wall, no other body near the lens or on the lens-hero / lens-victim lines
				const FVector Perp(-Ax.Y, Ax.X, 0);
				CineS.Dist = 3.0 + FVector::Dist(A, Tp) * 0.7; CineExtra = 0;
				double Bs = 1e18;
				for (double Sg : { 1.0, -1.0 })
					for (double Bk : { -0.45, 0.0, 0.45 })
					{
						const FVector Sd = (Perp * Sg * 0.9 + Ax * Bk).GetSafeNormal();
						FVector Cp = Mid + Sd * CineS.Dist; Cp.Z = Mid.Z + 0.4;
						double Sc = -FVector::DotProduct(Sd, FlatNorm(CamP - Mid)) * 0.8 + (Bk > 0 ? 0.6 : 0);
						FTravHit H2; if (Raycast(Mid, Sd, CineS.Dist + 0.5, H2)) Sc += 10;
						for (AWHEnemy* E : Enemies)
						{
							if (!E || E == T || E->State == EWHEnemyState::Out || E->Stuck) continue;
							const FVector Ep = E->Pos + FVector(0, 0, 1.0);
							if (HDist(Ep, Cp) < 2.4) Sc += 6;
							for (const FVector& Tg : { A, Tp }) if (FVector::Dist(FMath::ClosestPointOnSegment(Ep, Cp, Tg), Ep) < 0.8) Sc += 4;
						}
						if (Sc < Bs) { Bs = Sc; CineS.Side = Sd; }
					}
				CineS.bSide = true;
			}
			FVector Cp = Mid + CineS.Side * (CineS.Dist + CineExtra + CineS.T * 0.25); Cp.Z = Mid.Z + 0.4;""")
c.rep("""			const FRotator Cr = (Mid + FVector(0, 0, 0.1) - Cp).Rotation();""","""			const FRotator Cr = (Mid + FVector(0, 0, 0.1) - Cp).Rotation();
			// keep hero + victim inside a 7 % border: back off smoothly while either leaves it
			const double Ov = OutBy(Cp, Cr, HeroTop, 0.07) + OutBy(Cp, Cr, HeroFeet, 0.07) + OutBy(Cp, Cr, Tp + FVector(0, 0, 0.6), 0.05) + OutBy(Cp, Cr, T->Pos, 0.05);
			if (Ov > 0) CineExtra = FMath::Min(3.0, CineExtra + RDt * 4.0);""")
c.rep("""			Fov = FMath::Lerp(Fov, 58.0, K);""","""			Fov = FMath::Lerp(Fov, 62.0, K);""")
c.save(); print('ok')
