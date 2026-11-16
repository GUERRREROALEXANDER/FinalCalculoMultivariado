// Judge for codigo/lab/tour.js (UMD: `module.exports` under node, `window.NCtour` in the page).
//
// Contract
//   IDLE_MS = 25000, BEAT_INTRO_MS = 600, CURSOR_MS = 600 (time the cursor needs to glide to its target), SCROLL_MS = 700 (smooth page scroll)
//   createToken()  -> {cancelled: false, cancel()}
//   isUserEvent(e) -> true only when e.isTrusted === true
//   attach(doc, onUser) -> detach()    registers pointerdown, wheel, keydown on `doc` with
//        doc.addEventListener(type, fn, true) (capture); fn calls onUser(e) only for trusted events.
//        detach() removes the same three with doc.removeEventListener(type, fn, true).
//   createIdle({onIdle, setTimeout, clearTimeout}) -> {poke(), stop()}
//        poke(): clear the pending timer (if any), then setTimeout(onIdle, IDLE_MS). stop(): clear it.
//   BEATS: [{id, target, view?, caption, steps}]   target = DOM id of the element the cursor goes to first.
//     view = DOM id to bring into view first: host.scrollTo(view), then host.sleep(SCROLL_MS), before the caption and the cursor move.
//   Actions (every `id` is a DOM id that must exist in codigo/simulador_template.html):
//     {do:'wait', ms}                          host.sleep(ms)
//     {do:'click', id}                         move cursor to the center of host.rectOf(id), host.sleep(CURSOR_MS), then host.click(id)
//     {do:'set', id, value}                    move cursor to the element, host.sleep(CURSOR_MS), then host.setValue(id, value)
//     {do:'check', id, value}                  move cursor to the element, host.sleep(CURSOR_MS), then host.setChecked(id, value)
//     {do:'reset'}                             host.api.reset()
//     {do:'sweep', path:[[a,b],...], ms}       for each point, in order: host.moveCursor(host.mapXY(a,b)), host.sleep(CURSOR_MS),
//                                              host.api.setPoint(a,b), then sleep max(0, ms/path.length - CURSOR_MS) (not after the last point)
//     {do:'untilIdle', maxMs}                  poll every 100 ms: while host.isAnimating() and < maxMs elapsed, host.sleep(100);
//                                              if still animating at maxMs, host.api.stopAnim()
//   runTour(host, token, beats = BEATS) -> Promise<'done' | 'cancelled'>
//     per beat: check token, host.setCaption(caption), move cursor to the center of rectOf(target), host.sleep(BEAT_INTRO_MS),
//     then run the steps. The token is checked before every action and after every sleep. After a cancel the
//     runner makes NO further host calls except host.setCaption('') once.
//   host.moveCursor(x, y) always receives viewport coordinates of a rect center ({x + w/2, y + h/2}); a null rect is skipped.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const T = require('../tour.js');
const M = JSON.parse(fs.readFileSync(new URL('./meta.json', import.meta.url), 'utf8'));
const template = fs.readFileSync(new URL('../../simulador_template.html', import.meta.url), 'utf8');
const ids = new Set([...template.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]));

function makeHost({ onSleep, animating = () => false, rect = { x: 100, y: 200, w: 40, h: 20 } } = {}) {
  const log = [];
  return {
    log,
    rectOf: () => rect,
    mapXY: (a, b) => ({ x: a, y: b }),
    moveCursor: (x, y) => log.push(['move', x, y]),
    setCaption: t => log.push(['caption', t]),
    scrollTo: id => log.push(['scroll', id]),
    click: id => log.push(['click', id]),
    setValue: (id, v) => log.push(['set', id, v]),
    setChecked: (id, v) => log.push(['check', id, v]),
    isAnimating: animating,
    api: {
      reset: () => log.push(['reset']),
      stopAnim: () => log.push(['stopAnim']),
      setPoint: (a, b) => log.push(['point', a, b]),
    },
    sleep: async ms => { log.push(['sleep', ms]); if (onSleep) onSleep(ms, log); },
  };
}
const beat = (steps, target = 'btnAnim') => [{ id: 't', target, caption: 'c', steps }];
const noSleep = log => log.filter(e => e[0] !== 'sleep');

// ---------- the script itself ----------
test('BEATS: shape and every referenced DOM id exists in the template', () => {
  assert.ok(Array.isArray(T.BEATS) && T.BEATS.length >= 6);
  for (const b of T.BEATS) {
    assert.ok(b.id && b.caption && Array.isArray(b.steps) && b.steps.length > 0, `beat ${b.id}`);
    assert.ok(ids.has(b.target), `target ${b.target} missing in template`);
    for (const s of b.steps) if (s.id) assert.ok(ids.has(s.id), `step id ${s.id} missing in template`);
  }
});

test('BEATS: sweep points stay inside the lab box', () => {
  for (const s of T.BEATS.flatMap(b => b.steps).filter(s => s.do === 'sweep')) {
    for (const [a, b] of s.path) {
      assert.ok(Math.abs(a - M.astar) <= 3.2 && Math.abs(b - M.bstar) <= 420, `(${a}, ${b})`);
    }
  }
});

test('BEATS: tells the planned story', () => {
  const flat = T.BEATS.flatMap(b => b.steps);
  const idx = (pred, from = 0) => flat.findIndex((s, i) => i >= from && pred(s));
  const p = idx(s => s.do === 'set' && s.id === 'selMethod' && s.value === 'pure');
  assert.ok(p >= 0 && idx(s => s.do === 'click' && s.id === 'btnAnim', p) > p, 'pure descent is run');
  const q = idx(s => s.do === 'set' && s.id === 'selMethod' && s.value === 'scaled');
  assert.ok(q >= 0 && idx(s => s.do === 'click' && s.id === 'btnAnim', q) > q, 'scaled descent is run');
  const e = idx(s => s.do === 'set' && s.id === 'slEta' && s.value > 1);
  assert.ok(e >= 0 && idx(s => s.do === 'click' && s.id === 'btnAnim', e) > e, 'an eta > eta_crit run is shown');
  assert.ok(idx(s => s.do === 'check' && s.id === 'chkCenter' && s.value === true) >= 0, 'centering is shown');
  assert.ok(idx(s => s.do === 'sweep') >= 0, 'the map is dragged');
  const last = flat[flat.length - 1];
  assert.deepEqual([last.do, last.id], ['click', 'btnOpt']);
});

const BOX5 = ['msg', 'btnAnim', 'cvConv', 'slEta', 'selMethod'];   // the descent box: buttons, step size, message, chart
test('BEATS: every view id exists, the tour starts at the top and every descent is scrolled into view', () => {
  for (const b of T.BEATS) if (b.view) assert.ok(ids.has(b.view), `view ${b.view} missing in template`);
  assert.equal(T.BEATS[0].view, 'slA');
  for (const b of T.BEATS.filter(b => b.steps.some(s => s.do === 'click' && s.id === 'btnAnim'))) {
    assert.ok(BOX5.includes(b.view), `beat ${b.id} runs a descent but its view is ${b.view}`);
  }
  const check = T.BEATS.find(b => b.steps.some(s => s.do === 'check' && s.id === 'chkCenter'));
  assert.ok(check && !check.steps.some(s => s.do === 'click' && s.id === 'btnAnim'), 'the centering checkbox (top of the panel) and the descent run in different beats');
});

test('BEATS: total length is between 30 s and 120 s', () => {
  const ms = T.BEATS.reduce((t, b) => t + T.BEAT_INTRO_MS + (b.view ? T.SCROLL_MS : 0) + b.steps.reduce((u, s) => u + (s.ms || s.maxMs || 0) + (s.do === 'click' || s.do === 'set' || s.do === 'check' ? 500 : 0), 0), 0);
  assert.ok(ms >= 30000 && ms <= 120000, `${ms} ms`);
});

// ---------- runner ----------
test('runTour: a full run over the real beats is done and stays on the declared actions', async () => {
  const h = makeHost();
  const res = await T.runTour(h, T.createToken());
  assert.equal(res, 'done');
  assert.ok(h.log.filter(e => e[0] === 'click' && e[1] === 'btnAnim').length >= 3);
  assert.ok(h.log.some(e => e[0] === 'set' && e[1] === 'selMethod' && e[2] === 'pure'));
});

test('runTour: a beat with view scrolls first, waits SCROLL_MS, then captions and moves the cursor', async () => {
  assert.equal(T.SCROLL_MS, 700);
  const h = makeHost();
  await T.runTour(h, T.createToken(), [{ id: 't', target: 'btnAnim', view: 'msg', caption: 'c', steps: [] }]);
  assert.deepEqual(h.log.slice(0, 4), [['scroll', 'msg'], ['sleep', 700], ['caption', 'c'], ['move', 120, 210]]);
});

test('runTour: a beat without view never scrolls', async () => {
  const h = makeHost();
  await T.runTour(h, T.createToken(), beat([{ do: 'wait', ms: 10 }]));
  assert.ok(!h.log.some(e => e[0] === 'scroll'));
});

test('runTour: cancelling during the scroll wait shows no caption', async () => {
  const token = T.createToken();
  const h = makeHost({ onSleep: () => token.cancel() });
  const res = await T.runTour(h, token, [{ id: 't', target: 'btnAnim', view: 'msg', caption: 'c', steps: [{ do: 'click', id: 'btnAnim' }] }]);
  assert.equal(res, 'cancelled');
  assert.ok(!h.log.some(e => e[0] === 'caption' && e[1] !== ''));
  assert.ok(!h.log.some(e => e[0] === 'click'));
});

test('runTour: wait sleeps exactly ms', async () => {
  const h = makeHost();
  await T.runTour(h, T.createToken(), beat([{ do: 'wait', ms: 1234 }]));
  assert.ok(h.log.some(e => e[0] === 'sleep' && e[1] === 1234));
});

test('runTour: the cursor goes to the center of the element before a click', async () => {
  const h = makeHost();
  await T.runTour(h, T.createToken(), beat([{ do: 'click', id: 'btnAnim' }]));
  const f = noSleep(h.log), i = f.findIndex(e => e[0] === 'click');
  assert.deepEqual(f[i], ['click', 'btnAnim']);
  assert.deepEqual(f[i - 1], ['move', 120, 210]);
});

test('runTour: the cursor gets CURSOR_MS to arrive before click, set, check and each sweep point act', async () => {
  assert.equal(T.CURSOR_MS, 600);
  const h = makeHost();
  await T.runTour(h, T.createToken(), beat([
    { do: 'click', id: 'btnAnim' }, { do: 'set', id: 'slEta', value: 1 },
    { do: 'check', id: 'chkCenter', value: true }, { do: 'sweep', path: [[1, 2], [3, 4]], ms: 2000 }]));
  for (const kind of ['click', 'set', 'check', 'point']) {
    const i = h.log.findIndex(e => e[0] === kind);
    assert.deepEqual(h.log[i - 1], ['sleep', 600], `${kind} must follow a ${600} ms sleep`);
    assert.equal(h.log[i - 2][0], 'move');
  }
});

test('runTour: set and check move the cursor first, then act', async () => {
  const h = makeHost();
  await T.runTour(h, T.createToken(), beat([{ do: 'set', id: 'slEta', value: 2.2 }, { do: 'check', id: 'chkCenter', value: true }]));
  const f = noSleep(h.log);
  const i = f.findIndex(e => e[0] === 'set'), j = f.findIndex(e => e[0] === 'check');
  assert.deepEqual(f[i], ['set', 'slEta', 2.2]); assert.equal(f[i - 1][0], 'move');
  assert.deepEqual(f[j], ['check', 'chkCenter', true]); assert.equal(f[j - 1][0], 'move');
});

test('runTour: sweep visits the points in order, cursor first', async () => {
  const h = makeHost();
  const path = [[1, 2], [3, 4], [5, 6]];
  await T.runTour(h, T.createToken(), beat([{ do: 'sweep', path, ms: 900 }]));
  const f = noSleep(h.log), pts = f.filter(e => e[0] === 'point');
  assert.deepEqual(pts.map(e => [e[1], e[2]]), path);
  for (const e of pts) assert.deepEqual(f[f.indexOf(e) - 1], ['move', e[1], e[2]]);
});

test('runTour: reset calls api.reset', async () => {
  const h = makeHost();
  await T.runTour(h, T.createToken(), beat([{ do: 'reset' }]));
  assert.ok(h.log.some(e => e[0] === 'reset'));
});

test('runTour: untilIdle polls every 100 ms and stops the animation at maxMs', async () => {
  const h = makeHost({ animating: () => true });
  await T.runTour(h, T.createToken(), beat([{ do: 'untilIdle', maxMs: 1000 }]));
  const polls = h.log.filter(e => e[0] === 'sleep' && e[1] === 100).length;
  assert.ok(polls >= 9 && polls <= 12, `${polls} polls`);
  assert.ok(h.log.some(e => e[0] === 'stopAnim'));
});

test('runTour: untilIdle returns as soon as the animation ends, without stopAnim', async () => {
  let n = 0;
  const h = makeHost({ animating: () => ++n <= 3 });
  await T.runTour(h, T.createToken(), beat([{ do: 'untilIdle', maxMs: 60000 }]));
  assert.ok(!h.log.some(e => e[0] === 'stopAnim'));
  assert.ok(h.log.filter(e => e[0] === 'sleep' && e[1] === 100).length <= 4);
});

test('runTour: cancelling mid-run stops every host call', async () => {
  const token = T.createToken();
  let n = 0, at = -1;
  const h = makeHost({ onSleep: (ms, log) => { if (++n === 5) { token.cancel(); at = log.length; } } });
  const res = await T.runTour(h, token);
  assert.equal(res, 'cancelled');
  assert.ok(at > 0);
  assert.ok(h.log.slice(at).every(e => e[0] === 'caption' && e[1] === ''), JSON.stringify(h.log.slice(at)));
});

test('runTour: cancelling during a sweep stops the remaining points', async () => {
  const token = T.createToken();
  const h = makeHost({ onSleep: (ms, log) => { if (log.filter(e => e[0] === 'point').length === 2) token.cancel(); } });
  const res = await T.runTour(h, token, beat([{ do: 'sweep', path: [[1, 1], [2, 2], [3, 3], [4, 4]], ms: 800 }]));
  assert.equal(res, 'cancelled');
  assert.equal(h.log.filter(e => e[0] === 'point').length, 2);
});

test('runTour: an already-cancelled token does nothing', async () => {
  const token = T.createToken(); token.cancel();
  const h = makeHost();
  assert.equal(await T.runTour(h, token), 'cancelled');
  assert.ok(h.log.every(e => e[0] === 'caption' && e[1] === ''));
});

// ---------- hand-over to the visitor ----------
test('IDLE_MS is 25 s', () => assert.equal(T.IDLE_MS, 25000));

test('isUserEvent: only trusted events count', () => {
  assert.equal(T.isUserEvent({ isTrusted: true }), true);
  assert.equal(T.isUserEvent({ isTrusted: false }), false);
  assert.equal(T.isUserEvent({}), false);
  assert.equal(T.isUserEvent(null), false);
});

test('attach: capture listeners for pointerdown, wheel, keydown; synthetic events are ignored', () => {
  const reg = [], unreg = [];
  const doc = { addEventListener: (t, f, c) => reg.push([t, f, c]), removeEventListener: (t, f, c) => unreg.push([t, f, c]) };
  const seen = [];
  const detach = T.attach(doc, e => seen.push(e));
  assert.deepEqual(reg.map(r => r[0]).sort(), ['keydown', 'pointerdown', 'wheel']);
  assert.ok(reg.every(r => r[2] === true));
  for (const [, fn] of reg) fn({ isTrusted: false });
  assert.equal(seen.length, 0);
  reg[0][1]({ isTrusted: true, type: reg[0][0] });
  assert.equal(seen.length, 1);
  detach();
  assert.deepEqual(unreg.map(r => [r[0], r[1], r[2]]), reg.map(r => [r[0], r[1], true]));
});

test('createIdle: poke re-arms a 25 s timer, stop clears it, firing calls onIdle once', () => {
  const timers = [], cleared = [];
  const fake = { setTimeout: (fn, ms) => { timers.push({ fn, ms }); return timers.length; }, clearTimeout: h => cleared.push(h) };
  let idled = 0;
  const idle = T.createIdle({ onIdle: () => idled++, ...fake });
  idle.poke();
  assert.equal(timers.length, 1); assert.equal(timers[0].ms, 25000);
  idle.poke();
  assert.deepEqual(cleared, [1]); assert.equal(timers.length, 2);
  timers[1].fn();
  assert.equal(idled, 1);
  idle.poke(); idle.stop();
  assert.ok(cleared.includes(3));
  idle.stop();                                  // stopping twice must not throw
});
