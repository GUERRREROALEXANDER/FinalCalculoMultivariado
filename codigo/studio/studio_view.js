// Studio view layer: minimum marker, probe marker, trail tube, gradient arrow,
// the two static traces (b = b* and a = a*), bounding box + far-wall gridlines,
// CSS2D axis ticks and titles, and a hover tooltip on the surface.
//
// Contract (consumed by the page):
//   mountStudio(el, M) -> { name: 'studio', update(state), dispose() }
// state = { a, b, S, centered, trail:[{a,b}], grad:{a2,b2,S2} | undefined }
// Everything is allocated once and updated by mutation; only the trail tube
// geometry is rebuilt (and disposed) on update.
import * as THREE from 'three';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/CSS2DRenderer.js';
import { createStudio } from 'studio/core';

// Palette (fixed by the spec)
const COL_MIN = 0x006a86;
const COL_PROBE = 0x1a1a1a;
const COL_GRAD = 0x257aa2;
const COL_HOLO = 0x3aa6c8;   // trace a = a*
const COL_HAIR = 0xc9dbe2;

const stdMat = color => new THREE.MeshStandardMaterial({ color, roughness: 0.4, metalness: 0 });

// Injected once per document
let styleInjected = false;
function injectStyle() {
  if (styleInjected) return;
  styleInjected = true;
  const st = document.createElement('style');
  st.textContent =
    '.ax3{font:15px "CMU Serif",Georgia,serif;color:#46565e;white-space:nowrap;text-shadow:0 0 3px #fff,0 0 3px #fff}' +
    '.ax3.title{color:#1a1a1a;font-weight:700;font-size:16px}' +
    '.ax3.tag{color:#1a1a1a;font-size:14px;background:rgba(255,255,255,.88);border:1px solid #c9dbe2;border-radius:3px;padding:1px 6px;text-shadow:none}' +
    '.tip3{position:absolute;display:none;background:#fff;border:1px solid #c9dbe2;border-radius:3px;padding:4px 8px;color:#1a1a1a;font-size:14px;pointer-events:none;z-index:4}';
  document.head.appendChild(st);
}

export function mountStudio(el, M) {
  injectStyle();
  el.style.overflow = 'hidden';
  const studio = createStudio(el, M);
  const { THREE: T, scene, camera, controls, surface, renderer, box, floorY, half, toWorld } = studio;

  const sign = v => (v >= 0 ? 1 : -1);

  // ---- 1. minimum marker ----
  const minPos = toWorld(M.astar, M.bstar); minPos.y += 0.03;
  const minMarker = new T.Mesh(new T.SphereGeometry(0.034, 32, 16), stdMat(COL_MIN));
  minMarker.position.copy(minPos);
  scene.add(minMarker);
  const minLabel = new CSS2DObject(makeLabel('mínimo', 'ax3 tag'));
  minLabel.element.style.marginTop = '-22px';
  minLabel.position.copy(minMarker.position);
  scene.add(minLabel);

  // ---- 2. probe marker ----
  const probePos = toWorld(M.astar, M.bstar); probePos.y += 0.035;
  const probeMarker = new T.Mesh(new T.SphereGeometry(0.04, 32, 16), stdMat(COL_PROBE));
  probeMarker.position.copy(probePos);
  scene.add(probeMarker);
  const probeLabelEl = makeLabel('', 'ax3 tag');
  probeLabelEl.style.marginTop = '26px';   // below the marker, so it never collides with the 'mínimo' tag
  const probeLabel = new CSS2DObject(probeLabelEl);
  probeLabel.position.copy(probeMarker.position);
  scene.add(probeLabel);

  function makeLabel(text, cls) {
    const d = document.createElement('div');
    d.className = cls;
    d.textContent = text;
    return d;
  }

  // ---- 3. trail tube (rebuilt on update) ----
  const trailMat = stdMat(COL_PROBE);
  const trailMesh = new T.Mesh(new T.BufferGeometry(), trailMat);
  trailMesh.visible = false;
  scene.add(trailMesh);
  let trailGeom = null;

  // ---- 4. gradient arrow: shaft cylinder + head cone, oriented along +Y ----
  const arrowMat = stdMat(COL_GRAD);
  const shaftGeom = new T.CylinderGeometry(0.011, 0.011, 1, 12, 1, true);
  shaftGeom.translate(0, 0.5, 0);                    // spans y in [0, 1], scaled by shaft.scale.y
  const coneGeom = new T.CylinderGeometry(0, 0.032, 0.11, 16);
  coneGeom.translate(0, 0.055, 0);                   // spans y in [0, 0.11]
  const arrowGroup = new T.Group();
  const shaft = new T.Mesh(shaftGeom, arrowMat);
  const cone = new T.Mesh(coneGeom, arrowMat);
  arrowGroup.add(shaft); arrowGroup.add(cone);
  arrowGroup.visible = false;
  scene.add(arrowGroup);

  // ---- 5. static traces: b = b* (min color) and a = a* (holo color) ----
  function buildTrace(fixed, color) {
    const N = 160;
    const pts = [];
    for (let i = 0; i < N; i++) {
      const u = (i / (N - 1)) * 2 - 1;
      pts.push(fixed.axis === 'a'
        ? toWorld(M.astar + u * studio.ranges.RA, fixed.b)
        : toWorld(fixed.a, M.bstar + u * studio.ranges.RB));
      pts[pts.length - 1].y += 0.012;
    }
    const geom = new T.TubeGeometry(new T.CatmullRomCurve3(pts), 240, 0.0075, 8, false);
    const mesh = new T.Mesh(geom, stdMat(color));
    scene.add(mesh);
  }
  buildTrace({ axis: 'a', b: M.bstar }, COL_MIN);
  buildTrace({ axis: 'b', a: M.astar }, COL_HOLO);

  // ---- 6. bounding box edges + gridlines on the two farthest walls ----
  const H = box.H;
  const boxPts = [];
  const x0 = -half, x1 = half, z0 = -half, z1 = half;
  // bottom rectangle (y = floorY), top rectangle (y = H), 4 vertical edges
  const corners = [[x0, z0], [x1, z0], [x1, z1], [x0, z1]];
  corners.forEach(([x, z], i) => {
    const [xn, zn] = corners[(i + 1) % 4];
    boxPts.push(x, floorY, z, xn, floorY, zn);
    boxPts.push(x, H, z, xn, H, zn);
    boxPts.push(x, floorY, z, x, H, z);
  });
  const boxGeom = new T.BufferGeometry();
  boxGeom.setAttribute('position', new T.Float32BufferAttribute(boxPts, 3));
  scene.add(new T.LineSegments(boxGeom, new T.LineBasicMaterial({ color: COL_HAIR })));

  // one LineSegments per vertical wall with 5 horizontal gridlines at y = H*k/4
  const wallGrids = {};
  const gridY = [0, H / 4, H / 2, (3 * H) / 4, H];
  [['x', -1], ['x', 1], ['z', -1], ['z', 1]].forEach(([ax, s]) => {
    const off = 0.004;
    const pts = [];
    gridY.forEach(y => {
      if (ax === 'x') {
        const xo = s * half + s * off;
        pts.push(xo, y, x0, xo, y, x1);
      } else {
        const zo = s * half + s * off;
        pts.push(x0, y, zo, x1, y, zo);
      }
    });
    const g = new T.BufferGeometry();
    g.setAttribute('position', new T.Float32BufferAttribute(pts, 3));
    const ls = new T.LineSegments(g, new T.LineBasicMaterial({ color: COL_HAIR }));
    ls.visible = false;
    scene.add(ls);
    wallGrids[ax + s] = ls;
  });

  // ---- 7. CSS2D axis ticks and titles ----
  const labelRenderer = new CSS2DRenderer();
  labelRenderer.domElement.style.cssText = 'position:absolute;inset:0;pointer-events:none';
  el.appendChild(labelRenderer.domElement);
  const labelRO = new ResizeObserver(() => {
    labelRenderer.setSize(el.clientWidth || 1, el.clientHeight || 1);
    studio.requestRender();
  });
  labelRO.observe(el);
  labelRenderer.setSize(el.clientWidth || 1, el.clientHeight || 1);

  // 5 ticks along each floor edge nearest the camera, plus edge titles.
  // Tick positions are only re-placed when the near/far choice changes.
  const aTicks = [], bTicks = [], sTicks = [];
  for (let k = -2; k <= 2; k++) aTicks.push(makeAxisTick((M.astar + (studio.ranges.RA * k) / 2).toFixed(1)));
  for (let k = -2; k <= 2; k++) bTicks.push(makeAxisTick((M.bstar + (studio.ranges.RB * k) / 2).toFixed(0)));
  for (let k = 0; k <= 4; k++) sTicks.push(makeAxisTick(((M.smin + (studio.sMax - M.smin) * k / 4) / 1e8).toFixed(2)));
  const titleA = makeAxisLabel('a (ms/°)', 'ax3 title');
  const titleB = makeAxisLabel('b (ms)', 'ax3 title');
  const titleS = makeAxisLabel('S (×10⁸ ms²)', 'ax3 title');

  function makeAxisTick(text) {
    const d = document.createElement('div');
    d.className = 'ax3';
    d.textContent = text;
    const o = new CSS2DObject(d);
    scene.add(o);
    return o;
  }
  function makeAxisLabel(text, cls) {
    const d = document.createElement('div');
    d.className = cls;
    d.textContent = text;
    const o = new CSS2DObject(d);
    scene.add(o);
    return o;
  }

  let tickChoice = '';                // e.g. 'x+z-' — set on the first frame
  const placeTicks = (nx, nz, fx, fz) => {
    const tOff = 0.13, titleOff = 0.32;
    // a-axis ticks: run along x, on the z edge nearest the camera
    aTicks.forEach((o, k) => o.position.set((k - 2) / 2 * half, floorY, nz * (half + tOff)));
    titleA.position.set(0, floorY, nz * (half + titleOff));
    // b-axis ticks: run along z, on the x edge nearest the camera
    bTicks.forEach((o, k) => o.position.set(nx * (half + tOff), floorY, -(k - 2) / 2 * half));
    titleB.position.set(nx * (half + titleOff), floorY, 0);
    // S ticks: on the vertical edge at the floor corner farthest from the camera
    const sx = sign(fx), sz = sign(fz);
    const diag = 0.13 / Math.SQRT2;
    sTicks.forEach((o, k) => o.position.set(fx + sx * diag, (H * k) / 4, fz + sz * diag));
    titleS.position.set(fx + sx * 0.32 * Math.SQRT1_2, H + 0.14, fz + sz * 0.32 * Math.SQRT1_2);
  };

  // ---- 8. hover tooltip ----
  const tip = document.createElement('div');
  tip.className = 'ax3 tip3';
  el.appendChild(tip);

  const raycaster = new T.Raycaster();
  const ndc = new T.Vector2();
  let rayPending = false;

  const hideTip = () => { tip.style.display = 'none'; };

  const onPointerMove = ev => {
    if (rayPending) return;                       // at most one raycast per animation frame
    rayPending = true;
    requestAnimationFrame(() => { rayPending = false; });
    const rect = renderer.domElement.getBoundingClientRect();
    ndc.x = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
    ndc.y = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(ndc, camera);
    const hits = raycaster.intersectObject(surface, false);
    if (hits.length) {
      const { a, b, S } = studio.fromWorld(hits[0].point);
      tip.textContent = 'a = ' + a.toFixed(2) + '  b = ' + b.toFixed(0) + '  S = ' + (S / 1e8).toFixed(3) + ' ×10⁸';
      tip.style.display = 'block';
      tip.style.left = (ev.clientX - rect.left + 14) + 'px';
      tip.style.top = (ev.clientY - rect.top + 14) + 'px';
    } else {
      hideTip();
    }
  };
  const onPointerLeave = hideTip;
  renderer.domElement.addEventListener('pointermove', onPointerMove);
  renderer.domElement.addEventListener('pointerleave', onPointerLeave);
  controls.addEventListener('start', hideTip);
  controls.addEventListener('end', hideTip);

  // ---- per-frame: far-wall gridlines, tick re-pick, label render ----
  const tmpA = new T.Vector3();
  const tmpB = new T.Vector3();
  const UP = new T.Vector3(0, 1, 0);
  const dir = new T.Vector3();

  studio.onFrame(() => {
    // gridlines: show only the two walls farthest from the camera
    const fx = camera.position.x >= 0 ? -1 : 1;   // far wall in x
    const fz = camera.position.z >= 0 ? -1 : 1;   // far wall in z
    wallGrids['x1'].visible = fx === 1; wallGrids['x-1'].visible = fx === -1;
    wallGrids['z1'].visible = fz === 1; wallGrids['z-1'].visible = fz === -1;

    // ticks: re-place only when the near/far choice changes
    const choice = fx + 'x' + fz + 'z';
    if (choice !== tickChoice) {
      tickChoice = choice;
      placeTicks(-fx, -fz, fx * half, fz * half);   // near edges are opposite to the far walls
    }

    labelRenderer.render(scene, camera);
  });

  // ---- update on every published state ----
  function update(state) {
    // probe marker and label (toWorld(a, b) evaluates the surface height)
    tmpA.copy(toWorld(state.a, state.b));
    tmpA.y += 0.035;
    probeMarker.position.copy(tmpA);
    probeLabel.position.copy(tmpA);
    probeLabelEl.textContent = 'a = ' + state.a.toFixed(2) + ' · b = ' + state.b.toFixed(0);

    // trail tube (rebuilt; old geometry disposed)
    const trail = state.trail;
    if (trail && trail.length >= 2) {
      let pts = trail;
      if (pts.length > 300) {                     // subsample, always keep the last point
        const step = Math.ceil(pts.length / 300);
        const sub = [];
        for (let i = 0; i < pts.length; i += step) sub.push(pts[i]);
        if (sub[sub.length - 1] !== pts[pts.length - 1]) sub.push(pts[pts.length - 1]);
        pts = sub;
      }
      const curve = new T.CatmullRomCurve3(pts.map(p => {
        const w = toWorld(p.a, p.b);
        w.y += 0.014;
        return w;
      }));
      if (trailGeom) trailGeom.dispose();
      trailGeom = new T.TubeGeometry(curve, Math.min(pts.length * 4, 360), 0.011, 6, false);
      trailMesh.geometry = trailGeom;
      trailMesh.visible = true;
    } else {
      trailMesh.visible = false;
    }

    // gradient arrow
    const grad = state.grad;
    if (grad) {
      tmpA.copy(probeMarker.position);            // start (already lifted +0.035)
      tmpB.copy(toWorld(grad.a2, grad.b2, grad.S2));
      tmpB.y += 0.035;
      dir.subVectors(tmpB, tmpA);
      const len = dir.length();
      if (len >= 0.05) {
        arrowGroup.position.copy(tmpA);
        arrowGroup.quaternion.setFromUnitVectors(UP, dir.divideScalar(len));
        const shaftLen = Math.max(len - 0.11, 0);
        shaft.scale.y = shaftLen;
        cone.position.y = shaftLen;
        arrowGroup.visible = true;
      } else {
        arrowGroup.visible = false;
      }
    } else {
      arrowGroup.visible = false;
    }

    studio.requestRender();
  }

  // ---- 10. dispose ----
  function dispose() {
    renderer.domElement.removeEventListener('pointermove', onPointerMove);
    renderer.domElement.removeEventListener('pointerleave', onPointerLeave);
    controls.removeEventListener('start', hideTip);
    controls.removeEventListener('end', hideTip);
    labelRO.disconnect();
    labelRenderer.domElement.remove();
    if (trailGeom) trailGeom.dispose();
    studio.dispose();
  }

  return { name: 'studio', update, dispose };
}
