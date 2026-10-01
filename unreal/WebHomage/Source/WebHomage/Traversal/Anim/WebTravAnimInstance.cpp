// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Traversal/Anim/WebTravAnimInstance.h"
#include "Traversal/WebTravFlips.h"
#include "WebHomage.h"

#include "Animation/AnimNodeBase.h"
#include "Animation/AnimSequence.h"
#include "AnimationRuntime.h"
#include "Components/SkeletalMeshComponent.h"
#include "BonePose.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

FString UWebTravAnimInstance::ClipRoot = TEXT("/Game/Traversal/HeroDev");
FString UWebTravAnimInstance::ClipPrefix;
bool UWebTravAnimInstance::bWallGait = true;

namespace
{
	float Smooth01(float X) { X = FMath::Clamp(X, 0.f, 1.f); return X * X * (3.f - 2.f * X); }
#define WA_NAME(x) const FName NA_##x(TEXT(#x));
	WA_NAME(ground) WA_NAME(jumpCharge) WA_NAME(jumpLaunch) WA_NAME(land) WA_NAME(air) WA_NAME(trick) WA_NAME(swing) WA_NAME(zip)
	WA_NAME(perch) WA_NAME(crawl) WA_NAME(wallRun) WA_NAME(wallJump) WA_NAME(corner) WA_NAME(pointLaunch) WA_NAME(vault) WA_NAME(topOut)
#undef WA_NAME
}

// ------------------------------------------------------------------ game thread
void UWebTravAnimInstance::NativeInitializeAnimation()
{
	Super::NativeInitializeAnimation();
	{ int32 G = 1; if (FParse::Value(FCommandLine::Get(), TEXT("-WHWallGait="), G)) bWallGait = G != 0; }
	static const TCHAR* Names[] = { TEXT("idle"), TEXT("walk"), TEXT("jog"), TEXT("run"), TEXT("sprint"), TEXT("jumpCrouch"), TEXT("jumpLaunchSmall"),
		TEXT("jumpLaunchHigh"), TEXT("jump"), TEXT("land"), TEXT("landLight"), TEXT("landMedium"), TEXT("landHard"), TEXT("landRoll"),
		TEXT("airRise"), TEXT("airApex"), TEXT("fall"), TEXT("fallCalm"), TEXT("fallFast"), TEXT("releaseSpread"), TEXT("releaseTuck"),
		TEXT("releaseFlip"), TEXT("releaseCorkscrew"), TEXT("airTrick"), TEXT("webShootR"), TEXT("webShootL"), TEXT("pointLaunch"),
		TEXT("wallJump"), TEXT("webZipPull"), TEXT("webZipFire"), TEXT("zipFlight"), TEXT("zipFlightLevel"), TEXT("zipCatch"),
		TEXT("swingLow"), TEXT("swingBottom"), TEXT("swingHigh"), TEXT("swingLowL"), TEXT("swingBottomL"), TEXT("swingHighL"),
		TEXT("swingCornerBank"), TEXT("swingCornerBankL"), TEXT("perchLand"), TEXT("perchIdle"), TEXT("wallCrawl"), TEXT("wallIdle"),
		TEXT("wallRun"), TEXT("wallRunHorizontal"), TEXT("cornerWrap"), TEXT("wallToRoofVault") };
	int32 Missing = 0;
	for (const TCHAR* N : Names)
	{
		const FString Asset = ClipPrefix + N; // round 10: P2 names clips A_Hero_<clip>
		const FString Path = FString::Printf(TEXT("%s/%s.%s"), *ClipRoot, *Asset, *Asset);
		UAnimSequence* S = LoadObject<UAnimSequence>(nullptr, *Path);
		if (S) Clips.Add(FName(N), S); else ++Missing;
	}
	// round 11: gymnast shape clips keyed in Blender (docs/night1/traversal/blender/make_flip_shapes.py), spliced into the hero GLB
	int32 NFlip = 0;
	for (int32 K = 0; K < int32(EWebFlipShape::Num); ++K)
	{
		const FString Asset = ClipPrefix + WebFlips::ShapeClip(EWebFlipShape(K));
		const FString Path = FString::Printf(TEXT("%s/%s.%s"), *ClipRoot, *Asset, *Asset);
		if (UAnimSequence* S = LoadObject<UAnimSequence>(nullptr, *Path)) { Clips.Add(FName(WebFlips::ShapeClip(EWebFlipShape(K))), S); ++NFlip; }
	}
	bFlipClips = NFlip == int32(EWebFlipShape::Num);
	UE_LOG(LogWebHomage, Display, TEXT("WebTravAnimInstance: %d clips loaded from %s/%s* (%d missing), flip shapes %d/%d"), Clips.Num(), *ClipRoot, *ClipPrefix, Missing,
		NFlip, int32(EWebFlipShape::Num));
}

UAnimSequence* UWebTravAnimInstance::Clip(FName Name)
{
	TObjectPtr<UAnimSequence>* S = Clips.Find(Name);
	return S ? S->Get() : nullptr;
}

void UWebTravAnimInstance::SetDrive(const FWebTravAnim& InAnim, bool bInWebActive, const FVector& InWebAnchorWorldCm, bool bInWebRight, bool bInSwingHeld)
{
	A = InAnim;
	bWebActive = bInWebActive;
	WebAnchorWorld = InWebAnchorWorldCm;
	bWebRight = bInWebRight;
	bSwingHeld = bInSwingHeld;
}

FName UWebTravAnimInstance::Category(FName Node)
{
	const FString S = Node.ToString();
	if (S.StartsWith(TEXT("air_"))) return NA_air;
	if (S.StartsWith(TEXT("trick_")) || S.StartsWith(TEXT("flip_"))) return NA_trick;
	if (S.StartsWith(TEXT("land_"))) return NA_land;
	if (S.StartsWith(TEXT("zip_"))) return NA_zip;
	if (S.StartsWith(TEXT("perch_"))) return NA_perch;
	return Node;
}

// browser animator.js TRANS (seconds): TRANS[from][to] ?? TRANS[from]['*'] ?? TRANS['*'][to] ?? 0.2
float UWebTravAnimInstance::BlendTime(FName F, FName T)
{
	struct FRow { FName From, To; float S; };
	static const FRow Rows[] = {
		{ NAME_None, NA_land, 0.1f }, { NAME_None, NA_jumpCharge, 0.16f }, { NAME_None, NA_jumpLaunch, 0.12f }, { NAME_None, NA_swing, 0.24f },
		{ NAME_None, NA_zip, 0.14f }, { NAME_None, NA_trick, 0.16f }, { NAME_None, NA_perch, 0.14f }, { NAME_None, NA_crawl, 0.28f },
		{ NAME_None, NA_wallRun, 0.28f }, { NAME_None, NA_wallJump, 0.12f }, { NAME_None, NA_vault, 0.14f }, { NAME_None, NA_corner, 0.16f },
		{ NAME_None, NA_pointLaunch, 0.14f },
		{ NA_ground, NA_jumpCharge, 0.18f }, { NA_ground, NA_jumpLaunch, 0.2f }, { NA_ground, NA_air, 0.28f }, { NA_ground, NA_wallRun, 0.3f },
		{ NA_jumpCharge, NA_jumpLaunch, 0.14f }, { NA_jumpCharge, NA_ground, 0.24f },
		{ NA_jumpLaunch, NA_air, 0.38f }, { NA_jumpLaunch, NA_land, 0.12f },
		{ NA_air, NA_ground, 0.2f }, { NA_air, NA_land, 0.1f }, { NA_air, NA_swing, 0.26f }, { NA_air, NA_air, 0.25f },
		{ NA_swing, NA_air, 0.34f }, { NA_swing, NA_trick, 0.18f }, { NA_swing, NA_swing, 0.3f },
		{ NA_trick, NA_air, 0.22f } /* round 06: 0.4 -> 0.22 (sway now ramps in; the long blend held the flip's end pose) */, { NA_land, NA_ground, 0.38f }, { NA_land, NA_jumpCharge, 0.18f }, { NA_land, NA_jumpLaunch, 0.14f },
		{ NA_zip, NA_perch, 0.14f }, { NA_zip, NA_air, 0.34f }, { NA_perch, NA_ground, 0.34f },
		{ NA_crawl, NA_wallRun, 0.3f }, { NA_crawl, NA_air, 0.32f }, { NA_crawl, NA_jumpLaunch, 0.26f }, { NA_crawl, NA_wallJump, 0.24f },
		{ NA_wallRun, NA_crawl, 0.36f }, { NA_wallRun, NA_air, 0.34f }, { NA_wallRun, NA_jumpLaunch, 0.26f }, { NA_wallRun, NA_wallJump, 0.24f },
		{ NA_wallRun, NA_ground, 0.3f }, { NA_wallJump, NA_air, 0.4f },
		{ NA_wallRun, NA_topOut, 0.16f }, { NA_topOut, NA_land, 0.12f }, { NA_topOut, NA_air, 0.3f },
	};
	for (const FRow& R : Rows) { if (R.From == F && R.To == T) return R.S; }
	for (const FRow& R : Rows) { if (R.From == NAME_None && R.To == T) return R.S; }
	return 0.2f;
}

FName UWebTravAnimInstance::PickNode(float Dt)
{
	const FString Sub = A.Sub.ToString();
	switch (A.Mode)
	{
	case EWebTravMode::Ground:
		if (Sub == TEXT("jumpCharge")) return NA_jumpCharge;
		if (Sub == TEXT("vault")) return NA_vault;
		return NA_ground;
	case EWebTravMode::Land:
		return FName(*(TEXT("land_") + Sub));
	case EWebTravMode::Swing:
		return NA_swing;
	case EWebTravMode::Zip:
		return FName(*(TEXT("zip_") + Sub));
	case EWebTravMode::Perch:
		return A.Sub == FName(TEXT("perchLand")) ? FName(TEXT("perch_land")) : FName(TEXT("perch_idle"));
	case EWebTravMode::Wall:
		if (Sub == TEXT("wallRun")) return NA_wallRun;
		if (Sub == TEXT("wallRunSide")) return FName(TEXT("wallRunSide"));
		if (Sub == TEXT("cornerWrap")) return NA_corner;
		if (Sub == TEXT("wallZip")) return FName(TEXT("wallZip"));
		return NA_crawl;
	case EWebTravMode::Air:
	default:
		break;
	}
	// ---- air
	if (Sub == TEXT("topOut")) return bFlipClips ? FName(TEXT("flip_wallFront")) : NA_topOut; // round 06: wall-run top-out flip (r11: program)
	if (Sub == TEXT("trick") && !A.Trick.IsNone())
	{
		if (bFlipClips && WebFlips::Find(A.Trick)) return FName(*(TEXT("flip_") + A.Trick.ToString())); // round 11: flip program
		return FName(*(TEXT("trick_") + A.Trick.ToString()));
	}
	if (Sub == TEXT("jumpLaunch")) return NA_jumpLaunch;
	if (Sub == TEXT("pointLaunch")) return NA_pointLaunch;
	if (Sub == TEXT("wallJump")) return NA_wallJump;
	if (Sub == TEXT("zipPull")) return FName(TEXT("air_zipPull"));
	if (A.bDive) return FName(TEXT("air_dive"));
	// air cycle after a web release: per-cycle flavor timeline (never the previous cycle's flavor)
	if (bInAirCycle)
	{
		const float T = AirCycleT;
		// round 10 (critic r09 a 7.7-7.9 s: raised-fist hang with no rope): no held reach pose while searching for a web;
		// the web arm aims only once a strand is out (swing node)
		(void)bReachRight;
		const float TailStart = FlavorIdx == 0 ? 1.0f : FlavorIdx == 3 ? 0.8f : 0.9f;
		if (T >= TailStart) // long fall: alternate the two fall clips every 0.45 s (never one held pose)
			return (int32((T - TailStart) / 0.45f) % 2 == 0) ? (FlavorIdx % 2 ? FName(TEXT("air_fall")) : FName(TEXT("air_fallCalm")))
				: (FlavorIdx % 2 ? FName(TEXT("air_fallCalm")) : FName(TEXT("air_fall")));
		switch (FlavorIdx)
		{ // short segments of moving clips (no held static pose)
		case 0: return T < 0.55f ? FName(TEXT("air_spread")) : T < 1.0f ? FName(TEXT("air_fallCalm")) : FName(TEXT("air_fall"));
		case 1: return T < 0.45f ? FName(TEXT("air_tuck")) : T < 0.9f ? FName(TEXT("air_rise")) : FName(TEXT("air_fallCalm"));
		case 2: return T < 0.4f ? FName(TEXT("air_rise")) : T < 0.9f ? FName(TEXT("air_spread")) : FName(TEXT("air_fall"));
		default: return T < 0.4f ? FName(TEXT("air_fallCalm")) : T < 0.8f ? FName(TEXT("air_tuck")) : FName(TEXT("air_fall"));
		}
	}
	if (Sub == TEXT("rise")) return FName(TEXT("air_rise"));
	if (Sub == TEXT("apex")) return FName(TEXT("air_apex"));
	if (Sub == TEXT("dive")) return FName(TEXT("air_dive"));
	return FName(TEXT("air_fall"));
}

void UWebTravAnimInstance::BuildNode(FName Node, float T, TArray<FWebTravAnimLayer>& Out)
{
	Out.Reset();
	auto Add = [&](FName ClipName, float Time, float W, bool bLoop)
	{
		UAnimSequence* S = Clip(ClipName);
		if (!S || W <= 0.001f) return;
		const float Len = S->GetPlayLength();
		const float Tt = bLoop ? FMath::Fmod(FMath::Max(0.f, Time), FMath::Max(Len, 0.01f)) : FMath::Clamp(Time, 0.f, Len);
		Out.Add({ S, Tt, W, bLoop });
	};
	const FString N = Node.ToString();
	const float Sp = A.Speed;
	if (Node == NA_ground)
	{ // locomotion anchors (browser LOCO): walk 1.6, jog 4.5, run 8.5, sprint 14 m/s; one shared normalized phase
		struct FL { const TCHAR* C; float V; };
		static const FL Loco[] = { { TEXT("walk"), 1.6f }, { TEXT("jog"), 4.5f }, { TEXT("run"), 8.5f }, { TEXT("sprint"), 14.f } };
		if (Sp < 0.25f) { Add(TEXT("idle"), T, 1.f, true); return; }
		int32 K = 0;
		while (K < 3 && Sp > Loco[K + 1].V) ++K;
		const float W1 = K < 3 ? FMath::Clamp((Sp - Loco[K].V) / (Loco[K + 1].V - Loco[K].V), 0.f, 1.f) : 0.f;
		UAnimSequence* S0 = Clip(Loco[K].C);
		const float Len0 = S0 ? S0->GetPlayLength() : 1.f;
		LocoPhase = FMath::Fmod(LocoPhase + GetDeltaSeconds() * (Sp / Loco[K].V) / Len0 * (Sp < Loco[0].V ? 1.f : 1.f), 1.f);
		const float IdleW = Sp < Loco[0].V ? 1.f - Sp / Loco[0].V : 0.f;
		Add(TEXT("idle"), T, IdleW, true);
		for (int32 J = K; J <= FMath::Min(K + 1, 3); ++J)
		{
			UAnimSequence* S = Clip(Loco[J].C);
			const float W = (J == K ? 1.f - W1 : W1) * (1.f - IdleW);
			if (S) Add(Loco[J].C, LocoPhase * S->GetPlayLength(), W, true);
		}
		return;
	}
	if (Node == NA_jumpCharge) { Add(TEXT("jumpCrouch"), 0.08f + A.JumpCharge * 0.4f, 1.f, false); return; }
	if (Node == NA_jumpLaunch) { Add(A.JumpCharge > 0.5f ? TEXT("jumpLaunchHigh") : TEXT("jumpLaunchSmall"), T, 1.f, false); return; }
	if (Node == NA_vault) { Add(TEXT("jump"), T, 1.f, false); return; }
	if (N.StartsWith(TEXT("land_")))
	{
		const FString S = N.Mid(5);
		if (S == TEXT("landTopOut")) { Add(TEXT("perchLand"), T + 0.22f, 1.f, false); return; } // planted crouch, then the settle blend
		Add(S == TEXT("landRoll") ? TEXT("landRoll") : S == TEXT("landHard") ? TEXT("landHard") : S == TEXT("landMedium") ? TEXT("landMedium") : TEXT("landLight"), T, 1.f, false);
		return;
	}
	if (Node == NA_swing)
	{ // 3-way swing blend by arc phase (browser: bottom base, low by smoothstep(-ph), high by smoothstep(ph)) + corner bank
		const bool bL = !A.Swing.bRightHand;
		const float Ph = A.Swing.Phase;
		const float WLow = Smooth01(-Ph / 0.8f), WHigh = Smooth01(Ph / 0.8f);
		const float WBank = 0.85f * Smooth01(FMath::Abs(A.Swing.Bank));
		const float Base = 1.f - WBank;
		Add(bL ? TEXT("swingBottomL") : TEXT("swingBottom"), T, (1.f - WLow - WHigh) * Base, true);
		Add(bL ? TEXT("swingLowL") : TEXT("swingLow"), T, WLow * Base, true);
		Add(bL ? TEXT("swingHighL") : TEXT("swingHigh"), T, WHigh * Base, true);
		Add(bL ? TEXT("swingCornerBankL") : TEXT("swingCornerBank"), T, WBank, true);
		return;
	}
	if (N.StartsWith(TEXT("flip_")))
	{ // round 11: flip program — shapes on the program timeline (upper body leads, legs lag: Frame.LegLayers)
		BuildFlipLayers(FName(*N.Mid(5)), T, Out, PendingLegs);
		return;
	}
	if (N.StartsWith(TEXT("trick_")))
	{ // limb shape per trick (the whole-body spin is applied to the figure root, PTRICK timing)
		const FString Tr = N.Mid(6);
		const float Rate = A.TrickDur > 0.f ? 1.f / A.TrickDur : 1.f;
		if (Tr == TEXT("tuckFlip")) Add(TEXT("releaseTuck"), T * Rate * 0.667f, 1.f, false);
		else if (Tr == TEXT("layout")) Add(TEXT("releaseFlip"), T * Rate * 0.9f, 1.f, false);
		else if (Tr == TEXT("corkscrew")) Add(TEXT("releaseCorkscrew"), T * Rate * 1.0f, 1.f, false);
		else Add(TEXT("airTrick"), T * Rate * 0.9f, 1.f, false);
		return;
	}
	if (N.StartsWith(TEXT("air_")))
	{
		const FString S = N.Mid(4);
		if (S == TEXT("spread")) Add(TEXT("releaseSpread"), T, 1.f, false);
		else if (S == TEXT("tuck")) Add(TEXT("releaseTuck"), T, 1.f, false);
		else if (S == TEXT("rise")) Add(TEXT("airRise"), T, 1.f, false);
		else if (S == TEXT("apex")) Add(TEXT("airApex"), T, 1.f, false);
		else if (S == TEXT("fallCalm")) Add(TEXT("fallCalm"), T, 1.f, true);
		else if (S == TEXT("dive"))
		{ // round 09 (TRAVERSAL-SPEC T4: no held pose in a web-less phase): the dive flutters between the tucked fast fall and
		  // the spread calm fall (0.8 s period)
			const float F = 0.35f + 0.35f * FMath::Sin(2.f * PI * T / 0.8f);
			Add(TEXT("fallFast"), T, 1.f - F, true); Add(TEXT("fallCalm"), T, F, true);
		}
		else if (S == TEXT("reachR")) { Add(TEXT("webShootR"), T, 0.8f, false); Add(TEXT("airApex"), T, 0.2f, false); }
		else if (S == TEXT("reachL")) { Add(TEXT("webShootL"), T, 0.8f, false); Add(TEXT("airApex"), T, 0.2f, false); }
		else if (S == TEXT("zipPull")) Add(TEXT("webZipPull"), T, 1.f, false);
		else Add(TEXT("fall"), T, 1.f, true);
		return;
	}
	if (Node == NA_pointLaunch) { Add(TEXT("pointLaunch"), T, 1.f, false); return; }
	if (Node == NA_wallJump) { Add(TEXT("wallJump"), T, 1.f, false); return; }
	if (N.StartsWith(TEXT("zip_")))
	{
		const FString S = N.Mid(4);
		if (S == TEXT("zipFire")) Add(TEXT("webZipFire"), T, 1.f, false);
		else if (S == TEXT("zipCatch")) Add(TEXT("zipCatch"), T, 1.f, false);
		else
		{
			const float Lv = FMath::Clamp(1.f - FMath::Abs(A.Zip.Pitch) / 0.6f, 0.f, 1.f);
			Add(TEXT("zipFlight"), T, 1.f - Lv, true); Add(TEXT("zipFlightLevel"), T, Lv, true);
		}
		return;
	}
	if (N.StartsWith(TEXT("perch_"))) { if (N == TEXT("perch_land")) Add(TEXT("perchLand"), T + 0.22f, 1.f, false); /* round 09: straight into the impact crouch (its first 0.2 s is an upright arms-out pose) */ else Add(TEXT("perchIdle"), T, 1.f, true); return; }
	if ((Node == NA_wallRun || N == TEXT("wallRunSide")) && bWallGait)
	{ // round 19: procedural wall-run stride (proxy two-bone IK, FWebTravAnimFrame::WallW): the clip only gives the spine / head (upright idle)
		Add(TEXT("idle"), 0.f, 1.f, false);
		return;
	}
	if (Node == NA_wallRun)
	{ // round 06: head-up climb-run = the sprint stride on the wall (body frame from the traversal), steps driven by wall
	  // speed: 1.8 steps/s at 6 m/s .. 2.6 steps/s at 14 m/s (the clip's own stride is 3.75 steps/s)
		UAnimSequence* Spr = Clip(TEXT("sprint"));
		const float Len = Spr ? Spr->GetPlayLength() : 0.533f;
		const float StepsPerS = FMath::GetMappedRangeValueClamped(FVector2f(6.f, 14.f), FVector2f(1.8f, 2.6f), Sp);
		WallRunPhase = FMath::Fmod(WallRunPhase + GetDeltaSeconds() * StepsPerS * 0.5f, 1.f);
		Add(TEXT("sprint"), WallRunPhase * Len, 1.f, true);
		return;
	}
	if (Node == NA_topOut)
	{ // front flip over the roof edge: the releaseFlip clip carries its own full somersault and ends upright, legs
	  // forward (landing prep, held until touchdown); stretched to ~1.1 s to fill the top-out air time
		const float Tf = T * 0.72f;
		Add(TEXT("releaseFlip"), FMath::Min(Tf, 0.78f), 1.f, false); // the clip's last 0.1 s opens the arms wide
		// flip done, still falling to the roof: the limbs keep moving (a light fall cycle over the upright end pose)
		if (Tf > 0.78f) Add(TEXT("fallCalm"), Tf - 0.78f, 0.45f * FMath::Clamp((Tf - 0.78f) / 0.15f, 0.f, 1.f), true);
		return;
	}
	if (N == TEXT("wallRunSide")) { Add(TEXT("wallRunHorizontal"), T * FMath::Max(0.6f, Sp / 7.f), 1.f, true); return; }
	if (Node == NA_corner) { Add(TEXT("cornerWrap"), T, 1.f, false); return; }
	if (N == TEXT("wallZip")) { Add(TEXT("webZipPull"), T, 1.f, false); return; }
	if (Node == NA_crawl) { if (Sp > 0.3f) Add(TEXT("wallCrawl"), T * FMath::Max(0.5f, Sp / 1.4f), 1.f, true); else Add(TEXT("wallIdle"), T, 1.f, true); return; }
	Add(TEXT("idle"), T, 1.f, true);
}

void UWebTravAnimInstance::BuildFlipLayers(FName Program, float T, TArray<FWebTravAnimLayer>& Out, TArray<FWebTravAnimLayer>& OutLegs)
{
	OutLegs.Reset();
	const FWebFlipProgram* P = WebFlips::Find(Program);
	if (!P) return;
	const FWebFlipPose Po = WebFlips::Sample(*P, T);
	// a held shape "breathes": its 1 s clip runs 0 -> 1 s over the hold (limbs open ~7 % by the end of the hold)
	auto AddShape = [&](TArray<FWebTravAnimLayer>& Dst, EWebFlipShape S, float Hold, float W)
	{
		UAnimSequence* Seq = Clip(FName(WebFlips::ShapeClip(S)));
		if (!Seq || W <= 0.001f) return;
		Dst.Add({ Seq, FMath::Clamp(Hold, 0.f, 1.f) * Seq->GetPlayLength(), W, false });
	};
	{ // round 19: tuck share of the upper body and the legs (both must be tucked for the wrists-to-shins hold)
		const float TU = (Po.A == EWebFlipShape::Tuck ? 1.f - Po.W : 0.f) + (Po.B == EWebFlipShape::Tuck ? Po.W : 0.f);
		const float TL = (Po.LA == EWebFlipShape::Tuck ? 1.f - Po.LW : 0.f) + (Po.LB == EWebFlipShape::Tuck ? Po.LW : 0.f);
		PendingTuckW = FMath::Clamp(FMath::Min(TU, TL) * 1.6f - 0.3f, 0.f, 1.f);
	}
	AddShape(Out, Po.A, Po.HoldA, 1.f - Po.W);
	if (Po.B != Po.A || Po.W > 0.f) AddShape(Out, Po.B, Po.HoldB, Po.W);
	AddShape(OutLegs, Po.LA, Po.LHoldA, 1.f - Po.LW);
	if (Po.LB != Po.LA || Po.LW > 0.f) AddShape(OutLegs, Po.LB, Po.LHoldB, Po.LW);
}

void UWebTravAnimInstance::NativeUpdateAnimation(float Dt)
{
	Super::NativeUpdateAnimation(Dt);
	// air cycle bookkeeping: a cycle starts at a web release and ends at the next attach / landing
	// (any exit from a swing into the air: plain release, trick, quick boost, jump-release)
	const bool bRelease = A.Mode == EWebTravMode::Air && A.Sub != NA_topOut
		&& (LastMode != EWebTravMode::Air || A.Sub == FName(TEXT("release"))); // any entry into the air (not a wall top-out)
	if (bRelease && !bInAirCycle)
	{
		bInAirCycle = true; AirCycleT = 0.f; ++CycleCount;
		// deterministic flavor order that never repeats the previous flavor
		static const int32 Order[] = { 0, 2, 1, 3, 2, 0, 3, 1 };
		int32 Next = Order[CycleCount % 8];
		if (Next == FlavorIdx) Next = (Next + 1) % 4;
		FlavorIdx = Next;
		bReachRight = !bReachRight;
	}
	if (A.Mode != EWebTravMode::Air) bInAirCycle = false;
	AirCycleT += Dt;

	const FName Node = PickNode(Dt);
	if (Node != CurNode)
	{
		// snapshot the current output (already faded) as the "previous" pose set
		PrevLayers = Frame.Layers;
		FadeDur = FMath::Max(0.05f, BlendTime(Category(CurNode), Category(Node)));
		FadeT = 0.f;
		CurNode = Node;
		NodeT = 0.f;
	}
	NodeT += Dt;
	FadeT += Dt;
	for (FWebTravAnimLayer& L : PrevLayers)
	{
		if (!L.Seq) continue;
		const float Len = L.Seq->GetPlayLength();
		L.Time = L.bLoop ? FMath::Fmod(L.Time + Dt, FMath::Max(Len, 0.01f)) : FMath::Min(L.Time + Dt, Len);
	}
	TArray<FWebTravAnimLayer> Cur;
	PendingLegs.Reset();
	BuildNode(CurNode, NodeT, Cur);
	const float Alpha = Smooth01(FadeT / FadeDur);
	TArray<FWebTravAnimLayer> OutL;
	float PrevSum = 0.f;
	for (const FWebTravAnimLayer& L : PrevLayers) PrevSum += L.Weight;
	if (Alpha < 1.f && PrevSum > 0.001f)
	{
		for (FWebTravAnimLayer L : PrevLayers) { L.Weight *= (1.f - Alpha) / PrevSum; OutL.Add(L); }
	}
	float CurSum = 0.f;
	for (const FWebTravAnimLayer& L : Cur) CurSum += L.Weight;
	const float CurScale = OutL.Num() ? Alpha : 1.f; // prev layers present -> current fades in
	for (FWebTravAnimLayer L : Cur) { L.Weight *= CurScale / FMath::Max(CurSum, 0.001f); OutL.Add(L); }
	if (Alpha >= 1.f) PrevLayers.Reset();
	Frame.Layers = OutL;
	// round 11: leg overlay of a flip program fades with the node blend (Alpha), or out over its prev-fade when the flip ended
	if (PendingLegs.Num()) { Frame.LegLayers = PendingLegs; Frame.LegW = OutL.Num() && PrevLayers.Num() ? Alpha : 1.f; }
	else if (Frame.LegW > 0.f) { Frame.LegW = FMath::Max(0.f, Frame.LegW - Dt / FMath::Max(0.05f, FadeDur)); if (Frame.LegW <= 0.f) Frame.LegLayers.Reset(); }
	TotalWeight = 0.f;
	float Best = -1.f;
	Dominant = NAME_None;
	for (const FWebTravAnimLayer& L : OutL)
	{
		TotalWeight += L.Weight;
		if (L.Weight > Best) { Best = L.Weight; Dominant = L.Seq ? L.Seq->GetFName() : NAME_None; }
	}
	// procedural: web-hand arm aimed at the anchor while a web is held (swing / zip), spine bank with the swing
	const USkeletalMeshComponent* Mesh = GetSkelMeshComponent();
	// (round 07: also in the air — a web stuck on the rise before its swing starts, dash / boost webs)
	const bool bAim = bWebActive && (A.Mode == EWebTravMode::Swing || A.Mode == EWebTravMode::Zip || A.Mode == EWebTravMode::Air) && Mesh;
	Frame.bArmAim = bAim;
	Frame.bArmRight = bWebRight;
	Frame.ArmAimWeight = bAim ? FMath::Clamp(Frame.ArmAimWeight + Dt / 0.15f, 0.f, 1.f) : FMath::Clamp(Frame.ArmAimWeight - Dt / 0.2f, 0.f, 1.f);
	if (Mesh) Frame.ArmTargetCS = Mesh->GetComponentTransform().InverseTransformPosition(WebAnchorWorld);
	Frame.SpineBank = A.Mode == EWebTravMode::Swing ? -0.35f * A.Swing.Bank : 0.f;
	// round 07 (critic r06: "a plank about 45 deg off the rope at the arc bottom"): while the web is held the body hangs along
	// it — full at the bottom of the arc, 60 % at the ends (the swing clips' reach / tuck still read there); 0.2 s ramps
	{
		const float Want = bAim && A.Mode == EWebTravMode::Swing ? 1.f - 0.4f * FMath::Clamp(FMath::Abs(A.Swing.Phase), 0.f, 1.f) : 0.f;
		const float Step = Dt / 0.2f;
		Frame.BodyAlignW = Want > Frame.BodyAlignW ? FMath::Min(Want, Frame.BodyAlignW + Step) : FMath::Max(Want, Frame.BodyAlignW - Step);
	}
	// round 19: wall-run stride drive (component space)
	{
		const bool bGait = bWallGait && A.Mode == EWebTravMode::Wall && (A.Sub == NA_wallRun || A.Sub == FName(TEXT("wallRunSide"))) && Mesh;
		const float Want = bGait ? 1.f : 0.f;
		const float Step = Dt / (bGait ? 0.12f : 0.15f);
		Frame.WallW = Want > Frame.WallW ? FMath::Min(Want, Frame.WallW + Step) : FMath::Max(Want, Frame.WallW - Step);
		if (bGait)
		{
			const FTransform CT = Mesh->GetComponentTransform();
			const FVector N = CT.InverseTransformVectorNoScale(A.Wall.Normal).GetSafeNormal();
			FVector U = CT.InverseTransformVectorNoScale(A.Wall.Up);
			U = (U - N * FVector::DotProduct(U, N)).GetSafeNormal();
			if (U.IsNearlyZero()) U = (CT.InverseTransformVectorNoScale(FVector::UpVector) - N * FVector::DotProduct(CT.InverseTransformVectorNoScale(FVector::UpVector), N)).GetSafeNormal();
			Frame.WallN = N; Frame.WallU = U; Frame.WallP = CT.InverseTransformPosition(A.Wall.Point);
			// cadence: 3.4 steps/s at 4 m/s .. 6 steps/s at 17 m/s (ref wallrun-glass-midday ~5 steps/s)
			const float StepsPerS = FMath::Clamp(2.6f + 0.2f * A.Speed, 3.4f, 6.0f);
			WallGaitPh = FMath::Fmod(WallGaitPh + Dt * StepsPerS * 0.5f, 1.f);
		}
		Frame.GaitPh = WallGaitPh;
	}
	// round 19: swing leg shaping (legs trail the velocity at the arc bottom, knees tuck on the rising front) + the free arm
	{
		const bool bSw = A.Mode == EWebTravMode::Swing && Mesh;
		const float Want = bSw ? 0.65f : 0.f;
		const float Step = Dt / 0.2f;
		Frame.SwingLegW = Want > Frame.SwingLegW ? FMath::Min(Want, Frame.SwingLegW + Step) : FMath::Max(Want, Frame.SwingLegW - Step);
		Frame.SwingFreeArmW = Frame.SwingLegW;
		const float TuckWant = bSw ? FMath::Clamp((A.Swing.Phase - 0.15f) / 0.45f, 0.f, 1.f) : 0.f;
		Frame.SwingTuck = FMath::FInterpTo(Frame.SwingTuck, TuckWant, Dt, 8.f);
		if (Mesh && !A.Velocity.IsNearlyZero()) Frame.VelCS = Mesh->GetComponentTransform().InverseTransformVectorNoScale(A.Velocity).GetSafeNormal();
	}
	// round 19 (owner: between-swing tuck must read at speed): the release-cycle tuck flavor closes into the tight tuck too
	if (CurNode == FName(TEXT("air_tuck"))) PendingTuckW = FMath::Max(PendingTuckW, 0.85f * Smooth01(NodeT / 0.12f) * (1.f - Smooth01((NodeT - 0.33f) / 0.12f)));
		// round 19 (r18 critic): tight tuck weight from the flip program's current shapes
	{
		const float Step = Dt / 0.08f;
		Frame.TuckW = PendingTuckW > Frame.TuckW ? FMath::Min(PendingTuckW, Frame.TuckW + Step) : FMath::Max(PendingTuckW, Frame.TuckW - Step);
		PendingTuckW = 0.f;
	}
	LastMode = A.Mode;
}

// ------------------------------------------------------------------ proxy (worker thread)
void FWebTravAnimProxy::PreUpdate(UAnimInstance* InAnimInstance, float DeltaSeconds)
{
	FAnimInstanceProxy::PreUpdate(InAnimInstance, DeltaSeconds);
	if (const UWebTravAnimInstance* I = Cast<UWebTravAnimInstance>(InAnimInstance)) Frame = I->Frame;
}

bool FWebTravAnimProxy::Evaluate(FPoseContext& Output)
{
	bool bFirst = true;
	float Acc = 0.f;
	FAnimationPoseData OutData(Output);
	for (const FWebTravAnimLayer& L : Frame.Layers)
	{
		if (!L.Seq || L.Weight <= 0.001f) continue;
		if (bFirst)
		{
			L.Seq->GetAnimationPose(OutData, FAnimExtractContext(double(L.Time), false, {}, L.bLoop));
			Acc = L.Weight; bFirst = false;
			continue;
		}
		FPoseContext Tmp(this);
		FAnimationPoseData TmpData(Tmp);
		L.Seq->GetAnimationPose(TmpData, FAnimExtractContext(double(L.Time), false, {}, L.bLoop));
		FAnimationRuntime::BlendTwoPosesTogetherInPlace(OutData, TmpData, Acc / (Acc + L.Weight));
		Acc += L.Weight;
	}
	if (bFirst) { Output.ResetToRefPose(); return true; }

	FCompactPose& Pose = Output.Pose;
	const FBoneContainer& BC = Pose.GetBoneContainer();
	// round 11: flip overlapping action — the legs take their own (lagging) shape pose
	if (Frame.LegW > 0.001f && Frame.LegLayers.Num())
	{
		FPoseContext LegCtx(this);
		FAnimationPoseData LegData(LegCtx);
		bool bL0 = true; float LAcc = 0.f;
		for (const FWebTravAnimLayer& L : Frame.LegLayers)
		{
			if (!L.Seq || L.Weight <= 0.001f) continue;
			if (bL0) { L.Seq->GetAnimationPose(LegData, FAnimExtractContext(double(L.Time), false, {}, L.bLoop)); LAcc = L.Weight; bL0 = false; continue; }
			FPoseContext Tmp(this);
			FAnimationPoseData TmpData(Tmp);
			L.Seq->GetAnimationPose(TmpData, FAnimExtractContext(double(L.Time), false, {}, L.bLoop));
			FAnimationRuntime::BlendTwoPosesTogetherInPlace(LegData, TmpData, LAcc / (LAcc + L.Weight));
			LAcc += L.Weight;
		}
		if (!bL0)
		{
			static const TCHAR* LegBones[] = { TEXT("glute_L"), TEXT("glute_R"), TEXT("thigh_L"), TEXT("thigh_R"), TEXT("shin_L"), TEXT("shin_R"),
				TEXT("foot_L"), TEXT("foot_R"), TEXT("toe_L"), TEXT("toe_R") };
			for (const TCHAR* Bn : LegBones)
			{
				const int32 MI = BC.GetPoseBoneIndexForBoneName(FName(Bn));
				if (MI == INDEX_NONE) continue;
				const FCompactPoseBoneIndex CI = BC.MakeCompactPoseIndex(FMeshPoseBoneIndex(MI));
				if (!CI.IsValid()) continue;
				FTransform Tr = Pose[CI];
				Tr.BlendWith(LegCtx.Pose[CI], Frame.LegW);
				Pose[CI] = Tr;
			}
		}
	}
	auto Idx = [&BC](const TCHAR* Name) -> FCompactPoseBoneIndex
	{
		const int32 MI = BC.GetPoseBoneIndexForBoneName(FName(Name));
		return MI == INDEX_NONE ? FCompactPoseBoneIndex(INDEX_NONE) : BC.MakeCompactPoseIndex(FMeshPoseBoneIndex(MI));
	};
	auto CS = [&Pose, &BC](FCompactPoseBoneIndex B) -> FTransform
	{
		FTransform T = Pose[B];
		FCompactPoseBoneIndex P = BC.GetParentBoneIndex(B);
		while (P.IsValid()) { T = T * Pose[P]; P = BC.GetParentBoneIndex(P); }
		return T;
	};
	// round 07: body along the web — rotate the hips (component space) so hips -> head points at the anchor (weighted)
	if (Frame.BodyAlignW > 0.01f)
	{
		const FCompactPoseBoneIndex BH = Idx(TEXT("hips")), BHead = Idx(TEXT("head"));
		if (BH.IsValid() && BHead.IsValid())
		{
			const FCompactPoseBoneIndex P = BC.GetParentBoneIndex(BH);
			const FTransform ParentCS = P.IsValid() ? CS(P) : FTransform::Identity;
			FTransform HipCS = Pose[BH] * ParentCS;
			const FVector HipP = HipCS.GetLocation();
			const FVector Cur = (CS(BHead).GetLocation() - HipP).GetSafeNormal();
			const FVector Want = (Frame.ArmTargetCS - HipP).GetSafeNormal();
			if (!Cur.IsNearlyZero() && !Want.IsNearlyZero())
			{
				const FQuat D = FQuat::Slerp(FQuat::Identity, FQuat::FindBetweenNormals(Cur, Want), Frame.BodyAlignW);
				HipCS.SetRotation((D * HipCS.GetRotation()).GetNormalized());
				Pose[BH].SetRotation((ParentCS.GetRotation().Inverse() * HipCS.GetRotation()).GetNormalized());
			}
		}
	}
	// spine bank (roll about the spine's own forward in component space, split over two spine bones)
	if (FMath::Abs(Frame.SpineBank) > 0.01f)
	{
		for (const TCHAR* Sp : { TEXT("spine1"), TEXT("spine2") })
		{
			const FCompactPoseBoneIndex B = Idx(Sp);
			if (!B.IsValid()) continue;
			const FCompactPoseBoneIndex P = BC.GetParentBoneIndex(B);
			const FTransform ParentCS = P.IsValid() ? CS(P) : FTransform::Identity;
			FTransform BoneCS = Pose[B] * ParentCS;
			const FQuat Roll(FVector(0, 1, 0), Frame.SpineBank * 0.5f);
			BoneCS.SetRotation((Roll * BoneCS.GetRotation()).GetNormalized());
			Pose[B].SetRotation((ParentCS.GetRotation().Inverse() * BoneCS.GetRotation()).GetNormalized());
		}
	}
	// web-hand arm aim: rotate the upper arm so shoulder->hand points at the anchor; forearm eased toward straight
	if (Frame.ArmAimWeight > 0.01f)
	{
		const TCHAR* UA = Frame.bArmRight ? TEXT("upperArm_R") : TEXT("upperArm_L");
		const TCHAR* FA = Frame.bArmRight ? TEXT("forearm_R") : TEXT("forearm_L");
		const TCHAR* HA = Frame.bArmRight ? TEXT("hand_R") : TEXT("hand_L");
		const FCompactPoseBoneIndex BU = Idx(UA), BF = Idx(FA), BH = Idx(HA);
		if (BU.IsValid() && BF.IsValid() && BH.IsValid())
		{
			// straighten the elbow a little first (the rope pulls the arm long)
			{
				const FCompactPoseBoneIndex P = BC.GetParentBoneIndex(BF);
				const FTransform ParentCS = CS(P);
				FTransform FCSx = Pose[BF] * ParentCS;
				const FVector Elbow = FCSx.GetLocation();
				const FVector Hand = CS(BH).GetLocation();
				const FVector Shoulder = ParentCS.GetLocation();
				const FVector Want = (Elbow - Shoulder).GetSafeNormal();
				const FVector Now = (Hand - Elbow).GetSafeNormal();
				if (!Want.IsNearlyZero() && !Now.IsNearlyZero())
				{
					const FQuat D = FQuat::Slerp(FQuat::Identity, FQuat::FindBetweenNormals(Now, Want), 0.6f * Frame.ArmAimWeight);
					FCSx.SetRotation((D * FCSx.GetRotation()).GetNormalized());
					Pose[BF].SetRotation((ParentCS.GetRotation().Inverse() * FCSx.GetRotation()).GetNormalized());
				}
			}
			const FCompactPoseBoneIndex P = BC.GetParentBoneIndex(BU);
			const FTransform ParentCS = P.IsValid() ? CS(P) : FTransform::Identity;
			FTransform UCS = Pose[BU] * ParentCS;
			const FVector Shoulder = UCS.GetLocation();
			const FVector Hand = CS(BH).GetLocation();
			const FVector Cur = (Hand - Shoulder).GetSafeNormal();
			const FVector Want = (Frame.ArmTargetCS - Shoulder).GetSafeNormal();
			if (!Cur.IsNearlyZero() && !Want.IsNearlyZero())
			{
				const FQuat D = FQuat::Slerp(FQuat::Identity, FQuat::FindBetweenNormals(Cur, Want), Frame.ArmAimWeight);
				UCS.SetRotation((D * UCS.GetRotation()).GetNormalized());
				Pose[BU].SetRotation((ParentCS.GetRotation().Inverse() * UCS.GetRotation()).GetNormalized());
			}
		}
	}
	// ---------------------------------------------------------------- round 19 procedural layers (component space, cm)
	auto SetCS = [&](FCompactPoseBoneIndex B, const FQuat& NewCSRot)
	{
		const FCompactPoseBoneIndex P = BC.GetParentBoneIndex(B);
		const FQuat ParentRot = P.IsValid() ? CS(P).GetRotation() : FQuat::Identity;
		Pose[B].SetRotation((ParentRot.Inverse() * NewCSRot).GetNormalized());
	};
	auto RotateCS = [&](FCompactPoseBoneIndex B, const FQuat& Delta)
	{
		if (B.IsValid()) SetCS(B, (Delta * CS(B).GetRotation()).GetNormalized());
	};
	auto FirstChild = [&BC](FCompactPoseBoneIndex B) -> FCompactPoseBoneIndex
	{
		for (int32 K = B.GetInt() + 1; K < BC.GetCompactPoseNumBones(); ++K)
		{
			const FCompactPoseBoneIndex C(K);
			if (BC.GetParentBoneIndex(C) == B) return C;
		}
		return FCompactPoseBoneIndex(INDEX_NONE);
	};
	// two-bone IK: Upper -> Mid -> End reaches Target (weight W), bending toward PoleDir; EndDir (optional) aims the End bone's first child
	// (toe / fingers) along that direction with weight EndW. Returns the reached end position.
	auto TwoBone = [&](const TCHAR* UpN, const TCHAR* MidN, const TCHAR* EndN, const FVector& Target, const FVector& PoleDir, float W,
		const FVector* EndDir, float EndW)
	{
		const FCompactPoseBoneIndex BU = Idx(UpN), BM = Idx(MidN), BE = Idx(EndN);
		if (!BU.IsValid() || !BM.IsValid() || !BE.IsValid() || W <= 0.001f) return;
		const FTransform TU = CS(BU), TM = CS(BM), TE = CS(BE);
		const FVector PA = TU.GetLocation(), PB = TM.GetLocation(), PC = TE.GetLocation();
		const double La = (PB - PA).Size(), Lb = (PC - PB).Size();
		if (La < 1.0 || Lb < 1.0) return;
		const FVector T = FMath::Lerp(PC, Target, W);
		FVector Dir = T - PA;
		double Dd = Dir.Size();
		if (Dd < 1e-3) return;
		Dir /= Dd;
		Dd = FMath::Clamp(Dd, FMath::Abs(La - Lb) + 0.5, (La + Lb) * 0.999);
		FVector Bend = PoleDir - Dir * FVector::DotProduct(PoleDir, Dir);
		if (Bend.SizeSquared() < 1e-6) Bend = (PB - PA) - Dir * FVector::DotProduct(PB - PA, Dir);
		Bend = Bend.GetSafeNormal();
		const double CosA = FMath::Clamp((La * La + Dd * Dd - Lb * Lb) / (2.0 * La * Dd), -1.0, 1.0), SinA = FMath::Sqrt(FMath::Max(0.0, 1.0 - CosA * CosA));
		const FVector PB2 = PA + Dir * (La * CosA) + Bend * (La * SinA), PC2 = PA + Dir * Dd;
		const FQuat QA = FQuat::FindBetweenNormals((PB - PA).GetSafeNormal(), (PB2 - PA).GetSafeNormal());
		SetCS(BU, (QA * TU.GetRotation()).GetNormalized());
		const FVector PC1 = PA + QA.RotateVector(PC - PA);
		const FQuat QB = FQuat::FindBetweenNormals((PC1 - PB2).GetSafeNormal(), (PC2 - PB2).GetSafeNormal());
		SetCS(BM, (QB * QA * TM.GetRotation()).GetNormalized());
		FQuat NewE = (QB * QA * TE.GetRotation()).GetNormalized();
		if (EndDir && EndW > 0.001f)
		{
			const FCompactPoseBoneIndex BCh = FirstChild(BE);
			if (BCh.IsValid())
			{
				const FVector Cur = NewE.RotateVector(Pose[BCh].GetTranslation()).GetSafeNormal();
				if (!Cur.IsNearlyZero()) NewE = (FQuat::Slerp(FQuat::Identity, FQuat::FindBetweenNormals(Cur, EndDir->GetSafeNormal()), EndW) * NewE).GetNormalized();
			}
		}
		SetCS(BE, NewE);
	};
	auto Ease = [](float X) { X = FMath::Clamp(X, 0.f, 1.f); return X * X * (3.f - 2.f * X); };
	const FCompactPoseBoneIndex BHips = Idx(TEXT("hips"));
	// ---- wall-run stride
	if (Frame.WallW > 0.01f && BHips.IsValid())
	{
		const float W = Frame.WallW;
		const FVector N = Frame.WallN, U = Frame.WallU;
		const FVector Sd = FVector::CrossProduct(U, N).GetSafeNormal(); // lateral axis (sign fixed per limb below)
		const float Ph = Frame.GaitPh;
		auto Side = [&](const TCHAR* Bn) { const FCompactPoseBoneIndex B = Idx(Bn); return B.IsValid() && FVector::DotProduct(CS(B).GetLocation() - CS(BHips).GetLocation(), Sd) >= 0.0 ? 1.0 : -1.0; };
		// shoulders counter-twist with the arms: the planting hand's shoulder comes toward the wall (rotation about the run axis U)
		{
			const FCompactPoseBoneIndex BSh = Idx(TEXT("upperArm_R"));
			const double SR = BSh.IsValid() ? Side(TEXT("upperArm_R")) : 1.0;
			// rotation about U by +a moves the +Sd side by a * (U x Sd) = a * (-N) ... sign from the geometry:
			const double Toward = FVector::DotProduct(FVector::CrossProduct(U, Sd * SR), -N) >= 0.0 ? 1.0 : -1.0;
			const double Tw = 0.20 * FMath::Cos(2.0 * PI * (Ph - 0.2)) * Toward * W; // right hand mid-contact at Ph 0.2
			RotateCS(Idx(TEXT("spine2")), FQuat(U, Tw * 0.6));
			RotateCS(Idx(TEXT("spine1")), FQuat(U, Tw * 0.4));
			RotateCS(BHips, FQuat(U, -Tw * 0.35));
			// head up the wall a little (looks where he runs)
			const FCompactPoseBoneIndex BHd = Idx(TEXT("head"));
			if (BHd.IsValid()) RotateCS(BHd, FQuat(FVector::CrossProduct(N, U).GetSafeNormal(), -0.18 * W));
		}
		// legs: stance sweeps the planted foot down the wall (push), swing drives the knee up and out
		for (int32 L = 0; L < 2; ++L)
		{
			const TCHAR* Th = L == 0 ? TEXT("thigh_L") : TEXT("thigh_R");
			const TCHAR* Sh = L == 0 ? TEXT("shin_L") : TEXT("shin_R");
			const TCHAR* Ft = L == 0 ? TEXT("foot_L") : TEXT("foot_R");
			const FCompactPoseBoneIndex BT = Idx(Th), BS = Idx(Sh), BF = Idx(Ft);
			if (!BT.IsValid() || !BS.IsValid() || !BF.IsValid()) continue;
			const double Sg = Side(Th);
			const FVector Hip = CS(BT).GetLocation();
			const double Ll = (CS(BS).GetLocation() - Hip).Size() + (CS(BF).GetLocation() - CS(BS).GetLocation()).Size();
			const double DH = FVector::DotProduct(Hip - Frame.WallP, N);
			const FVector Base = Hip - N * DH; // hip projected onto the wall
			const double OTd = -0.26 * Ll, OTo = -FMath::Min(0.9 * Ll, FMath::Sqrt(FMath::Max(1.0, FMath::Square(0.97 * Ll) - FMath::Square(DH - 7.0))));
			const float Phi = FMath::Fmod(Ph + (L == 0 ? 0.f : 0.5f), 1.f);
			const float Sig = 0.42f;
			double O, Off, Lat;
			bool bStance = Phi < Sig;
			if (bStance) { const float K = Phi / Sig; O = FMath::Lerp(OTd, OTo, double(K)); Off = 7.0; Lat = 9.0; }
			else
			{
				const float K = (Phi - Sig) / (1.f - Sig);
				O = FMath::Lerp(OTo, OTd, double(Ease(K))) + 0.14 * Ll * FMath::Square(FMath::Sin(PI * K));
				Off = 7.0 + 24.0 * FMath::Sin(PI * K); Lat = 9.0 + 7.0 * FMath::Sin(PI * K);
			}
			const FVector Tgt = Base + U * O + N * Off + Sd * (Sg * Lat);
			const FVector Pole = U * 1.0 + Sd * (Sg * 0.75) + N * 0.55;
			const FVector ToeUp = (U * 0.9 - N * 0.25).GetSafeNormal();
			TwoBone(Th, Sh, Ft, Tgt, Pole, W, &ToeUp, bStance ? 0.85f * W : 0.3f * W);
		}
		// arms: contralateral to the legs (right hand with the left foot); plant above the shoulder, pull down to the hip
		for (int32 L = 0; L < 2; ++L)
		{
			const TCHAR* UA = L == 0 ? TEXT("upperArm_L") : TEXT("upperArm_R");
			const TCHAR* FA = L == 0 ? TEXT("forearm_L") : TEXT("forearm_R");
			const TCHAR* HA = L == 0 ? TEXT("hand_L") : TEXT("hand_R");
			const FCompactPoseBoneIndex BU = Idx(UA), BF = Idx(FA), BH = Idx(HA);
			if (!BU.IsValid() || !BF.IsValid() || !BH.IsValid()) continue;
			const double Sg = Side(UA);
			const FVector Sh = CS(BU).GetLocation();
			const double La = (CS(BF).GetLocation() - Sh).Size() + (CS(BH).GetLocation() - CS(BF).GetLocation()).Size();
			const double DS = FVector::DotProduct(Sh - Frame.WallP, N);
			const FVector Base = Sh - N * DS;
			const double Reach = FMath::Sqrt(FMath::Max(1.0, FMath::Square(0.96 * La) - FMath::Square(FMath::Max(0.0, DS - 4.0))));
			const double OUp = FMath::Min(0.62 * La, Reach), ODn = -FMath::Min(0.5 * La, Reach);
			const float Phi = FMath::Fmod(Ph + (L == 0 ? 0.5f : 0.f), 1.f);
			const float Sig = 0.42f;
			double O, Off, Lat;
			const bool bPlant = Phi < Sig;
			if (bPlant) { const float K = Phi / Sig; O = FMath::Lerp(OUp, ODn, double(Ease(K))); Off = 4.0; Lat = 6.0; }
			else
			{
				const float K = (Phi - Sig) / (1.f - Sig);
				O = FMath::Lerp(ODn, OUp, double(Ease(K)));
				Off = 4.0 + 20.0 * FMath::Sin(PI * K); Lat = 6.0 + 12.0 * FMath::Sin(PI * K);
			}
			const FVector Tgt = Base + U * O + N * Off + Sd * (Sg * Lat);
			const FVector Pole = Sd * (Sg * 1.0) - U * 0.55 + N * 0.45;
			const FVector Fingers = (U * 0.85 + Sd * (Sg * 0.2) - N * 0.15).GetSafeNormal();
			TwoBone(UA, FA, HA, Tgt, Pole, W, &Fingers, bPlant ? 0.8f * W : 0.25f * W);
		}
	}
	// ---- swing: legs trail the velocity at the arc bottom (straight, together), knees tuck on the rising front; the free arm opens
	if (Frame.SwingLegW > 0.01f && BHips.IsValid() && !Frame.VelCS.IsNearlyZero())
	{
		const float W = Frame.SwingLegW;
		const FVector V = Frame.VelCS;
		const FVector HipC = CS(BHips).GetLocation();
		const FCompactPoseBoneIndex BHead = Idx(TEXT("head"));
		const FVector BodyUp = BHead.IsValid() ? (CS(BHead).GetLocation() - HipC).GetSafeNormal() : FVector::UpVector;
		for (int32 L = 0; L < 2; ++L)
		{
			const TCHAR* Th = L == 0 ? TEXT("thigh_L") : TEXT("thigh_R");
			const TCHAR* Sh = L == 0 ? TEXT("shin_L") : TEXT("shin_R");
			const TCHAR* Ft = L == 0 ? TEXT("foot_L") : TEXT("foot_R");
			const FCompactPoseBoneIndex BT = Idx(Th), BS = Idx(Sh), BF = Idx(Ft);
			if (!BT.IsValid() || !BS.IsValid() || !BF.IsValid()) continue;
			const FVector Hip = CS(BT).GetLocation();
			const double Ll = (CS(BS).GetLocation() - Hip).Size() + (CS(BF).GetLocation() - CS(BS).GetLocation()).Size();
			// trail direction: down the body, swept back against the velocity; legs slightly apart in a scissor (one a little ahead)
			const FVector Down = -BodyUp;
			const FVector Trail = (Down - V * 0.55).GetSafeNormal();
			const double Tuck = Frame.SwingTuck;
			const double Len = Ll * FMath::Lerp(0.97, 0.55, Tuck) * (L == 0 ? 1.0 : 0.96);
			const FVector Lat = (Hip - HipC) - BodyUp * FVector::DotProduct(Hip - HipC, BodyUp);
			const FVector Tgt = Hip + Trail * Len + V * (Tuck * 0.25 * Ll) - Lat * 0.35 + V * ((L == 0 ? 0.06 : -0.04) * Ll);
			const FVector Pole = (V * 1.0 - Down * 0.2).GetSafeNormal(); // knees forward (with the motion)
			const FVector Toe = (Trail - V * 0.3).GetSafeNormal();       // pointed toes
			TwoBone(Th, Sh, Ft, Tgt, Pole, W, &Toe, 0.6f * W);
		}
		// the free arm (not on the web) opens away from the rope for balance, elbow soft
		const bool bRightOnWeb = Frame.bArmRight;
		const TCHAR* UA = bRightOnWeb ? TEXT("upperArm_L") : TEXT("upperArm_R");
		const TCHAR* FA = bRightOnWeb ? TEXT("forearm_L") : TEXT("forearm_R");
		const TCHAR* HA = bRightOnWeb ? TEXT("hand_L") : TEXT("hand_R");
		const FCompactPoseBoneIndex BU = Idx(UA), BF = Idx(FA), BH = Idx(HA);
		if (BU.IsValid() && BF.IsValid() && BH.IsValid() && Frame.SwingFreeArmW > 0.01f)
		{
			const FVector Sh = CS(BU).GetLocation();
			const double La = (CS(BF).GetLocation() - Sh).Size() + (CS(BH).GetLocation() - CS(BF).GetLocation()).Size();
			FVector Out = (Sh - HipC) - BodyUp * FVector::DotProduct(Sh - HipC, BodyUp);
			Out = Out.GetSafeNormal();
			const FVector Dir = (Out * 0.8 - V * 0.45 - BodyUp * 0.15).GetSafeNormal();
			TwoBone(UA, FA, HA, Sh + Dir * (0.88 * La), (-BodyUp - V * 0.3).GetSafeNormal(), 0.55f * Frame.SwingFreeArmW, nullptr, 0.f);
		}
	}
	// ---- tight tuck (r18 critic: wrists <= 0.15 m from the shins, knees <= 0.25 m apart, held >= 0.25 s)
	if (Frame.TuckW > 0.01f)
	{
		const float W = Frame.TuckW;
		const FCompactPoseBoneIndex BTL = Idx(TEXT("thigh_L")), BTR = Idx(TEXT("thigh_R")), BSL = Idx(TEXT("shin_L")), BSR = Idx(TEXT("shin_R"));
		if (BTL.IsValid() && BTR.IsValid() && BSL.IsValid() && BSR.IsValid())
		{
			// knees together: each thigh turns so its knee sits 8 cm from the knees' midpoint
			const FVector KL = CS(BSL).GetLocation(), KR = CS(BSR).GetLocation(), M = (KL + KR) * 0.5;
			for (int32 L = 0; L < 2; ++L)
			{
				const FCompactPoseBoneIndex BT = L == 0 ? BTL : BTR;
				const FVector K = L == 0 ? KL : KR;
				const FVector Hip = CS(BT).GetLocation();
				const FVector KT = M + (K - M).GetSafeNormal() * 8.0;
				const FQuat D = FQuat::FindBetweenNormals((K - Hip).GetSafeNormal(), (KT - Hip).GetSafeNormal());
				RotateCS(BT, FQuat::Slerp(FQuat::Identity, D, W));
			}
			// wrists to the shins: each hand grabs its shin a third of the way down from the knee
			for (int32 L = 0; L < 2; ++L)
			{
				const FCompactPoseBoneIndex BS = L == 0 ? BSL : BSR;
				const FCompactPoseBoneIndex BFt = Idx(L == 0 ? TEXT("foot_L") : TEXT("foot_R"));
				if (!BFt.IsValid()) continue;
				const FVector Knee = CS(BS).GetLocation(), Ankle = CS(BFt).GetLocation();
				const FVector Grip = FMath::Lerp(Knee, Ankle, 0.35);
				const FVector HipC = BHips.IsValid() ? CS(BHips).GetLocation() : FVector::ZeroVector;
				FVector Outw = Grip - HipC; Outw -= (Ankle - Knee).GetSafeNormal() * FVector::DotProduct(Outw, (Ankle - Knee).GetSafeNormal());
				const FVector Tgt = Grip + Outw.GetSafeNormal() * 4.0;
				const TCHAR* UA = L == 0 ? TEXT("upperArm_L") : TEXT("upperArm_R");
				const TCHAR* FA = L == 0 ? TEXT("forearm_L") : TEXT("forearm_R");
				const TCHAR* HA = L == 0 ? TEXT("hand_L") : TEXT("hand_R");
				const FCompactPoseBoneIndex BU = Idx(UA);
				const FVector Elb = BU.IsValid() ? (CS(BU).GetLocation() - HipC).GetSafeNormal() : FVector::UpVector;
				TwoBone(UA, FA, HA, Tgt, (Elb + Outw.GetSafeNormal()).GetSafeNormal(), W, nullptr, 0.f);
			}
		}
	}
	return true;
}
