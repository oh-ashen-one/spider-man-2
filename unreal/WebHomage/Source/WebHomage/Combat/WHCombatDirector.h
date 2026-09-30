// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
// Piece P5 (combat): the combat director — C++ port of src/game/combat/index.js (+ input.js, the spidey.js move set lives in
// FWHSpidey, WHCombatSpidey.h). One actor per world, spawned by AWHCombatHero; it ticks AFTER the hero (traversal) and BEFORE
// the hero's / enemies' meshes, so every frame is: traversal (P3, unchanged) -> combat input -> hero move (body placed through
// the traversal component's public Teleport / SetVelocityM) -> director (tokens, slots, threats) -> enemies -> late (clip
// stacks -> anim instances) -> web shots -> spider-sense -> time scale (hit-stop / slow-mo = global time dilation) -> combat
// camera layer (moves the P3 follow camera after the chase camera placed it) -> script beats / telemetry.
//
// Automation (all optional; times are REAL seconds since the director started, deterministic under -benchmark -fps=60):
//   -WHCmbScript=<abs json>   scripted fight: spawn spec + timed input beats (docs/night1/combat/scripts/*.json)
//   -WHCmbFight=mmgb          spawn a fight without a script (m melee, g gunman, b brute), -WHCmbDist=7
//   -WHCmbOut=<abs dir>       telemetry CSV, beats / events JSONL, summary JSON (default <Project>/Saved/WHCombat)
//   -WHCmbShots=t1,t2         screenshots (true back-buffer size) at those real times, -WHCmbShotName=
//   -WHCmbQuit=<s>            request exit at that real time
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Combat/WHCombatFx.h"
#include "Combat/WHEnemy.h"
#include "Traversal/WebTravWorld.h"
#include "WHCombatDirector.generated.h"

class AWHCombatHero;
class FWHSpidey;
class UStaticMeshComponent;

/** A blow dealt by the hero (index.js playerHit h). */
struct FWHPlayerHit
{
	FName Kind;             // light ender launch strike air slam finisher throw web
	double Dmg = 0;
	double Heavy = 0;
	double Reach = -1;      // < 0: default 1.9 m
	int32 Side = 0;
	bool bStunBrute = false;
	bool bSilent = false;
	bool bHasFrom = false;
	FVector From = FVector::ZeroVector;
};

struct FWHThreat
{
	TWeakObjectPtr<AWHEnemy> E;
	double At = 0;
	FName Kind;
	bool bHinted = false;
};

/** Combat buttons (input.js): presses buffered in GAME time (0.45 s), LMB hold detected in REAL time (0.22 s). */
struct FWHCombatInput
{
	TMap<FName, double> Pressed;
	bool bLmbDown = false, bHoldSent = true;
	double PressT = 0;
	void Press(FName K, double GameT) { Pressed.Add(K, GameT); }
	bool Has(FName K, double GameT) { const double* T = Pressed.Find(K); if (!T) return false; if (GameT - *T > 0.45) { Pressed.Remove(K); return false; } return true; }
	bool Take(FName K, double GameT) { const bool Ok = Has(K, GameT); Pressed.Remove(K); return Ok; }
	bool HoldNow(double RealT) { if (!bHoldSent && bLmbDown && RealT - PressT >= 0.22) { bHoldSent = true; return true; } return false; }
	void LmbDown(double RealT, double GameT) { bLmbDown = true; PressT = RealT; bHoldSent = false; Press("attack", GameT); }
	void LmbUp() { bLmbDown = false; bHoldSent = true; }
	void Clear() { Pressed.Reset(); }
};

struct FWHBeat
{
	double T = 0;
	FName Key;
	double Hold = 0;
	FString Toward;       // enemy tag (e1..): the stick points at him for this beat (targeting only)
	FName React;          // record runs only: 'threat' = fire when a threat is 0.08-0.25 s from contact (window s after T)
	double Window = 3.0;
	FString Label;
	bool bFired = false;
	double FiredRT = -1, FiredGT = -1;
	FString Result;
};

UCLASS(NotPlaceable)
class WEBHOMAGE_API AWHCombatDirector : public AActor
{
	GENERATED_BODY()

public:
	AWHCombatDirector();
	virtual ~AWHCombatDirector();
	virtual void Tick(float DeltaSeconds) override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;

	void Init(AWHCombatHero* InHero);

	// ---- live input (AWHCombatHero key bindings)
	void KeyPress(FName Action);
	void LmbDown();
	void LmbUp();

	// ---- world (P3's traversal world index; metres)
	bool Raycast(const FVector& O, const FVector& D, double MaxD, FTravHit& Out) const;
	double GroundHeight(double X, double Y, double FromZ) const;
	bool IsFacade(const FVector& Point, const FVector& Normal) const;
	bool FindWall(const FVector& Pos, const FVector& Dir, double MaxD, FVector& OutP, FVector& OutN) const;

	// ---- enemy callbacks (enemy.js -> index.js)
	FVector SlotFor(const AWHEnemy* E) const;
	void EnemyStrike(AWHEnemy* E);
	void EnemyShoot(AWHEnemy* E);
	void Threat(AWHEnemy* E, double Lead, const TCHAR* Kind);
	void ClearThreats(const AWHEnemy* E);
	const FWHThreat* NearestThreat() const;
	void ReleaseToken(AWHEnemy* E);
	void OnEnemyInterrupted(AWHEnemy* E) { ReleaseToken(E); ClearThreats(E); }
	void OnEnemyOut(AWHEnemy* E, const TCHAR* How);
	void OnDodge(const FWHThreat* T, bool bPerfect);
	void ThrowPistol(const FVector& P, const FVector& V);
	void Shake(double A);
	void Impact(double A);
	bool HeroAirborne() const;
	FVector PlayerChest() const;
	double Rnd(double A, double B) { return A + Rng.FRand() * (B - A); }
	void LogEvent(const FString& S);
	void Deny(const FString& Msg) { LogEvent(TEXT("deny ") + Msg); }

	// ---- hero side
	AWHEnemy* PickTarget(const FVector* Dir, double MaxD, const FVector& From, double MinD = 0, double NeedView = 0) const;
	void PlayerHit(AWHEnemy* E, const FWHPlayerHit& H);
	void GroundPound(const FVector& P);
	void Heal(double N);
	void Cine(AWHEnemy* Target, double Dur, FName Kind);
	void FireWebLater(AWHEnemy* T, double Delay) { PendingShot = T; PendingShotAt = Time + Delay; }
	void HitStop(double Dur, double Scale = 0.04);
	void Slowmo(double Dur, double Scale = 0.3, double Ease = 0.25);
	void Banner(const FString& S) { LogEvent(TEXT("banner ") + S); }

	// ---- state (public like the browser's `c`)
	UPROPERTY(Transient) TObjectPtr<AWHCombatHero> Hero;
	UPROPERTY(Transient) TArray<TObjectPtr<AWHEnemy>> Enemies;
	FWHCombatFx Fx;
	FWHCombatInput Input;
	FWHSpidey* Me = nullptr;
	double Time = 0, RTime = 0, TimeScale = 1, SlowK = 0;
	FVector PlayerFeet = FVector::ZeroVector;
	TArray<FWHThreat> Threats;
	TWeakObjectPtr<AWHEnemy> MeleeToken, GunToken;
	double GlobalCd = 0, GunCd = 0;
	int32 ComboN = 0; double ComboT = 0;
	int32 WarnCount = 0;
	bool bFight = false, bEngaged = false;
	FVector FightCenter = FVector::ZeroVector;
	double ClearT = 0;
	FVector StickDir = FVector::ZeroVector;   // world stick direction this frame (script 'toward'), zero = neutral

	// cinematic (finisher / wall pin)
	struct FCine { TWeakObjectPtr<AWHEnemy> Target; double T = 0, Dur = 1, Dist = 3; FVector Side = FVector::ZeroVector; bool bSide = false; FName Kind; bool bOn = false; } CineS;
	double CamW = 0, CamAir = 0, CamExtra = -1, CamSide = 0, CamPunchT = 9, CamPunch = 0, CamHard = -1, CamSoft = -1, CamYawOff = 0;
	FVector CamFrame = FVector::ZeroVector;
	double CamTrauma = 0, CamImpact = 0, SenseLvl = 0;

	// stats (telemetry / summary)
	int32 NHits = 0, NWhiffs = 0, NKOs = 0, NPerfect = 0, NDodges = 0, NLaunch = 0, NAirHits = 0, NFinishers = 0, NWebHits = 0, NShots = 0, NShotHits = 0, NEnemyHits = 0, NHitStops = 0, NSlowmo = 0;
	double DamageTaken = 0, MinTimeScale = 1, SlowmoGameT = 0, SlowmoRealT = 0;

private:
	void StartFight(const FString& Spec, double Dist);
	void FireWeb(AWHEnemy* T);
	void EndFight(bool bWon);
	void DirectorStep(double Dt);
	void UpdateTime();
	void UpdateShots(double Dt);
	void CombatCamera(double RealDt);
	void Separate();
	void LoadScript(const FString& Path);
	void RunBeats();
	void WriteTelemetry();
	void WriteSummary();
	FString StateString() const;

	struct FTimeReq { double Until = 0, Start = 0, Scale = 1, Ease = 0.25; bool bSlow = false; };
	TArray<FTimeReq> TimeReq;
	TMap<const AWHEnemy*, FVector> Slots;
	struct FShot { TSharedPtr<FVector> P; TWeakObjectPtr<AWHEnemy> Target; double T = 0; bool bHit = false; double Fade = 0; int32 Strand = 0; };
	TArray<FShot> Shots;
	TWeakObjectPtr<AWHEnemy> PendingShot; double PendingShotAt = -1;
	struct FLoose { TObjectPtr<UStaticMeshComponent> Obj; FVector Pos, Vel; bool bRest = false; };
	TArray<FLoose> Loose;
	FRandomStream Rng = FRandomStream(20260929);

	// automation
	TArray<FWHBeat> Beats;
	FString ScriptPath, OutDir, ShotName = TEXT("cmb"), FightSpec;
	double FightDist = 7, FightStartAt = 0.5, QuitAt = -1;
	bool bFightStarted = false, bQuitSent = false, bSummaryDone = false;
	TArray<double> ShotTimes; int32 NextShot = 0;
	TArray<FString> TelemetryRows, EventRows, BeatRows;
	int64 Frame = 0;
	double StickUntil = 0;
};
