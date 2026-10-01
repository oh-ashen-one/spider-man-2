// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Traversal/Anim/WebTravAnimInstance.h"
#include "Traversal/WebTravFlips.h"
#include "WebHomage.h"

#include "Animation/AnimNodeBase.h"
#include "Animation/AnimSequence.h"
#include "AnimationRuntime.h"
#include "Components/SkeletalMeshComponent.h"
#include "BonePose.h"

FString UWebTravAnimInstance::ClipRoot = TEXT("/Game/Traversal/HeroDev");
FString UWebTravAnimInstance::ClipPrefix;

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
	return true;
}
