> **This is a homage game.** It is a non-commercial fan tribute. We are not trying to make anything copyrighted, and this is **not an official Marvel game**. It is not affiliated with, endorsed by or sponsored by Marvel, Disney, Sony Interactive Entertainment or Insomniac Games. The AI company logos used on character suits (Claude, OpenAI Codex, Gemini, Kimi, Qwen) belong to their owners and appear only as a playful tribute, with no affiliation or endorsement. See [DISCLAIMER.md](DISCLAIMER.md).
>
> **About this fork.** Spider-Man 2 is a fork of [xikhar/spiderbench](https://github.com/xikhar/spiderbench) by Shikhar. All credit for the original game goes to its author. We use it as the baseline for an enhanced version, made in this fork under the upstream [LICENSE](LICENSE). That means it stays non-commercial and is not redistributed outside GitHub's fork mechanism. The original README follows.

# Spiderbench — a browser web-swinging game written by Claude

A non-commercial fan project and benchmark. It shows the kind of code and assets that **Claude** (Anthropic's AI model, working through Claude Code) can produce for a real-time 3D game running in the browser.

The code, shaders, procedural city, Blender-built models and generated textures were produced by Claude under the direction of a human, who steered the work through feedback and reference images.

## What's in it
- **Traversal:** third-person web-swinging, wall-running, perching, zipping and diving, driven by a custom physics and animation state machine.
- **City:** a procedural Manhattan-style island with an authored street network, including Broadway, Greenwich Village and the Financial District. It has thousands of buildings, rooftops, parks, Times Square, bridges, traffic and pedestrians.
- **Rendering:** a Three.js (WebGL2) pipeline with cascaded shadows, screen-space GI, AO and reflections, bloom, TAA, motion blur, fixed time-of-day presets (including night and rain), and a day/night city.
- **Assets:** character, vehicle and pedestrian models and animation clips built by Blender Python scripts, plus AI-generated textures and ad art. Advertised brands are invented, apart from in-universe Marvel names such as the Daily Bugle and Oscorp.

## Hero animation branch

The 3d-animations-astra branch adds eight Blender-authored hero clips, manual **X / L3** tricks alongside automatic releases, and an animated suit-selection entrance. See [controls, editable sources, motion previews and verification](docs/anim/hero/README.md).

## Run it
Requires Node.js 20.19+ or 22.12+ and a WebGL2-capable browser. A discrete GPU is recommended.

```bash
npm install
npm run dev      # then open http://127.0.0.1:5173
npm run build    # production build in dist/
```

Controls are listed in-game (press **H**). On the dev server, **~** opens a developer menu (on a build, add `?dev` to the URL).

## Disclaimer
This is an unofficial fan project, made only as a technical demonstration. It is not affiliated with, endorsed by or sponsored by Marvel, Disney, Sony or Insomniac Games. Spider-Man and related names, characters and likenesses are trademarks and copyrighted material of their respective owners, and no rights to them are claimed. **This project is not for sale and may not be redistributed or used commercially.** See [LICENSE](LICENSE).

Bundled fonts are under the SIL Open Font License; see `public/assets/ui/fonts/`.
