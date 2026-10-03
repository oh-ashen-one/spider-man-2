// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Traversal/WebTravFlips.h"
#include "Traversal/WebTraversalComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/GameViewportClient.h"
#include "GameFramework/Character.h"
#include "GameFramework/PlayerController.h"
#include "Components/SkeletalMeshComponent.h"
#include "Misc/CoreDelegates.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"

namespace WebFlips
{
	float FlipLead = 0.04f, FlipLag = 0.07f;
	bool bVariants = true;
	bool bTempo = true;

	namespace
	{
		// effective "inertia" per shape, tuned to the owner clip (FLIPS_SPEC F3/F4): tuck spins ~600 deg/s, the open holds
		// turn 40-90 deg/s (pencil / swan / throne), pike and layout sit between
		float Inertia(EWebFlipShape S)
		{
			switch (S)
			{
			case EWebFlipShape::Tuck: return 1.0f;
			case EWebFlipShape::Pike: return 1.35f;
			case EWebFlipShape::Layout: return 3.2f;
			case EWebFlipShape::Swan: return 7.5f;
			case EWebFlipShape::Pencil: return 9.0f;
			case EWebFlipShape::Straddle: return 7.5f; // round 18: corkscrew's inverted shape (replaces its swan: same timeline)
			case EWebFlipShape::Throne: return 9.0f;
			case EWebFlipShape::Twist: return 3.5f;
			case EWebFlipShape::Reach: return 7.0f;
			// round 13: open finish; round 14 5.5 -> 10.5 (rendered r13 hold 0.21 s: the keyed arch adds ~40 deg/s to the program's 123)
			case EWebFlipShape::Kickout: return 10.5f;
			default: return 3.f;
			}
		}
		float Smooth(float X) { X = FMath::Clamp(X, 0.f, 1.f); return X * X * (3.f - 2.f * X); }
		constexpr float BPre = 0.06f, BPost = 0.11f; // shape transition window around a segment boundary (s)
		constexpr float EnvIn = 0.12f, EnvOut = 0.22f; // rotation set-in / settle at the program ends (s)
		constexpr int32 TableHz = 240;

		struct FTable { TArray<float> G; float L = 0.f; int32 Ver = -1; }; // cumulative rotation (deg) at 1/TableHz steps

		TArray<FWebFlipProgram>& Programs()
		{
			static TArray<FWebFlipProgram> P;
			if (P.Num()) return P;
			using S = EWebFlipShape;
			auto Add = [&](const TCHAR* Name, float Pitch, std::initializer_list<FWebFlipSeg> Segs, float Boost = 3.5f, float Up = 1.5f, float CatchOpen = 0.16f)
			{
				FWebFlipProgram F; F.Name = FName(Name); F.PitchDeg = Pitch; F.Segs = Segs; F.Boost = Boost; F.Up = Up; F.CatchOpen = CatchOpen; P.Add(F);
			};
			// ---- P3 rounds 11-19 (kept unchanged so traversal's merged r23 flips do not regress) --------------------------------------------
			// backDouble: a double tuck that kicks out into an open finish (Kickout: arms sweep wide, legs scissor behind them, the web arm
			// comes up for the catch). round 14: Tuck 1.20 s eased, Kickout 0.60 s at <= ~100 deg/s; catch 1.60 s after the release
			Add(TEXT("backDouble"), -720.f, { {S::Tuck, 1.20f, 0.f, 0.85f, 0.8f}, {S::Kickout, 0.60f} }, 3.5f, 1.5f, 0.2f);
			// front pike into a slow inverted swan that unwinds, tuck up, reach (round 14: pike 0.40 / swan 0.55 / tuck 0.38 / reach 0.26 s)
			Add(TEXT("frontPikeSwan"), 360.f, { {S::Pike, 0.40f, 0.f, 1.3f, 0.3f}, {S::Swan, 0.55f}, {S::Tuck, 0.38f, 0.f, 1.2f, 0.7f}, {S::Reach, 0.36f} });
			// corkscrew: a layout that turns over while it twists a full turn (arms crossed), opens into its own inverted straddle, tucks, reach
			Add(TEXT("corkscrew"), 360.f, { {S::Layout, 0.31f}, {S::Twist, 0.42f, 360.f}, {S::Straddle, 0.36f}, {S::Tuck, 0.34f, 0.f, 1.2f, 0.7f}, {S::Reach, 0.36f} }, 4.0f, 1.2f);
			// short air (plain trick release): tuck to inverted, pencil hold, tuck round, reach
			// Tricks C r01: every program's final Reach is >= 0.36 s, so the catch window (CatchOpen 0.16 s before the end) opens only after
			// >= 0.2 s of the open reach -- r01 probe: backSingle's 0.24 s reach was caught 0.08 s in, straight out of a 446 deg/s tuck
			Add(TEXT("backSingle"), -360.f, { {S::Tuck, 0.32f, 0.f, 0.5f, 0.3f}, {S::Pencil, 0.36f}, {S::Tuck, 0.32f, 0.f, 0.3f, 0.6f}, {S::Reach, 0.38f} });
			// wall-run top-out: front flip over the roof edge, layout on top, throne into the landing
			Add(TEXT("wallFront"), 360.f, { {S::Tuck, 0.27f}, {S::Layout, 0.3f}, {S::Tuck, 0.27f}, {S::Throne, 0.3f} }, 0.f, 0.f);
			// ---- Tricks C round 1 (owner: "look like a gymnast", "many tricks"): the gymnastics vocabulary, built from the same keyed shapes.
			// Every program opens out of its rotation into a slow open shape (Kickout / Straddle / Layout / Reach) before the catch (clean open-out); a
			// twist always exits into a shape keyed out of the twist wrap (Straddle / Layout), never into the Kickout (which starts from the tuck grab); every
			// fast phase is a tuck or pike (the rate follows the shape: F3 / F5). Durations were tuned with tools/tricks/flip_sim.py so the
			// base program peaks <= ~650 deg/s (a fast 0.85x variant stays <= ~770). Twists: a body can only finish a WHOLE number of
			// twists facing along its travel (a half twist lands facing back), so the 180 / 540 programs do their named twist inside the
			// flip and turn the last half in slowly as they open toward the catch (the catch-turn), never as a spring at the attach.
			// Release push (Boost / Up, m/s) 2.0 / 1.0 on every new program (r01 probe: 3.5 / 1.5 on a flip every release took the chain from
			// 39 to 60 m/s in 12 s and through the avenue corner into a facade).
			// front tuck: set, tight tuck, kick out, reach for the web
			Add(TEXT("frontSingle"), 360.f, { {S::Tuck, 0.74f, 0.f, 0.9f, 0.7f}, {S::Kickout, 0.44f}, {S::Reach, 0.22f} }, 2.0f, 1.0f);
			// front double tuck with a kick-out (the front twin of backDouble)
			Add(TEXT("frontDouble"), 720.f, { {S::Tuck, 1.40f, 0.f, 0.85f, 0.8f}, {S::Kickout, 0.54f}, {S::Reach, 0.2f} }, 2.0f, 1.0f, 0.2f);
			// back pike: the body folds at the hips with straight legs (keyed pike), opens into the kick-out
			Add(TEXT("backPike"), -360.f, { {S::Pike, 0.72f, 0.f, 1.0f, 0.6f}, {S::Kickout, 0.46f}, {S::Reach, 0.22f} }, 2.0f, 1.0f);
			// back layout: one straight line all the way round (hips / knees >= 170 deg), arms by the sides, opens to the reach
			Add(TEXT("backLayout"), -360.f, { {S::Layout, 0.92f, 0.f, 0.5f, 0.4f}, {S::Reach, 0.40f} }, 2.0f, 1.0f);
			// barani: front pike with a half twist (180 deg, arms wrapped), then the straddle flings open out of the wrap and turns the last half in toward the catch
			Add(TEXT("barani"), 360.f, { {S::Pike, 0.50f, 0.f, 1.0f, 0.3f}, {S::Twist, 0.34f, 180.f}, {S::Straddle, 0.46f, 180.f}, {S::Reach, 0.36f} }, 2.0f, 1.0f);
			// back full: a back layout with one full twist (360 deg) in the middle of the rotation, opens straight back into the layout, reach
			Add(TEXT("fullTwist"), -360.f, { {S::Layout, 0.34f, 0.f, 0.5f, 0.f}, {S::Twist, 0.52f, 360.f}, {S::Layout, 0.32f}, {S::Reach, 0.38f} }, 2.0f, 1.0f);
			// rudi: front flip with one and a half twists (540 deg) wrapped tight, the catch-turn finishes the last half in the open straddle
			Add(TEXT("rudi"), 360.f, { {S::Pike, 0.40f, 0.f, 1.0f, 0.3f}, {S::Twist, 0.66f, 540.f}, {S::Straddle, 0.48f, 180.f}, {S::Reach, 0.36f} }, 2.0f, 1.0f);
			// chain: three back rotations in one release with a shape per rotation (owner clip S3: tuck -> layout -> tuck -> straddle -> tuck
			// -> open, 3 rotations in 2.8 s, ~385 deg/s mean)
			Add(TEXT("backTripleChain"), -1080.f, { {S::Tuck, 0.60f, 0.f, 0.9f, 0.3f}, {S::Layout, 0.40f}, {S::Tuck, 0.52f, 0.f, 0.3f, 0.3f}, {S::Straddle, 0.36f},
				{S::Tuck, 0.52f, 0.f, 0.3f, 0.6f}, {S::Kickout, 0.44f}, {S::Reach, 0.2f} }, 2.0f, 1.0f, 0.2f);
			return P;
		}

		float SegStart(const FWebFlipProgram& P, int32 K) { float T = 0.f; for (int32 I = 0; I < K; ++I) T += P.Segs[I].Dur; return T; }
		int32 SegAt(const FWebFlipProgram& P, float T)
		{
			float Acc = 0.f;
			for (int32 I = 0; I < P.Segs.Num(); ++I) { Acc += P.Segs[I].Dur; if (T < Acc) return I; }
			return P.Segs.Num() - 1;
		}
		// shape blend at time T: (A, B, W) and hold progress of A / B
		void ShapeAt(const FWebFlipProgram& P, float T, EWebFlipShape& A, EWebFlipShape& B, float& W, float& HA, float& HB)
		{
			const float Dur = P.Dur();
			T = FMath::Clamp(T, 0.f, Dur - 1e-4f);
			const int32 K = SegAt(P, T);
			const float S0 = SegStart(P, K), S1 = S0 + P.Segs[K].Dur;
			auto Hold = [&](int32 J, float Tt) { const float St = SegStart(P, J); return FMath::Clamp((Tt - St) / FMath::Max(0.05f, P.Segs[J].Dur), 0.f, 1.f); };
			if (K > 0 && T < S0 + BPost)
			{
				A = P.Segs[K - 1].Shape; B = P.Segs[K].Shape; W = Smooth((T - (S0 - BPre)) / (BPre + BPost));
				HA = 1.f; HB = Hold(K, T);
			}
			else if (K + 1 < P.Segs.Num() && T > S1 - BPre)
			{
				A = P.Segs[K].Shape; B = P.Segs[K + 1].Shape; W = Smooth((T - (S1 - BPre)) / (BPre + BPost));
				HA = Hold(K, T); HB = 0.f;
			}
			else { A = B = P.Segs[K].Shape; W = 0.f; HA = HB = Hold(K, T); }
		}
		// round 14: segment K's inertia at time T including its end ease (see FWebFlipSeg::EaseIn / EaseOut)
		constexpr float EaseW = 0.45f;
		float SegInertia(const FWebFlipProgram& P, int32 K, float T)
		{
			const FWebFlipSeg& S = P.Segs[K];
			const float U = FMath::Clamp((T - SegStart(P, K)) / FMath::Max(0.05f, S.Dur), 0.f, 1.f);
			return Inertia(S.Shape) * (1.f + S.EaseIn * (1.f - Smooth(U / EaseW)) + S.EaseOut * (1.f - Smooth((1.f - U) / EaseW)));
		}
		float InertiaAt(const FWebFlipProgram& P, float T)
		{
			const float Dur = P.Dur();
			T = FMath::Clamp(T, 0.f, Dur - 1e-4f);
			const int32 K = SegAt(P, T);
			const float S0 = SegStart(P, K), S1 = S0 + P.Segs[K].Dur;
			if (K > 0 && T < S0 + BPost)
				return FMath::Lerp(SegInertia(P, K - 1, T), SegInertia(P, K, T), Smooth((T - (S0 - BPre)) / (BPre + BPost)));
			if (K + 1 < P.Segs.Num() && T > S1 - BPre)
				return FMath::Lerp(SegInertia(P, K, T), SegInertia(P, K + 1, T), Smooth((T - (S1 - BPre)) / (BPre + BPost)));
			return SegInertia(P, K, T);
		}
		float Env(float T, float Dur)
		{
			const float In = 0.35f + 0.65f * Smooth(T / EnvIn);
			const float Out = 0.12f + 0.88f * Smooth((Dur - T) / EnvOut);
			return In * Out;
		}
		const FTable& Table(const FWebFlipProgram& P)
		{
			static TMap<const FWebFlipProgram*, FTable> Cache;
			if (const FTable* T = Cache.Find(&P)) { if (T->Ver == P.Ver) return *T; }
			FTable Tb;
			Tb.Ver = P.Ver;
			const float Dur = P.Dur();
			const int32 N = FMath::CeilToInt(Dur * TableHz) + 1;
			Tb.G.SetNum(N + 1);
			double Acc = 0.0;
			Tb.G[0] = 0.f;
			for (int32 I = 1; I <= N; ++I)
			{
				const float Tm = (I - 0.5f) / TableHz;
				Acc += Env(Tm, Dur) / InertiaAt(P, Tm) / TableHz;
				Tb.G[I] = float(Acc);
			}
			const float GEnd = Tb.G[FMath::Min(N, FMath::CeilToInt(Dur * TableHz))];
			Tb.L = GEnd > 1e-6f ? P.PitchDeg / GEnd : 0.f;
			for (float& V : Tb.G) V *= Tb.L;
			return Cache.Add(&P, Tb);
		}
	}

	const TCHAR* ShapeClip(EWebFlipShape S)
	{
		static const TCHAR* C[] = { TEXT("flipTuck"), TEXT("flipPike"), TEXT("flipLayout"), TEXT("flipSwan"), TEXT("flipPencil"),
			TEXT("flipStraddle"), TEXT("flipThrone"), TEXT("flipTwist"), TEXT("flipReach"), TEXT("flipKickout"),
			// Tricks C r02: the swing node's catch poses (hero clips loaded from the same folder as the flip shapes)
			TEXT("swingLow"), TEXT("swingLowL"), TEXT("swingCornerBank"), TEXT("swingCornerBankL") };
		static_assert(UE_ARRAY_COUNT(C) == int32(EWebFlipShape::Num), "one clip per shape");
		return C[FMath::Clamp(int32(S), 0, int32(EWebFlipShape::Num) - 1)];
	}
	const TCHAR* ShapeName(EWebFlipShape S)
	{
		switch (S)
		{
		case EWebFlipShape::CatchLow: return TEXT("CatchLow");
		case EWebFlipShape::CatchLowL: return TEXT("CatchLowL");
		case EWebFlipShape::CatchBank: return TEXT("CatchBank");
		case EWebFlipShape::CatchBankL: return TEXT("CatchBankL");
		default: return ShapeClip(S) + 4;
		}
	}

	// round 14: rendered hips->head axis minus the program pitch while each shape is held (probe f4, 60 fps; + = head forward)
	float ShapeAxisDeg(EWebFlipShape S)
	{
		switch (S)
		{
		case EWebFlipShape::Tuck: return 20.f;
		case EWebFlipShape::Pike: return 22.f;
		case EWebFlipShape::Swan: return -15.f;
		case EWebFlipShape::Kickout: return -6.f;
		case EWebFlipShape::Reach: return 3.f;
		default: return 0.f;
		}
	}

	// round 18: vertical extent (m, joints + 0.2 m pad) a shape reaches during its hold (flip_motion_sim.py z-extent): the trick camera backs
	// out ahead of an opening shape so the hero stays inside TC-C's .12-.36 of the frame at 5.0-6.4 m (TC4)
	float ShapeExtent(EWebFlipShape S)
	{
		switch (S)
		{
		case EWebFlipShape::Tuck: return 0.95f;
		case EWebFlipShape::Pike: return 1.3f;
		case EWebFlipShape::Twist: return 1.4f;
		case EWebFlipShape::Throne: return 1.5f;
		case EWebFlipShape::Reach: return 1.8f;
		default: return 2.0f; // layout, swan, pencil, straddle, kickout
		}
	}

	namespace
	{
		// one variant slot per base program (stable addresses: the rate-table cache and callers hold pointers)
		TArray<FWebFlipProgram>& Variants()
		{
			static TArray<FWebFlipProgram> V;
			if (V.Num() != Programs().Num()) { V = Programs(); for (FWebFlipProgram& P : V) P.Ver = -2; }
			return V;
		}
	}
	const FWebFlipProgram* FindBase(FName Name)
	{
		for (const FWebFlipProgram& P : Programs()) { if (P.Name == Name) return &P; }
		return nullptr;
	}
	const FWebFlipProgram* Find(FName Name)
	{
		const TArray<FWebFlipProgram>& B = Programs();
		for (int32 I = 0; I < B.Num(); ++I)
		{
			if (B[I].Name != Name) continue;
			const FWebFlipProgram& V = Variants()[I];
			return (bVariants && V.Ver >= 0) ? &V : &B[I];
		}
		return nullptr;
	}
	const FWebFlipProgram* MakeVariant(FName Name, float Scale, uint32 Seed)
	{
		const TArray<FWebFlipProgram>& B = Programs();
		static int32 VerCounter = 0;
		static const bool bTempoParsed = []() { int32 V = 1; if (FParse::Value(FCommandLine::Get(), TEXT("-WHTrickTempo="), V)) bTempo = V != 0; return true; }();
		(void)bTempoParsed;
		for (int32 I = 0; I < B.Num(); ++I)
		{
			if (B[I].Name != Name) continue;
			if (!bVariants) return &B[I];
			FWebFlipProgram& V = Variants()[I];
			V = B[I];
			FRandomStream R{ int32(Seed) };
			// Tricks C r01 (PLAN §4: same-type durations vary +-10-20 %; r23 flow flips at ~40 m/s all came out 0.86-0.99x): half of the
			// caller's release-speed / apex term plus a per-instance TEMPO -- this performance is a slow, floated one (+10-16 %) or a snappy one
			// (-10-13 %), alternating at random; the fast side is capped at 0.85x so a tuck never passes ~800 deg/s by much (FLIPS_SPEC F3)
			// r01 resume (probe: frontSingle / barani drew the same sign twice -> 12 / 65 deg/s apart): the first instance of a program picks the
			// sign at random, every later instance of the SAME program takes the opposite one, so a repeat is always the other performance
			static TArray<int32> LastSign; LastSign.SetNumZeroed(B.Num());
			const float Coin = R.FRand();
			const float Tempo = LastSign[I] != 0 ? -float(LastSign[I]) : (Coin < 0.5f ? -1.f : 1.f);
			LastSign[I] = Tempo > 0.f ? 1 : -1;
			const float TempoMag = Tempo > 0.f ? 0.10f + 0.06f * R.FRand() : 0.10f + 0.03f * R.FRand();
			const float Sc = bTempo ? FMath::Clamp(1.f + 0.5f * (FMath::Clamp(Scale, 0.78f, 1.22f) - 1.f) + Tempo * TempoMag, 0.85f, 1.20f)
				: FMath::Clamp(Scale, 0.78f, 1.22f);
			// each segment its own jitter, renormalised so the total is exactly Sc x the base duration
			float Sum0 = 0.f, Sum1 = 0.f;
			for (FWebFlipSeg& Sg : V.Segs) { Sum0 += Sg.Dur; Sg.Dur *= 0.92f + 0.16f * R.FRand(); Sum1 += Sg.Dur; }
			for (FWebFlipSeg& Sg : V.Segs)
			{
				Sg.Dur *= Sc * Sum0 / FMath::Max(Sum1, 1e-3f);
				Sg.EaseIn = FMath::Max(0.f, Sg.EaseIn * (0.8f + 0.4f * R.FRand()));
				Sg.EaseOut = FMath::Max(0.f, Sg.EaseOut * (0.8f + 0.4f * R.FRand()));
			}
			V.CatchOpen = B[I].CatchOpen * Sc;
			V.Lead = FlipLead * (0.5f + 1.5f * R.FRand());   // 0.02-0.08 s: the arms open / close earlier or later per instance
			V.Lag = FlipLag * (0.7f + 0.8f * R.FRand());     // 0.05-0.11 s
			V.Scale = Sc;
			V.Ver = ++VerCounter;
			return &V;
		}
		return nullptr;
	}
	const TArray<FName>& ReleasePrograms()
	{
		static TArray<FName> N;
		if (!N.Num())
		{
			for (const TCHAR* S : { TEXT("backSingle"), TEXT("frontSingle"), TEXT("backPike"), TEXT("barani"), TEXT("backLayout"), TEXT("frontDouble"),
				TEXT("fullTwist"), TEXT("frontPikeSwan"), TEXT("backDouble"), TEXT("rudi"), TEXT("corkscrew"), TEXT("backTripleChain") }) N.Add(FName(S));
		}
		return N;
	}
	FName ChooseForInput(float StickFwd, float StickLat, int32 K, float AirS, FName Last)
	{
		static const TCHAR* Front[] = { TEXT("frontSingle"), TEXT("frontPikeSwan"), TEXT("barani"), TEXT("frontDouble"), TEXT("corkscrew"), TEXT("rudi") };
		static const TCHAR* Back[] = { TEXT("backSingle"), TEXT("backPike"), TEXT("backLayout"), TEXT("backDouble"), TEXT("fullTwist"), TEXT("backTripleChain") };
		static const TCHAR* Twist[] = { TEXT("barani"), TEXT("fullTwist"), TEXT("corkscrew"), TEXT("rudi") };
		TArray<FName> Pool;
		const float Mag = FMath::Sqrt(StickFwd * StickFwd + StickLat * StickLat);
		if (Mag < 0.35f) Pool = ReleasePrograms();
		else if (FMath::Abs(StickLat) > FMath::Abs(StickFwd)) { for (const TCHAR* S : Twist) Pool.Add(FName(S)); }
		else if (StickFwd > 0.f) { for (const TCHAR* S : Front) Pool.Add(FName(S)); }
		else { for (const TCHAR* S : Back) Pool.Add(FName(S)); }
		// the first program in the cycle (from K) that fits the air and is not a repeat; else the shortest that fits; else none
		FName Shortest = NAME_None; float ShortT = 1e9f;
		for (int32 I = 0; I < Pool.Num(); ++I)
		{
			const FName N = Pool[(K + I) % Pool.Num()];
			const FWebFlipProgram* P = FindBase(N);
			if (!P) continue;
			const bool bFits = AirS <= 0.f || P->CatchT() * 1.15f <= AirS;
			if (bFits && N != Last) return N;
			if (P->CatchT() < ShortT && N != Last) { ShortT = P->CatchT(); Shortest = N; }
		}
		return (AirS <= 0.f || ShortT * 1.15f <= AirS) ? Shortest : NAME_None;
	}
	const TArray<FName>& Names()
	{
		static TArray<FName> N;
		if (!N.Num()) for (const FWebFlipProgram& P : Programs()) N.Add(P.Name);
		return N;
	}

	// the program alone (round 11-r01 behaviour); Sample() adds the r02 catch lean on top
	static FWebFlipPose SampleBase(const FWebFlipProgram& P, float T)
	{
		FWebFlipPose O;
		const float Dur = P.Dur();
		if (Dur <= 0.f) return O;
		O.bValid = true;
		const FTable& Tb = Table(P);
		const float Tc = FMath::Clamp(T, 0.f, Dur);
		const float X = Tc * TableHz;
		const int32 I0 = FMath::Clamp(FMath::FloorToInt(X), 0, Tb.G.Num() - 2);
		const float F = FMath::Clamp(X - I0, 0.f, 1.f);
		O.PitchDeg = FMath::Lerp(Tb.G[I0], Tb.G[I0 + 1], F);
		if (Tc >= Dur - 1e-4f) O.PitchDeg = P.PitchDeg;
		O.PitchRate = T < Dur ? Tb.L * Env(Tc, Dur) / InertiaAt(P, Tc) : 0.f;
		// twist: eased inside its own segments
		float Tw = 0.f, St = 0.f;
		for (const FWebFlipSeg& S : P.Segs)
		{
			if (S.TwistDeg != 0.f)
			{
				const float U = FMath::Clamp((Tc - St) / FMath::Max(0.05f, S.Dur), 0.f, 1.f);
				Tw += S.TwistDeg * 0.5f * (1.f - FMath::Cos(PI * U));
			}
			St += S.Dur;
		}
		O.TwistDeg = Tw;
		O.Seg = SegAt(P, Tc);
		ShapeAt(P, T + (P.Lead >= 0.f ? P.Lead : FlipLead), O.A, O.B, O.W, O.HoldA, O.HoldB);
		O.AxisOffDeg = FMath::Lerp(ShapeAxisDeg(O.A), ShapeAxisDeg(O.B), O.W);
		ShapeAt(P, T - (P.Lag >= 0.f ? P.Lag : FlipLag), O.LA, O.LB, O.LW, O.LHoldA, O.LHoldB);
		// r01 resume (L: a program that runs out before the web catches held its final reach still -- backLayout 0.01-0.06 m per 0.1 s):
		// past the end the reach plays back and forth between u 1 and .45 (its scissor / free-arm swing) until the traversal ends the flip
		if (P.Segs.Num() && (P.Segs.Last().Shape == EWebFlipShape::Reach || P.Segs.Last().Shape == EWebFlipShape::Kickout))
		{
			auto Pong = [](float Ov) { const float X = FMath::Fmod(Ov / 0.25f, 2.f); return 1.f - 0.55f * (1.f - FMath::Abs(1.f - X)); };
			const float OvU = T + (P.Lead >= 0.f ? P.Lead : FlipLead) - Dur, OvL = T - (P.Lag >= 0.f ? P.Lag : FlipLag) - Dur;
			if (OvU > 0.f && O.W <= 0.f) O.HoldA = O.HoldB = Pong(OvU);
			if (OvL > 0.f && O.LW <= 0.f) O.LHoldA = O.LHoldB = Pong(OvL);
		}
		return O;
	}

	// ---- Tricks C round 2: catch lean ------------------------------------------------------------------------------------------------
	// Critic r01 ("every catch snaps"): after a trick the chest turned 300-921 deg/s for 0.1-0.2 s, because the web catch swaps the upright
	// air frame for the swing frame (body up along the rope, chest along the projected velocity: WebTraversalComponent::Orient, slerp 14/s),
	// the flip offset springs back (0.07 s, WebTravCharacter::PoseFigure) and the anim swaps the reach for the swing pose (0.24 s). The catch
	// lean starts that change inside the program. From 0.3-0.6 s before the program's catch time it predicts the catch (the traversal's own
	// anchor search run from the predicted body position at the catch; the swing frame that anchor and StartSwing's velocity projection give)
	// -- or, with no web in reach, the streamlined air frame the body takes after the program -- fits that frame relative to the current body
	// frame as a pitch about the lateral axis + a twist about the long axis (the two channels PoseFigure applies), and lerps the program's
	// rotation into it (smoothstep, peak <= ~250 deg/s). The shapes blend from the program's open shape into the swing node's starting pose
	// (swingLow + its corner-bank share, hand of the predicted anchor) over the last 0.3 s. At the catch the body frame then springs to where
	// the hero already is while the flip offset springs back by the same amount (14/s vs 14.3/s); only the rope's sideways lean (a roll,
	// which neither channel can express) is left to the catch itself.
	bool bCatchLean = true;
	namespace
	{
		// r02 probe c: G4 (open-out <= 300 deg/s) needs the lean + the moving target well under 300 deg/s; G3 (head spot in the open-out)
		// needs the program's own reach / kick-out to play before the catch pose takes over -> 0.22 s shape window; L -> the catch clip plays
		// (backward into its frame 0) at 2.4x so the limbs keep moving while the pose is held
		constexpr float CatchWinMin = 0.3f, CatchWinMax = 0.7f, CatchShapeWin = 0.22f, CatchRate = 200.f, CatchTargetRate = 110.f, CatchLook = 0.85f, CatchClipLen = 0.5f;
		// r02 probe b: the predicted facing about the rope is ill-conditioned (the rope runs almost along the velocity at a catch: the swing
		// frame's forward is the small velocity component off the rope) -- the measured post-catch twist was ~0.3 x the predicted one
		// (residual vs the body 0.1 s after the catch, 18 catches: mean 35 deg at 0.3 x, 46 deg at 1 x, 37 deg at 0 x)
		constexpr float CatchTwistK = 0.3f;
		struct FCatchLean
		{
			uint64 Frame = ~0ull;
			const FWebFlipProgram* P = nullptr; int32 Ver = -99; float Side = 1.f;
			bool bTarget = false, bOn = false, bSwing = false, bRight = true, bShapeRight = true;
			float ShapeK = 0.f;                        // weight of the swing node's catch pose (follows the prediction: 0.15 s ramps)
			float Ts = 0.f, Te = 0.f;                  // root window [Ts, Te] (program time); the lean weight is 1 from Te on
			float Beta = 0.f, Gamma = 0.f, Rho = 0.f;  // smoothed lean (deg): pitch about the lateral axis (+ head forward), twist about the long axis, sideways rest
			float BankW = 0.f;
			FVector Anchor = FVector::ZeroVector;
			FQuat TargetQ = FQuat::Identity;           // the predicted frame (world), pose log only
			double LastWT = -1.0; FVector LastVel = FVector::ZeroVector;
		};
		FCatchLean GC;

		const UWebTraversalComponent* HeroTrav(UWorld** OutW = nullptr)
		{
			if (OutW) *OutW = nullptr;
			if (!GEngine) return nullptr;
			UWorld* W = nullptr;
			for (const FWorldContext& C : GEngine->GetWorldContexts())
			{
				if ((C.WorldType == EWorldType::Game || C.WorldType == EWorldType::PIE) && C.World()) { W = C.World(); break; }
			}
			if (OutW) *OutW = W;
			APlayerController* PC = W ? W->GetFirstPlayerController() : nullptr;
			ACharacter* Ch = PC ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
			return Ch ? Ch->FindComponentByClass<UWebTraversalComponent>() : nullptr;
		}
		FVector RotZv(const FVector& V, double A) { const double C = FMath::Cos(A), S = FMath::Sin(A); return FVector(V.X * C - V.Y * S, V.X * S + V.Y * C, V.Z); }

		// the frame the body takes right after the program (world space): the swing start if a web will catch, else the air frame
		bool PredictFrame(const UWebTraversalComponent* Tr, const FWebFlipProgram& P, float T, const FVector& Acc, FQuat& OutW, bool& bSwing, bool& bRight, FVector& OutAnchor)
		{
			using UT = UWebTraversalComponent;
			const FWebTravAnim& A = Tr->Anim;
			const FVector Pos = Tr->PosM(), Vel = Tr->VelM(), ZUp(0, 0, 1);
			const float Tc = P.CatchT() - 0.02f;
			const double Dt = FMath::Max(0.0, double(Tc - T));
			const FVector Pc = Pos + Vel * Dt + 0.5 * Acc * Dt * Dt, Vc = Vel + Acc * Dt;
			FVector HV(Vc.X, Vc.Y, 0.0);
			if (HV.Size() < 1.0) return false;
			HV.Normalize();
			bSwing = false;
			FVector AP = FVector::ZeroVector;
			const FWebTravStrand& St = Tr->Strands[0];
			if (St.bActive && St.ReleaseT < 0.f && T >= Tc - 0.05f) { AP = St.Anchor; bSwing = true; } // the web already shot (pending swing)
			else if (Tr->Anchors.IsValid())
			{
				// the search TryStartSwing runs at the catch: the travel heading leaned AnchorAltDeg away from the previous web's side
				const double SideW = A.Swing.bRightHand ? 1.0 : -1.0;
				const FVector FwdS = RotZv(HV, -SideW * FMath::DegreesToRadians(double(Tr->AnchorAltDeg)));
				const double Fl = Tr->TravWorld.GroundHeight(Pc.X, Pc.Y, Pc.Z - UT::H + 0.1 - 0.5);
				FTravAnchor An;
				if (Tr->Anchors->Find(Pc, FwdS, nullptr, Vc.Size(), Fl, An))
				{
					const bool bBehind = FVector(Vc.X, Vc.Y, 0.0).Size() > 6.0 && FVector::DotProduct(FVector(An.Point.X - Pc.X, An.Point.Y - Pc.Y, 0.0), HV) < 2.0;
					if (An.Point.Z >= Pc.Z + double(Tr->AnchorMinAbove) && !bBehind) { AP = An.Point; bSwing = true; }
				}
			}
			if (bSwing)
			{
				const FVector Rt(-HV.Y, HV.X, 0.0);
				const double Lat = FVector::DotProduct(AP - Pc, Rt);
				bRight = FMath::Abs(Lat) > 2.0 ? Lat > 0.0 : !A.Swing.bRightHand;
				// StartSwing's virtual pivot at the expected arc depth (altitude band / sky band / shallow-deep middle; the per-swing jitter is unknown)
				const double AheadA = FMath::Max(FVector::DotProduct(AP - Pc, HV), 10.0);
				double FMaxD = -1e9;
				for (const double K : { 0.0, 0.5, 1.0, 1.4 })
				{
					const FVector Q = Pc + HV * (AheadA * K);
					FMaxD = FMath::Max(FMaxD, Tr->TravWorld.StreetHeight(Q.X, Q.Y, Pc.Z - 0.5));
				}
				const double HEntry = Pc.Z - UT::H - FMaxD;
				const bool bSky = Tr->IsSkyLaunch();
				double BottomFeet;
				if (bSky) BottomFeet = double(Tr->ArcLowMin) + 0.5 * double(Tr->SkyArcExtra);
				else if (Tr->AltChain > 0.f && Tr->bAltArcNext && HEntry >= double(Tr->AltEntryMin)) BottomFeet = 0.5 * double(Tr->AltLowLo + Tr->AltLowHi);
				else BottomFeet = FMath::Max(double(Tr->ArcLowMin), HEntry - 0.5 * double(Tr->ArcDropShallow + Tr->ArcDropDeep) - 0.75);
				double DZ = FMath::Max(AP.Z - Pc.Z, double(Tr->MinPivotRise));
				const double BottomZ = FMaxD + BottomFeet + UT::H;
				const double RopeCap = bSky ? double(Tr->SkyRopeMax) : double(Tr->MaxArcRope) * (1.0 - 0.5 * double(Tr->RopeCapJitter));
				if (Pc.Z - BottomZ + DZ > RopeCap) DZ = FMath::Max(double(Tr->MinPivotRise), RopeCap - (Pc.Z - BottomZ));
				const double L = FMath::Clamp(Pc.Z + DZ - BottomZ, DZ + 3.0, FMath::Max(RopeCap, DZ + 3.0));
				const double DH = FMath::Min(FMath::Sqrt(FMath::Max(L * L - DZ * DZ, 16.0)), bSky ? double(Tr->SkyRopeMax) : double(Tr->MaxPivotAhead));
				const FVector Piv = Tr->PivotLateralKeep >= 1.f ? AP : Pc + HV * DH + Rt * (Lat * double(Tr->PivotLateralKeep)) + ZUp * DZ;
				const FVector RD = (Piv - Pc).GetSafeNormal();
				FVector Tan = Vc - RD * FVector::DotProduct(Vc, RD);
				if (Tan.SizeSquared() < 0.01) Tan = HV;
				const FVector Up = ((AP - Pc).GetSafeNormal() + ZUp * 0.12).GetSafeNormal();
				const FVector F2 = Tan - Up * FVector::DotProduct(Tan, Up);
				if (F2.SizeSquared() < 1e-6) return false;
				OutW = FRotationMatrix::MakeFromZX(Up, F2).ToQuat();
				OutAnchor = AP;
				return true;
			}
			// no web in reach: the air frame after the program (Orient, Air, non-trick sub: the streamlined lean along the flight path at speed)
			const double De = FMath::Max(0.0, double(P.Dur() + Tr->FlipReachHold - T));
			const FVector Ve = Vel + Acc * De;
			const double Sp = Ve.Size(), HVl = FVector(Ve.X, Ve.Y, 0.0).Size();
			double Pitch = FMath::Clamp(-Ve.Z * 0.008, -0.2, 0.25);
			const double K = FMath::Clamp((-Ve.Z - 4.0) / 14.0, 0.0, 1.0) * FMath::Clamp((Sp - 14.0) / 16.0, 0.0, 1.0);
			Pitch = FMath::Lerp(Pitch, 0.85, K);
			const double KA = FMath::Clamp((Sp - double(Tr->AirAlignV0)) / FMath::Max(1.0, double(Tr->AirAlignV1 - Tr->AirAlignV0)), 0.0, 1.0);
			if (KA > 0.0 && HVl > 1.5) Pitch = FMath::Lerp(Pitch, FMath::Min(FMath::Acos(FMath::Clamp(Ve.Z / FMath::Max(Sp, 1e-3), -1.0, 1.0)), 2.6), KA);
			const FVector HVe = HVl > 0.1 ? FVector(Ve.X / HVl, Ve.Y / HVl, 0.0) : HV;
			OutW = FRotationMatrix::MakeFromZX(ZUp, HVe).ToQuat() * FQuat(FVector(0, 1, 0), Pitch);
			bRight = A.Swing.bRightHand;
			OutAnchor = FVector::ZeroVector;
			return true;
		}

		// once per engine frame: follow the program the hero plays, predict its catch, open the window
		void UpdateCatch()
		{
			if (GC.Frame == GFrameCounter) return;
			GC.Frame = GFrameCounter;
			static const bool bParsed = []() { int32 V = 1; if (FParse::Value(FCommandLine::Get(), TEXT("-WHTrickCatch="), V)) bCatchLean = V != 0; return true; }();
			(void)bParsed;
			UWorld* W = nullptr;
			const UWebTraversalComponent* Tr = bCatchLean ? HeroTrav(&W) : nullptr;
			if (!Tr || !W) { GC.P = nullptr; GC.bOn = false; return; }
			const FWebTravAnim& A = Tr->Anim;
			// body acceleration (frame-to-frame velocity change): the flip's float gravity is the traversal's
			const double WT = W->GetTimeSeconds();
			FVector Acc(0, 0, -UWebTraversalComponent::G);
			if (GC.LastWT >= 0.0 && WT - GC.LastWT > 1e-4 && WT - GC.LastWT < 0.1) Acc = (Tr->VelM() - GC.LastVel) / (WT - GC.LastWT);
			const double DtF = GC.LastWT >= 0.0 ? FMath::Clamp(WT - GC.LastWT, 0.0, 0.1) : 1.0 / 60.0;
			GC.LastWT = WT; GC.LastVel = Tr->VelM();
			static const FName NTrick(TEXT("trick"));
			const FWebFlipProgram* P = (A.Mode == EWebTravMode::Air && A.Sub == NTrick && !A.Trick.IsNone()) ? Find(A.Trick) : nullptr;
			if (!P || P->Boost <= 0.f || !P->Segs.Num()) { GC.P = nullptr; GC.bOn = false; GC.bTarget = false; return; }
			if (GC.P != P || GC.Ver != P->Ver)
			{
				const double LW = GC.LastWT; const FVector LV = GC.LastVel;
				GC = FCatchLean();
				GC.Frame = GFrameCounter; GC.LastWT = LW; GC.LastVel = LV; GC.P = P; GC.Ver = P->Ver;
			}
			GC.Side = A.TrickSide < 0.f ? -1.f : 1.f;
			const float T = A.T, Tc = P->CatchT() - 0.02f;
			if (T < Tc - CatchLook) return;
			FQuat Wq; bool bSwing = false, bRight = true; FVector AP;
			if (!PredictFrame(Tr, *P, T, Acc, Wq, bSwing, bRight, AP)) return;
			// fit: D = body^-1 * target ~= Ry(Beta) * Rz(Gamma) [* Rx(Rho), the rest]
			const FQuat D = (A.BodyQ.Inverse() * Wq).GetNormalized();
			const FVector U = D.RotateVector(FVector(0, 0, 1));
			const float Beta = FMath::RadiansToDegrees(FMath::Atan2(U.X, U.Z));
			const FQuat R2 = FQuat(FVector(0, 1, 0), FMath::DegreesToRadians(Beta)).Inverse() * D;
			const float Gamma = FMath::UnwindDegrees(FMath::RadiansToDegrees(2.f * FMath::Atan2(float(R2.Z), float(R2.W))));
			const FQuat Tw = FQuat(FVector(0, 0, 1), FMath::DegreesToRadians(Gamma));
			const FQuat Sw = R2 * Tw.Inverse();
			const float Rho = FMath::UnwindDegrees(FMath::RadiansToDegrees(2.f * FMath::Atan2(float(Sw.X), float(Sw.W))));
			const float GammaK = CatchTwistK * Gamma;
			if (!GC.bTarget) { GC.Beta = Beta; GC.Gamma = GammaK; GC.Rho = Rho; GC.bTarget = true; }
			else
			{
				// the target follows the prediction smoothly and at <= CatchRate deg/s (a prediction that changes from the air frame to a swing
				// frame late in the window must not whip the body round)
				const float K = 1.f - FMath::Exp(-float(DtF) * 14.f), MaxStep = CatchTargetRate * float(DtF);
				GC.Beta += FMath::Clamp(K * FMath::UnwindDegrees(Beta - GC.Beta), -MaxStep, MaxStep);
				GC.Gamma = FMath::UnwindDegrees(GC.Gamma + FMath::Clamp(K * FMath::UnwindDegrees(GammaK - GC.Gamma), -MaxStep, MaxStep));
				GC.Rho += K * FMath::UnwindDegrees(Rho - GC.Rho);
			}
			GC.bSwing = bSwing; GC.bRight = bRight; GC.Anchor = AP; GC.TargetQ = Wq;
			GC.BankW = bSwing ? 0.85f * Smooth(FMath::Abs(A.Swing.Bank)) : 0.f;
			if (GC.bOn)
			{ // the catch pose follows the prediction (a web found / lost late in the window); the hand is chosen while the pose is out.
			  // A catch overdue by > 0.08 s (the traversal's search found nothing yet) hands the pose back to the program's moving reach.
				if (GC.ShapeK <= 0.f) GC.bShapeRight = bRight;
				const bool bWant = bSwing && T <= GC.Te + 0.08f;
				GC.ShapeK = FMath::Clamp(GC.ShapeK + (bWant ? 1.f : -1.f) * float(DtF) / 0.15f, 0.f, 1.f);
			}
			if (!GC.bOn)
			{
				// window: ends at the catch time (also with no web predicted: the lean then holds while the program runs out); length = the
				// whole turn at <= CatchRate deg/s peak (smoothstep peaks at 1.5 x its mean rate)
				const float Te = Tc;
				const float Rest = FMath::Abs(P->PitchDeg - SampleBase(*P, FMath::Min(Te, P->Dur())).PitchDeg);
				const float Ang = FMath::RadiansToDegrees((FQuat(FVector(0, 1, 0), FMath::DegreesToRadians(GC.Beta)) * FQuat(FVector(0, 0, 1), FMath::DegreesToRadians(GC.Gamma))).GetAngle()) + Rest;
				const float Win = FMath::Clamp(1.5f * Ang / CatchRate + 0.04f, CatchWinMin, CatchWinMax);
				if (T >= Te - Win)
				{
					GC.bOn = true; GC.Ts = T; GC.Te = FMath::Max(T + 0.15f, Te - 1.f / 60.f);
					GC.ShapeK = bSwing ? 1.f : 0.f; GC.bShapeRight = bRight;
					UE_LOG(LogTemp, Display, TEXT("WH_TRICK_CATCH %s t %.3f window %.3f-%.3f %s lean pitch %.1f twist %.1f rest-roll %.1f hand %s bank %.2f anchor (%.1f, %.1f, %.1f)"),
						*P->Name.ToString(), T, GC.Ts, GC.Te, bSwing ? TEXT("swing") : TEXT("air"), GC.Beta, GC.Gamma, GC.Rho, bRight ? TEXT("R") : TEXT("L"), GC.BankW, AP.X, AP.Y, AP.Z);
				}
			}
		}

		float CatchW(float T) { return Smooth((T - GC.Ts) / FMath::Max(0.05f, GC.Te - GC.Ts)); }

		void ApplyCatch(const FWebFlipProgram& P, float T, FWebFlipPose& O)
		{
			float TwTot = 0.f;
			for (const FWebFlipSeg& S : P.Segs) TwTot += S.TwistDeg;
			const float PitchTgt = P.PitchDeg + GC.Beta, TwTgt = TwTot + GC.Gamma * GC.Side;
			const float W = CatchW(T);
			{
				const float H = 1.f / 240.f;
				const float P0 = FMath::Lerp(SampleBase(P, T - H).PitchDeg, PitchTgt, CatchW(T - H));
				const float P1 = FMath::Lerp(SampleBase(P, T + H).PitchDeg, PitchTgt, CatchW(T + H));
				O.PitchRate = (P1 - P0) / (2.f * H);
			}
			O.PitchDeg = FMath::Lerp(O.PitchDeg, PitchTgt, W);
			O.TwistDeg = FMath::Lerp(O.TwistDeg, TwTgt, W);
			O.AxisOffDeg *= 1.f - W;
			// a program that ends in the kick-out already opens into the catch reach (web arm up, head lifting): its pose plays out
			if (GC.ShapeK <= 0.f || (P.Segs.Num() && P.Segs.Last().Shape == EWebFlipShape::Kickout)) return;
			// shapes: the program's shape at the start of the last 0.3 s -> the swing node's starting pose (major clip, then its minor share)
			// the program's last shape change that can finish before the catch plays out first (its head spot and limb change, G3), then
			// the catch pose blends in over what is left (>= 0.1 s)
			float SLast = 0.f;
			for (int32 K = P.Segs.Num() - 1; K > 0; --K)
			{
				const float S0 = SegStart(P, K);
				if (S0 + BPost + 0.1f <= GC.Te) { SLast = S0 + BPost; break; }
			}
			const float Ts2 = FMath::Max3(GC.Ts, GC.Te - CatchShapeWin, FMath::Min(SLast, GC.Te - CatchShapeWin)), Span2 = FMath::Max(0.05f, GC.Te - Ts2);
			const EWebFlipShape Low = GC.bShapeRight ? EWebFlipShape::CatchLow : EWebFlipShape::CatchLowL;
			const EWebFlipShape Bank = GC.bShapeRight ? EWebFlipShape::CatchBank : EWebFlipShape::CatchBankL;
			const bool bBankMajor = GC.BankW > 0.5f;
			const EWebFlipShape Major = bBankMajor ? Bank : Low, Minor = bBankMajor ? Low : Bank;
			const float WMinor = bBankMajor ? 1.f - GC.BankW : GC.BankW;
			// the catch clips reach frame 0 at the catch (the swing node starts its clips at T 0): before it they play backward into it (moving limbs)
			const float ClipH = FMath::Clamp(FMath::Abs(T - GC.Te) / CatchClipLen, 0.f, 1.f);
			const float SK = GC.ShapeK;
			const float Lead = P.Lead >= 0.f ? P.Lead : FlipLead, Lag = P.Lag >= 0.f ? P.Lag : FlipLag;
			auto Blend = [&](float U, float Tf, EWebFlipShape& A, EWebFlipShape& B, float& Wt, float& HA, float& HB)
			{
				if (U <= 0.f) return;
				EWebFlipShape FA, FB; float FW, FHA, FHB;
				ShapeAt(P, Tf, FA, FB, FW, FHA, FHB);
				if (T > GC.Te) { FA = A; FB = B; FW = Wt; FHA = HA; FHB = HB; } // an overdue catch hands back to the program's pose now
				const EWebFlipShape From = FW < 0.5f ? FA : FB;
				float FromH = FW < 0.5f ? FHA : FHB;
				if (Wt < 0.5f && A == From) FromH = HA; else if (Wt >= 0.5f && B == From) FromH = HB; // the shape keeps breathing / marching
				constexpr float Split = 0.6f;
				if (U < Split || SK < 0.999f) { A = From; HA = FromH; B = Major; HB = ClipH; Wt = Smooth(FMath::Min(1.f, U / Split)) * SK; }
				else { A = Major; HA = ClipH; B = Minor; HB = ClipH; Wt = WMinor * Smooth((U - Split) / (1.f - Split)); }
			};
			// upper body Lead ahead (reaches the pose Lead s before the catch), legs start Lag later and arrive at the catch
			Blend(FMath::Clamp((T + Lead - Ts2) / Span2, 0.f, 1.f), Ts2 + Lead, O.A, O.B, O.W, O.HoldA, O.HoldB);
			Blend(FMath::Clamp((T - Ts2 - Lag) / FMath::Max(0.05f, Span2 - Lag), 0.f, 1.f), Ts2 - Lag, O.LA, O.LB, O.LW, O.LHoldA, O.LHoldB);
		}
	}

	FWebFlipPose Sample(const FWebFlipProgram& P, float T)
	{
		FWebFlipPose O = SampleBase(P, T);
		if (!O.bValid) return O;
		UpdateCatch();
		if (bCatchLean && GC.bOn && GC.P == &P && GC.Ver == P.Ver) ApplyCatch(P, T, O);
		return O;
	}
}

// ---- Tricks C round 1: rendered-pose logger (opt-in, -WHTrickPose=<csv path>). Once per engine frame (OnEndFrame) it writes the hero's
// world bone positions (cm) and the head / chest bone axes for the gymnast-shape checks in tools/tricks/pose_check.py (tuck grip, layout
// hip / knee angles, pointed toes, head spot). It reads the pawn only; nothing in the traversal or the anim instance is changed by it.
namespace WebFlips
{
	namespace
	{
		struct FPoseLog
		{
			FString Path;
			TArray<FString> Rows;
			bool bInit = false, bOn = false, bHeader = false;
			double T0 = -1.0;
			static const TArray<FName>& Bones()
			{
				static TArray<FName> B;
				if (!B.Num())
				{
					for (const TCHAR* N : { TEXT("hips"), TEXT("spine2"), TEXT("neck"), TEXT("head"), TEXT("upperArm_L"), TEXT("forearm_L"), TEXT("hand_L"),
						TEXT("upperArm_R"), TEXT("forearm_R"), TEXT("hand_R"), TEXT("thigh_L"), TEXT("shin_L"), TEXT("foot_L"), TEXT("toe_L"),
						TEXT("thigh_R"), TEXT("shin_R"), TEXT("foot_R"), TEXT("toe_R") }) B.Add(FName(N));
				}
				return B;
			}
			void Flush()
			{
				if (!Rows.Num() || Path.IsEmpty()) return;
				FString Out;
				for (const FString& R : Rows) { Out += R; Out += TEXT("\n"); }
				FFileHelper::SaveStringToFile(Out, *Path, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), bHeader ? FILEWRITE_Append : FILEWRITE_None);
				bHeader = true;
				Rows.Reset();
			}
			// -WHTrickDumpFrom=<s> -WHTrickDumpTo=<s> (sequence seconds, i.e. world time minus the -WHTravPreroll pre-roll and one frame):
			// with -dumpmovie, movie frames are written only for this window (r.DumpingMovie toggled per frame), so a long fixed-step
			// capture can be rendered in segments of one deterministic run (r01: background-priority PNG dumps ran at ~1 frame/s)
			float DumpFrom = -1.f, DumpTo = -1.f, Preroll = 0.f, Warm = -1.f;
			bool bDumpWin = false, bDumpWas = false;
			void Tick()
			{
				if (!bInit)
				{
					bInit = true; bOn = FParse::Value(FCommandLine::Get(), TEXT("-WHTrickPose="), Path) && !Path.IsEmpty();
					bDumpWin = FParse::Value(FCommandLine::Get(), TEXT("-WHTrickDumpFrom="), DumpFrom) | FParse::Value(FCommandLine::Get(), TEXT("-WHTrickDumpTo="), DumpTo);
					FParse::Value(FCommandLine::Get(), TEXT("-WHTravPreroll="), Preroll);
					FParse::Value(FCommandLine::Get(), TEXT("-WHTrickWarm="), Warm);
					if (DumpTo < 0.f) DumpTo = 1e9f;
				}
				if (!GEngine) return;
				UWorld* W = nullptr;
				for (const FWorldContext& C : GEngine->GetWorldContexts())
				{
					if ((C.WorldType == EWorldType::Game || C.WorldType == EWorldType::PIE) && C.World()) { W = C.World(); break; }
				}
				if (bDumpWin)
				{
					// the flag set at the end of frame N decides whether frame N+1 is written: test N+1's sequence time
					const double SeqNext = W ? W->GetTimeSeconds() - double(Preroll) - 1.0 / 60.0 + 1.0 / 60.0 : -1.0;
					const bool bIn = W && SeqNext >= double(DumpFrom) - 1e-4 && SeqNext < double(DumpTo) - 1e-4;
					GIsDumpingMovie = bIn ? -1 : 0;
					if (bIn != bDumpWas) UE_LOG(LogTemp, Display, TEXT("WH_TRICK_DUMP %s at next-frame seq t %.4f"), bIn ? TEXT("on") : TEXT("off"), SeqNext);
					bDumpWas = bIn;
					// r01 resume (-WHTrickWarm=<s>): the world is not rendered outside [From - Warm, To) -- the simulation, animation (the hero
					// mesh ticks its pose when unseen) and telemetry run unchanged, only the GPU work of frames nobody keeps is skipped; Warm s
					// of rendered frames before the window let texture streaming, Lumen and TSR history settle before the first kept frame
					if (Warm >= 0.f && GEngine->GameViewport)
					{
						const bool bDraw = !W || (SeqNext >= double(DumpFrom - Warm) - 1e-4 && SeqNext < double(DumpTo) - 1e-4);
						if (bool(GEngine->GameViewport->bDisableWorldRendering) == bDraw)
						{
							GEngine->GameViewport->bDisableWorldRendering = !bDraw;
							UE_LOG(LogTemp, Display, TEXT("WH_TRICK_RENDER %s at next-frame seq t %.4f"), bDraw ? TEXT("on") : TEXT("off"), SeqNext);
						}
					}
				}
				if (!bOn || !W) return;
				APlayerController* PC = W->GetFirstPlayerController();
				ACharacter* Ch = PC ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
				const UWebTraversalComponent* Tr = Ch ? Ch->FindComponentByClass<UWebTraversalComponent>() : nullptr;
				USkeletalMeshComponent* M = Ch ? Ch->GetMesh() : nullptr;
				if (!Tr || !M || !M->GetSkeletalMeshAsset()) return;
				if (Rows.Num() == 0 && !bHeader)
				{
					FString H = TEXT("frame,wt,mode,sub,anim_t,trick,trick_side,x_m,y_m,z_m,vx,vy,vz");
					for (const FName& B : Bones()) { const FString N = B.ToString(); H += FString::Printf(TEXT(",%s_x,%s_y,%s_z"), *N, *N, *N); }
					H += TEXT(",head_fx,head_fy,head_fz,head_ux,head_uy,head_uz,chest_fx,chest_fy,chest_fz,chest_ux,chest_uy,chest_uz,pelvis_fx,pelvis_fy,pelvis_fz");
					H += TEXT(",catch_on,catch_w,catch_beta,catch_gamma,catch_rho,catch_bank,catch_hand,catch_swing,catch_ax,catch_ay,catch_az"); // r02 catch lean
					H += TEXT(",mesh_qx,mesh_qy,mesh_qz,mesh_qw,body_qx,body_qy,body_qz,body_qw,catch_qx,catch_qy,catch_qz,catch_qw"); // r02: root / body frame / predicted frame
					Rows.Add(H);
				}
				const FWebTravAnim& A = Tr->Anim;
				const FVector P = Tr->PosM();
				FString R = FString::Printf(TEXT("%llu,%.4f,%d,%s,%.4f,%s,%.0f,%.3f,%.3f,%.3f,%.2f,%.2f,%.2f"), (unsigned long long)GFrameCounter, W->GetTimeSeconds(),
					int32(A.Mode), *A.Sub.ToString(), A.T, A.Trick.IsNone() ? TEXT("") : *A.Trick.ToString(), A.TrickSide, P.X, P.Y, P.Z,
					A.Velocity.X / 100.0, A.Velocity.Y / 100.0, A.Velocity.Z / 100.0);
				for (const FName& B : Bones())
				{
					if (M->GetBoneIndex(B) == INDEX_NONE) { R += TEXT(",,,"); continue; }
					const FVector L = M->GetBoneLocation(B);
					R += FString::Printf(TEXT(",%.2f,%.2f,%.2f"), L.X, L.Y, L.Z);
				}
				// bone axes in world space: the imported (Blender) bones run along their local Y; X / Z span the bone's cross section
				auto Axes = [&](const TCHAR* N, bool bUp)
				{
					const FName B(N);
					if (M->GetBoneIndex(B) == INDEX_NONE) { R += bUp ? TEXT(",,,,,,") : TEXT(",,,"); return; }
					const FQuat Q = M->GetBoneQuaternion(B, EBoneSpaces::WorldSpace);
					const FVector Ax = Q.GetAxisX(), Ay = Q.GetAxisY(), Az = Q.GetAxisZ();
					R += FString::Printf(TEXT(",%.4f,%.4f,%.4f"), Az.X, Az.Y, Az.Z);
					if (bUp) R += FString::Printf(TEXT(",%.4f,%.4f,%.4f"), Ay.X, Ay.Y, Ay.Z);
					(void)Ax;
				};
				Axes(TEXT("head"), true); Axes(TEXT("spine2"), true); Axes(TEXT("hips"), false);
				{ // r02: the catch lean of the program playing now (prediction made during this frame's Sample calls)
					const bool bC = GC.bOn && GC.P && A.Trick == GC.P->Name && A.Sub == FName(TEXT("trick"));
					R += FString::Printf(TEXT(",%d,%.3f,%.2f,%.2f,%.2f,%.3f,%d,%d,%.2f,%.2f,%.2f"), bC ? 1 : 0, bC ? CatchW(A.T) : 0.f, bC ? GC.Beta : 0.f, bC ? GC.Gamma : 0.f,
						bC ? GC.Rho : 0.f, bC ? GC.BankW * GC.ShapeK : 0.f, bC ? (GC.bShapeRight ? 1 : -1) : 0, bC ? int32(GC.bSwing) : 0, GC.Anchor.X, GC.Anchor.Y, GC.Anchor.Z);
					const FQuat MQ = M->GetComponentQuat(), BQ = A.BodyQ, CQ = GC.TargetQ;
					R += FString::Printf(TEXT(",%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f"), MQ.X, MQ.Y, MQ.Z, MQ.W, BQ.X, BQ.Y, BQ.Z, BQ.W, CQ.X, CQ.Y, CQ.Z, CQ.W);
				}
				Rows.Add(R);
				if (Rows.Num() >= 240) Flush();
			}
		};
		FPoseLog& PoseLog() { static FPoseLog L; return L; }
		struct FPoseLogReg
		{
			FPoseLogReg()
			{
				FCoreDelegates::OnEndFrame.AddLambda([]() { PoseLog().Tick(); });
				FCoreDelegates::OnPreExit.AddLambda([]() { PoseLog().Flush(); });
				FCoreDelegates::OnEnginePreExit.AddLambda([]() { PoseLog().Flush(); });
			}
		};
		FPoseLogReg GPoseLogReg;
	}
}
