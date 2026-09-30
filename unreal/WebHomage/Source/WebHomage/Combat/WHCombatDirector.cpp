// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Combat/WHCombatDirector.h"
#include "Combat/WHCombatHero.h"
#include "Combat/WHCombatSpidey.h"
#include "Combat/WHCombatUtil.h"
#include "WebHomage.h"
#include "Camera/CameraComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/WorldSettings.h"
#include "HAL/FileManager.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Traversal/WebTraversalComponent.h"
#include "UnrealClient.h"

using namespace WHCmb;

static const double HH = 0.95;   // body centre over the feet (browser H)

AWHCombatDirector::AWHCombatDirector()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickGroup = TG_PrePhysics;
	SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
}

AWHCombatDirector::~AWHCombatDirector()
{
	delete Me; Me = nullptr;
}

void AWHCombatDirector::EndPlay(const EEndPlayReason::Type Reason)
{
	if (!bSummaryDone) { WriteTelemetry(); WriteSummary(); }
	Fx.Clear();
	Super::EndPlay(Reason);
}

void AWHCombatDirector::Init(AWHCombatHero* InHero)
{
	Hero = InHero;
	delete Me; Me = new FWHSpidey(this, InHero);
	Fx.Init(this);
	AddTickPrerequisiteActor(InHero);
	if (InHero->GetMesh()) InHero->GetMesh()->PrimaryComponentTick.AddPrerequisite(this, PrimaryActorTick);
	const TCHAR* Cmd = FCommandLine::Get();
	FParse::Value(Cmd, TEXT("WHCmbScript="), ScriptPath);
	FParse::Value(Cmd, TEXT("WHCmbFight="), FightSpec);
	FParse::Value(Cmd, TEXT("WHCmbDist="), FightDist);
	FParse::Value(Cmd, TEXT("WHCmbQuit="), QuitAt);
	FParse::Value(Cmd, TEXT("WHCmbShotName="), ShotName);
	FString ShotList;
	if (FParse::Value(Cmd, TEXT("WHCmbShots="), ShotList, false))
	{
		TArray<FString> Parts; ShotList.ParseIntoArray(Parts, TEXT(","));
		for (const FString& P : Parts) ShotTimes.Add(FCString::Atod(*P));
		ShotTimes.Sort();
	}
	if (!FParse::Value(Cmd, TEXT("WHCmbOut="), OutDir)) OutDir = FPaths::ProjectSavedDir() / TEXT("WHCombat");
	OutDir = FPaths::ConvertRelativePathToFull(OutDir);
	IFileManager::Get().MakeDirectory(*OutDir, true);
	if (!ScriptPath.IsEmpty()) LoadScript(ScriptPath);
	UE_LOG(LogWebHomage, Display, TEXT("WH_CMB director ready: script=%s fight=%s beats=%d shots=%d quit=%.1f out=%s"),
		*ScriptPath, *FightSpec, Beats.Num(), ShotTimes.Num(), QuitAt, *OutDir);
}

// ------------------------------------------------------------------------------------------------ script
// Minimal JSON reader for the script format (the module's Build.cs is shared: no Json module dependency). Values: objects,
// arrays, strings, numbers, true / false / null.
namespace
{
	struct FJ
	{
		enum EK { Null, Num, Str, Arr, Obj, Bool } K = Null;
		double N = 0; FString S; TArray<FJ> A; TArray<TPair<FString, FJ>> O;
		const FJ* Get(const TCHAR* Key) const { for (const auto& P : O) if (P.Key == Key) return &P.Value; return nullptr; }
		double Num_(const TCHAR* Key, double Def) const { const FJ* V = Get(Key); return V && V->K == Num ? V->N : Def; }
		FString Str_(const TCHAR* Key) const { const FJ* V = Get(Key); return V && V->K == Str ? V->S : FString(); }
	};
	struct FJParser
	{
		const FString& T; int32 I = 0; bool bErr = false;
		explicit FJParser(const FString& In) : T(In) {}
		void Ws() { while (I < T.Len() && FChar::IsWhitespace(T[I])) ++I; }
		bool Eat(TCHAR C) { Ws(); if (I < T.Len() && T[I] == C) { ++I; return true; } return false; }
		FJ Value()
		{
			FJ V; Ws(); if (I >= T.Len()) { bErr = true; return V; }
			const TCHAR C = T[I];
			if (C == '{')
			{
				++I; V.K = FJ::Obj;
				if (Eat('}')) return V;
				do { Ws(); FJ Key = Value(); if (Key.K != FJ::Str || !Eat(':')) { bErr = true; return V; } V.O.Add(TPair<FString, FJ>(Key.S, Value())); } while (Eat(','));
				if (!Eat('}')) bErr = true;
			}
			else if (C == '[')
			{
				++I; V.K = FJ::Arr;
				if (Eat(']')) return V;
				do { V.A.Add(Value()); } while (Eat(','));
				if (!Eat(']')) bErr = true;
			}
			else if (C == '"')
			{
				++I; V.K = FJ::Str;
				while (I < T.Len() && T[I] != '"') { if (T[I] == '\\' && I + 1 < T.Len()) ++I; V.S.AppendChar(T[I++]); }
				++I;
			}
			else if (T.Mid(I, 4) == TEXT("true")) { V.K = FJ::Bool; V.N = 1; I += 4; }
			else if (T.Mid(I, 5) == TEXT("false")) { V.K = FJ::Bool; V.N = 0; I += 5; }
			else if (T.Mid(I, 4) == TEXT("null")) { I += 4; }
			else
			{
				const int32 S0 = I;
				while (I < T.Len() && (FChar::IsDigit(T[I]) || T[I] == '-' || T[I] == '+' || T[I] == '.' || T[I] == 'e' || T[I] == 'E')) ++I;
				if (I == S0) { bErr = true; return V; }
				V.K = FJ::Num; V.N = FCString::Atod(*T.Mid(S0, I - S0));
			}
			return V;
		}
	};
}

void AWHCombatDirector::LoadScript(const FString& Path)
{
	FString Txt;
	if (!FFileHelper::LoadFileToString(Txt, *Path)) { UE_LOG(LogWebHomage, Error, TEXT("WH_CMB script missing: %s"), *Path); return; }
	FJParser P(Txt);
	const FJ J = P.Value();
	if (P.bErr || J.K != FJ::Obj) { UE_LOG(LogWebHomage, Error, TEXT("WH_CMB script parse error near %d: %s"), P.I, *Path); return; }
	if (J.Get(TEXT("spec"))) FightSpec = J.Str_(TEXT("spec"));
	FightDist = J.Num_(TEXT("dist"), FightDist);
	FightStartAt = J.Num_(TEXT("start"), FightStartAt);
	const double Q = J.Num_(TEXT("quit"), -1); if (Q > 0 && QuitAt < 0) QuitAt = Q;
	if (J.Get(TEXT("seed"))) Rng.Initialize(int32(J.Num_(TEXT("seed"), 0)));
	if (const FJ* Arr = J.Get(TEXT("beats")))
	{
		for (const FJ& O : Arr->A)
		{
			if (O.K != FJ::Obj) continue;
			FWHBeat B;
			B.T = O.Num_(TEXT("t"), 0); B.Key = FName(*O.Str_(TEXT("key"))); B.Hold = O.Num_(TEXT("hold"), 0);
			B.Toward = O.Str_(TEXT("toward")); B.Label = O.Str_(TEXT("label"));
			B.React = FName(*O.Str_(TEXT("react"))); B.Window = O.Num_(TEXT("window"), 3.0);
			Beats.Add(B);
		}
		Beats.Sort([](const FWHBeat& A, const FWHBeat& B) { return A.T < B.T; });
	}
}

void AWHCombatDirector::RunBeats()
{
	if (!bFightStarted && !FightSpec.IsEmpty() && RTime >= FightStartAt) { bFightStarted = true; StartFight(FightSpec, FightDist); }
	// release the scripted LMB hold
	for (FWHBeat& B : Beats)
	{
		if (B.Key == "attack" && B.Hold > 0 && B.bFired && B.Result.IsEmpty() && RTime >= B.FiredRT + B.Hold) { Input.LmbUp(); B.Result = TEXT("released"); }
	}
	if (RTime > StickUntil) StickDir = FVector::ZeroVector;
	for (FWHBeat& B : Beats)
	{
		if (B.bFired || RTime < B.T) continue;
		FString Why;
		if (B.React == "threat")
		{ // record-run reflex: press when the nearest threat is about to land (the frozen script replays the recorded time)
			const FWHThreat* Th = NearestThreat();
			const double R = Th ? Th->At - Time : 9;
			if (!(R >= 0.08 && R <= 0.25) && RTime < B.T + B.Window) continue;
			Why = R >= 0.08 && R <= 0.25 ? FString::Printf(TEXT("threat %s in %.3f"), Th && Th->E.IsValid() ? *Th->E->Tag() : TEXT("?"), R) : TEXT("window timeout");
		}
		else if (B.React == "free")
		{
			if (!Me->IsFree() && RTime < B.T + B.Window) continue;
			Why = Me->IsFree() ? TEXT("hero free") : TEXT("window timeout");
		}
		B.bFired = true; B.FiredRT = RTime; B.FiredGT = Time;
		StickDir = FVector::ZeroVector; StickUntil = RTime + 0.5;
		if (!B.Toward.IsEmpty())
		{
			for (AWHEnemy* E : Enemies) if (E && E->Tag() == B.Toward) StickDir = FlatNorm(E->Pos - Me->Pos);
		}
		if (B.Key == "attack")
		{
			Input.LmbDown(RTime, Time);
			if (B.Hold <= 0) Input.LmbUp();
		}
		else if (B.Key == "focus") { Me->Focus = 3; }
		else KeyPress(B.Key);
		const FString Row = FString::Printf(TEXT("{\"t\":%.3f,\"rt\":%.3f,\"gt\":%.3f,\"key\":\"%s\",\"hold\":%.2f,\"toward\":\"%s\",\"label\":\"%s\",\"move_before\":\"%s\",\"react\":\"%s\"}"),
			B.T, RTime, Time, *B.Key.ToString(), B.Hold, *B.Toward, *B.Label, *Me->MoveName().ToString(), *Why);
		BeatRows.Add(Row);
		UE_LOG(LogWebHomage, Display, TEXT("WH_CMB_BEAT %s"), *Row);
	}
}

// ------------------------------------------------------------------------------------------------ input
void AWHCombatDirector::KeyPress(FName Action) { if (bEngaged) Input.Press(Action, Time); }
void AWHCombatDirector::LmbDown() { if (bEngaged) Input.LmbDown(RTime, Time); }
void AWHCombatDirector::LmbUp() { Input.LmbUp(); }

// ------------------------------------------------------------------------------------------------ world
bool AWHCombatDirector::Raycast(const FVector& O, const FVector& D, double MaxD, FTravHit& Out) const
{
	if (!Hero || !Hero->GetTraversal()) return false;
	return Hero->GetTraversal()->TravWorld.Raycast(O, D, MaxD, Out);
}

double AWHCombatDirector::GroundHeight(double X, double Y, double FromZ) const
{
	if (!Hero || !Hero->GetTraversal()) return 0.0;
	const double G = Hero->GetTraversal()->TravWorld.GroundHeight(X, Y, FromZ);
	return G < -999 ? 0.0 : G;
}

// a hit is a facade (not a bin / lamp post) if the surface continues above and to both sides at about the same depth
bool AWHCombatDirector::IsFacade(const FVector& Point, const FVector& Normal) const
{
	FVector N(Normal.X, Normal.Y, 0); if (N.SizeSquared() < 0.25) return false; N.Normalize();
	const FVector Side(-N.Y, N.X, 0), Back = -N;
	static const double S[4][2] = { { 0, 1.4 }, { 0.9, 0.2 }, { -0.9, 0.2 }, { 0, 2.4 } };
	int32 Ok = 0;
	for (const auto& P : S)
	{
		FVector O = Point + N * 0.6 + Side * P[0]; O.Z += P[1];
		FTravHit H;
		if (Raycast(O, Back, 2.2, H) && H.Distance < 1.8) ++Ok;
	}
	return Ok >= 3;
}

bool AWHCombatDirector::FindWall(const FVector& Pos, const FVector& Dir, double MaxD, FVector& OutP, FVector& OutN) const
{
	FVector D0(Dir.X, Dir.Y, 0); if (D0.SizeSquared() < 1e-4) return false; D0.Normalize();
	double Best = 1e9; bool bAny = false;
	for (double A : { 0.0, 0.5, -0.5, 1.0, -1.0 })
	{
		const FVector D = FQuat(FVector::UpVector, A).RotateVector(D0);
		FTravHit H;
		if (Raycast(Pos, D, MaxD, H) && !H.bGround && FMath::Abs(H.Normal.Z) < 0.5 && H.Distance < Best && IsFacade(H.Point, H.Normal))
		{ Best = H.Distance; OutP = H.Point; OutN = H.Normal; bAny = true; }
	}
	return bAny;
}

// ------------------------------------------------------------------------------------------------ targeting
AWHEnemy* AWHCombatDirector::PickTarget(const FVector* Dir, double MaxD, const FVector& From, double MinD, double NeedView) const
{
	FVector Want;
	if (Dir && Dir->SizeSquared() > 0.04) Want = FlatNorm(*Dir);
	else Want = YawDir(Hero->GetTravCamera().Yaw + CamYawOff * Smooth(CamW));
	AWHEnemy* Best = nullptr; double Bs = 1e18;
	for (AWHEnemy* E : Enemies)
	{
		if (!E || !E->Targetable()) continue;
		const double D = HDist(From, E->Pos); if (D > MaxD || D < MinD) continue;
		if (FMath::Abs(E->Pos.Z - From.Z) > 6 && E->State != EWHEnemyState::Air) continue;
		if (E->State == EWHEnemyState::Air && E->Pos.Z - From.Z > 1.2 && !Me->bAirborne) continue;
		const FVector To = FlatNorm(E->Pos - From);
		const double Ang = FMath::Acos(FMath::Clamp(FVector::DotProduct(To, Want), -1.0, 1.0));
		if (NeedView > 0 && Ang > NeedView) continue;
		double Sc = D * 0.6 + Ang * 3.2;
		if (E == Me->Target.Get()) Sc -= 1.2;
		if (E->State == EWHEnemyState::Attack || E->State == EWHEnemyState::Approach) Sc -= 0.4;
		if (Sc < Bs) { Bs = Sc; Best = E; }
	}
	return Best;
}

// ------------------------------------------------------------------------------------------------ threats / spider-sense
void AWHCombatDirector::Threat(AWHEnemy* E, double Lead, const TCHAR* Kind)
{
	FWHThreat T; T.E = E; T.At = Time + Lead; T.Kind = FName(Kind);
	Threats.Add(T);
	LogEvent(FString::Printf(TEXT("threat %s %s lead %.2f"), *E->Tag(), Kind, Lead));
}

void AWHCombatDirector::ClearThreats(const AWHEnemy* E)
{
	Threats.RemoveAll([E](const FWHThreat& T) { return T.E.Get() == E; });
}

const FWHThreat* AWHCombatDirector::NearestThreat() const
{
	const FWHThreat* B = nullptr;
	for (const FWHThreat& T : Threats)
	{
		const double R = T.At - Time; if (R < -0.08 || R > 0.8) continue;
		if (!B || T.At < B->At) B = &T;
	}
	return B;
}

void AWHCombatDirector::ReleaseToken(AWHEnemy* E)
{
	if (MeleeToken.Get() == E) { MeleeToken = nullptr; GlobalCd = Rnd(0.35, 0.9); }
	if (GunToken.Get() == E) { GunToken = nullptr; GunCd = Rnd(1.2, 2.4); }
}

void AWHCombatDirector::OnDodge(const FWHThreat* T, bool bPerfect)
{
	++NDodges;
	if (bPerfect)
	{
		++NPerfect;
		Slowmo(0.85, 0.22, 0.35); Banner(TEXT("PERFECT DODGE")); Me->Focus = FMath::Min(3.0, Me->Focus + 0.35);
		Impact(0.15);
	}
	LogEvent(FString::Printf(TEXT("dodge %s threat=%s"), bPerfect ? TEXT("PERFECT") : TEXT("plain"), T && T->E.IsValid() ? *T->E->Tag() : TEXT("none")));
}

// ------------------------------------------------------------------------------------------------ hits dealt by the hero
void AWHCombatDirector::PlayerHit(AWHEnemy* E, const FWHPlayerHit& H)
{
	if (!E || !E->Alive()) return;
	static const TSet<FName> Melee = { "light", "ender", "launch", "strike", "air", "slam", "finisher" };
	const FVector HP = Me->Pos;
	if (Melee.Contains(H.Kind) && !H.bHasFrom)
	{ // melee blows only connect in reach: a blow that would land from further away whiffs
		const double Lim = (H.Reach < 0 ? 1.9 : H.Reach) + (E->Type == EWHEnemyType::Brute ? 0.3 : 0.0);
		const double Dy = (HP.Z - HH) - E->Pos.Z;
		if (HDist(HP, E->Pos) > Lim || Dy > 2.4 || Dy < -1.2)
		{
			++NWhiffs; LogEvent(FString::Printf(TEXT("whiff %s -> %s (%.2f m)"), *H.Kind.ToString(), *E->Tag(), HDist(HP, E->Pos))); return;
		}
	}
	const FVector From = H.bHasFrom ? H.From : HP;
	const FVector D = FlatNorm(E->Pos - From, YawDir(Hero->GetTraversal()->Facing()));
	FWHHitIn In; In.Dmg = H.Dmg; In.Dir = D; In.Kind = H.Kind; In.bStunBrute = H.bStunBrute; In.Side = H.Side;
	const FWHHitResult R = E->Hit(In);
	if (!R.bValid) return;
	const double Heavy = R.bArmored ? 0.1 : H.Heavy;
	FVector Cp = E->Chest() - D * 0.28;
	if (H.Kind == "air" || H.Kind == "slam" || E->State == EWHEnemyState::Air) Cp.Z = E->Pos.Z + 1.0;
	++NHits;
	if (R.bLaunched) ++NLaunch;
	if (H.Kind == "air" || H.Kind == "slam") ++NAirHits;
	if (H.Kind == "finisher") ++NFinishers;
	if (!H.bSilent)
	{
		const FLinearColor Arm(3.f, 3.f, 3.4f);
		Fx.Hit(Cp, -D, Heavy, R.bArmored ? &Arm : nullptr);
		if (H.Kind == "finisher") HitStop(0.12, 0.05); else if (Heavy > 0.5) HitStop(0.065, 0.08); else HitStop(0.035, 0.15);
		Shake(0.05 + Heavy * 0.25);
		if (Heavy > 0.5) Impact(0.12 + Heavy * 0.15);
		if (!R.bArmored) { ++ComboN; ComboT = 0; }
		if (Heavy > 0.5) CamPunchT = 0;
		const double Mult = 1 + FMath::Min(1.0, ComboN / 15.0);
		Me->Focus = FMath::Min(3.0, Me->Focus + (Heavy > 0.5 ? 0.14 : 0.075) * Mult);
	}
	LogEvent(FString::Printf(TEXT("hit %s -> %s dmg %.0f hp %.0f %s%s%s%s combo %d focus %.2f"), *H.Kind.ToString(), *E->Tag(), H.Dmg, FMath::Max(0.0, E->Hp),
		R.bArmored ? TEXT("ARMORED ") : TEXT(""), R.bLaunched ? TEXT("LAUNCHED ") : TEXT(""), R.bKnocked ? TEXT("KNOCKED ") : TEXT(""), R.bStagger ? TEXT("stagger ") : TEXT(""), ComboN, Me->Focus));
}

void AWHCombatDirector::GroundPound(const FVector& P)
{
	Fx.Dust(P, 1.4); Shake(0.35); Impact(0.35);
	for (AWHEnemy* E : Enemies)
		if (E && E->Alive() && E->State != EWHEnemyState::Air && HDist(E->Pos, P) < 2.8)
		{ FWHPlayerHit H; H.Kind = "ender"; H.Dmg = 8; H.Heavy = 0.4; H.Reach = 3.2; H.bSilent = true; PlayerHit(E, H); }
	LogEvent(TEXT("groundPound"));
}

void AWHCombatDirector::Heal(double N)
{
	Me->Hp = FMath::Min(Me->MaxHp, Me->Hp + N);
	Fx.Heal(Me->Pos);
	LogEvent(FString::Printf(TEXT("heal +%.0f hp %.0f"), N, Me->Hp));
}

void AWHCombatDirector::Cine(AWHEnemy* Target, double Dur, FName Kind)
{
	CineS = FCine(); CineS.Target = Target; CineS.Dur = Dur; CineS.Kind = Kind; CineS.bOn = true;
	if (Kind == "finisher") Slowmo(1.2, 0.45, 0.4); else Slowmo(0.7, 0.4, 0.3);
	LogEvent(FString::Printf(TEXT("cine %s %s %.2f s"), *Kind.ToString(), Target ? *Target->Tag() : TEXT("-"), Dur));
}

void AWHCombatDirector::OnEnemyOut(AWHEnemy* E, const TCHAR* How)
{
	ReleaseToken(E); ClearThreats(E);
	const FString H(How);
	++NKOs;
	if (H == TEXT("wall")) Cine(E, 1.0, "pin");
	if (H == TEXT("wall") || H == TEXT("ground")) { Shake(0.12); Fx.WebHit(E->Chest(), FVector(0, 0, -1)); }
	if (H == TEXT("wall") && E->State == EWHEnemyState::Stuck) Me->Focus = FMath::Min(3.0, Me->Focus + 0.2);
	LogEvent(FString::Printf(TEXT("out %s %s"), *E->Tag(), How));
}

// ------------------------------------------------------------------------------------------------ hits dealt by enemies
FVector AWHCombatDirector::PlayerChest() const { return Me ? Me->Pos + FVector(0, 0, 0.45) : FVector::ZeroVector; }
bool AWHCombatDirector::HeroAirborne() const { return Me && Me->bAirborne; }
void AWHCombatDirector::Shake(double A) { CamTrauma = FMath::Min(1.0, CamTrauma + A); }

void AWHCombatDirector::Impact(double A)
{
	CamImpact = FMath::Min(1.0, CamImpact + A);
}

void AWHCombatDirector::EnemyStrike(AWHEnemy* E)
{
	ClearThreats(E);
	const FVector Pf = PlayerFeet;
	const double D = HDist(E->Pos, Pf), Dy = FMath::Abs(Pf.Z - E->Pos.Z);
	const bool bInReach = D <= E->T.Reach + 0.75 && Dy < 1.1;
	if (!bInReach || Me->Invuln()) { LogEvent(FString::Printf(TEXT("enemy swing %s %s missed (%s)"), *E->Tag(), *E->Atk.ToString(), Me->Invuln() ? TEXT("invulnerable") : TEXT("out of reach"))); return; }
	const bool bHeavy = E->Type == EWHEnemyType::Brute || (E->Atk == "thugKick" && Rng.FRand() < 0.3);
	const double Dmg = E->T.Dmg * (bHeavy && E->Type != EWHEnemyType::Brute ? 1.3 : 1.0);
	Me->TakeHit(E, Dmg, bHeavy);
	const FLinearColor Col(5, 2, 1.5);
	Fx.Hit(Me->Pos + FVector(0, 0, 0.5), FlatNorm(Pf - E->Pos), bHeavy ? 0.6 : 0.2, &Col);
	HitStop(bHeavy ? 0.08 : 0.045, bHeavy ? 0.06 : 0.12); Shake(bHeavy ? 0.4 : 0.22); if (bHeavy) Impact(0.3);
	ComboN = 0; ++NEnemyHits; DamageTaken += Dmg;
	LogEvent(FString::Printf(TEXT("hero hit by %s %s dmg %.0f hp %.0f%s"), *E->Tag(), *E->Atk.ToString(), Dmg, Me->Hp, bHeavy ? TEXT(" HEAVY") : TEXT("")));
}

void AWHCombatDirector::EnemyShoot(AWHEnemy* E)
{
	const FVector Mz = E->Muzzle();
	const FVector Ch = PlayerChest();
	const FVector D = (Ch - Mz).GetSafeNormal();
	Fx.Muzzle(Mz, D);
	FTravHit Hb;
	const bool bBlocked = Raycast(Mz, D, FVector::Dist(Mz, Ch) - 0.5, Hb);
	const bool bMiss = Me->Invuln() || bBlocked || (Me->bAirborne && Rng.FRand() < 0.6);
	const FVector End = bMiss ? Ch + FVector(Rnd(-1, 1), Rnd(-1, 1), Rnd(-0.4, 1)) + D * 6 : Ch;
	Fx.Tracer(Mz, End);
	++NShots;
	if (E->Shots >= 3) ClearThreats(E);
	if (bMiss) { LogEvent(FString::Printf(TEXT("shot %s missed%s"), *E->Tag(), Me->Invuln() ? TEXT(" (invulnerable)") : bBlocked ? TEXT(" (blocked)") : TEXT(""))); return; }
	Me->Hp = FMath::Max(0.0, Me->Hp - E->T.Dmg);
	const FLinearColor Col(5, 2, 1.2);
	Fx.Hit(Ch, -D, 0.05, &Col);
	Shake(0.1); ComboN = 0; ++NShotHits; DamageTaken += E->T.Dmg;
	if ((Me->IsFree() && !Me->bAirborne) || Me->Hp <= 0) Me->TakeHit(E, 0, Me->Hp <= 0);
	LogEvent(FString::Printf(TEXT("shot %s HIT hp %.0f"), *E->Tag(), Me->Hp));
}

void AWHCombatDirector::ThrowPistol(const FVector& P, const FVector& V)
{
	UStaticMeshComponent* C = NewObject<UStaticMeshComponent>(this);
	C->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
	C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	C->SetUsingAbsoluteLocation(true); C->SetUsingAbsoluteRotation(true); C->SetUsingAbsoluteScale(true);
	C->SetupAttachment(GetRootComponent()); C->RegisterComponent();
	C->SetWorldScale3D(FVector(0.2, 0.035, 0.13));
	if (UMaterialInterface* M = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Combat/Materials/M_CmbSolid.M_CmbSolid")))
	{
		UMaterialInstanceDynamic* Mi = UMaterialInstanceDynamic::Create(M, this);
		Mi->SetVectorParameterValue(TEXT("Color"), FLinearColor(0.03f, 0.03f, 0.035f)); Mi->SetScalarParameterValue(TEXT("Metal"), 0.6f);
		C->SetMaterial(0, Mi);
	}
	FLoose L; L.Obj = C; L.Pos = P; L.Vel = V;
	Loose.Add(L);
}

// ------------------------------------------------------------------------------------------------ time scale (real time based)
void AWHCombatDirector::HitStop(double Dur, double Scale)
{
	FTimeReq R; R.Until = RTime + Dur; R.Scale = Scale; R.bSlow = false; TimeReq.Add(R); ++NHitStops;
}

void AWHCombatDirector::Slowmo(double Dur, double Scale, double Ease)
{
	FTimeReq R; R.Start = RTime; R.Until = RTime + Dur; R.Scale = Scale; R.Ease = Ease; R.bSlow = true; TimeReq.Add(R); ++NSlowmo;
	LogEvent(FString::Printf(TEXT("slowmo %.2f s x%.2f"), Dur, Scale));
}

void AWHCombatDirector::UpdateTime()
{
	double Sc = 1, Slow = 0;
	for (int32 i = TimeReq.Num() - 1; i >= 0; --i)
	{
		const FTimeReq& R = TimeReq[i];
		if (RTime >= R.Until) { TimeReq.RemoveAt(i); continue; }
		double S = R.Scale;
		if (R.bSlow) { const double Left = R.Until - RTime; const double K = Smooth(Left / R.Ease); S = 1 - (1 - R.Scale) * K; Slow = FMath::Max(Slow, 1 - S); }
		Sc = FMath::Min(Sc, S);
	}
	TimeScale = Sc; SlowK = Slow;
	MinTimeScale = FMath::Min(MinTimeScale, Sc);
	UGameplayStatics::SetGlobalTimeDilation(this, float(Sc));
}

// ------------------------------------------------------------------------------------------------ fight lifecycle
void AWHCombatDirector::StartFight(const FString& Spec, double Dist)
{
	const FVector Pf = Me->Pos - FVector(0, 0, HH);
	const FVector Fwd = YawDir(Hero->GetTravCamera().Yaw);
	FightCenter = Pf + Fwd * Dist * 0.6;
	// P2 armed street people (hero skeleton): variety per type
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
	}
	bFight = true; bEngaged = true; ComboN = 0; Me->Hp = FMath::Max(Me->Hp, 60.0); WarnCount = 0; ClearT = 0;
	Input.Clear();
	FString Types; for (AWHEnemy* E : Enemies) Types += FString::Printf(TEXT("%s%s:%s(%.1f,%.1f) "), Types.IsEmpty() ? TEXT("") : TEXT(""), *E->Tag(), E->TypeName(), E->Pos.X, E->Pos.Y);
	LogEvent(TEXT("fight start ") + Types);
}

void AWHCombatDirector::EndFight(bool bWon)
{
	if (!bFight) return;
	bFight = false; bEngaged = false; ComboN = 0;
	Threats.Reset(); MeleeToken = nullptr; GunToken = nullptr;
	Me->Reset();
	if (bWon) { Banner(TEXT("AREA CLEAR")); Slowmo(0.8, 0.35, 0.5); }
	LogEvent(FString::Printf(TEXT("fight end %s"), bWon ? TEXT("WON") : TEXT("ended")));
}

void AWHCombatDirector::DirectorStep(double Dt)
{
	const FVector Pf = PlayerFeet;
	GlobalCd -= Dt; GunCd -= Dt;
	TArray<AWHEnemy*> Standing;
	for (AWHEnemy* E : Enemies)
	{
		if (!E || !E->Alive()) continue;
		switch (E->State)
		{
		case EWHEnemyState::Hold: case EWHEnemyState::Approach: case EWHEnemyState::Attack: case EWHEnemyState::Aim: case EWHEnemyState::Fire:
		case EWHEnemyState::Stagger: case EWHEnemyState::GetUp: Standing.Add(E); break;
		default: break;
		}
	}
	// surround: melee enemies around the player at ~3 m, gunmen at ~10 m
	for (int32 Gp = 0; Gp < 2; ++Gp)
	{
		TArray<AWHEnemy*> Group;
		for (AWHEnemy* E : Standing) if ((E->Type == EWHEnemyType::Gunman) == (Gp == 1)) Group.Add(E);
		if (!Group.Num()) continue;
		const bool bGun = Gp == 1;
		TArray<double> Ang;
		for (AWHEnemy* E : Group) Ang.Add(FMath::Atan2(E->Pos.Y - Pf.Y, E->Pos.X - Pf.X));
		const double MinSep = bGun ? 0.7 : FMath::Min(2 * PI / Group.Num(), 1.25);
		for (int32 It = 0; It < 4; ++It)
			for (int32 i = 0; i < Ang.Num(); ++i)
				for (int32 j = i + 1; j < Ang.Num(); ++j)
				{
					const double D = AngWrap(Ang[j] - Ang[i]);
					if (FMath::Abs(D) < MinSep) { const double Push = (MinSep - FMath::Abs(D)) * 0.5 * (D >= 0 ? 1 : -1); Ang[i] -= Push; Ang[j] += Push; }
				}
		for (int32 i = 0; i < Group.Num(); ++i)
		{
			AWHEnemy* E = Group[i];
			double R = bGun ? 9.5 + (i % 2) * 1.5 : E->Type == EWHEnemyType::Brute ? 3.6 : 3.0 + (i % 2) * 0.7;
			if (Me->bAirborne && !bGun) R += 1.2;
			const FVector D(FMath::Cos(Ang[i]), FMath::Sin(Ang[i]), 0);
			FTravHit H;
			if (Raycast(Pf + FVector(0, 0, 1), D, R + 0.6, H) && !H.bGround) R = FMath::Max(1.8, H.Distance - 0.8);
			Slots.Add(E, FVector(Pf.X + D.X * R, Pf.Y + D.Y * R, Pf.Z));
		}
	}
	const FName MN = Me->MoveName();
	if (MN == "down" || MN == "finisher") return;
	// melee token: one committed attacker at a time
	if (!MeleeToken.IsValid() && GlobalCd <= 0 && !Me->bAirborne)
	{
		AWHEnemy* Best = nullptr; double Bs = 1e18;
		for (AWHEnemy* E : Standing)
		{
			if ((E->Type == EWHEnemyType::Gunman && E->bHasGun) || E->State != EWHEnemyState::Hold || E->Cd > 0) continue;
			const double D = HDist(E->Pos, Pf); if (D > 9) continue;
			const double Sc = D + Rng.FRand() * 2;
			if (Sc < Bs) { Bs = Sc; Best = E; }
		}
		if (Best) { MeleeToken = Best; Best->Set(EWHEnemyState::Approach); LogEvent(TEXT("token melee ") + Best->Tag()); }
	}
	if (!GunToken.IsValid() && GunCd <= 0)
	{
		for (AWHEnemy* E : Standing)
		{
			if (!E->bHasGun || E->State != EWHEnemyState::Hold || E->Cd > 0) continue;
			const double D = HDist(E->Pos, Pf); if (D > 24 || D < 2.5) continue;
			const FVector From = E->Pos + FVector(0, 0, 1.4), To = PlayerChest();
			FTravHit H;
			if (Raycast(From, (To - From).GetSafeNormal(), FVector::Dist(From, To) - 0.5, H)) continue;
			GunToken = E; E->Set(EWHEnemyState::Aim); E->AimDur = 0.95; Threat(E, 0.95, TEXT("gun"));
			LogEvent(TEXT("token gun ") + E->Tag());
			break;
		}
	}
}

FVector AWHCombatDirector::SlotFor(const AWHEnemy* E) const
{
	const FVector* S = Slots.Find(E);
	return S ? *S : PlayerFeet;
}

void AWHCombatDirector::Separate()
{
	auto Free = [](const AWHEnemy* E) { return E && E->Alive() && E->State != EWHEnemyState::Air && E->State != EWHEnemyState::Knock && E->State != EWHEnemyState::Down; };
	for (int32 i = 0; i < Enemies.Num(); ++i)
	{
		AWHEnemy* A = Enemies[i]; if (!Free(A)) continue;
		for (int32 j = i + 1; j < Enemies.Num(); ++j)
		{
			AWHEnemy* B = Enemies[j]; if (!Free(B)) continue;
			const double Dx = B->Pos.X - A->Pos.X, Dy = B->Pos.Y - A->Pos.Y, D = FMath::Sqrt(Dx * Dx + Dy * Dy), Mn = 0.85 * FMath::Max(A->T.Scale, B->T.Scale);
			if (D < Mn && D > 1e-4) { const double K = (Mn - D) * 0.5 / D; A->MoveXZ(-Dx * K, -Dy * K); B->MoveXZ(Dx * K, Dy * K); }
		}
		const FVector Pf = PlayerFeet;
		const double Dx = A->Pos.X - Pf.X, Dy = A->Pos.Y - Pf.Y, D = FMath::Sqrt(Dx * Dx + Dy * Dy), Mn = 0.8 * A->T.Scale;
		if (D < Mn && D > 1e-4 && FMath::Abs(A->Pos.Z - Pf.Z) < 1) A->MoveXZ(Dx / D * (Mn - D), Dy / D * (Mn - D));
	}
}

// ------------------------------------------------------------------------------------------------ web shooter
void AWHCombatDirector::FireWeb(AWHEnemy* T)
{
	FShot S; S.P = MakeShared<FVector>(Hero->HandM(true)); S.Target = T;
	TWeakObjectPtr<AWHCombatHero> WH = Hero; TSharedPtr<FVector> P = S.P;
	S.Strand = Fx.Strand([WH]() { return WH.IsValid() ? WH->HandM(true) : FVector::ZeroVector; }, [P]() { return *P; }, 2.0, 0, 0.14);
	Shots.Add(S);
	LogEvent(TEXT("web fired -> ") + T->Tag());
}

void AWHCombatDirector::UpdateShots(double Dt)
{
	for (int32 i = Shots.Num() - 1; i >= 0; --i)
	{
		FShot& S = Shots[i]; S.T += Dt;
		AWHEnemy* T = S.Target.Get();
		if (!S.bHit)
		{
			const FVector To = T ? T->Chest() : *S.P;
			const FVector D = To - *S.P; const double L = D.Size();
			const double Step = 48 * Dt;
			if (L <= Step || S.T > 1 || !T)
			{
				S.bHit = true; *S.P = To;
				if (T && T->Alive())
				{
					T->AddWeb(0.34, D.GetSafeNormal());
					Fx.WebHit(To, D.GetSafeNormal()); Me->Focus = FMath::Min(3.0, Me->Focus + 0.03); ++NWebHits;
					LogEvent(FString::Printf(TEXT("web hit %s web %.2f state %s"), *T->Tag(), T->Web, T->StateName()));
				}
			}
			else *S.P += D / L * Step;
			Fx.Pellet(*S.P);
		}
		else
		{
			S.Fade += Dt / 0.14;
			if (S.Fade >= 1) { Fx.KillTag(S.Strand); Shots.RemoveAt(i); continue; }
		}
	}
}

// ------------------------------------------------------------------------------------------------ combat camera layer
void AWHCombatDirector::CombatCamera(double RDt)
{
	UCameraComponent* Cam = Hero->Camera(); if (!Cam) return;
	const FVector Pc = Me->Pos;
	double NearD = 1e9, Spread = 0, N = 0; FVector Cen = FVector::ZeroVector;
	for (AWHEnemy* E : Enemies)
	{
		if (!E || !E->Alive()) continue;
		const double D = HDist(E->Pos, Pc); NearD = FMath::Min(NearD, D); if (D > 12) continue;
		const double K = E->Type == EWHEnemyType::Gunman ? 0.5 : 1; N += K; Cen += E->Pos * K; Spread = FMath::Max(Spread, D * (E->Type == EWHEnemyType::Gunman ? 0.7 : 1));
	}
	const bool bGrounded = Hero->GetTraversal()->Mode() == EWebTravMode::Ground || Me->Busy();
	const double Want = bFight && bEngaged && bGrounded && NearD < 14 ? 1 : 0;
	CamW = Damp(CamW, Want, Want > 0 ? 2.0 : 1.3, RDt);
	const double W = Smooth(CamW);
	CamPunchT += RDt;
	CamPunch = CamPunchT < 0.15 ? Smooth(CamPunchT / 0.15) : 1 - Smooth((CamPunchT - 0.15) / 0.45);
	FVector CamPos = Cam->GetComponentLocation() / 100.0;
	FRotator CamRot = Cam->GetComponentRotation();
	const FVector Fwd = CamRot.Vector(), Right = FRotationMatrix(CamRot).GetUnitAxis(EAxis::Y);
	const FName MN = Me->MoveName();
	const bool bJuggle = MN == "air" || MN == "airStrike" || MN == "slamDown" || (MN == "launch" && Me->M.bRise);
	if (W > 0.002)
	{
		const bool bAir = Me->bAirborne || Hero->GetTraversal()->Mode() == EWebTravMode::Air;
		CamAir = Damp(CamAir, bJuggle ? 1 : bAir ? 0.4 : 0, bJuggle ? 3 : 1.5, RDt);
		const double WantExtra = Clamp(0.35 + (Spread - 3) * 0.16, 0.2, 1.5) + CamAir * 1.1;
		CamExtra = Damp(CamExtra < 0 ? WantExtra : CamExtra, WantExtra, 1.6, RDt);
		FVector WantP = CamPos - Fwd * CamExtra * W; WantP.Z += (0.3 + CamAir * 0.9) * W;
		if (CamAir > 0.01 && Me->Target.IsValid())
		{
			const FVector Tp = Me->Target->Pos; const double Lat = FVector::DotProduct(Tp - Pc, Right);
			CamSide = Damp(CamSide, Lat >= 0 ? 1 : -1, 2, RDt);
			WantP += Right * CamSide * 1.0 * CamAir * W;
		}
		if (CamPunch > 0) WantP += Fwd * 0.25 * CamPunch * W;
		FVector Off = N > 0 ? Flat(Cen / N - Pc) * 0.22 : FVector::ZeroVector;
		if (Off.Size() > 1.6) Off = Off.GetSafeNormal() * 1.6;
		CamFrame.X = Damp(CamFrame.X, Off.X, 2.2, RDt); CamFrame.Y = Damp(CamFrame.Y, Off.Y, 2.2, RDt);
		WantP += Right * FVector::DotProduct(CamFrame, Right) * W;
		// yaw drift (the orbit yaw belongs to P3's camera: combat keeps its own offset and orbits the final camera by it)
		const double CamYaw = Hero->GetTravCamera().Yaw + CamYawOff * W;
		AWHEnemy* Tg = Me->Target.IsValid() && Me->Target->Alive() ? Me->Target.Get() : nullptr;
		if (Tg && !CineS.bOn && Time - Me->LastAttackT < 2.5 && !bJuggle)
		{ // 3/4 framing: target not straight ahead along the view (his body would hide the blows)
			const double YawST = FMath::Atan2(Tg->Pos.Y - Pc.Y, Tg->Pos.X - Pc.X), DA = AngWrap(YawST - CamYaw);
			if (FMath::Abs(DA) < 0.72 && HDist(Tg->Pos, Pc) > 0.6)
			{
				const double Goal = YawST - (DA >= 0 ? 1 : -1) * 0.8, Step = AngWrap(Goal - CamYaw);
				CamYawOff += FMath::Clamp(Step, -1.3 * RDt * W, 1.3 * RDt * W);
			}
		}
		if (!CineS.bOn)
		{ // an attacker winding up outside the view: drift the orbit toward him
			const AWHEnemy* TT = nullptr; double Best = 1e9;
			for (const FWHThreat& T : Threats) { const double R = T.At - Time; if (R > 0 && R < Best && T.E.IsValid()) { Best = R; TT = T.E.Get(); } }
			if (TT)
			{
				const double Rel = AngWrap(FMath::Atan2(TT->Pos.Y - Pc.Y, TT->Pos.X - Pc.X) - CamYaw);
				const double Over = FMath::Abs(Rel) - 0.62;
				if (Over > 0) CamYawOff += FMath::Sign(Rel) * FMath::Min(Over, 1.4 * RDt * W);
			}
		}
		const FVector Pivot = Pc + FVector(0, 0, 0.5);
		const FQuat YQ(FVector::UpVector, CamYawOff * W);
		WantP = Pivot + YQ.RotateVector(WantP - Pivot);
		CamRot.Yaw += FMath::RadiansToDegrees(CamYawOff * W);
		// world collision from the body
		FVector ToCam = WantP - Pivot; const double Lc = ToCam.Size(); ToCam /= FMath::Max(1e-4, Lc);
		double Raw = Lc + 0.6;
		FTravHit H; if (Raycast(Pivot, ToCam, Lc + 0.9, H)) Raw = FMath::Min(Raw, H.Distance);
		const double LimH = FMath::Max(0.6, Raw - 0.12), TgtH = FMath::Max(0.6, Raw - 0.6);
		CamHard = FMath::Min(LimH, Damp(CamHard < 0 ? TgtH : CamHard, TgtH, TgtH < CamHard ? 12 : 2.5, RDt));
		double Allow = FMath::Min(Lc, CamHard);
		const double Hard = Allow;
		for (AWHEnemy* E : Enemies)
		{ // bodies between lens and hero: pull in only to a normal over-the-shoulder distance
			if (!E || E->Stuck == 1 || E->State == EWHEnemyState::Out) continue;
			const double R = 0.5 * E->T.Scale + (E->Web > 0.3 ? 0.25 : 0);
			for (double Hg : { 0.6, 1.3 })
			{
				const FVector Ep = E->Pos + FVector(0, 0, Hg * E->T.Scale);
				const double T = FVector::DotProduct(Ep - Pivot, ToCam); if (T < 0.5 || T > Allow + 0.4) continue;
				const double D = FVector::Dist(Ep, Pivot + ToCam * T);
				if (D < R + 0.25) Allow = FMath::Max(2.4, FMath::Min(Allow, T - R - 0.2));
			}
		}
		CamSoft = Damp(CamSoft < 0 ? Lc : CamSoft, Allow, Allow < CamSoft ? 9 : 2.5, RDt);
		const double CamAllow = FMath::Min(Hard, CamSoft);
		if (CamAllow < Lc) { WantP = Pivot + ToCam * CamAllow; WantP.Z += (Lc - CamAllow) * 0.3; }
		const double Gy = GroundHeight(WantP.X, WantP.Y, WantP.Z + 0.3) + 0.35; if (WantP.Z < Gy) WantP.Z = Gy;
		CamPos = WantP;
	}
	else CamYawOff = Damp(CamYawOff, 0, 0.8, RDt);
	// shake / impact (combat trauma on top of the chase camera's own)
	CamTrauma = FMath::Max(0.0, CamTrauma - RDt * 1.6);
	CamImpact = FMath::Max(0.0, CamImpact - RDt * 3.0);
	if (CamTrauma > 0.001 || CamImpact > 0.001)
	{
		const double Tr = CamTrauma * CamTrauma;
		const double Ph = RTime * 47.0;
		CamRot.Pitch += Tr * 2.2 * FMath::Sin(Ph * 1.3) - CamImpact * 1.2;
		CamRot.Yaw += Tr * 1.8 * FMath::Sin(Ph * 0.9 + 1.7);
		CamRot.Roll += Tr * 1.5 * FMath::Sin(Ph * 1.1 + 0.4);
	}
	// cinematic beats (finisher / wall pin): low side angle that frames BOTH actors every frame
	if (CineS.bOn)
	{
		CineS.T += RDt;
		const double K = Smooth(CineS.T / 0.22) * (1 - Smooth((CineS.T - CineS.Dur + 0.3) / 0.3));
		AWHEnemy* T = CineS.Target.Get();
		if (CineS.T > CineS.Dur || !T) CineS.bOn = false;
		else if (K > 0.001)
		{
			const FVector Tp = T->Chest();
			const FVector A = Pc + FVector(0, 0, 0.2);
			const FVector Mid = A + (Tp - A) * (CineS.Kind == "pin" ? 0.55 : 0.5);
			const double Span = FVector::Dist(A, Tp);
			if (!CineS.bSide)
			{
				const FVector Ax = FlatNorm(Tp - A);
				TArray<FVector> Cands = { FVector(-Ax.Y, Ax.X, 0), FVector(Ax.Y, -Ax.X, 0) };
				for (int32 i = 0; i < 2; ++i) { Cands.Add((Cands[i] - Ax * 0.8).GetSafeNormal()); Cands.Add((Cands[i] + Ax * 0.8).GetSafeNormal()); }
				double Bs = 1e18;
				for (const FVector& Sd : Cands)
				{
					const double Dist = 2.6 + Span * 0.8; FVector Cp = Mid + Sd * Dist; Cp.Z = Mid.Z + 0.35;
					double Sc = 0;
					for (const FVector& Tg : { A, Tp })
					{
						const FVector Dd = Tg - Cp; const double L = Dd.Size(); FTravHit H;
						if (Raycast(Cp, Dd / L, L - 0.3, H)) Sc += 10;
						for (AWHEnemy* E : Enemies)
						{
							if (!E || E == T || !E->Alive()) continue;
							const FVector Ep = E->Pos + FVector(0, 0, 1);
							const FVector Q = FMath::ClosestPointOnSegment(Ep, Cp, Tg);
							if (FVector::Dist(Q, Ep) < 0.7) Sc += 4;
						}
					}
					FTravHit H2; if (Raycast(Mid, Sd, Dist, H2)) Sc += 6;
					Sc -= FVector::DotProduct(Sd, FlatNorm(CamPos - Mid)) * 0.8;
					if (Sc < Bs) { Bs = Sc; CineS.Side = Sd; CineS.Dist = Dist; }
				}
				CineS.bSide = true;
			}
			FVector Cpos = Mid + CineS.Side * (CineS.Dist + CineS.T * 0.35); Cpos.Z = Mid.Z + 0.35;
			const FVector Dm = (Cpos - Mid).GetSafeNormal(); FTravHit Hh;
			if (Raycast(Mid, Dm, FVector::Dist(Mid, Cpos), Hh)) Cpos = Mid + Dm * FMath::Max(1.0, Hh.Distance - 0.3);
			const FVector Look0 = CamPos + CamRot.Vector() * FMath::Max(2.0, FVector::Dist(CamPos, Pc));
			const FVector Look = Look0 + (Mid - Look0) * K;
			CamPos = CamPos + (Cpos - CamPos) * K;
			CamRot = (Look - CamPos).Rotation();
		}
	}
	Cam->SetWorldLocationAndRotation(CamPos * 100.0, CamRot);
}

// ------------------------------------------------------------------------------------------------ per frame
void AWHCombatDirector::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!Hero || !Me || !Hero->GetTraversal()) return;
	const double Dt = FMath::Clamp(double(DeltaSeconds), 0.0, 0.1);
	const double RDt = FMath::Clamp(double(GetWorld()->DeltaRealTimeSeconds), 0.0, 0.1);
	Time += Dt; RTime += RDt; ++Frame;
	if (TimeScale < 0.999) { SlowmoGameT += Dt; SlowmoRealT += RDt; }
	RunBeats();
	// hero (spidey.js override): input -> moves -> body placed through the traversal component
	Me->Override(Dt);
	PlayerFeet = Me->Pos - FVector(0, 0, HH);
	if (bFight)
	{
		FVector C = FVector::ZeroVector; int32 N = 0;
		for (AWHEnemy* E : Enemies) if (E && E->Alive()) { C += E->Pos; ++N; }
		if (N) FightCenter += (C / N - FightCenter) * (1 - FMath::Exp(-0.5 * Dt));
		if (bEngaged) DirectorStep(Dt);
		if (!N && Enemies.Num()) { ClearT += Dt; if (ClearT > 1.3 && (Me->IsFree() || ClearT > 3)) EndFight(true); } else ClearT = 0;
	}
	for (AWHEnemy* E : Enemies) if (E && (bEngaged || !E->Alive())) E->Update(Dt);
	Separate();
	for (AWHEnemy* E : Enemies) if (E) E->Late(Dt);
	Me->Late(Dt);
	if (PendingShot.IsValid() && Time >= PendingShotAt) { AWHEnemy* T = PendingShot.Get(); PendingShot = nullptr; if (T->Alive()) FireWeb(T); }
	UpdateShots(Dt);
	for (FLoose& L : Loose)
	{
		if (L.bRest || !L.Obj) continue;
		L.Vel.Z -= 20 * Dt; L.Pos += L.Vel * Dt;
		const double Gy = GroundHeight(L.Pos.X, L.Pos.Y, L.Pos.Z + 0.5);
		if (L.Pos.Z < Gy + 0.03) { L.Pos.Z = Gy + 0.03; if (L.Vel.Z < -3) { L.Vel.Z *= -0.3; L.Vel.X *= 0.5; L.Vel.Y *= 0.5; } else L.bRest = true; }
		L.Obj->SetWorldLocationAndRotation(L.Pos * 100.0, FRotator(Time * 700, Time * 400, 0));
	}
	// threats -> spider-sense (streaks + slow-mo hint for the first warnings of a fight)
	Threats.RemoveAll([this](const FWHThreat& T) { return T.At <= Time - 0.15 || !T.E.IsValid() || !T.E->Alive(); });
	double Lvl = 0; bool bRed = false;
	for (FWHThreat& T : Threats)
	{
		const double R = T.At - Time; const double K = FMath::Clamp(1 - R / 0.75, 0.0, 1.0) * (R > -0.1 ? 1 : 0);
		if (K > Lvl) { Lvl = K; bRed = T.Kind == "gun"; }
		if (!T.bHinted && R < 0.5 && R > 0.2)
		{
			T.bHinted = true;
			if (WarnCount < 2 && Hero->GetTraversal()->Mode() == EWebTravMode::Ground) Slowmo(0.28, 0.45, 0.2);
			++WarnCount;
		}
	}
	SenseLvl = bEngaged ? Lvl : 0;
	Fx.Sense(SenseLvl, bRed, Hero->HeadM() + FVector(0, 0, 0.08), RDt);
	Fx.Update(Dt);
	ComboT += Dt; if (ComboT > 3.2) ComboN = 0;
	UpdateTime();
	CombatCamera(RDt);
	// automation: telemetry row, stills, quit
	TelemetryRows.Add(FString::Printf(TEXT("%lld,%.4f,%.4f,%.3f,%s,%.3f,%.3f,%.3f,%.0f,%.2f,%d,%.2f,%d,%s,%s,%.2f,%s"),
		Frame, RTime, Time, TimeScale, *Me->MoveName().ToString(), Me->Pos.X, Me->Pos.Y, Me->Pos.Z, Me->Hp, Me->Focus, ComboN, SenseLvl,
		Threats.Num(), CineS.bOn ? *CineS.Kind.ToString() : TEXT("-"), Hero->GetTraversal()->Mode() == EWebTravMode::Ground ? TEXT("ground") : TEXT("air"),
		CamW, *StateString()));
	while (NextShot < ShotTimes.Num() && RTime >= ShotTimes[NextShot])
	{
		const FString File = OutDir / FString::Printf(TEXT("%s_%02d_t%05.2f.png"), *ShotName, NextShot, ShotTimes[NextShot]);
		FScreenshotRequest::RequestScreenshot(File, false, false);
		LogEvent(TEXT("still ") + File);
		++NextShot;
	}
	if (QuitAt > 0 && RTime >= QuitAt && !bQuitSent)
	{
		bQuitSent = true;
		WriteTelemetry(); WriteSummary();
		if (APlayerController* PC = GetWorld()->GetFirstPlayerController()) PC->ConsoleCommand(TEXT("quit"));
		else FGenericPlatformMisc::RequestExit(false);
	}
}

FString AWHCombatDirector::StateString() const
{
	FString S;
	for (const AWHEnemy* E : Enemies)
	{
		if (!E) continue;
		S += FString::Printf(TEXT("%s%c:%s%s:%d%s"), S.IsEmpty() ? TEXT("") : TEXT(" "), E->TypeName()[0], E->StateName(),
			E->Stuck == 1 ? TEXT("-wall") : E->Stuck == 2 ? TEXT("-ground") : TEXT(""), FMath::Max(0, FMath::RoundToInt(E->Hp)),
			E->Web > 0.01 ? *FString::Printf(TEXT(":w%.1f"), E->Web) : TEXT(""));
	}
	return S;
}

void AWHCombatDirector::LogEvent(const FString& S)
{
	const FString Row = FString::Printf(TEXT("{\"rt\":%.3f,\"gt\":%.3f,\"ts\":%.3f,\"move\":\"%s\",\"ev\":\"%s\"}"), RTime, Time, TimeScale,
		Me ? *Me->MoveName().ToString() : TEXT("-"), *S.Replace(TEXT("\""), TEXT("'")));
	EventRows.Add(Row);
	UE_LOG(LogWebHomage, Display, TEXT("WH_CMB_EV %s"), *Row);
}

void AWHCombatDirector::WriteTelemetry()
{
	if (OutDir.IsEmpty()) return;
	FString Csv = TEXT("frame,rt,gt,timescale,move,x_m,y_m,z_m,hp,focus,combo,sense,threats,cine,trav,cam_w,enemies\n");
	for (const FString& R : TelemetryRows) { Csv += R; Csv += TEXT("\n"); }
	FFileHelper::SaveStringToFile(Csv, *(OutDir / (ShotName + TEXT("_telemetry.csv"))));
	FFileHelper::SaveStringToFile(FString::Join(EventRows, TEXT("\n")) + TEXT("\n"), *(OutDir / (ShotName + TEXT("_events.jsonl"))));
	FFileHelper::SaveStringToFile(FString::Join(BeatRows, TEXT("\n")) + TEXT("\n"), *(OutDir / (ShotName + TEXT("_beats.jsonl"))));
}

void AWHCombatDirector::WriteSummary()
{
	bSummaryDone = true;
	if (OutDir.IsEmpty()) return;
	int32 Alive = 0; FString Final;
	for (const AWHEnemy* E : Enemies) if (E) { Alive += E->Alive() ? 1 : 0; }
	const FString J = FString::Printf(TEXT("{\n \"engine\": \"ue5.8\", \"frames\": %lld, \"real_s\": %.3f, \"game_s\": %.3f,\n \"enemies\": %d, \"enemies_alive\": %d, \"final_states\": \"%s\",\n")
		TEXT(" \"hero_hp\": %.0f, \"hero_focus\": %.2f, \"damage_taken\": %.0f,\n \"hits\": %d, \"whiffs\": %d, \"kos\": %d, \"launches\": %d, \"air_hits\": %d, \"finishers\": %d,\n")
		TEXT(" \"dodges\": %d, \"perfect_dodges\": %d, \"web_hits\": %d, \"enemy_melee_hits\": %d, \"shots\": %d, \"shot_hits\": %d,\n")
		TEXT(" \"hitstops\": %d, \"slowmos\": %d, \"min_timescale\": %.3f, \"slowmo_game_s\": %.3f, \"slowmo_real_s\": %.3f,\n \"beats\": %d, \"beats_fired\": %d, \"fx_spawned\": %d\n}\n"),
		Frame, RTime, Time, Enemies.Num(), Alive, *StateString(), Me->Hp, Me->Focus, DamageTaken, NHits, NWhiffs, NKOs, NLaunch, NAirHits, NFinishers,
		NDodges, NPerfect, NWebHits, NEnemyHits, NShots, NShotHits, NHitStops, NSlowmo, MinTimeScale, SlowmoGameT, SlowmoRealT,
		Beats.Num(), Beats.FilterByPredicate([](const FWHBeat& B) { return B.bFired; }).Num(), Fx.Spawned);
	FFileHelper::SaveStringToFile(J, *(OutDir / (ShotName + TEXT("_summary.json"))));
	UE_LOG(LogWebHomage, Display, TEXT("WH_CMB_SUMMARY %s"), *J.Replace(TEXT("\n"), TEXT(" ")));
}
