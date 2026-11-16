/* Gradient descent for S(a, b) with an adjustable step eta = k * etaCrit.
   UMD: `module.exports` under node, `window.NCdescent` in the page. No DOM, no dependencies. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.NCdescent = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var RA = 3.2, RB = 420;                       // half-ranges of the lab box

  function lam2(M) {                            // largest eigenvalue of H = [[2sxx, 2sx], [2sx, 2n]]
    var tr = 2 * M.sxx + 2 * M.n, det = 4 * M.sxx * M.n - 4 * M.sx * M.sx;
    return tr / 2 + Math.sqrt(tr * tr / 4 - det);
  }
  function rho(M) {                             // correlation of the two gradient components
    return M.sx / Math.sqrt(M.sxx * M.n);
  }
  function sxxC(M) {                            // sum of squared centered x
    return M.sxx - M.n * M.xbar * M.xbar;
  }
  function vStar(M, centered) {
    return centered ? M.bstar + M.astar * M.xbar : M.bstar;
  }

  function grad(M, cur) {
    return [
      2 * M.sxx * cur.a + 2 * M.sx * cur.b - 2 * M.sxy,
      2 * M.sx * cur.a + 2 * M.n * cur.b - 2 * M.sy
    ];
  }

  function etaCrit(M, method, centered) {
    if (method === 'pure') return 2 / lam2(M);          // eigenvalues of I - eta*H
    if (centered) return 2;                             // H is diagonal in (a, v): I - eta*I
    return 2 / (1 + rho(M));                            // I - eta*D^-1*H, |1 - eta(1 +- rho)| < 1
  }

  function defaultK(M, method, centered) {
    if (method === 'pure') return 0.5;                  // legacy step 1/lam2 = 0.5 * 2/lam2
    return 0.15 / etaCrit(M, method, centered);         // legacy step 0.15 * etaCrit
  }

  function step(M, cur, method, centered, eta) {
    var g = grad(M, cur), ga = g[0], gb = g[1];
    if (method === 'pure') return { a: cur.a - eta * ga, b: cur.b - eta * gb };
    if (centered) {
      var v = cur.b + cur.a * M.xbar - eta * gb / (2 * M.n);
      var a = cur.a - eta * (ga - M.xbar * gb) / (2 * sxxC(M));
      return { a: a, b: v - a * M.xbar };
    }
    return { a: cur.a - eta * ga / (2 * M.sxx), b: cur.b - eta * gb / (2 * M.n) };
  }

  function isConverged(M, cur) {
    return Math.abs(cur.a - M.astar) < 0.004 && Math.abs(cur.b - M.bstar) < 0.8;
  }

  function outOfBox(M, cur, centered) {
    var v = centered ? cur.b + cur.a * M.xbar : cur.b;
    return Math.abs(cur.a - M.astar) > RA || Math.abs(v - vStar(M, centered)) > RB;
  }

  function run(M, opts) {
    opts = opts || {};
    var method = opts.method || 'scaled', centered = !!opts.centered;
    var k = opts.k == null ? defaultK(M, method, centered) : opts.k;
    var maxSteps = opts.maxSteps == null ? 5000 : opts.maxSteps;
    var eta = k * etaCrit(M, method, centered);
    var cur = opts.start ? { a: opts.start.a, b: opts.start.b } : { a: M.astar + 2.2, b: M.bstar - 260 };
    var steps = 0, next;
    while (steps < maxSteps) {
      if (isConverged(M, cur)) return { steps: steps, status: 'converged', cur: cur };
      next = step(M, cur, method, centered, eta);
      if (outOfBox(M, next, centered)) return { steps: steps, status: 'diverged', cur: cur };
      cur = next; steps++;
    }
    return { steps: steps, status: 'maxed', cur: cur };
  }

  return {
    RA: RA, RB: RB,
    etaCrit: etaCrit,
    defaultK: defaultK,
    step: step,
    isConverged: isConverged,
    outOfBox: outOfBox,
    run: run
  };
});
