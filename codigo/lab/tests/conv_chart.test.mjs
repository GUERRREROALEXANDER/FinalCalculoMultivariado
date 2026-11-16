// Judge for codigo/lab/conv_chart.js (UMD: `module.exports` under node, `window.NCconv` in the page).
//
// Contract:
//   hist entry = {step: integer, dS: S - Smin in ms^2}
//   NCconv.FLOOR = -8, NCconv.CEIL = 6
//   yOf(dS, smin)        -> log10(dS/smin) clamped to [FLOOR, CEIL]; dS <= 0 or NaN -> FLOOR; +Infinity -> CEIL
//   scale(hist, smin)    -> {xMax, yMin, yMax, pts:[{x, y}]}
//        xMax = max(1, largest step); yMin = FLOOR; yMax = max(0, ceil(largest y)); pts in hist order
//   draw(ctx, W, H, hist, {smin, tolRel}) -> {plotted}   draws axes + labels (Spanish), a dashed horizontal
//        line at log10(tolRel) (the convergence tolerance), then the polyline and a dot at the last point.
//        `plotted` = number of hist points drawn. Must not throw on an empty hist, and must never pass a
//        non-finite or out-of-canvas coordinate to moveTo/lineTo/arc/fillText. Restores a solid line dash.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const C = require('../conv_chart.js');
const M = JSON.parse(fs.readFileSync(new URL('./meta.json', import.meta.url), 'utf8'));
const smin = M.smin;

function fakeCtx() {
  const calls = [];
  return new Proxy({}, {
    get(_, k) {
      if (k === 'calls') return calls;
      if (k === 'measureText') return () => ({ width: 10 });
      return (...args) => { calls.push([k, args]); };
    },
    set() { return true; },
  });
}

test('constants', () => {
  assert.equal(C.FLOOR, -8);
  assert.equal(C.CEIL, 6);
});

test('yOf: log mapping, floor and ceiling', () => {
  assert.equal(C.yOf(smin * 100, smin), 2);
  assert.ok(Math.abs(C.yOf(smin * 0.1, smin) + 1) < 1e-12);
  assert.equal(C.yOf(smin * 1e-9, smin), -8);
  assert.equal(C.yOf(0, smin), -8);
  assert.equal(C.yOf(-5, smin), -8);
  assert.equal(C.yOf(NaN, smin), -8);
  assert.equal(C.yOf(Infinity, smin), 6);
  assert.equal(C.yOf(smin * 1e12, smin), 6);
});

test('scale autoscales x to the last step and y to the largest value', () => {
  const hist = [{ step: 0, dS: smin * 10 }, { step: 5, dS: smin * 0.1 }, { step: 120, dS: smin * 1e-3 }];
  const s = C.scale(hist, smin);
  assert.equal(s.xMax, 120);
  assert.equal(s.yMin, -8);
  assert.equal(s.yMax, 1);
  assert.equal(s.pts.length, 3);
  assert.equal(s.pts[0].x, 0);
  assert.ok(Math.abs(s.pts[1].y + 1) < 1e-12);
});

test('scale on an empty history and on a diverging one', () => {
  const e = C.scale([], smin);
  assert.deepEqual([e.xMax, e.yMin, e.yMax, e.pts.length], [1, -8, 0, 0]);
  const d = C.scale([{ step: 0, dS: smin }, { step: 3, dS: smin * 1e3 }], smin);
  assert.equal(d.yMax, 3);
});

test('draw: empty history draws no data and does not throw', () => {
  const ctx = fakeCtx();
  const r = C.draw(ctx, 440, 170, [], { smin, tolRel: 1e-6 });
  assert.equal(r.plotted, 0);
  assert.ok(ctx.calls.some(([k]) => k === 'stroke'), 'axes should still be stroked');
});

test('draw: reports the number of plotted points and draws a dot at the last one', () => {
  const ctx = fakeCtx();
  const hist = [{ step: 0, dS: smin }, { step: 10, dS: smin * 0.01 }, { step: 20, dS: smin * 1e-4 }];
  const r = C.draw(ctx, 440, 170, hist, { smin, tolRel: 1e-6 });
  assert.equal(r.plotted, 3);
  assert.ok(ctx.calls.some(([k]) => k === 'arc'), 'a dot marks the current point');
});

test('draw: tolerance line is dashed and the dash is restored to solid', () => {
  const ctx = fakeCtx();
  C.draw(ctx, 440, 170, [{ step: 0, dS: smin }], { smin, tolRel: 1e-6 });
  const dashes = ctx.calls.filter(([k]) => k === 'setLineDash').map(([, a]) => a[0]);
  assert.ok(dashes.some(d => d.length > 0), 'a dashed segment is drawn');
  assert.deepEqual(dashes[dashes.length - 1], []);
});

test('draw: every coordinate is finite and inside the canvas, even for Infinity/NaN/0', () => {
  const ctx = fakeCtx();
  const hist = [{ step: 0, dS: smin }, { step: 2, dS: Infinity }, { step: 3, dS: NaN }, { step: 4, dS: 0 }, { step: 5, dS: smin * 1e-12 }];
  C.draw(ctx, 440, 170, hist, { smin, tolRel: 1e-6 });
  for (const [k, args] of ctx.calls) {
    if (!['moveTo', 'lineTo', 'arc', 'fillText'].includes(k)) continue;
    const [x, y] = k === 'fillText' ? args.slice(1, 3) : args.slice(0, 2);
    assert.ok(Number.isFinite(x) && Number.isFinite(y), `${k} got (${x}, ${y})`);
    assert.ok(x >= 0 && x <= 440 && y >= 0 && y <= 170, `${k} got (${x}, ${y}) outside the canvas`);
  }
});
