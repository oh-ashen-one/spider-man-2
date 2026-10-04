# Studio recovery snapshot — 2026-10-04

This backup preserves the sole uncommitted change found after the Studio restart,
plus local-only authored scripts from the Spider-Man Unreal loop. It does not
change the original worktrees, install the scripts, restart the loop, or merge a
change into the integration or main branches.

The parent commit is the verified GitHub tip of night1/perf. The snapshot retains
the observed deletion of unreal/WebHomage/Config/Mac/MacEngine.ini; the previous
26-line file remains in the parent commit. The deletion's intent was not decided.

local-scripts contains unchanged source bytes from sm2-n1/_scratch for the GPU,
city, combat, water, life, traversal, terrain, island, characters, perf, look, and
tricks work streams. These are archival copies, stored non-executable. They may
contain machine-specific paths, obsolete experiments, and unsafe old operating
behavior. They have not been executed, tested, or endorsed as prevention fixes.
The manifest provides relative filenames, byte counts, and SHA-256 checksums.

Excluded: virtual environments/dependencies, generated caches, AppleDouble files,
symlinks, binary assets, media/captures, raw health and runtime logs, terminal data,
authentication material, and unrelated projects. Historical backup-suffix files
and non-source scratch documents are outside this snapshot.

Before this backup, a fresh origin comparison verified all 24 local branch tips:
22 matched exactly; local main and 3d-animations-astra were ancestors of newer
remote tips. Integration Opus-5.5-Loop-Night-1 was already preserved at
7094940146da974955a6daed8b4d9ce3ea16cc26. No existing remote branch is changed.
