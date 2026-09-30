// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Traversal/WebTravFlips.h"

namespace WebFlips
{
	float FlipLead = 0.04f, FlipLag = 0.07f;

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
			case EWebFlipShape::Straddle: return 6.0f;
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

		struct FTable { TArray<float> G; float L = 0.f; }; // cumulative rotation (deg) at 1/TableHz steps

		TArray<FWebFlipProgram>& Programs()
		{
			static TArray<FWebFlipProgram> P;
			if (P.Num()) return P;
			using S = EWebFlipShape;
			auto Add = [&](const TCHAR* Name, float Pitch, std::initializer_list<FWebFlipSeg> Segs, float Boost = 3.5f, float Up = 1.5f)
			{
				FWebFlipProgram F; F.Name = FName(Name); F.PitchDeg = Pitch; F.Segs = Segs; F.Boost = Boost; F.Up = Up; P.Add(F);
			};
			// round 13 (critic r12 single gap: tricks were isolated set pieces -- 1.7 s rise, trick, 1.3 s dive, cut): every program starts AT
			// the web release and is 1.2-1.7 s long, so release -> next attach fits 1.4-1.8 s and attach -> attach <= 3.3 s (TRAVERSAL-SPEC T2/T4)
			// backDouble: two shapes only (critic r11/r12 secondary): a double tuck that kicks out into an open finish (Kickout: arms sweep
			// wide, legs scissor behind them, the web arm comes up for the catch) -- the gymnast's double back with a kick-out.
			// Tuck 1.0 s (peak ~680 deg/s), Kickout 0.7 s (<= 150 deg/s for ~0.65 s), mean ~420 deg/s (FLIPS_SPEC F2 300-500).
			// (r12: tuck / layout / tuck / layout / reach 2.3 s; r11: nine segments)
			{
				// round 14 (critic r13 "a spinning ball at a constant 678 deg/s"; F4 Kickout hold 0.22 s): Tuck 1.15 s eased (ends ~60 % of the
				// ~740 deg/s middle), Kickout 0.62 s at <= ~100 deg/s (inertia 10.5); catch 1.57 s after the release (r13 1.50)
				FWebFlipProgram F; F.Name = FName(TEXT("backDouble")); F.PitchDeg = -720.f;
				F.Segs = { {S::Tuck, 1.15f, 0.f, 0.75f, 0.85f}, {S::Kickout, 0.62f} };
				F.CatchOpen = 0.2f; P.Add(F);
			}
			// front pike into a slow inverted swan that unwinds (critic r10 reference description), tuck up, reach (r12 1.97 s -> 1.65 s)
			// round 14 (critic r13: "b uses 5 shapes in 1.7 s", every shape >= 0.3 s, F3 rendered peak 980-1180 deg/s): the pencil is dropped,
			// pike 0.40 s and tuck 0.38 s eased at both ends, swan 0.55 s (1.65 -> 1.59 s)
			Add(TEXT("frontPikeSwan"), 360.f, { {S::Pike, 0.40f, 0.f, 0.7f, 0.3f}, {S::Swan, 0.55f}, {S::Tuck, 0.38f, 0.f, 0.7f, 0.7f}, {S::Reach, 0.26f} });
			// corkscrew: a layout that turns over while it twists a full turn (arms crossed), opens to a swan, tucks up, reach (1.84 -> 1.66 s)
			// round 14: every shape >= 0.3 s (layout 0.22 -> 0.31, tuck 0.26 -> 0.34 eased), twist 0.42 s, swan 0.36 s (1.66 -> 1.67 s)
			Add(TEXT("corkscrew"), 360.f, { {S::Layout, 0.31f}, {S::Twist, 0.42f, 360.f}, {S::Swan, 0.36f}, {S::Tuck, 0.34f, 0.f, 0.6f, 0.7f}, {S::Reach, 0.24f} }, 4.0f, 1.2f);
			// short air (plain trick release): tuck to inverted, pencil hold, tuck round, reach
			Add(TEXT("backSingle"), -360.f, { {S::Tuck, 0.32f, 0.f, 0.5f, 0.3f}, {S::Pencil, 0.36f}, {S::Tuck, 0.32f, 0.f, 0.3f, 0.6f}, {S::Reach, 0.24f} });
			// wall-run top-out: front flip over the roof edge, layout on top, throne into the landing
			Add(TEXT("wallFront"), 360.f, { {S::Tuck, 0.27f}, {S::Layout, 0.3f}, {S::Tuck, 0.27f}, {S::Throne, 0.3f} }, 0.f, 0.f);
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
			static TMap<FName, FTable> Cache;
			if (const FTable* T = Cache.Find(P.Name)) return *T;
			FTable Tb;
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
			return Cache.Add(P.Name, Tb);
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

	const FWebFlipProgram* Find(FName Name)
	{
		for (const FWebFlipProgram& P : Programs()) { if (P.Name == Name) return &P; }
		return nullptr;
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
		ShapeAt(P, T + FlipLead, O.A, O.B, O.W, O.HoldA, O.HoldB);
		O.AxisOffDeg = FMath::Lerp(ShapeAxisDeg(O.A), ShapeAxisDeg(O.B), O.W);
		ShapeAt(P, T - FlipLag, O.LA, O.LB, O.LW, O.LHoldA, O.LHoldB);
		return O;
	}
}
