import * as THREE from 'three';

// Load additive Blender-authored clips without rewriting the original mesh, skeleton or 79 clips.
export async function loadHeroClips(root) {
  try {
    const response = await fetch('/assets/animations/hero-acrobatics.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    if (!Array.isArray(data.clips) || data.clips.length < 8) throw new Error('Incomplete hero animation library');
    const names = new Set(); root.traverse(o => names.add(o.name));
    const clips = data.clips.map(c => THREE.AnimationClip.parse(c));
    if (new Set(clips.map(c => c.uuid)).size !== clips.length || clips.some(c => !c.uuid)) throw new Error('Missing or duplicate clip identity');
    for (const clip of clips) {
      if (!(clip.duration > 0) || !clip.name.startsWith('hero')) throw new Error('Invalid authored clip');
      for (const track of clip.tracks) {
        const node = THREE.PropertyBinding.parseTrackName(track.name).nodeName;
        if (!names.has(node)) throw new Error(`Missing hero joint: ${node}`);
        if (!track.validate()) throw new Error(`Invalid animation track: ${track.name}`);
      }
    }
    console.info('[hero-animation] loaded', clips.map(c => c.name).join(', '));
    return clips;
  } catch (error) {
    console.warn('[hero-animation] authored library unavailable; retaining original animation fallback', error);
    return [];
  }
}
