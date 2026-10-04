#!/bin/bash
# one hold: probe c, then the reel windows (hero fill raised for the dark facades)
TAG=c PROBE=1 RENDER=1 RENDER_ARGS="-WHHeroFill=16000,36000" /Users/midir/sm2-n1/tricks/tools/tricks/hold_r02.sh
# (appended 19:4x: the windows above were stopped for a code change; rebuild + probe d + windows in the same hold)
HOLD_T0=1791070590 TAG=d PROBE=1 RENDER=1 RENDER_ARGS="-WHHeroFill=16000,36000" /Users/midir/sm2-n1/tricks/tools/tricks/hold_r02.sh
# (appended 19:5x: window 0 stopped again for the G3 / L fix: rebuild + probe e only, no time left for a window)
TAG=e PROBE=1 RENDER=0 /Users/midir/sm2-n1/tricks/tools/tricks/hold_r02.sh
HOLD_T0=1791070590 TAG=e PROBE=0 RENDER=1 RENDER_ARGS="-WHHeroFill=16000,36000" /Users/midir/sm2-n1/tricks/tools/tricks/hold_r02.sh
# (appended 19:5x: stopped for the overdue-pose / kick-out fix: rebuild + probe f)
TAG=f PROBE=1 RENDER=0 /Users/midir/sm2-n1/tricks/tools/tricks/hold_r02.sh
