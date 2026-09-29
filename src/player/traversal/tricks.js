// Authored Action lengths; the clip manifest test guards drift from Blender.
export const TRICK_DURATION = { layout: 1.3, corkscrew: 1.1, tuckFlip: 0.98, scissor: 1.1 };

// Manual intent is deterministic; automatic releases retain trajectory-based variety.
export function manualTrick(move, sequence = 0) {
  if (Math.abs(move.x) > 0.35 && Math.abs(move.x) > Math.abs(move.y) * 0.8)
    return { name: 'corkscrew', side: Math.sign(move.x) };
  if (move.y < -0.35) return { name: 'layout', side: -1 };
  if (move.y > 0.35) return { name: 'tuckFlip', side: 1 };
  return { name: sequence % 2 ? 'scissor' : 'layout', side: 1 };
}

export function hasTrickRoom(height, verticalSpeed, duration, gravity = 25) {
  if (!Number.isFinite(height) || height < 2.5) return false;
  const airtime = (verticalSpeed + Math.sqrt(verticalSpeed ** 2 + 2 * gravity * height)) / gravity;
  return airtime > duration + 0.16;
}
