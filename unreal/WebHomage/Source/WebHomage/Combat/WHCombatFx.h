// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
// Piece P5 (combat): combat VFX — a round-01 port of src/game/combat/fx.js with pooled engine basic shapes (no Niagara assets
// yet): hit flashes + spark streaks + shock rings, dust puffs, web strands (hand -> target, drawn every frame), web-shot
// pellets, bullet tracers + muzzle flashes, web splats (wall / ground), spider-sense streaks around the head.
// Materials (built by Scripts/build_combat.py): /Game/Combat/Materials/M_CmbFX (additive unlit, Color / Opacity),
// M_CmbTrans (lit translucent, Color / Opacity / Emissive), M_CmbSolid (lit opaque, Color / Rough / Emissive / Metal).
#pragma once

#include "CoreMinimal.h"

class AActor;
class UStaticMeshComponent;
class UStaticMesh;
class UMaterialInterface;
class UMaterialInstanceDynamic;

enum class EWHFxMat : uint8 { Glow, Trans, Solid, Flare };

struct FWHFxItem
{
	UStaticMeshComponent* Comp = nullptr;
	UMaterialInstanceDynamic* Mid = nullptr;
	EWHFxMat Mat = EWHFxMat::Glow;
	bool bLive = false;
	double T = 0, Life = 0.2, Drag = 0;
	FVector Pos = FVector::ZeroVector, Vel = FVector::ZeroVector, Gravity = FVector::ZeroVector;   // m
	FVector Dir = FVector::UpVector;      // long axis (streaks / strands / discs: normal)
	FVector Size0 = FVector(0.1), Size1 = FVector(0.1);   // m (x, y = cross-section, z = length along Dir)
	FLinearColor Color = FLinearColor::White;
	double Op0 = 1, Op1 = 0;
	bool bStretch = false;                // streak: length follows the velocity
	TFunction<FVector()> A, B;            // strand end points (m); valid while bStrand
	bool bStrand = false;
	double Width = 0.012, Sag = 0;
	int32 Tag = 0;
	bool bReal = false;                   // r02 impact sparks: REAL-time life (hold static for Hold s, then fly + fade); others: game time
	double Hold = 0;
};

class WEBHOMAGE_API FWHCombatFx
{
public:
	void Init(AActor* Owner);
	void Update(double Dt, double RealDt);
	void Clear();

	/** Small spark burst + core flash (wall bumps, web hits, bullets). P, Dir in metres; Dir = direction the sparks fly. HoldFrames > 0: static for that many frames first. */
	void Hit(const FVector& P, const FVector& Dir, double Heavy, const FLinearColor* Color = nullptr, int32 HoldFrames = 0);
	/** r03 blow impact: an additive red-orange flare covering FlareFrac (~2 %) of the frame, static through the local hit-stop (HoldFrames) and gone 2.3 frames later
	 *  (frame 8 for a 5-frame hold), plus the spark burst of Hit(). The flare radius follows the camera distance, so its on-screen area is constant. */
	void Impact(const FVector& P, const FVector& Dir, double Heavy, const FLinearColor* Color, int32 HoldFrames);
	/** the framing camera of the last frame (m, horizontal fov deg): sizes the flare */
	void SetCam(const FVector& P, double FovH) { CamP = P; CamFovH = FovH; bCam = true; }
	double FlareFrac = 0.022, FlareK = 1.0, FlareI = 1.0;   // area (share of the frame), size factor, intensity factor (-WHCmbFlareK= / -WHCmbFlareI=)
	void Dust(const FVector& P, double Amount);
	/** Web line between two moving points for Life s (fades over the last Fade s). Returns a handle (tag). */
	int32 Strand(TFunction<FVector()> A, TFunction<FVector()> B, double Life, double Sag = 0.05, double Fade = 0.1);
	void KillTag(int32 Tag);
	void WebHit(const FVector& P, const FVector& Dir);
	void Pellet(const FVector& P);
	void Muzzle(const FVector& P, const FVector& Dir);
	void Tracer(const FVector& A, const FVector& B);
	void Splat(const FVector& P, const FVector& N, double Size);
	/** Spider-sense level 0..1 (red = gun threat) around the head (m). */
	void Sense(double Level, bool bRed, const FVector& Head, double Dt);
	void Heal(const FVector& P);

	int32 LiveCount() const;
	int32 Spawned = 0;

private:
	FWHFxItem& Alloc(EWHFxMat Mat, UStaticMesh* Mesh);
	void Place(FWHFxItem& It, double K);
	TWeakObjectPtr<AActor> Owner;
	UStaticMesh* Sphere = nullptr;
	UStaticMesh* Cyl = nullptr;
	UMaterialInterface* MGlow = nullptr;
	UMaterialInterface* MTrans = nullptr;
	UMaterialInterface* MSolid = nullptr;
	UMaterialInterface* MFlare = nullptr;
	FVector CamP = FVector::ZeroVector; double CamFovH = 75; bool bCam = false;
	TArray<FWHFxItem> Items;
	int32 NextTag = 1;
	FRandomStream Rng = FRandomStream(4711);
	double SenseT = 0;
	TArray<int32> SenseIdx;
};
