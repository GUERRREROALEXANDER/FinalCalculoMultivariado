// Studio view core: a lit, physically shaded 3D model of S(a, b).
//
// Contract (read by studio_view.js and by the template):
//   createStudio(el, M) -> {
//     THREE, scene, camera, renderer, controls, surface, box:{W,D,H}, floorY, half, ranges:{RA,RB}, sMax (S at box top, ms^2),
//     toWorld(a, b, S) -> THREE.Vector3   (S in ms^2, NOT scaled by 1e8)
//     fromWorld(v)     -> {a, b, S}
//     requestRender(), onFrame(fn)        (fn runs before every render)
//     dispose()
//   }
//
// World axes: x = a (slope), z = -b (intercept, so that a x b = up), y = S (height).
// The box is 2.2 x 2.2 x 1.3, the same proportions as the Plotly view (1.1 : 1.1 : 0.65).
// The shading is computed per pixel from the exact quadratic form, so the color bands
// and isolines match the 2D level map exactly and have no mesh kink at the minimum.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/RoomEnvironment.js';

const RA = 3.2, RB = 420;          // half-ranges of the lab (same as the Plotly grid and the map)
const HALF = 1.1, BOX_H = 1.3;     // half width of the box and its height, in world units
const BANDS = 16, T_SCALE = 1.1;   // same banding and sqrt scale as the 2D map
const GRID = 180;                  // vertices per side of the surface mesh
const SKIRT = 0.14;                // how far the slab walls reach below the minimum

export function createStudio(el, M) {
  const dS = (da, db) => M.sxx * da * da + 2 * M.sx * da * db + M.n * db * db;   // S - Smin, exact
  const sAt = (a, b) => M.smin + dS(a - M.astar, b - M.bstar);
  const sMax = Math.max(sAt(M.astar - RA, M.bstar - RB), sAt(M.astar + RA, M.bstar - RB),
                        sAt(M.astar - RA, M.bstar + RB), sAt(M.astar + RA, M.bstar + RB));
  const yOfS = S => (S - M.smin) / (sMax - M.smin) * BOX_H;
  const toWorld = (a, b, S) => new THREE.Vector3(
    (a - M.astar) / RA * HALF,
    yOfS(S === undefined ? sAt(a, b) : S),
    -(b - M.bstar) / RB * HALF);
  const fromWorld = v => {
    const a = M.astar + v.x / HALF * RA, b = M.bstar - v.z / HALF * RB;
    return { a, b, S: sAt(a, b) };
  };

  // ---- renderer: transparent canvas so the page background shows through ----
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  // Khronos PBR Neutral keeps the colormap faithful; ACES would desaturate the ramp.
  renderer.toneMapping = THREE.NeutralToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.domElement.style.cssText = 'display:block;width:100%;height:100%;touch-action:none';
  el.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envTex = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;   // soft studio: softbox + strips
  scene.environment = envTex;
  scene.environmentIntensity = 0.95;

  // one soft key light on top of the studio environment, to give the slope a direction
  const key = new THREE.DirectionalLight(0xffffff, 1.1);
  key.position.set(-2.2, 3.6, 1.6);       // from the north-west, high
  scene.add(key);

  const camera = new THREE.PerspectiveCamera(28, 1, 0.1, 60);
  camera.position.set(5.6, 4.2, 3.0);
  const target = new THREE.Vector3(0, 0.5, 0);
  camera.lookAt(target);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.copy(target);
  controls.enableDamping = true;
  controls.dampingFactor = 0.09;
  controls.enablePan = false;
  controls.minDistance = 4.0;
  controls.maxDistance = 14;
  controls.minPolarAngle = 0.12;
  controls.maxPolarAngle = 1.46;          // never goes under the slab
  controls.rotateSpeed = 0.8;
  controls.update();

  // ---- the surface ----
  const ramp = (M.ramp || [[255,238,194],[251,207,128],[242,154,76],[217,87,58],[156,44,74],[79,24,64]])
    .map(c => new THREE.Color().setRGB(c[0] / 255, c[1] / 255, c[2] / 255, THREE.SRGBColorSpace));
  const lineCol = new THREE.Color().setRGB(0.27, 0.10, 0.16, THREE.SRGBColorSpace);

  const uniforms = {
    uQ: { value: new THREE.Vector3(M.sxx, M.sx, M.n) },
    uSmin: { value: M.smin },
    uRamp: { value: ramp.map(c => new THREE.Vector3(c.r, c.g, c.b)) },
    uLine: { value: new THREE.Vector3(lineCol.r, lineCol.g, lineCol.b) },
    uRange: { value: new THREE.Vector2(RA / HALF, RB / HALF) },
  };

  const mat = new THREE.MeshPhysicalMaterial({
    color: 0xffffff, roughness: 0.52, metalness: 0.0,
    clearcoat: 0.32, clearcoatRoughness: 0.38,
    envMapIntensity: 1.0,
  });
  mat.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, uniforms);
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nuniform vec2 uRange;\nvarying vec2 vDab;')
      .replace('#include <begin_vertex>', '#include <begin_vertex>\nvDab = vec2(position.x, -position.z) * uRange;');
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', `#include <common>
uniform vec3 uQ; uniform float uSmin; uniform vec3 uRamp[${ramp.length}]; uniform vec3 uLine;
varying vec2 vDab;
vec3 rampAt(float t) {
  float x = clamp(t, 0.0, 1.0) * ${(ramp.length - 1).toFixed(1)};
  int i = int(min(floor(x), ${(ramp.length - 2).toFixed(1)}));
  return mix(uRamp[i], uRamp[i + 1], x - float(i));
}`)
      .replace('#include <color_fragment>', `#include <color_fragment>
{
  float dS = uQ.x * vDab.x * vDab.x + 2.0 * uQ.y * vDab.x * vDab.y + uQ.z * vDab.y * vDab.y;
  float t = sqrt(max(dS, 0.0) / uSmin) / ${T_SCALE.toFixed(2)};
  vec3 base = rampAt(t);
  float tb = t * ${BANDS.toFixed(1)};
  float fw = fwidth(tb);
  float d = min(fract(tb), 1.0 - fract(tb)) / max(fw, 1e-5);
  float ln = (1.0 - smoothstep(0.35, 1.35, d)) * (1.0 - smoothstep(0.45, 0.95, fw));
  vec3 lc = mix(uLine, vec3(1.0), smoothstep(0.5, 0.72, t));   // dark line on light bands, light line on dark bands
  diffuseColor.rgb = mix(base, lc, ln * mix(0.5, 0.2, smoothstep(0.5, 0.72, t)));
}`);
  };
  mat.customProgramCacheKey = () => 'nc-surface-v1';

  const g = new THREE.BufferGeometry();
  const pos = new Float32Array(GRID * GRID * 3), idx = new Uint32Array((GRID - 1) * (GRID - 1) * 6);
  for (let j = 0, k = 0; j < GRID; j++) for (let i = 0; i < GRID; i++, k += 3) {
    const a = M.astar + (i / (GRID - 1) * 2 - 1) * RA, b = M.bstar + (j / (GRID - 1) * 2 - 1) * RB;
    const w = toWorld(a, b);
    pos[k] = w.x; pos[k + 1] = w.y; pos[k + 2] = w.z;
  }
  for (let j = 0, k = 0; j < GRID - 1; j++) for (let i = 0; i < GRID - 1; i++, k += 6) {
    const p = j * GRID + i, q = p + GRID;
    // wind so that the normals point up (+y): b grows toward -z
    idx[k] = p; idx[k + 1] = p + 1; idx[k + 2] = q; idx[k + 3] = p + 1; idx[k + 4] = q + 1; idx[k + 5] = q;
  }
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  g.computeVertexNormals();
  if (g.attributes.normal.getY(0) < 0) {            // safety: flip the winding if it came out inverted
    for (let k = 0; k < idx.length; k += 3) { const t = idx[k + 1]; idx[k + 1] = idx[k + 2]; idx[k + 2] = t; }
    g.index.needsUpdate = true; g.computeVertexNormals();
  }
  const surface = new THREE.Mesh(g, mat);
  scene.add(surface);

  // ---- slab walls: the cross-section of the surface, like a physical model ----
  const wallPos = [], wallIdx = [];
  const edge = (pts) => {                            // pts: world points along one edge of the surface
    const base = wallPos.length / 3;
    pts.forEach(p => { wallPos.push(p.x, p.y, p.z, p.x, -SKIRT, p.z); });
    for (let i = 0; i < pts.length - 1; i++) {
      const t0 = base + i * 2;
      wallIdx.push(t0, t0 + 1, t0 + 2, t0 + 1, t0 + 3, t0 + 2);
    }
  };
  const line = (fn) => Array.from({ length: GRID }, (_, i) => fn(i / (GRID - 1) * 2 - 1));
  edge(line(u => toWorld(M.astar + u * RA, M.bstar - RB)));   // front (b min)  -> +z
  edge(line(u => toWorld(M.astar - u * RA, M.bstar + RB)));   // back
  edge(line(u => toWorld(M.astar - RA, M.bstar - u * RB)));   // left
  edge(line(u => toWorld(M.astar + RA, M.bstar + u * RB)));   // right
  const wg = new THREE.BufferGeometry();
  wg.setAttribute('position', new THREE.Float32BufferAttribute(wallPos, 3));
  wg.setIndex(wallIdx);
  wg.computeVertexNormals();
  // emissive lifts the faces that look away from the key light, so all four walls read as one material
  const wallMat = new THREE.MeshStandardMaterial({ color: 0xe4dcd4, emissive: 0xb9aea4, emissiveIntensity: 0.4, roughness: 0.9, metalness: 0, side: THREE.DoubleSide });
  scene.add(new THREE.Mesh(wg, wallMat));

  // ---- soft contact shadow on the floor ----
  const sh = document.createElement('canvas'); sh.width = sh.height = 256;
  const sc = sh.getContext('2d'), rg = sc.createRadialGradient(128, 128, 20, 128, 128, 128);
  rg.addColorStop(0, 'rgba(48,32,32,.30)'); rg.addColorStop(0.55, 'rgba(48,32,32,.13)'); rg.addColorStop(1, 'rgba(48,32,32,0)');
  sc.fillStyle = rg; sc.fillRect(0, 0, 256, 256);
  const shadow = new THREE.Mesh(new THREE.PlaneGeometry(4.3, 4.3),
    new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(sh), transparent: true, depthWrite: false, toneMapped: false }));
  shadow.rotation.x = -Math.PI / 2; shadow.position.y = -SKIRT - 0.004;
  scene.add(shadow);

  // ---- render on demand ----
  let needs = true, raf = 0, disposed = false;
  const frameFns = [];
  const requestRender = () => { needs = true; };
  const onFrame = fn => frameFns.push(fn);
  controls.addEventListener('change', requestRender);
  const loop = () => {
    if (disposed) return;
    const moved = controls.update();                // true while the camera is moving (incl. damping)
    if (moved || needs) { needs = false; frameFns.forEach(f => f()); renderer.render(scene, camera); }
    raf = requestAnimationFrame(loop);
  };
  const resize = () => {
    const w = el.clientWidth || 1, h = el.clientHeight || 1;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.fov = w / h < 1.15 ? 38 : 28;            // a little wider on narrow panels
    camera.updateProjectionMatrix();
    requestRender();
  };
  const ro = new ResizeObserver(resize); ro.observe(el);
  resize(); loop();

  return {
    THREE, scene, camera, renderer, controls, surface, box: { W: 2 * HALF, D: 2 * HALF, H: BOX_H },
    floorY: -SKIRT, ranges: { RA, RB }, half: HALF, sMax,
    toWorld, fromWorld, requestRender, onFrame,
    dispose() { disposed = true; cancelAnimationFrame(raf); ro.disconnect(); renderer.dispose(); },
  };
}
