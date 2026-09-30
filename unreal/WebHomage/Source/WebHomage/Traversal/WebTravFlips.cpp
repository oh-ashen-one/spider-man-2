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
			// sky launch / long air: double back in the owner clip's S3 rhythm (3 turns in 2.8 s, short holds): tuck to inverted, inverted
			// pencil, tuck round, a flash of upright layout, tuck to inverted again, straddle, tuck round, upright "throne" spread, reach
			// round 12 (critic r11 secondary: "snaps at 640 deg/s through four shapes that last 0.15-0.36 s; hold each shape >= 0.5 s,
			// at most 2 shapes, blend >= 0.15 s"): two shapes only, tuck and layout, each held 0.5-0.55 s, then the reach
			// (r11: tuck / pencil / tuck / layout / tuck / straddle / tuck / throne / reach, 2.35 s)
			Add(TEXT("backDouble"), -720.f, { {S::Tuck, 0.55f}, {S::Layout, 0.5f}, {S::Tuck, 0.55f}, {S::Layout, 0.5f}, {S::Reach, 0.2f} });
			// front pike into a slow inverted swan that unwinds (critic r10 reference description), tuck up, reach
			Add(TEXT("frontPikeSwan"), 360.f, { {S::Pike, 0.36f}, {S::Pencil, 0.36f}, {S::Swan, 0.72f}, {S::Tuck, 0.27f}, {S::Reach, 0.26f} });
			// corkscrew: a layout that turns over while it twists a full turn (arms crossed), opens to a swan, tucks up, reach
			Add(TEXT("corkscrew"), 360.f, { {S::Layout, 0.22f}, {S::Twist, 0.5f, 360.f}, {S::Swan, 0.6f}, {S::Tuck, 0.28f}, {S::Reach, 0.24f} }, 4.0f, 1.2f);
			// short air (plain trick release): tuck to inverted, pencil hold, tuck round, reach
			Add(TEXT("backSingle"), -360.f, { {S::Tuck, 0.31f}, {S::Pencil, 0.46f}, {S::Tuck, 0.31f}, {S::Reach, 0.24f} });
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
		float InertiaAt(const FWebFlipProgram& P, float T)
		{
			EWebFlipShape A, B; float W, HA, HB;
			ShapeAt(P, T, A, B, W, HA, HB);
			return FMath::Lerp(Inertia(A), Inertia(B), W);
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
			TEXT("flipStraddle"), TEXT("flipThrone"), TEXT("flipTwist"), TEXT("flipReach") };
		return C[FMath::Clamp(int32(S), 0, 8)];
	}
	const TCHAR* ShapeName(EWebFlipShape S) { return ShapeClip(S) + 4; }

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
		ShapeAt(P, T - FlipLag, O.LA, O.LB, O.LW, O.LHoldA, O.LHoldB);
		return O;
	}
}
