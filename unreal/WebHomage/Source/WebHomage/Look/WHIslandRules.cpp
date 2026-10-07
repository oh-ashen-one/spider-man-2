// Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
#include "Look/WHIslandRules.h"
#include "WebHomage.h"
#include "Engine/World.h"
#include "Engine/Level.h"
#include "GameFramework/Actor.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

bool UWHIslandRules::ShouldCreateSubsystem(UObject* Outer) const
{
	const UWorld* W = Cast<UWorld>(Outer);
	return W && W->IsGameWorld() && (W->GetMapName().Contains(TEXT("Manhattan_Island")) || FParse::Param(FCommandLine::Get(), TEXT("WHIslandRules")));
}

void UWHIslandRules::OnWorldBeginPlay(UWorld& InWorld)
{
	Super::OnWorldBeginPlay(InWorld);
	Handle = FWorldDelegates::LevelAddedToWorld.AddUObject(this, &UWHIslandRules::OnLevelAdded);
	for (ULevel* L : InWorld.GetLevels()) if (L) OnLevelAdded(L, &InWorld);
}

void UWHIslandRules::Deinitialize()
{
	if (Handle.IsValid()) { FWorldDelegates::LevelAddedToWorld.Remove(Handle); Handle.Reset(); }
	Super::Deinitialize();
}

void UWHIslandRules::OnLevelAdded(ULevel* Level, UWorld* InWorld)
{
	if (InWorld != GetWorld() || !Level) return;
	const int32 N = HideLevel(Level);
	TotalHidden += N;
	if (N > 0) UE_LOG(LogWebHomage, Display, TEXT("WH_ISLAND hide +level %s: %d city actors hidden in game (park ribbons / lawns / ez park trees / flat water), total %d"), *Level->GetOuter()->GetName(), N, TotalHidden);
}

int32 UWHIslandRules::HideLevel(ULevel* Level)
{
	int32 N = 0;
#if WITH_EDITOR
	static const TCHAR* Prefix[] = { TEXT("ISM_ez_park"), TEXT("ISM_ez_elm"), TEXT("ISM_ez_conifer"), TEXT("ISM_trees_park_crownfar"), TEXT("ISM_trees_elm_crownfar"), TEXT("ISM_trees_conifer_crownfar") };
	for (AActor* A : Level->Actors)
	{
		if (!A || A->IsHidden()) continue;
		FString L = A->GetActorLabel();
		L.ReplaceInline(TEXT("-"), TEXT("_"));
		bool bHide = false;
		for (const TCHAR* P : Prefix) if (L.StartsWith(P)) { bHide = true; break; }
		if (!bHide && A->IsA<AStaticMeshActor>() && (L.StartsWith(TEXT("parkPaths")) || L.StartsWith(TEXT("mapLawns")))) bHide = true;
		if (!bHide && (L == TEXT("WaterPlane") || L.StartsWith(TEXT("WaterPlane__")))) bHide = true;
		if (bHide) { A->SetActorHiddenInGame(true); ++N; }
	}
#endif
	return N;
}
