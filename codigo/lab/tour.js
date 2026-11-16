/* Tour guiado para el laboratorio S(a,b).
 *
 * Módulo UMD puro: sin dependencias y sin acceso propio al DOM; cada
 * interacción pasa por el objeto `host` (ver codigo/lab/tests/tour.test.mjs).
 * Un cursor falso pulsa los controles reales del simulador y el visitante
 * puede tomar el control en cualquier momento (attach + createIdle).
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.NCtour = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var IDLE_MS = 25000;      // tiempo sin interacción antes de reanudar el tour
  var BEAT_INTRO_MS = 600;  // pausa tras mostrar el rótulo de cada beat
  var POLL_MS = 100;        // sondeo de untilIdle
  var CURSOR_MS = 600;      // tiempo que tarda el cursor en llegar a su destino
  var SCROLL_MS = 700;      // tiempo que tarda el panel en terminar el desplazamiento suave

  // ---- token de cancelación (el visitante toma el control) ----
  function createToken() {
    var t = { cancelled: false };
    t.cancel = function () { t.cancelled = true; };
    return t;
  }

  function isUserEvent(e) {
    return !!(e && e.isTrusted === true);
  }

  // ---- escucha de eventos reales del visitante (captura) ----
  function attach(doc, onUser) {
    var types = ['pointerdown', 'wheel', 'keydown'];
    function fn(e) {
      if (isUserEvent(e)) onUser(e);
    }
    types.forEach(function (type) { doc.addEventListener(type, fn, true); });
    return function detach() {
      types.forEach(function (type) { doc.removeEventListener(type, fn, true); });
    };
  }

  // ---- controlador de inactividad ----
  function createIdle(deps) {
    var onIdle = deps.onIdle;
    var setTimeoutFn = deps.setTimeout;
    var clearTimeoutFn = deps.clearTimeout;
    var handle = null;
    var idle = {
      poke: function () {
        if (handle !== null) clearTimeoutFn(handle);
        handle = setTimeoutFn(onIdle, IDLE_MS);
      },
      stop: function () {
        if (handle !== null) clearTimeoutFn(handle);
        handle = null;
      },
    };
    return idle;
  }

  // ---- puntos del recorrido sobre el mapa (a*, b* de meta.json) ----
  var A_STAR = 2.7467;
  var B_STAR = 683.12;
  var START = [A_STAR + 2.2, B_STAR - 260];
  var SWEEP_PATH = [
    START,
    [A_STAR - 1.5, B_STAR - 120],
    [A_STAR - 2.8, B_STAR + 180],
    [A_STAR + 1.2, B_STAR + 330],
  ];

  var BEATS = [
    {
      id: 'intro',
      target: 'hA',
      view: 'slA',
      caption: 'S(a,b) mide el error total de la recta y = a·x + b',
      steps: [{ do: 'wait', ms: 3500 }],
    },
    {
      id: 'mapa',
      target: 'cvMap',
      view: 'cvMap',
      caption: 'Cada punto del mapa es una recta distinta',
      steps: [{ do: 'sweep', path: SWEEP_PATH, ms: 4500 }],
    },
    {
      id: 'gradiente',
      target: 'cvMap',
      view: 'cvMap',
      caption: '−∇S apunta cuesta abajo, perpendicular a las curvas de nivel',
      steps: [{ do: 'wait', ms: 3500 }],
    },
    {
      id: 'puro',
      target: 'selMethod',
      view: 'msg',
      caption: 'Descenso puro: con cond ≈ 38 000 el paso zigzaguea entre las elipses',
      steps: [
        { do: 'set', id: 'selMethod', value: 'pure' },
        { do: 'click', id: 'btnAnim' },
        { do: 'untilIdle', maxMs: 6000 },
      ],
    },
    {
      id: 'escalado',
      target: 'selMethod',
      view: 'msg',
      caption: 'Paso escalado: la dirección se ajusta y el descenso baja casi recto',
      steps: [
        { do: 'reset' },
        { do: 'set', id: 'selMethod', value: 'scaled' },
        { do: 'click', id: 'btnAnim' },
        { do: 'untilIdle', maxMs: 12000 },
      ],
    },
    {
      id: 'diverge',
      target: 'slEta',
      view: 'msg',
      caption: 'η = 2.2 supera η_crit: el error crece en cada paso y el descenso diverge',
      steps: [
        { do: 'reset' },
        { do: 'set', id: 'slEta', value: 2.2 },
        { do: 'click', id: 'btnAnim' },
        { do: 'untilIdle', maxMs: 6000 },
        { do: 'wait', ms: 2500 },
      ],
    },
    {
      id: 'centrado',
      target: 'chkCenter',
      view: 'slA',
      caption: 'Centrar x̃ = x − 90° elimina la correlación y las elipses se enderezan',
      steps: [
        { do: 'reset' },
        { do: 'check', id: 'chkCenter', value: true },
        { do: 'wait', ms: 2500 },
      ],
    },
    {
      id: 'centrado-descenso',
      target: 'selMethod',
      view: 'msg',
      caption: 'Con ejes alineados el descenso baja directo al mínimo',
      steps: [
        { do: 'set', id: 'selMethod', value: 'scaled' },
        { do: 'click', id: 'btnAnim' },
        { do: 'untilIdle', maxMs: 8000 },
      ],
    },
    {
      id: 'optimo',
      target: 'btnOpt',
      view: 'msg',
      caption: '∇S = 0: este es el mínimo, la recta que mejor ajusta los datos',
      steps: [
        { do: 'wait', ms: 1500 },
        { do: 'click', id: 'btnOpt' },
      ],
    },
  ];

  // ---- ejecución de un paso ----
  function moveTo(host, id) {
    var r = host.rectOf(id);
    if (!r) return; // rect nulo: se omite el movimiento
    host.moveCursor(r.x + r.w / 2, r.y + r.h / 2);
  }

  async function runStep(host, s, cancelled) {
    switch (s.do) {
      case 'wait':
        return host.sleep(s.ms);
      case 'click':
        moveTo(host, s.id);
        await host.sleep(CURSOR_MS);
        if (cancelled()) return;
        host.click(s.id);
        return;
      case 'set':
        moveTo(host, s.id);
        await host.sleep(CURSOR_MS);
        if (cancelled()) return;
        host.setValue(s.id, s.value);
        return;
      case 'check':
        moveTo(host, s.id);
        await host.sleep(CURSOR_MS);
        if (cancelled()) return;
        host.setChecked(s.id, s.value);
        return;
      case 'reset':
        host.api.reset();
        return;
      case 'sweep': {
        var path = s.path;
        for (var i = 0; i < path.length; i++) {
          if (cancelled()) return;
          var p = host.mapXY(path[i][0], path[i][1]);
          host.moveCursor(p.x, p.y);
          await host.sleep(CURSOR_MS);
          if (cancelled()) return;
          host.api.setPoint(path[i][0], path[i][1]);
          if (i < path.length - 1) {
            await host.sleep(Math.max(0, s.ms / path.length - CURSOR_MS));
          }
        }
        return;
      }
      case 'untilIdle': {
        var elapsed = 0;
        while (!cancelled() && host.isAnimating() && elapsed < s.maxMs) {
          await host.sleep(POLL_MS);
          elapsed += POLL_MS;
        }
        if (!cancelled() && host.isAnimating()) host.api.stopAnim();
        return;
      }
      default:
        return;
    }
  }

  // ---- runner del tour ----
  async function runTour(host, token, beats) {
    beats = beats || BEATS;
    if (token.cancelled) {
      host.setCaption('');
      return 'cancelled';
    }
    for (var bi = 0; bi < beats.length; bi++) {
      var b = beats[bi];
      if (token.cancelled) break;
      if (b.view) {                                  // bring the beat's area into view before anything else
        host.scrollTo(b.view);
        await host.sleep(SCROLL_MS);
        if (token.cancelled) break;
      }
      host.setCaption(b.caption);
      moveTo(host, b.target);
      if (token.cancelled) break;
      await host.sleep(BEAT_INTRO_MS);
      if (token.cancelled) break;
      for (var si = 0; si < b.steps.length; si++) {
        if (token.cancelled) break;
        await runStep(host, b.steps[si], function () { return token.cancelled; });
        if (token.cancelled) break;
      }
      if (token.cancelled) break;
    }
    if (token.cancelled) {
      host.setCaption('');
      return 'cancelled';
    }
    return 'done';
  }

  return {
    IDLE_MS: IDLE_MS,
    BEAT_INTRO_MS: BEAT_INTRO_MS,
    CURSOR_MS: CURSOR_MS,
    SCROLL_MS: SCROLL_MS,
    createToken: createToken,
    isUserEvent: isUserEvent,
    attach: attach,
    createIdle: createIdle,
    BEATS: BEATS,
    runTour: runTour,
  };
});
