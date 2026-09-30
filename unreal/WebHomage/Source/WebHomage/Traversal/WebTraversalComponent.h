// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
// Piece P3: UWebTraversalComponent — C++ port of the browser's Insomniac-style traversal state machine
// (src/player/traversal/traversal.js). It runs its own 120 Hz substep and owns the body while it is active
// (CharacterMovement is switched off); collision uses Unreal traces / capsule penetration (FWebTravWorld).
//
//   modes: ground | air | swing | zip | perch | wall   (+ anim mode 'land' while a landing recovery plays)
//   kin moves: vault | cornerWrap | wallHop (scripted curves that take over the step)
//
// Owner feel notes from the browser are kept next to the code they shaped (user r4..r13, feedback #3..#19).
// Not ported yet (browser features): web slingshot (Ctrl), web tightrope (T), water plunge / yank, bridge halfway
// bounce, car-roof riding (C3 dynamics), tree-canopy anchors, Shift-walk (disabled in the browser too: user r-nowalk).
//
// Simulation units are METRES (browser constants unchanged), UE axes (Z up). Yaw angles: atan2(Y, X).
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Traversal/WebTravTypes.h"
#include "Traversal/WebTravWorld.h"
#include "Traversal/WebTravAnchors.h"
#include "WebTraversalComponent.generated.h"

class FWebTravCamera;

UCLASS(ClassGroup=(WebHomage), meta=(BlueprintSpawnableComponent))
class WEBHOMAGE_API UWebTraversalComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UWebTraversalComponent();

	/** World setup (building index) — call once the level is loaded. */
	void InitWorld(UWorld* World, const AActor* Owner);
	/** One frame: substeps at 120 Hz. `I` is consumed (edge flags cleared). Writes Anim + Events. */
	void UpdateTraversal(double Dt, FWebTravInput I);
	/** Place the body (metres; feet snapped to the floor if below). */
	void Teleport(const FVector& PosM, double YawRad);
	/** Set the body velocity (m/s), e.g. a scripted airborne start. */
	void SetVelocityM(const FVector& V) { S.Vel = V; if (V.SizeSquared() > 1) { S.Facing = FMath::Atan2(V.Y, V.X); } }

	/** C1 animation contract (read by P2's AnimBP). */
	UPROPERTY(BlueprintReadOnly, Category="Traversal")
	FWebTravAnim Anim;

	UFUNCTION(BlueprintPure, Category="Traversal")
	const FWebTravAnim& GetTravAnim() const { return Anim; }

	/** Progression hook 'swingReleaseBoost' multiplier. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal")
	float ReleaseBoostMul = 1.f;
	/** Round 07: a held swing button re-searches for the next anchor this long (s) after a web release, even while rising. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float ReattachAfter = 0.22f;
	/** Round 07: a web stuck while rising faster than this (m/s) starts its pendulum at the top of the hop, at most PendingMax s later. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float PendingVz = 5.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float PendingMax = 0.5f;
	/** Round 07: upward speed kept by a plain web release (m/s); the rest turns into forward speed. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float ReleaseVzMax = 8.f;
	/** Round 08: facade clearance kept by the canyon spring (m) and the spring rate (1/s). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float WallClearance = 3.5f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float WallKeepRate = 2.5f;
	/** Round 09: weave inside the corridor — swing target line toward the active anchor (x WeaveK, <= WeaveAmp m off centre). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float WeaveK = 0.45f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float WeaveAmp = 6.f;
	/** Round 09: alternating arc depth below the entry height (m): odd swings shallow, even swings deep. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float ArcDropShallow = 10.2f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float ArcDropDeep = 17.5f;
	/** Round 10: lowest designed arc bottom (feet over the floor, m; T7: 1-4 storeys over the street, never skimming car roofs). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float ArcLowMin = 5.f;
	/** Round 10: the first web after a sky launch bottoms out ArcLowMin + 0..SkyArcExtra m over the street (dives back into the canyon). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float SkyArcExtra = 4.f;
	/** Round 09: the next anchor search leans this far (deg) toward the side opposite the previous web. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float AnchorAltDeg = 30.f;
	/**
	 * Round 10 (critic r09 T3/T4/T7: four identical 2 s swings, never at the roofline): a jump-release with a trick pressed is a
	 * SKY LAUNCH — the release climbs at up to SkyLaunchVz m/s (plain jump-release: 22), gravity is x SkyHangK while |vz| <
	 * SkyHangVz (hang time at the top, tricks chained on input), and no web is searched on the way up. The camera drops under the
	 * hero and looks up (sky behind him) until he falls faster than 8 m/s.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float SkyLaunchVz = 26.f;
	/** Round 10 (T7 "peak at roofline height"): the launch speed is solved so the apex lands SkyRoofOver m above the lower street
	 *  wall's roofline beside the path ahead (RoofBesideAhead), the peak clamped to SkyPeakMin..SkyPeakMax m over the street and the
	 *  launch to SkyLaunchVz..SkyLaunchVzMax m/s. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float SkyRoofOver = 3.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float SkyPeakMin = 38.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float SkyPeakMax = 58.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float SkyLaunchVzMax = 52.f;
	/** Round 10: rope cap (and pivot reach) of the first web after a sky launch (a long dive back to the street). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float SkyRopeMax = 50.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float SkyHangK = 0.55f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float SkyHangVz = 7.f;
	/** Round 10: gravity scale on the rest of a sky launch's climb (vz >= SkyHangVz): the release carries him to the roofline. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float SkyRiseK = 1.4f;
	/** Round 10: a new web's anchor must sit at least this far (m) above the body (critic r09: rope anchored below / behind, b 2.0 s). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float AnchorMinAbove = 3.f;

	/**
	 * Fraction of the anchor's lateral offset (relative to the swing direction) kept in the physics pivot.
	 * 1 = browser r13 flight dynamics (pivot = the real anchor: a facade anchor 15-25 m to the side swings him sideways).
	 * 0 = travel-plane pivot (older browser build, spiderman-learnings 02 §5): the web still draws to the real anchor but the
	 * arc stays in the direction of travel, and steering turns the whole arc about the body. P3 round-01 default: 0.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal")
	float PivotLateralKeep = 0.25f; // round 09: 0.1 -> 0.25 (the pivot keeps some of the anchor's side: a weave)

	/** Travel-plane pivot only: the pivot sits at least this high over the body at attach (m)... */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal")
	float MinPivotRise = 6.f;
	/** ...and at least this steep (deg) from the body, so an attach never turns forward speed into a vertical climb. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal")
	float MinPivotElevDeg = 35.f;

	/** Canyon keeping: extra arc dip per metre the swing entry is above the anchor band (0 = browser r10f only). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal")
	float CanyonDipK = 0.6f;

	/**
	 * Round 02 (critic: "swings are flat"): deep vertical pendulum. With PivotLateralKeep < 1 every swing's pivot is built so
	 * the circle through the body bottoms out ArcBottomMin..ArcBottomMax m above the floor (random per swing, so no two arcs
	 * are alike) and at least MinArcDrop m below the entry height (never below 3 m: car roofs).
	 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float ArcBottomMin = 5.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float ArcBottomMax = 12.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float ArcDropJitter = 5.f;   // round 07: extra drop 0..N m per swing
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float MinArcDrop = 14.f;   // round 07: 16 -> 14 (critic r06: depth AND rhythm; drop test >= 10 m)
	/** Max horizontal distance of the virtual pivot ahead of the body (m). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float MaxPivotAhead = 30.f;   // round 07: 55 -> 30
	/** Longest virtual rope (m): high entries keep a brisk ~2 s arc and bottom out higher instead of a slow 50 m pendulum. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float RopeCapJitter = 0.12f;   // round 07: rope cap 30-34 m per swing
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal") float MaxArcRope = 34.f;   // round 07: 50 -> 34 (1.2-1.8 s swings)

	/** Deterministic trick RNG seed (replays). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Traversal")
	int32 RandomSeed = 1234;

	FWebTravCamera* Cam = nullptr;
	FWebTravWorld TravWorld;
	TUniquePtr<FWebTravAnchors> Anchors;
	TArray<FWebTravEvent> Events;
	FWebTravStrand Strands[2];

	// ---- read-only accessors for camera / telemetry (metres)
	EWebTravMode Mode() const { return S.Mode; }
	FName Sub() const { return S.Sub; }
	double ModeT() const { return S.ModeT; }
	const FVector& PosM() const { return S.Pos; }
	const FVector& VelM() const { return S.Vel; }
	FVector RootPosM() const { return RootPos; }
	double Facing() const { return S.Facing; }
	bool IsDiving() const { return S.bDive || S.bGliding; }
	/** Round 10: airborne from a sky launch (jump-release + trick) and not yet falling into the dive. */
	/** Round 10: feet height over the street / building mass below (props, trees, awnings ignored). */
	double HeightAboveStreet() const { return FeetZ() - TravWorld.StreetHeight(S.Pos.X, S.Pos.Y, FeetZ() + 0.1); }
	bool IsSkyLaunch() const { return S.bSky && S.Mode == EWebTravMode::Air; }
	/** Round 10: roofline (m, world Z) of the LOWER of the two street walls beside the path 0..Ahead m ahead along Dir; -1 if none. */
	double RoofBesideAhead(const FVector& Dir, double Ahead = 60.0) const;
	/** Round 10: that roofline over the street below (m), along the current horizontal velocity; -1 if none. */
	double SkyRoofOverStreet() const;
	/** Round 10: sky-launch telemetry: the peak the launch was solved for (m over the street), the roofline used (m over the street). */
	double SkyPeakWant = 0.0, SkyRoofUsed = 0.0;
	mutable bool bRoofDebug = false;
	bool IsSwinging() const { return S.Mode == EWebTravMode::Swing; }
	const FVector& SwingAnchor() const { return S.Sw.Anchor; }
	const FVector& SwingDir() const { return S.Sw.Dir; }
	double SwingTension() const { return S.Sw.Tension; }
	double SwingBank() const { return S.Sw.Bank; }
	double SwingRope() const { return S.Sw.Rope; }
	double SwingTime() const { return S.Sw.T; }
	int32 Chain() const { return S.Chain; }
	const FVector& WallNormal() const { return S.W.Normal; }
	FName TrickName() const { return S.Trick; }
	double HeightAboveFloor_() const { return HeightAboveFloor(); }
	double FloorBelow() const { return FloorAt(S.Pos.X, S.Pos.Y, FeetZ() + 0.1); }
	bool HasZipTarget() const { return Anchors && Anchors->HasTarget(); }
	FVector ZipTargetPos() const { return Anchors && Anchors->HasTarget() ? Anchors->Best().Pos : FVector::ZeroVector; }
	FQuat BodyQuat() const { return FinalQ; }
	/** Round 06 capture pre-roll: write Anim / root from the current state without stepping the simulation. */
	void PosePreview() { FinalQ = Orient(1e-4); WriteAnim(FinalQ); }
	int32 BuildingCount() const { return TravWorld.Boxes.Num(); }
	int32 ZipKindCode() const;

private:
	enum class EKin : uint8 { None, Vault, CornerWrap, WallHop };

	struct FSwing
	{
		FVector Anchor = FVector::ZeroVector, Normal = FVector::ForwardVector, Pivot = FVector::ZeroVector, Dir = FVector::ForwardVector;
		double Rope = 20, RopeTarget = 20, T = 0, Phase = 0, Bank = 0, Tension = 0, Kick = 0, KickCd = 0, AngMax = -9, Angle = 0, TautT = 0, Y0 = 0;
		double SideT = 0, SideK = 0, ModelT = 0, WrapT = 0, FdTension = 0;
		bool bRightHand = true, bApexed = false, bSideN = false;
		FVector SideN = FVector::ZeroVector;
		FName Kind;
	};
	struct FZip
	{
		FVector Target = FVector::ZeroVector, Normal = FVector::ForwardVector, P0 = FVector::ZeroVector, P1 = FVector::ZeroVector, P2 = FVector::ZeroVector;
		FVector FlightDir = FVector::ForwardVector, LaunchDir = FVector::ForwardVector;
		FName Kind;
		double T = 0, U = 0, Tau = 0, Dur = 0.5, FireDur = 0.05, Taut = 0, Len = 0, V0 = 0, VP = 0, DR = 0, DC = 0, DB = 0, TC = 0, TBrake = 0, AB = 0, Pitch = 0;
		double LUT[33] = { 0 };
		bool bLaunch = false, bDash = false, bWebs = false, bFromGround = false;
	};
	struct FPerch
	{
		FVector Pos = FVector::ZeroVector, Normal = FVector::ForwardVector, Impact = FVector::ZeroVector;
		FName Kind;
		bool bRoof = true;
	};
	struct FWall
	{
		FVector Normal = FVector::ForwardVector, Up = FVector::UpVector, Point = FVector::ZeroVector, LockDir = FVector::ZeroVector;
		FVector2D Move = FVector2D::ZeroVector;
		double RunV = 0, Phase = 0, Off = 0, Dist = 0.38, RunK = 0, LockMx = 0, ZipT = 0;
		bool bFast = false, bLockDir = false, bZipWeb = false;
	};
	struct FKin
	{
		EKin Type = EKin::None;
		double T = 0, Dur = 0.3, Sp = 0, Floor = 0;
		FVector P0 = FVector::ZeroVector, P1 = FVector::ZeroVector, P2 = FVector::ZeroVector, N0 = FVector::ZeroVector, N1 = FVector::ZeroVector;
		FVector ExitVel = FVector::ZeroVector, Dir1 = FVector::ZeroVector;
		bool bRun = false, bHasDir1 = false;
		// wallHop
		double TA = 0, TB = 0, F0 = 0, Apex = 0, LandTop = 0, DTot = 0, ExitSpeed = 0;
		FVector Inward = FVector::ZeroVector;
	};
	struct FQuick
	{
		bool bActive = false, bRightHand = true, bApplied = false, bWebOn = false, bSky = false;
		double T = 0, HitT = 0.08, Dist = 0, K = 1, Last = -9;
		int32 N = 0, Seq = 0;
		FVector Anchor = FVector::ZeroVector, Normal = FVector::ForwardVector;
	};
	struct FState
	{
		EWebTravMode Mode = EWebTravMode::Air;
		FName Sub;
		double SubT = 0, ModeT = 0;
		FVector Pos = FVector::ZeroVector, Vel = FVector::ZeroVector, Carry = FVector::ZeroVector;
		double Facing = 0, Speed = 0, FloorZ = 0, StepOff = 0;
		bool bGrounded = false, bCharging = false;
		double ChargeT = 0, JumpCharge = 0, Coyote = 0, JumpBuf = 0;
		double AirT = 0, ApexZ = 0, RelT = 99, NoAnchorT = 0, AirTapT = -9;
		bool bDive = false, bGliding = false, bGroundSwing = false, bJumpRelHold = false, bAirTrickUsed = false;
		FSwing Sw;
		int32 Chain = 0;
		double SinceSwing = 99;
		bool bLastTrick = false, bTrickBoosted = false, bTrickNoUp = false;
		FName Trick, LastTrickName;
		double TrickSide = 1, TrickDur = 0, TrickSnapT = 9, TrickLat = 0, TrickSteep = 0;
		double TrickBuf = 0;
		double SearchT = 0, SwingCooldown = 0, WallCooldown = 0, ZipCooldown = 0, DashWebT = 0, QuickBuf = 0;
		int32 DashCount = 0;
		FZip Z;
		FPerch P;
		FWall W;
		FKin Kin;
		double LandSeverity = 0, LandLock = 0;
		FQuat BodyQ = FQuat::Identity;
		double Roll = 0, Pitch = 0, Bank = 0, RollA = 0, PitchA = 0;
		bool bSky = false;      // round 10: sky launch (jump-release + trick) until the next web / landing
		bool bTopOut = false;   // round 06: airborne from a wall-run top-out (crouch landing on touchdown)
		int32 SwingIdx = 0;     // round 09: swings started (alternating arc depth)
		int32 LastAnchorSide = 0; // round 09: side of the last web anchor (+1 right of travel, -1 left)
		// round 07: web stuck on the rise, swing pending until the top of the hop
		bool bWebPending = false, bPendingTurn = false, bPendingRight = true;
		double PendingT = 0;
		FTravAnchor PendingA;
		FVector PendingFwd = FVector::ForwardVector, PendingTurn = FVector::ForwardVector;
		FQuick Q;
		double Clock = 0;
	};

	// ---- helpers
	double FeetZ() const { return S.Pos.Z - H; }
	double FloorAt(double X, double Y, double Z) const { return TravWorld.GroundHeight(X, Y, Z - 0.5); }
	double StandAt(double X, double Y, double Z) const;
	FVector InputDir(const FWebTravInput& I) const;
	void SetMode(EWebTravMode M, FName Sub);
	void SetSub(FName Sub);
	bool Collide(double StepH, double Rad, FTravContact& C);
	bool Collide(FTravContact& C) { return Collide(STEP, R, C); }
	static bool HDir(const FVector& V, FVector& Out);
	double VmaxC() const { return VMAX + CHAIN_CAP * S.Chain; }
	void CapSpeed(double M);
	void CapSpeed() { CapSpeed(VmaxC()); }
	double HeightAboveFloor() const { return FeetZ() - FloorAt(S.Pos.X, S.Pos.Y, FeetZ() + 0.1); }
	double ReleaseBoost() const { return RELEASE_BOOST * ReleaseBoostMul; }
	void Emit(FName Type, float Sev = 0.f, float Dist = 0.f, float K = 1.f, bool bRun = false);

	// ---- web strands
	void WebAttach(bool bRight, const FVector& Anchor, double ShootDur = 0.08, bool bSecond = false);
	void WebRelease(bool bSnap = false);
	void WebReleaseSecond();

	// ---- ground
	void EnterGround(FName Sub);
	void StepGround(double H, FWebTravInput& I);
	bool StartMantleOnto(const FTravContact& C);
	void LaunchJump(bool bParkour);
	void StartVault(const FTravContact& C, bool bFast);
	// ---- air
	void StepAir(double H, FWebTravInput& I);
	void Land(double F, const FWebTravInput& I);
	void Corridor(double H, const FVector& InD);
	// ---- swing
	bool SteerHeading(const FVector& InD, FVector& Out) const;
	double FacadeAvoid(double H);
	FVector TravelDir(const FWebTravInput& I) const;
	bool TryStartSwing(const FWebTravInput& I);
	void StartSwing(const FTravAnchor& A, const FVector& Fwd, const FVector* Turn, double HS);
	double SwingPhase() const;
	FVector PivotFor(const FVector& AnchorPoint) const;
	double SwingAngle() const;
	void StepSwing(double H, FWebTravInput& I);
	bool AnchorCheck(double H);
	void Reanchor(const FTravAnchor& A);
	void RopeWrap(double H);
	// ---- tricks / release
	FName ChooseTrick(const FWebTravInput& I);
	void StartTrick(FName Name);
	void TrickBoost(const FWebTravInput& I);
	void ReleaseSwing(bool bJump, const FWebTravInput& I);
	// ---- wall
	bool WideWall(const FVector& N, const FVector& Point) const;
	void EnterWall(const FVector& N, const FVector& Point, bool bRun, double Speed);
	FVector WallBasis(const FVector& N) const;
	void StepWall(double H, FWebTravInput& I);
	void WallZip();
	double WallProtrusion(const FVector& N, double BX, double BY) const;
	void StartCornerWrap(const FVector& N1, const FVector& P1, double Dur, const FVector& Dir1, double Mx);
	bool StartWallHop(const FVector& N, bool bFast);
	void StepWallHop(double H);
	void StepKin(double H);
	// ---- zip / perch / launches
	void StartZip(const FTravZipPoint& T);
	void ZipCurve(const FVector& Vel);
	double ZipDist(double Tau) const;
	double ZipArcE(double D) const;
	bool ZipClear() const;
	FVector Bez(double E) const;
	void StepZip(double H, FWebTravInput& I);
	void ArriveZip();
	void AnchorLaunch(const FVector& TravelV);
	void PointLaunch(const FVector& Normal, const FVector& TravelV);
	void WebDash();
	// ---- quick boost
	void QuickAnchor(FVector& Out, FVector& NOut, double& Dist, bool& bSky);
	void QuickBoostStart();
	void QuickImpulse();
	void StepQuickBoost(double Dt);
	void StepPerch(double H, FWebTravInput& I);
	// ---- orientation / anim
	FQuat Orient(double Dt);
	void WriteAnim(const FQuat& Q);

	FState S;
	FRandomStream Rng;
	FWebTravInput LastInput;
	bool bLeaveSwingOK = false;
	bool bWorldReady = false;
	FVector RootPos = FVector::ZeroVector;
	FQuat FinalQ = FQuat::Identity;
	double LastVelYaw = 0;
	double CorrT = 0; FVector CorrPush = FVector::ZeroVector;
	FVector CorrWallN[8]; double CorrWallD[8] = { 0 }; int32 CorrN = 0; // round 08: facade planes around the body (normal, distance m)
	double AvoidT = 0, AvoidRate = 0;

public:
	// ---- constants (browser traversal.js :16-65)
	static constexpr double H = 0.95, R = 0.36, HEIGHT = 1.8, STEP = 0.55, G = 24, GS = 25;
	static constexpr double WALK = 2.6, RUN = 9.8, SPRINT = 15.5, WALLRUN = 14, VMAX = 45;
	static constexpr double CHAIN_BUF = 1.6, CHAIN_CAP = 2.5, CHAIN_REL = 1.5;
	static constexpr int32 CHAIN_MAX = 6;
	static constexpr double SWING_JUMP = 4.0, SWING_JUMP_UP = 16, SWING_JUMP_VY = 22, REL_NOTRICK = 4.0, REL_UP = 9, REL_UP_VY = 16;
	static constexpr double SWING_DIP = 6, SWING_GAIN = 5, RELEASE_BOOST = 1.5, SWING_DRAG = 0.0022, PUMP_MAX_ANG = 1.15;
	static constexpr double JUMP = 11.2, JUMP_MAX = 19.5;
	// round 06 wall-run body: lean back off the wall (rad) and feet offset from the wall plane (m) while running
	static constexpr double WallRunLean = 0.16, WallRunFootOff = 0.42;
	static constexpr double WEB_MASS = 80;
};
