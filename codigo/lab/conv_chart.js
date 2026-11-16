/* conv_chart.js — convergence chart (UMD, dependency-free, no DOM access).
 *
 * Public API (see tests/conv_chart.test.mjs):
 *   NCconv.FLOOR, NCconv.CEIL
 *   NCconv.yOf(dS, smin)                       -> log10(dS/smin) clamped to [FLOOR, CEIL]
 *   NCconv.scale(hist, smin)                  -> { xMax, yMin, yMax, pts:[{x,y}] }
 *   NCconv.draw(ctx, W, H, hist, {smin, tolRel}) -> { plotted }
 *
 * All drawing goes through the supplied 2D `ctx`; the module itself never
 * touches the DOM. Under node it exports via module.exports, in a page it is
 * exposed as window.NCconv.
 */
;(function (root, factory) {
  'use strict';
  if (typeof module === 'object' && module && typeof module.exports === 'object') {
    module.exports = factory();
  } else {
    root.NCconv = factory();
  }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  var FLOOR = -8;
  var CEIL = 6;

  // Look, kept in sync with the page.
  var PAD = { l: 44, r: 12, t: 10, b: 26 };
  var COL_BG = '#ffffff';
  var COL_GRID = '#dbe6ea';
  var COL_AXIS = '#46565e';
  var COL_LINE = '#009e73';
  var COL_TOL = '#0072b2';
  var FONT = '13px "CMU Serif",Georgia,serif';

  function clamp(v, lo, hi) {
    if (!(v > lo)) return lo; // also maps NaN / -Infinity to lo
    if (v > hi) return hi;
    return v;
  }

  function yOf(dS, smin) {
    if (typeof dS !== 'number' || Number.isNaN(dS)) return FLOOR;
    if (dS === Infinity) return CEIL;
    if (dS <= 0) return FLOOR;
    var v = Math.log10(dS / smin);
    if (Number.isNaN(v) || v === -Infinity) return FLOOR;
    if (v === Infinity) return CEIL;
    if (v < FLOOR) return FLOOR;
    if (v > CEIL) return CEIL;
    return v;
  }

  function scale(hist, smin) {
    var pts = [];
    var maxStep = 0;
    var maxY = -Infinity;
    var list = Array.isArray(hist) ? hist : [];
    for (var i = 0; i < list.length; i++) {
      var h = list[i] || {};
      var step = Number.isFinite(h.step) ? h.step : 0;
      var y = yOf(h.dS, smin);
      pts.push({ x: step, y: y });
      if (step > maxStep) maxStep = step;
      if (y > maxY) maxY = y;
    }
    return {
      xMax: Math.max(1, maxStep),
      yMin: FLOOR,
      yMax: list.length ? Math.max(0, Math.ceil(maxY)) : 0,
      pts: pts
    };
  }

  function draw(ctx, W, H, hist, opts) {
    var o = opts || {};
    var smin = o.smin;
    var tolRel = o.tolRel;
    var s = scale(hist, smin);

    var w = (typeof W === 'number' && Number.isFinite(W) && W > 0) ? W : 1;
    var h = (typeof H === 'number' && Number.isFinite(H) && H > 0) ? H : 1;

    var x0 = PAD.l, x1 = w - PAD.r;
    var y0 = PAD.t, y1 = h - PAD.b;
    if (x1 < x0) x1 = x0;
    if (y1 < y0) y1 = y0;
    var pw = x1 - x0, ph = y1 - y0;

    var xMin = 0, xMax = s.xMax;
    var yMin = s.yMin, yMax = s.yMax;
    var xr = (xMax - xMin) || 1;
    var yr = (yMax - yMin) || 1;

    // Map data coordinates into the plot rectangle, clamped so that no
    // non-finite / out-of-canvas coordinate ever reaches the 2D context.
    function mx(x) {
      var v = (typeof x === 'number' && Number.isFinite(x)) ? clamp(x, xMin, xMax) : xMin;
      return x0 + pw * (v - xMin) / xr;
    }
    function my(y) {
      var v = (typeof y === 'number' && Number.isFinite(y)) ? clamp(y, yMin, yMax) : yMin;
      return y1 - ph * (v - yMin) / yr;
    }
    // Label positions are clamped to the canvas as a final guard.
    function fx(x) { return clamp(x, 0, w); }
    function fy(y) { return clamp(y, 0, h); }

    // White background over the whole canvas.
    ctx.fillStyle = COL_BG;
    ctx.fillRect(0, 0, w, h);

    ctx.font = FONT;
    ctx.lineWidth = 1;

    // y ticks, every 2 from yMin to yMax.
    var ticks = [];
    for (var t = yMin; t <= yMax; t += 2) ticks.push(t);

    // Grid (#dbe6ea): horizontal lines at y ticks, vertical subdivisions.
    ctx.strokeStyle = COL_GRID;
    ctx.beginPath();
    for (var i = 0; i < ticks.length; i++) {
      var gy = my(ticks[i]);
      ctx.moveTo(x0, gy);
      ctx.lineTo(x1, gy);
    }
    var NDIV = 4;
    for (var j = 0; j <= NDIV; j++) {
      var gx = mx(xMin + (xMax - xMin) * j / NDIV);
      ctx.moveTo(gx, y0);
      ctx.lineTo(gx, y1);
    }
    ctx.stroke();

    // Axes (left + bottom) in the axis/label colour.
    ctx.strokeStyle = COL_AXIS;
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x0, y1);
    ctx.lineTo(x1, y1);
    ctx.stroke();

    // Tick labels.
    ctx.fillStyle = COL_AXIS;
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    for (var k = 0; k < ticks.length; k++) {
      ctx.fillText(String(ticks[k]), fx(x0 - 6), fy(my(ticks[k])));
    }
    ctx.textAlign = 'center';
    ctx.textBaseline = 'alphabetic';
    ctx.fillText('0', fx(mx(xMin)), fy(y1 + 16));
    ctx.fillText(String(xMax), fx(mx(xMax)), fy(y1 + 16));

    // Axis label: 'paso' centered under the plot. The y axis is named by the legend under the canvas
    // (a title inside the canvas collided with the first tick and the start of the curve).
    ctx.fillStyle = COL_AXIS;
    ctx.textAlign = 'center';
    ctx.fillText('paso', fx(x0 + pw / 2), fy(y1 + 16));

    // Convergence tolerance: dashed horizontal line at log10(tolRel).
    var ty = Math.log10(tolRel);
    if (!Number.isFinite(ty)) ty = yMin;
    var py = my(clamp(ty, yMin, yMax));
    ctx.strokeStyle = COL_TOL;
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 5]);
    ctx.beginPath();
    ctx.moveTo(x0, py);
    ctx.lineTo(x1, py);
    ctx.stroke();
    ctx.setLineDash([]); // restore a solid dash

    // Data polyline (#009e73, 2.5) and a dot (r = 4) at the last point.
    var pts = s.pts;
    var plotted = pts.length;
    ctx.strokeStyle = COL_LINE;
    ctx.fillStyle = COL_LINE;
    ctx.lineWidth = 2.5;
    if (plotted > 0) {
      ctx.beginPath();
      ctx.moveTo(mx(pts[0].x), my(pts[0].y));
      for (var q = 1; q < pts.length; q++) {
        ctx.lineTo(mx(pts[q].x), my(pts[q].y));
      }
      ctx.stroke();

      var last = pts[pts.length - 1];
      ctx.beginPath();
      ctx.arc(mx(last.x), my(last.y), 4, 0, 2 * Math.PI);
      ctx.fill();
    }

    return { plotted: plotted };
  }

  return {
    FLOOR: FLOOR,
    CEIL: CEIL,
    yOf: yOf,
    scale: scale,
    draw: draw
  };
}));
