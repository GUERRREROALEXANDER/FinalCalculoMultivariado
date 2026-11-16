// Static judge for codigo/simulador_template.html: the page must still parse, expose the ids the lab modules
// and the tour rely on, and part A's marker region must be wired to NCdescent / the history / the eta slider.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const html = fs.readFileSync(new URL('../../simulador_template.html', import.meta.url), 'utf8');
const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]));
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const main = scripts[scripts.length - 1];
const region = main.slice(main.indexOf('/*__ANIM_BEGIN__*/'), main.indexOf('/*__ANIM_END__*/'));

test('the main inline script parses', () => {
  assert.ok(scripts.length >= 1);
  assert.doesNotThrow(() => new vm.Script(main));
});

test('ids used by the tour and the lab modules exist', () => {
  for (const id of ['slEta', 'lblEta', 'etaTag', 'cvConv', 'btnTour', 'chkTourAuto', 'tourCursor', 'tourCaption',
    'hA', 'slA', 'slB', 'chkCenter', 'cvMap', 'cvLine', 'selMethod', 'slSpd', 'btnAnim', 'btnOpt', 'btnReset', 'msg']) {
    assert.ok(ids.has(id), `missing #${id}`);
  }
});

test('the lab placeholder sits before the main script, once', () => {
  assert.equal(html.split('<!--__LAB__-->').length, 2);
  assert.ok(html.indexOf('<!--__LAB__-->') < html.indexOf('window.NC = '));
});

test('part A region: markers present and wired', () => {
  assert.ok(region.length > 200, 'ANIM markers missing');
  for (const needle of ['NCdescent', 'NC.hist.push', 'slEta', 'lblEta', 'etaTag', 'Divergió', 'selMethod', 'btnAnim']) {
    assert.ok(region.includes(needle), `region lacks ${needle}`);
  }
  assert.ok(!/1\s*\/\s*lam2/.test(region) && !/eta\s*=\s*0\.15/.test(region), 'hard-coded legacy step sizes must be gone');
});

test('outside the region: hist is cleared and the chart is drawn', () => {
  const outside = main.replace(region, '');
  assert.ok(outside.includes('NCconv.draw') && outside.includes('clearHist'));
});
