# Hulk in Manhattan

**An AI-built homage to *The Incredible Hulk: Ultimate Destruction* (2005), rebuilt in Unreal Engine 5.8 on top of the Manhattan we already made for our Spider-Man 2 port.**

Goal, in one sentence: a fully playable Hulk-like character tearing through the whole island of Manhattan, built by Claude Opus 5.5 with Jev and Haiku 5.5 running the people around him, and filmed as a YouTube series.

> This is an unofficial, non-commercial fan homage. It is not affiliated with or endorsed by Marvel, Disney, Radical Entertainment, Vivendi, Activision, or Sierra. No trademarked logos, ripped assets, music, or audio from the original game are used. The character is an original green brawler in the spirit of the 2005 game. It will never be sold.

---

## 1. Why this game

- *Ultimate Destruction* is the game people have been begging for a remake of for twenty years. Nobody has made one. Not Marvel, not Radical (who went on to make Prototype), not the fan scene. The only thing that exists is a fake concept trailer and some texture packs for the 2005 original.
- Every signature move is a physics clip: running up skyscrapers, ripping a car in half to wear as gauntlets, swinging a bus as a shield, the thunderclap, the ground pound, surfing on a flattened car, throwing a tank at a helicopter.
- Unreal Engine 5's Chaos destruction, Nanite, and Lumen are the exact upgrade the game deserves. The 2005 version was impressive for a PS2. In UE5 it can look like the thing it was always trying to be.
- We already own most of the hard parts. See section 3.

Gameplay reference: [full 4K walkthrough of the original](https://www.youtube.com/watch?v=quXozQOTbf4).

## 2. What we are building

**A Hulk-like character in the full Manhattan island, playable end to end.**

### 2.1 The character
- Original design: a huge green brawler, torn purple shorts, no logo, no likeness of any actor. Working name **Brute**.
- Built through our existing Unreal character and suit pipeline (the one that produced the Spider-Man suits and the Invincible hero), with a Blender-script fallback. The asset is modelled fresh; the customuse site in Chrome on the studio is the first stop for the base mesh.
- Scale: about 2.5 m tall, 3x the mass of a human. Every system below is tuned to that.

### 2.2 Traversal (replaces web-swinging and flight)
- **Super jump**: charged leap, 40 m vertical, 100 m horizontal, with landing crater and dust.
- **Wall run**: sprint straight up any building face. Momentum carries over the roof edge.
- **Sprint**: faster than cars, knocks cars aside, leaves cracked pavement.
- **Dash and air dash**: short bursts for direction changes mid-leap.
- **Landing**: a controlled "superhero landing" with shockwave, or a full crater at high speed.
- Camera: field of view widens with speed, exactly as the swing camera already does. Keep full-body framing and collision-aware placement from the manual-camera work.

### 2.3 Destruction
- Buildings on the path break under Chaos destruction with destructible proxies, not full-city fracture. Facades, glass, awnings, scaffolding, water towers, street furniture, lamp posts.
- Every car, bus, truck, dumpster, and lamp post is a physics object that can be picked up, thrown, or ripped.
- Cars can be torn into **gauntlets**. Buses become **shields**. Lamp posts become **bats**.
- A **collateral damage counter** on screen, in dollars, because it's funny.

### 2.4 Combat
- Melee: light, heavy, grab, throw. Weaponized objects change the moveset.
- **Thunderclap** (hands together, shockwave), **ground pound** (crater, launches cars), **sonic boom charge**.
- Rage meter fills from damage dealt and taken; full rage unlocks the big moves.
- Enemies, in order of introduction: police cruisers, SWAT vans, army jeeps, tanks, attack helicopters, mechs, and then a boss.

### 2.5 The people of Manhattan (the AI twist)
- Pedestrians, drivers, cops, and soldiers run on **Jev**, TypeSafe's decision model. Each tick Jev picks from a finite menu: flee, hide, film on phone, freeze, drive away, ram, retreat, call for backup. Jev returns probabilities and we sample from them, so no two bystanders react the same way. This is the same crowd brain we built for the Markhor Meadow living village, reused.
- **Haiku 5.5** writes the words: radio chatter, news tickers, bystander shouts, and the end-of-session news report about what you destroyed.
- Rules-based fallback for both, so the game runs with no keys and no network.

### 2.6 Other fighters (phase 2)
- Once Brute works, other super-powered characters come into the same city: an Abomination-style boss first, then a flying hero (we already have the flight controller from the Invincible branch), then whatever the channel votes for.
- Boss fights level blocks. Collateral counter goes vertical.
- Eventually: two AI-driven fighters in the same city, each controlled by Jev, with Opus coaching each one between rounds.

## 3. What we already have (do not rebuild these)

| Need | Already built | Where |
|---|---|---|
| The whole island of Manhattan, procedural buildings, streets, water, foliage, night mode | Spider-Man 2 port, Unreal 5.8 | `oh-ashen-one/spider-man-2`, `main`, project `unreal/WebHomage` |
| Third-person character, chase camera, input mapping (keyboard, mouse, DualSense) | Same | `Source/WebHomage/Traversal/` |
| Character and suit pipeline, Blender rig scripts | Same | suit integration stages in `Scripts/build_manhattan.py` |
| Flight controller, destruction proxies, crowd hook, rescue clock, HUD | Invincible branch | `oh-ashen-one/spider-man-2`, branch `invincible`, PR #5 |
| Deterministic capture harness and critic protocol | Same | `docs/night1/final/swing/.../REVIEW_PROTOCOL.md` |
| Guarded engine launcher and shared GPU coordinator | Same | `tools/m5/guarded_preview.py`, `~/.cache/gpu-slot` |
| Jev + Haiku NPC sidecar (decisions, memory, dialogue, offline fallback) | Markhor Meadow living village | `oh-ashen-one/markhor-meadow`, branch `living-village`, PR #6, `tools/village-brain/` |
| Shared house rules, Unreal MCP routing, operating rules | Shared brain | `oh-ashen-one/agents-md` |

This project is a **new branch or fork of `spider-man-2`**, starting from the `invincible` branch, not a fresh Unreal project.

## 4. Who does what

| Role | Who | Notes |
|---|---|---|
| Builder (code, pipeline, integration, docs) | Claude Opus 5.5 | Runs on the Mac Studio M3 Ultra via Claude Code, with subagents for clean splits |
| Crowd and enemy decisions at runtime | Jev (TypeSafe AI) | About 95% of calls. Finite menus, sampled probabilities |
| Words at runtime | Claude Haiku 5.5 | Radio, news, shouts, reports. About 5% of calls |
| Managing session, briefs, planning | Claude Fable 5.1 | The session that wrote this document |
| Owner, playtester, final say on feel | Hari (`oh-ashen-one`) | Owner playtest decides subjective acceptance |

## 5. House rules (summary of the shared brain)

- All heavy compute runs on the Mac Studio M3 Ultra (`midirstudio.local`). Cloud sessions cannot reach it; run Claude Code on the studio itself for anything that compiles, cooks, renders, or captures.
- Task-owned branch and worktree only. Push in the same session. Merging to `main` requires explicit owner permission. One rolling `HANDOFF.md` per thread.
- Shared GPU slot coordinator at `~/.cache/gpu-slot`: hard cap two renderer-bearing engines, never clear PAUSED, never touch foreign processes, SIGTERM then wait 60 seconds before SIGKILL, never auto-relaunch after two crashes, never launch anything that raises a macOS dialog.
- Performance timing is only valid from a game launched inside the logged-in desktop session (`open -a`), never from an SSH shell.
- Unreal work goes through the shared brain's `unreal-engine` routing and Epic's native Unreal MCP on an instance you own, after verifying it is yours.
- Never commit secrets, signing files, or generated Content. Keys live in env vars (`ANTHROPIC_API_KEY`, `TYPESAFE_API_KEY`).
- No owner-acceptance claims from a build. Fixed-step capture footage is not proof of real-time frame rate.
- Each repo carries a `.claude/settings.json` with permission allow rules so sessions don't stall on prompts.

## 6. Milestones

1. **Brute walks**: new character in the city, scaled, with the existing camera. One screenshot.
2. **Brute moves**: super jump, wall run, sprint, dash, landings. Capture suite: 10 traversal cases.
3. **Manhattan breaks**: destructible proxies on one district, cars and props as physics objects, collateral counter. Capture suite: 8 destruction cases.
4. **Brute fights**: melee, grab, throw, gauntlets, bus shield, thunderclap, ground pound, rage. Cops and SWAT respond. Capture suite: 10 combat cases.
5. **Manhattan reacts**: Jev crowd and vehicle brains, Haiku radio and news ticker, offline fallback. Debug panel showing every decision with its probabilities, for filming.
6. **Escalation**: army, tanks, helicopters, mechs. A 10-minute play session that ends in a boss fight against an Abomination-style enemy.
7. **Other fighters**: the flying hero from the Invincible branch enters the city. AI vs AI mode.
8. **Owner playtest copy**: staged with `Play-Brute.command` through the guarded launcher, 1920x1080 windowed, 60 fps cap.

Each milestone ends with: pushed branch, updated `HANDOFF.md`, capture set, independent critic pass with quoted defects, and a `RESULTS.md` with before and after stills.

## 7. The YouTube series: "Remaking my favorite old games with AI"

| Episode | Game | Hook |
|---|---|---|
| 1 | Hulk: Ultimate Destruction | "Nobody remade this in 20 years. AI did it in two weeks." |
| 2 | SSX 3 | One peak, top to bottom, snow and speed in UE5 |
| 3 | Open. Candidates: Black (destruction shooter), Crimson Skies (reuses flight), Freedom Fighters (NYC) | |

Rules for the series: beloved game, dormant publisher, no serious remake exists, one iconic slice rather than the whole game, built as an original homage.

Other content this repo feeds: the Jev decision debug panel on screen during play, the collateral damage counter, AI-vs-AI fights, and the news reports Haiku writes after each session.

## 8. How this was decided

This brief is the output of a planning session on 2026-10-15. Decisions made along the way:

- Started from "let's have Jev play Doom". Jev turned out to be a decision model, not a text model: it picks from a menu in about 100 ms and returns probabilities. That makes it the reflexes, with a Claude model as the planner.
- Built the Markhor Meadow living village with that split (Jev decides, Haiku writes). The same brain gets reused here for crowds and enemies.
- Built the Invincible flight game on the Spider-Man 2 Unreal port. Its city, destruction proxies, and character pipeline are the base here.
- Considered TimeSplitters 2 (Chicago 1932) and dropped it because the TimeSplitters Rewind fan remake already shipped.
- Considered Black, Freedom Fighters, Crimson Skies, Motorstorm, Medal of Honor Frontline, Psi-Ops, Twisted Metal Black, Mercenaries, Def Jam, Condemned, True Crime NYC. Picked Hulk because the lane is empty and the base already exists.
- Backlog kept for later: Pokemon Emerald 30-minute runs on the PokeAgent harness, RuneScape on a Lost City private server, Clone Hero blind with Jev, a Souls-like boss bake-off between models, Splinter-Cell-style stealth with Jev guards, a Hunza Valley photoreal test, and an iOS hot dog cart game with AI customers.

## 9. Layout of this repo

```
README.md          this brief
docs/
  BRIEF.md         same content, kept in sync, for linking from the game repo
  SERIES.md        episode plan and per-episode checklist
  MOVESET.md       full move list with inputs, timings, and reference clips
  AI_BRAINS.md     Jev menus and Haiku prompts for crowd, cops, army, boss
  LEGAL.md         homage rules, what is and is not allowed
```

The game code itself lives in `oh-ashen-one/spider-man-2` on a `brute` branch cut from `invincible`. This repo is the plan, the design, and the public record.
