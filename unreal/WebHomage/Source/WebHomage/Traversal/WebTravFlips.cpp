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
			TEXT("flipStraddle"), TEXT("flipThrone"), TEXT("flipTwist"), TEXT("flipReach"), TEXT("flipKickout") };
		static_assert(UE_ARRAY_COUNT(C) == int32(EWebFlipShape::Num), "one clip per shape");
		return C[FMath::Clamp(int32(S), 0, int32(EWebFlipShape::Num) - 1)];
	}
	const TCHAR* ShapeName(EWebFlipShape S) { return ShapeClip(S) + 4; }

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

	FWebFlipPose Sample(const FWebFlipProgram& P, float T)
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
