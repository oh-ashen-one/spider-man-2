import * as THREE from 'three';

// A private mixer and saved transforms keep the showcase completely outside traversal time.
export function createHeroPreview(rig, feet, yaw) {
  const bones = [];
  rig.model.traverse(o => { if (o.isBone) bones.push(o); });
  const saved = bones.map(b => [b, b.position.clone(), b.quaternion.clone(), b.scale.clone()]);
  const root = { p: rig.object.position.clone(), q: rig.object.quaternion.clone(), s: rig.object.scale.clone(), visible: rig.object.visible };
  const mixer = new THREE.AnimationMixer(rig.model);
  const entrance = rig.allClips.find(c => c.name === 'heroSuitEnter');
  const idle = rig.allClips.find(c => c.name === 'heroShowcaseIdle') || rig.allClips.find(c => c.name === 'idle');
  const world = new THREE.Matrix4().compose(feet.clone(), new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), yaw), new THREE.Vector3(1, 1, 1));
  let time = 0, current = null, disposed = false;
  const place = () => {
    rig.object.parent?.updateMatrixWorld(true);
    const local = rig.object.parent ? rig.object.parent.matrixWorld.clone().invert().multiply(world) : world;
    local.decompose(rig.object.position, rig.object.quaternion, rig.object.scale);
  };
  const api = {
    get time() { return time; },
    get duration() { return entrance?.duration || 0; },
    restart() { time = 0; current = null; mixer.stopAllAction(); api.update(0); },
    update(dt) {
      if (disposed) return;
      time += Math.max(0, dt);
      const entering = entrance && time < entrance.duration;
      const clip = entering ? entrance : idle;
      if (clip) {
        if (clip !== current) { mixer.stopAllAction(); mixer.clipAction(clip).play(); current = clip; }
        mixer.setTime(entering ? time : Math.max(0, time - (entrance?.duration || 0)));
      }
      place();
      rig._ranThisFrame = true;
      rig.object.visible = true;
      rig.object.updateMatrixWorld(true);
    },
    dispose() {
      if (disposed) return;
      disposed = true;
      mixer.stopAllAction(); mixer.uncacheRoot(rig.model);
      for (const [b, p, q, s] of saved) { b.position.copy(p); b.quaternion.copy(q); b.scale.copy(s); }
      rig.object.position.copy(root.p); rig.object.quaternion.copy(root.q); rig.object.scale.copy(root.s); rig.object.visible = root.visible;
      rig.object.updateMatrixWorld(true);
    },
  };
  api.update(0);
  return api;
}
