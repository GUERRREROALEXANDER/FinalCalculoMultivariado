// Judge for codigo/lab/descent.js (UMD: `module.exports` under node, `window.NCdescent` in the page).
//
// Contract:
//   NCdescent.RA = 3.2, NCdescent.RB = 420                    half-ranges of the lab box
//   etaCrit(M, method, centered)    -> number   largest stable step size
//   defaultK(M, method, centered)   -> number   default k = eta / etaCrit (reproduces the legacy step)
//   step(M, cur, method, centered, eta) -> {a, b}   NEW object, never mutates `cur`
//   isConverged(M, cur)             -> boolean  |a-a*| < 0.004 && |b-b*| < 0.8
//   outOfBox(M, cur, centered)      -> boolean  |a-a*| > RA || |v-v*| > RB, with v = centered ? b + a*xbar : b
//   run(M, {method, centered, k, maxSteps, start?}) -> {steps, status, cur}
//        status: 'converged' | 'diverged' | 'maxed'. A step that would leave the box is NOT applied
//        (status 'diverged', `steps` counts only applied steps). start defaults to {a: a*+2.2, b: b*-260}.
//   method is 'pure' (plain -grad S) or 'scaled' (-grad S scaled by the diagonal of H).
//
// Legacy behaviour that must be preserved (see git history of simulador_template.html):
//   pure:              a -= ga/lam2,  b -= gb/lam2                   (lam2 = largest eigenvalue of H)
//   scaled, centered:  v = v - 0.15*gb/(2n);  a -= 0.15*(ga - xbar*gb)/(2*sxxC);  b = v - a*xbar
//   scaled, plain:     a -= 0.15*ga/(2sxx);  b -= 0.15*gb/(2n)
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const D = require('../descent.js');
const M = JSON.parse(fs.readFileSync(new URL('./meta.json', import.meta.url), 'utf8'));

const grad = (a, b) => [2 * M.sxx * a + 2 * M.sx * b - 2 * M.sxy, 2 * M.sx * a + 2 * M.n * b - 2 * M.sy];
const S = (a, b) => M.syy - 2 * a * M.sxy - 2 * b * M.sy + a * a * M.sxx + 2 * a * b * M.sx + M.n * b * b;
const tr = 2 * M.sxx + 2 * M.n, det = 4 * M.sxx * M.n - 4 * M.sx * M.sx;
const lam2 = tr / 2 + Math.sqrt(tr * tr / 4 - det);
const rho = M.sx / Math.sqrt(M.sxx * M.n);
const sxxC = M.sxx - M.n * M.xbar * M.xbar;
const close = (x, y, tol = 1e-9) => assert.ok(Math.abs(x - y) <= tol * (1 + Math.abs(y)), `${x} vs ${y}`);

function legacyStep(method, centered, cur) {
  const [ga, gb] = grad(cur.a, cur.b);
  if (method === 'pure') return { a: cur.a - ga / lam2, b: cur.b - gb / lam2 };
  if (centered) {
    const v = cur.b + cur.a * M.xbar - 0.15 * gb / (2 * M.n);
    const a = cur.a - 0.15 * (ga - M.xbar * gb) / (2 * sxxC);
    return { a, b: v - a * M.xbar };
  }
  return { a: cur.a - 0.15 * ga / (2 * M.sxx), b: cur.b - 0.15 * gb / (2 * M.n) };
}

const COMBOS = [['pure', false], ['scaled', false], ['scaled', true]];

test('box constants', () => {
  assert.equal(D.RA, 3.2);
  assert.equal(D.RB, 420);
});

test('etaCrit matches the exact iteration matrix', () => {
  close(D.etaCrit(M, 'pure', false), 2 / lam2, 1e-12);
  close(D.etaCrit(M, 'scaled', false), 2 / (1 + rho), 1e-12);
  close(D.etaCrit(M, 'scaled', true), 2, 1e-12);
});

test('pure descent ignores centering (as the legacy code did)', () => {
  close(D.etaCrit(M, 'pure', true), 2 / lam2, 1e-12);
});

test('defaultK reproduces the legacy step size', () => {
  close(D.defaultK(M, 'pure', false), 0.5, 1e-12);
  close(D.defaultK(M, 'scaled', false) * D.etaCrit(M, 'scaled', false), 0.15, 1e-12);
  close(D.defaultK(M, 'scaled', true) * D.etaCrit(M, 'scaled', true), 0.15, 1e-12);
});

test('step with the default k equals the legacy step', () => {
  const starts = [{ a: M.astar + 2.2, b: M.bstar - 260 }, { a: M.astar - 1.5, b: M.bstar + 300 }, { a: M.astar + 0.3, b: M.bstar - 10 }];
  for (const [method, centered] of COMBOS) {
    const eta = D.defaultK(M, method, centered) * D.etaCrit(M, method, centered);
    for (const s of starts) {
      const got = D.step(M, s, method, centered, eta), want = legacyStep(method, centered, s);
      close(got.a, want.a); close(got.b, want.b);
    }
  }
});

test('step returns a new object and does not mutate its input', () => {
  const s = { a: 1, b: 2 }, out = D.step(M, s, 'scaled', false, 0.1);
  assert.deepEqual(s, { a: 1, b: 2 });
  assert.notEqual(out, s);
});

test('isConverged thresholds', () => {
  assert.equal(D.isConverged(M, { a: M.astar + 0.003, b: M.bstar + 0.7 }), true);
  assert.equal(D.isConverged(M, { a: M.astar + 0.005, b: M.bstar }), false);
  assert.equal(D.isConverged(M, { a: M.astar, b: M.bstar + 0.9 }), false);
});

test('outOfBox, plain and centered', () => {
  assert.equal(D.outOfBox(M, { a: M.astar + 3.3, b: M.bstar }, false), true);
  assert.equal(D.outOfBox(M, { a: M.astar + 3.1, b: M.bstar + 419 }, false), false);
  assert.equal(D.outOfBox(M, { a: M.astar, b: M.bstar - 421 }, false), true);
  const p = { a: M.astar + 3.1, b: M.bstar + 200 };      // v offset = 200 + 3.1*90 = 479 > 420 only when centered
  assert.equal(D.outOfBox(M, p, false), false);
  assert.equal(D.outOfBox(M, p, true), true);
});

test('k = 0.95 converges for the scaled modes (measured: 34 and 60 steps)', () => {
  const u = D.run(M, { method: 'scaled', centered: false, k: 0.95, maxSteps: 5000 });
  assert.equal(u.status, 'converged'); assert.ok(u.steps <= 60, `plain took ${u.steps}`);
  const c = D.run(M, { method: 'scaled', centered: true, k: 0.95, maxSteps: 5000 });
  assert.equal(c.status, 'converged'); assert.ok(c.steps <= 100, `centered took ${c.steps}`);
});

test('k = 0.95 pure stays stable and lowers S (it just crawls)', () => {
  const start = { a: M.astar + 2.2, b: M.bstar - 260 };
  const r = D.run(M, { method: 'pure', centered: false, k: 0.95, maxSteps: 2000 });
  assert.equal(r.status, 'maxed');
  assert.ok(S(r.cur.a, r.cur.b) < S(start.a, start.b));
});

test('k = 1.05 diverges in every mode (measured: 20, 37 and 4 steps)', () => {
  const p = D.run(M, { method: 'pure', centered: false, k: 1.05, maxSteps: 5000 });
  assert.equal(p.status, 'diverged'); assert.ok(p.steps <= 50, `pure ${p.steps}`);
  const u = D.run(M, { method: 'scaled', centered: false, k: 1.05, maxSteps: 5000 });
  assert.equal(u.status, 'diverged'); assert.ok(u.steps <= 80, `plain ${u.steps}`);
  const c = D.run(M, { method: 'scaled', centered: true, k: 1.05, maxSteps: 5000 });
  assert.equal(c.status, 'diverged'); assert.ok(c.steps <= 10, `centered ${c.steps}`);
});

test('a diverging run never leaves a point outside the box', () => {
  for (const [method, centered] of COMBOS) {
    const r = D.run(M, { method, centered, k: 2.2, maxSteps: 5000 });
    assert.equal(r.status, 'diverged');
    assert.equal(D.outOfBox(M, r.cur, centered), false);
  }
});

test('default k converges like the legacy loop (measured: 250 and 39 steps)', () => {
  const u = D.run(M, { method: 'scaled', centered: false, k: D.defaultK(M, 'scaled', false), maxSteps: 5000 });
  assert.equal(u.status, 'converged'); assert.ok(u.steps >= 200 && u.steps <= 300, `plain ${u.steps}`);
  const c = D.run(M, { method: 'scaled', centered: true, k: D.defaultK(M, 'scaled', true), maxSteps: 5000 });
  assert.equal(c.status, 'converged'); assert.ok(c.steps >= 30 && c.steps <= 50, `centered ${c.steps}`);
});
