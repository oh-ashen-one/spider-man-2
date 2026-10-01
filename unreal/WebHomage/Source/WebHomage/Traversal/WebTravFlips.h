// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
// Piece P3 round 11 (owner brief FLIPS_BRIEF.md, spec docs/night1/traversal/FLIPS_SPEC.md): gymnast flip programs.
// A flip program is a timeline of held gymnastic SHAPES (tuck, pike, layout, swan, pencil, straddle, throne, twist, reach,
// keyed in Blender on the hero rig: /Game/Traversal/HeroDev/flip<Shape>). The body rotation is not keyed: it follows one
// angular momentum through the whole program, rate = L * env(t) / I(shape(t)), so the flip spins fast through a tuck and
// slows almost to a hold in an open shape (pencil / swan / throne) -- the ease comes from the shapes, as in real tumbling.
// L is solved so the program ends exactly at its total angle (upright). Twists (corkscrews) turn about the body's long axis
// inside their own segments. Limbs overlap: the upper body samples the timeline FlipLead s ahead, the legs FlipLag s behind.
// Pure functions: the traversal (durations, telemetry), the character (root rotation) and the anim instance (shapes) all
// sample the same program at the same time.
#pragma once

#include "CoreMinimal.h"

// round 13: Kickout = the double's open finish (critic r12: "backDouble uses 5 shapes", "rigid identical plank"): a layout whose arms
// sweep wide while the legs scissor a little behind them, ending with the web arm up (the catch reach) -- keyed motion, not a held plank
enum class EWebFlipShape : uint8 { Tuck, Pike, Layout, Swan, Pencil, Straddle, Throne, Twist, Reach, Kickout, Num };

struct FWebFlipSeg
{
	EWebFlipShape Shape = EWebFlipShape::Tuck;
	float Dur = 0.3f;     // s
	float TwistDeg = 0.f; // twist about the long axis inside this segment (deg, eased in/out)
	// round 14 (critic r13: "the tuck spins at a constant 678 deg/s -- ease the ends >= 30 % slower than mid-flip"): the effective
	// inertia rises toward the segment's ends by these factors (1 + EaseIn at its start, 1 + EaseOut at its end, smooth over
	// WebFlips::EaseW of the segment) -- the gymnast grabs the knees tighter mid-tuck and opens a little going in / coming out
	float EaseIn = 0.f, EaseOut = 0.f;
};

struct FWebFlipProgram
{
	FName Name;
	float PitchDeg = 360.f;   // total rotation about the lateral axis; + = front flip (head goes forward), - = back flip
	TArray<FWebFlipSeg> Segs;
	float Boost = 3.5f, Up = 1.5f; // traversal release boost (m/s) at 0.3 x the first segment
	// round 13 (critic r12: "attach a web within 0.3 s of Reach"): the next web may attach from CatchOpen s before the program's end
	// (inside its final reach, once that pose reads) -- the catch cuts the last few degrees and springs them back in ~0.07 s
	float CatchOpen = 0.16f;
	float CatchT() const { return FMath::Max(0.f, Dur() - CatchOpen); }
	float Dur() const { float D = 0.f; for (const FWebFlipSeg& S : Segs) D += S.Dur; return D; }
};

struct FWebFlipPose
{
	bool bValid = false;
	float PitchDeg = 0.f, TwistDeg = 0.f, PitchRate = 0.f;  // deg, deg, deg/s
	// upper-body shape blend (sampled FlipLead ahead) and legs (FlipLag behind): A -> B by W; HoldA = 0..1 progress through A's hold
	EWebFlipShape A = EWebFlipShape::Tuck, B = EWebFlipShape::Tuck, LA = EWebFlipShape::Tuck, LB = EWebFlipShape::Tuck;
	float W = 0.f, LW = 0.f, HoldA = 0.f, HoldB = 0.f, LHoldA = 0.f, LHoldB = 0.f;
	// round 14: the upper-body shape's own hips->head lean off the body frame (deg, + = head forward), blended A -> B by W. The
	// character subtracts it from the root pitch so the VISIBLE body axis follows the momentum timeline (r13 rendered: a swan -> tuck
	// change curled the axis ~55 deg in 0.17 s on top of the program, so every tuck entered at ~460 deg/s and pikeSwan peaked 1045-1090)
	float AxisOffDeg = 0.f;
	int32 Seg = 0;
};

namespace WebFlips
{
	/** Blender clip name of a shape (flipTuck ...). */
	const TCHAR* ShapeClip(EWebFlipShape S);
	const TCHAR* ShapeName(EWebFlipShape S);
	/** Round 14: hips->head lean of a keyed shape off the body frame (deg, + = head forward), measured on the rendered r14 probe. */
	float ShapeAxisDeg(EWebFlipShape S);
	/** Program by name (backDouble, frontPikeSwan, corkscrew, backSingle, wallFront); nullptr if unknown. */
	const FWebFlipProgram* Find(FName Name);
	/** All program names (for cycling). */
	const TArray<FName>& Names();
	/** Sample a program at T seconds (clamped to [0, Dur]). */
	FWebFlipPose Sample(const FWebFlipProgram& P, float T);
	extern float FlipLead, FlipLag;
}
