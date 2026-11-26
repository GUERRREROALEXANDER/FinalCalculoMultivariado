"""Gráficas matemáticas de NeuroCode renderizadas en Blender (Cycles), construidas desde los datos reales.

Uso (sin abrir la interfaz):
    blender -b -P blender/graficas_v2.py -- <raiz_del_repo> [muestras] [escenas]
    escenas: lista separada por comas de  superficie, nivel, recta   (por defecto: todas)

Salida:
    blender/renders/v2/S_superficie_malla.png
    blender/renders/v2/S_nivel_gradiente.png
    blender/renders/v2/recta_datos.png
    blender/graficas_v2_<escena>.blend   (escenas editables)

Todo se calcula aquí: las sumatorias salen de csvs/*.csv, la superficie es exactamente
S(a,b) = a²Σx² + 2abΣx + nb² − 2aΣxy − 2bΣy + Σy², las curvas de nivel se obtienen con
marching squares y las flechas son −∇S en las coordenadas de la escena (perpendiculares a las curvas).
"""
import bpy
import bmesh
from mathutils import Matrix
import csv
import glob
import math
import os
import random
import sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ROOT = argv[0] if argv else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = int(argv[1]) if len(argv) > 1 else 160
WHICH = argv[2].split(",") if len(argv) > 2 else ["superficie", "nivel", "recta"]
OUT = os.path.join(ROOT, "blender", "renders", "v2")
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------- datos y modelo
X, Y, WHO = [], [], []
for path in sorted(glob.glob(os.path.join(ROOT, "csvs", "*.csv"))):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            X.append(float(row["angulo_grados"]))
            Y.append(float(row["tiempo_ms"]))
            WHO.append(os.path.basename(path).split("_")[-1][:-4].upper())
n = len(X)
sx, sy = sum(X), sum(Y)
sxx = sum(x * x for x in X)
sxy = sum(x * y for x, y in zip(X, Y))
syy = sum(y * y for y in Y)
D0 = n * sxx - sx * sx
A = (n * sxy - sx * sy) / D0
B = (sy - A * sx) / n
SMIN = sum((y - A * x - B) ** 2 for x, y in zip(X, Y))
print(f"[NeuroCode] n={n} a*={A:.6f} b*={B:.4f} Smin={SMIN:.2f}")
assert n == 595 and abs(A - 2.746737) < 1e-6, "los datos no coinciden con resultados.txt"


def S(a, b):
    return a * a * sxx + 2 * a * b * sx + n * b * b - 2 * a * sxy - 2 * b * sy + syy


def grad(a, b):
    return (2 * sxx * a + 2 * sx * b - 2 * sxy, 2 * sx * a + 2 * n * b - 2 * sy)


MEANS = []
for ang in sorted(set(X)):
    ys = [y for x, y in zip(X, Y) if x == ang]
    MEANS.append((ang, sum(ys) / len(ys)))

# caja de parámetros (la misma del laboratorio interactivo)
RA, RB = 3.2, 420.0
W = 2.0          # semiancho de la escena
HZ = 2.3         # altura máxima de la superficie


def a_of(xs):
    return A + xs / W * RA


def b_of(ys):
    return B + ys / W * RB


def sx_of(a):
    return (a - A) / RA * W


def sy_of(b):
    return (b - B) / RB * W


SMAX = max(S(a_of(i), b_of(j)) for i in (-W, W) for j in (-W, W))


def h(xs, ys):
    return (S(a_of(xs), b_of(ys)) - SMIN) / (SMAX - SMIN) * HZ


# paleta: azul petróleo → verde agua → arena → ámbar (misma que la calculadora)
STOPS = [(0.02, 0.18, 0.28), (0.04, 0.36, 0.47), (0.20, 0.58, 0.58), (0.62, 0.75, 0.55), (0.93, 0.72, 0.38), (0.85, 0.42, 0.20)]


def cmap(t):
    t = min(1.0, max(0.0, t)) * (len(STOPS) - 1)
    i = min(len(STOPS) - 2, int(t))
    f = t - i
    return tuple(STOPS[i][k] + (STOPS[i + 1][k] - STOPS[i][k]) * f for k in range(3))


# ----------------------------------------------------------------- utilidades de escena
def reset():
    global FONT
    bpy.ops.wm.read_factory_settings(use_empty=True)
    FONT = None                      # la fuente cargada se pierde al reiniciar


def setup_render(w=1920, h_=1080):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = w, h_
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    try:
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.exposure = -0.15
    except Exception:
        pass
    sc.cycles.device = "CPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for kind in ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"):
            try:
                prefs.compute_device_type = kind
            except Exception:
                continue
            prefs.get_devices()
            devs = [d for d in prefs.devices if d.type == kind]
            if devs:
                for d in prefs.devices:
                    d.use = d.type in (kind,)
                sc.cycles.device = "GPU"
                print(f"[NeuroCode] render en GPU ({kind})")
                break
    except Exception as e:
        print("[NeuroCode] GPU no disponible:", e)
    print("[NeuroCode] dispositivo:", sc.cycles.device)


def world(color=(0.93, 0.95, 0.97), strength=0.75):
    wd = bpy.data.worlds.new("Mundo")
    bpy.context.scene.world = wd
    try:
        wd.use_nodes = True
    except Exception:
        pass
    bg = wd.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (*color, 1)
    bg.inputs["Strength"].default_value = strength


def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def setin(node, names, value):
    for nm in names:
        if nm in node.inputs:
            node.inputs[nm].default_value = value
            return


def material(name, color, rough=0.4, metal=0.0, coat=0.0, alpha=1.0, emit=0.0, transmission=0.0):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    setin(p, ["Coat Weight", "Clearcoat"], coat)
    setin(p, ["Alpha"], alpha)
    setin(p, ["Transmission Weight", "Transmission"], transmission)
    if emit:
        setin(p, ["Emission Color", "Emission"], (*color, 1))
        setin(p, ["Emission Strength"], emit)
    return m


def vertex_color_material(name, attr="col", rough=0.32, coat=0.55):
    m = material(name, (1, 1, 1), rough=rough, coat=coat)
    nt = m.node_tree
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = attr
    nt.links.new(at.outputs["Color"], nt.nodes.get("Principled BSDF").inputs["Base Color"])
    return m


def area_light(name, loc, energy, size, target=(0, 0, 0), color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy, ld.size, ld.color = energy, size, color
    ob = link(bpy.data.objects.new(name, ld))
    ob.location = loc
    aim(ob, target)
    return ob


def aim(ob, target):
    tgt = bpy.data.objects.new(ob.name + "_obj", None)
    link(tgt)
    tgt.location = target
    c = ob.constraints.new("TRACK_TO")
    c.target, c.track_axis, c.up_axis = tgt, "TRACK_NEGATIVE_Z", "UP_Y"


def camera(loc, target, lens=40, ortho=None):
    cd = bpy.data.cameras.new("Camara")
    cd.lens = lens
    if ortho:
        cd.type, cd.ortho_scale = "ORTHO", ortho
    ob = link(bpy.data.objects.new("Camara", cd))
    ob.location = loc
    aim(ob, target)
    bpy.context.scene.camera = ob
    return ob


FONT = None


TXT = 1.0


def font():
    global FONT
    if FONT is None:
        for f in ("C:/Windows/Fonts/cambriab.ttf", "C:/Windows/Fonts/arialbd.ttf"):
            if os.path.exists(f):
                try:
                    FONT = bpy.data.fonts.load(f)
                    break
                except Exception:
                    pass
    return FONT


def flat(mat):
    name = "plano_" + mat.name
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    col = tuple(mat.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value)[:3]
    m = material(name, (0, 0, 0), rough=1.0)
    p = m.node_tree.nodes.get("Principled BSDF")
    setin(p, ["Specular IOR Level", "Specular"], 0.0)
    setin(p, ["Emission Color", "Emission"], (*[c * 0.8 for c in col], 1))
    setin(p, ["Emission Strength"], 1.0)
    return m


def plate(loc, w, h_, rot=(math.pi / 2, 0, 0), face=None):
    """Fondo blanco detrás de un rótulo."""
    m = material("fondo_rotulo", (0, 0, 0), rough=1.0) if "fondo_rotulo" not in bpy.data.materials else bpy.data.materials["fondo_rotulo"]
    p = m.node_tree.nodes.get("Principled BSDF")
    setin(p, ["Specular IOR Level", "Specular"], 0.0)
    setin(p, ["Emission Color", "Emission"], (0.96, 0.96, 0.96, 1))
    setin(p, ["Emission Strength"], 1.0)
    ob = plane("placa", w / 2, h_ / 2, loc, m, rot=rot)
    ob.visible_shadow = False
    return ob


def text(body, loc, size, mat, rot=(math.pi / 2, 0, 0), align="CENTER", face=None, extrude=0.004):
    p_ = mat.node_tree.nodes.get("Principled BSDF")
    setin(p_, ["Specular IOR Level", "Specular"], 0.0)
    p_.inputs["Roughness"].default_value = 1.0
    size *= TXT
    cu = bpy.data.curves.new("txt", "FONT")
    cu.body, cu.size, cu.align_x, cu.align_y, cu.extrude = body, size, align, "CENTER", extrude
    if font():
        cu.font = font()
    ob = link(bpy.data.objects.new("T_" + body[:14], cu))
    ob.location, ob.rotation_euler = loc, rot
    ob.data.materials.append(flat(mat))
    ob.visible_shadow = False
    if face is not None:
        c = ob.constraints.new("TRACK_TO")
        c.target, c.track_axis, c.up_axis = face, "TRACK_Z", "UP_Y"
    return ob


def tubes(name, polys, radius, mat, res=4):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions, cu.bevel_depth, cu.bevel_resolution, cu.use_fill_caps = "3D", radius, res, True
    for poly in polys:
        if len(poly) < 2:
            continue
        sp = cu.splines.new("POLY")
        sp.points.add(len(poly) - 1)
        for pt, (x, y, z) in zip(sp.points, poly):
            pt.co = (x, y, z, 1)
    ob = link(bpy.data.objects.new(name, cu))
    ob.data.materials.append(mat)
    return ob


def sphere(name, loc, r, mat, seg=48):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = link(bpy.data.objects.new(name, me))
    ob.location = loc
    ob.data.materials.append(mat)
    return ob


def plane(name, sx_, sy_, loc, mat, rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    me.from_pydata([(-sx_, -sy_, 0), (sx_, -sy_, 0), (sx_, sy_, 0), (-sx_, sy_, 0)], [], [(0, 1, 2, 3)])
    ob = link(bpy.data.objects.new(name, me))
    ob.location, ob.rotation_euler = loc, rot
    ob.data.materials.append(mat)
    return ob


def arrow_mesh(length=1.0, r=0.012, head=0.34, rh=0.042):
    """Flecha a lo largo de +X, con la base en el origen."""
    me = bpy.data.meshes.new("flecha")
    bm = bmesh.new()

    def cone(r1, r2, depth, x0):
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=r1, radius2=r2, depth=depth)
        verts = res["verts"]
        bmesh.ops.rotate(bm, verts=verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y"))
        bmesh.ops.translate(bm, verts=verts, vec=(x0 + depth / 2, 0, 0))

    cone(r, r, length - head, 0)
    cone(rh, 0.0, head, length - head)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


# ----------------------------------------------------------------- geometría de S
def surface_mesh(N=200, flat=False):
    verts, cols, faces = [], [], []
    for j in range(N + 1):
        for i in range(N + 1):
            xs, ys = -W + 2 * W * i / N, -W + 2 * W * j / N
            z = h(xs, ys)
            verts.append((xs, ys, 0.0 if flat else z))
            cols.append(cmap(math.sqrt(z / HZ)))
    for j in range(N):
        for i in range(N):
            k = j * (N + 1) + i
            faces.append((k, k + 1, k + N + 2, k + N + 1))
    me = bpy.data.meshes.new("S")
    me.from_pydata(verts, [], faces)
    attr = me.color_attributes.new("col", "FLOAT_COLOR", "POINT")
    for k, c in enumerate(cols):
        attr.data[k].color = (*c, 1)
    for p in me.polygons:
        p.use_smooth = True
    return me


def contours(levels, N=240):
    """Marching squares sobre h(x, y); devuelve, por nivel, una lista de polilíneas (x, y)."""
    xs = [-W + 2 * W * i / N for i in range(N + 1)]
    g = [[h(xs[i], xs[j]) for i in range(N + 1)] for j in range(N + 1)]
    out = []
    for L in levels:
        pts, adj = {}, {}

        def cross(key, p, q, va, vb):
            t = (L - va) / (vb - va)
            pts[key] = (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
            return key

        for j in range(N):
            for i in range(N):
                c = [g[j][i], g[j][i + 1], g[j + 1][i + 1], g[j + 1][i]]
                P = [(xs[i], xs[j]), (xs[i + 1], xs[j]), (xs[i + 1], xs[j + 1]), (xs[i], xs[j + 1])]
                keys = [("h", i, j), ("v", i + 1, j), ("h", i, j + 1), ("v", i, j)]
                hit = []
                for e in range(4):
                    va, vb = c[e], c[(e + 1) % 4]
                    if (va < L) != (vb < L):
                        hit.append(cross(keys[e], P[e], P[(e + 1) % 4], va, vb))
                for k in range(0, len(hit) - 1, 2):
                    a_, b_ = hit[k], hit[k + 1]
                    adj.setdefault(a_, []).append(b_)
                    adj.setdefault(b_, []).append(a_)
        seen, polys = set(), []
        # primero los extremos (curvas abiertas que tocan el borde), luego los lazos cerrados
        for s in [k for k in adj if len(adj[k]) == 1] + list(adj):
            if s in seen:
                continue
            line, prev, cur = [s], None, s
            seen.add(s)
            while True:
                nxt = [k for k in adj[cur] if k != prev and k not in seen]
                if not nxt:
                    if len(line) > 2 and s in adj[cur]:
                        line.append(s)           # cerrar la elipse
                    break
                prev, cur = cur, nxt[0]
                line.append(cur)
                seen.add(cur)
            polys.append([pts[k] for k in line])
        out.append(polys)
    return out


LEVELS = [SMIN + (SMAX - SMIN) * ((i + 0.6) / 13) ** 2 for i in range(13)]
LEVEL_Z = [(L - SMIN) / (SMAX - SMIN) * HZ for L in LEVELS]


def fmt(v, d=0):
    s = f"{v:,.{d}f}".replace(",", " ")
    return s


# ================================================================= ESCENA 1 · SUPERFICIE
def escena_superficie():
    global TXT
    TXT = 2.1
    reset()
    setup_render()
    world((0.94, 0.96, 0.975), 0.38)
    cam = camera((7.9, -7.7, 6.0), (0.05, 0.15, 0.95), lens=38)

    floor = plane("Piso", 30, 30, (0, 0, -0.001), material("piso", (0.86, 0.89, 0.91), rough=0.55))
    base = plane("Base", W, W, (0, 0, 0.0), material("base", (0.97, 0.98, 0.985), rough=0.8))

    surf = link(bpy.data.objects.new("S(a,b)", surface_mesh()))
    m_s = vertex_color_material("superficie")
    p = m_s.node_tree.nodes.get("Principled BSDF")
    setin(p, ["Alpha"], 0.97)
    surf.data.materials.append(m_s)

    # malla: retícula siguiendo la superficie
    m_wire = material("malla", (0.03, 0.14, 0.19), rough=0.35, coat=0.3)
    grid_lines, K, M = [], 20, 160
    for k in range(K + 1):
        c = -W + 2 * W * k / K
        grid_lines.append([(c, -W + 2 * W * t / M, h(c, -W + 2 * W * t / M) + 0.004) for t in range(M + 1)])
        grid_lines.append([(-W + 2 * W * t / M, c, h(-W + 2 * W * t / M, c) + 0.004) for t in range(M + 1)])
    tubes("Malla", grid_lines, 0.0042, m_wire, res=2)

    # curvas de nivel: sobre la superficie y proyectadas al piso
    lv = contours(LEVEL_Z)
    m_iso = material("nivel", (0.98, 0.98, 0.96), rough=0.25, emit=0.15)
    m_iso_floor = material("nivel_piso", (0.05, 0.38, 0.52), rough=0.4)
    tubes("Nivel_superficie", [[(x, y, z + 0.006) for x, y in poly] for polys, z in zip(lv, LEVEL_Z) for poly in polys], 0.0075, m_iso)
    tubes("Nivel_piso", [[(x, y, 0.004) for x, y in pl] for pls in lv for pl in pls], 0.0065, m_iso_floor)

    # trazas por el óptimo
    M2 = 220
    tubes("Traza S(a, b*)", [[(-W + 2 * W * t / M2, 0, h(-W + 2 * W * t / M2, 0) + 0.012) for t in range(M2 + 1)]], 0.017,
          material("traza_a", (0.13, 0.55, 0.27), rough=0.3, coat=0.6))
    tubes("Traza S(a*, b)", [[(0, -W + 2 * W * t / M2, h(0, -W + 2 * W * t / M2) + 0.012) for t in range(M2 + 1)]], 0.017,
          material("traza_b", (0.42, 0.25, 0.75), rough=0.3, coat=0.6))

    # mínimo, plano tangente y tallo
    gold = material("oro", (0.95, 0.66, 0.18), rough=0.18, metal=1.0)
    sphere("Minimo", (0, 0, 0.06), 0.06, gold)
    plane("Plano tangente", 0.55, 0.55, (0, 0, 0.003), material("tangente", (0.85, 0.25, 0.22), rough=0.2, alpha=0.38, coat=0.4))
    tubes("Tallo", [[(0, 0, 0.12), (0, 0, 1.55)]], 0.006, material("tallo", (0.75, 0.22, 0.17), rough=0.4))

    # ejes y rótulos
    ink = material("tinta", (0.04, 0.06, 0.08), rough=0.5)
    accent = material("acento", (0.75, 0.22, 0.17), rough=0.45)
    teal = material("azul", (0.0, 0.36, 0.47), rough=0.45)
    tubes("Eje a", [[(-W, -W - 0.05, 0.002), (W + 0.25, -W - 0.05, 0.002)]], 0.012, ink)
    tubes("Eje b", [[(W + 0.05, -W, 0.002), (W + 0.05, W + 0.25, 0.002)]], 0.012, ink)
    tubes("Eje S", [[(-W, W, 0.0), (-W, W, HZ + 0.3)]], 0.012, ink)
    rot_floor = (0, 0, math.radians(45))
    for av in range(0, 7):
        xs = sx_of(av)
        if -W <= xs <= W:
            tubes(f"tick a{av}", [[(xs, -W - 0.05, 0.002), (xs, -W - 0.15, 0.002)]], 0.008, ink)
            text(str(av), (xs, -W - 0.34, 0.002), 0.2, ink, rot=rot_floor)
    for bv in (300, 500, 700, 900, 1100):
        ys = sy_of(bv)
        if -W <= ys <= W:
            tubes(f"tick b{bv}", [[(W + 0.05, ys, 0.002), (W + 0.15, ys, 0.002)]], 0.008, ink)
            text(str(bv), (W + 0.48, ys, 0.002), 0.2, ink, rot=rot_floor)
    for sv in (2, 3, 4, 5, 6, 7):
        zz = (sv * 1e8 - SMIN) / (SMAX - SMIN) * HZ
        if 0 < zz <= HZ:
            tubes(f"tick S{sv}", [[(-W, W, zz), (-W - 0.1, W, zz)]], 0.008, ink)
            text(f"{sv}", (-W - 0.25, W, zz), 0.18, ink, face=cam)
    text("a  (ms por grado)", (-0.9, -W - 1.55, 0.002), 0.2, ink, rot=rot_floor)
    text("b  (ms)", (W + 1.05, 0, 0.002), 0.26, ink, rot=(0, 0, math.pi / 2))
    text("S(a, b)  ×10⁸ ms²", (-W, W, HZ + 0.55), 0.22, ink, face=cam)
    text("mínimo: gradiente = 0", (-2.2, -2.14, 3.25), 0.2, accent, face=cam)
    text(f"a* = {A:.4f}", (-2.2, -2.14, 2.78), 0.19, ink, face=cam)
    text(f"b* = {B:.2f}", (-2.2, -2.14, 2.35), 0.19, ink, face=cam)
    text("S(a, b*)", (W + 0.15, 0, h(W, 0) + 0.25), 0.18, material("lt_a", (0.13, 0.55, 0.27)), face=cam)
    text("S(a*, b)", (0, W + 0.1, h(0, W) + 0.25), 0.18, material("lt_b", (0.42, 0.25, 0.75)), face=cam)

    # iluminación de estudio
    area_light("Clave", (-4.5, -5.5, 7.5), 585, 5.0, (0, 0, 0.5))
    area_light("Relleno", (7.0, -1.5, 3.5), 171, 6.0, (0, 0, 0.6), (0.92, 0.96, 1.0))
    area_light("Contra", (1.5, 7.0, 5.0), 292, 4.0, (0, 0, 0.8), (1.0, 0.95, 0.88))

    finish("superficie", "S_superficie_malla.png")


# ================================================================= ESCENA 2 · CURVAS DE NIVEL + −∇S
def escena_nivel():
    global TXT
    TXT = 2.1
    reset()
    setup_render()
    world((0.95, 0.965, 0.975), 0.45)
    cam = camera((0.75, -4.0, 12.2), (0.75, -0.2, 0), lens=50)

    plane("Piso", 30, 30, (0, 0, -0.02), material("piso", (0.9, 0.92, 0.93), rough=0.6))
    heat = link(bpy.data.objects.new("Mapa S", surface_mesh(N=220, flat=True)))
    m_h = vertex_color_material("mapa", rough=0.5, coat=0.25)
    heat.data.materials.append(m_h)

    lv = contours(LEVEL_Z[:11])
    tubes("Elipses", [[(x, y, 0.012) for x, y in poly] for polys in lv for poly in polys], 0.011,
          material("elipse", (0.98, 0.98, 0.96), rough=0.25, emit=0.1))

    # eje del valle: b = ȳ − a·x̄  (la recta de mínimos de cada sección)
    xbar, ybar = sx / n, sy / n
    valley = []
    for t in range(101):
        a = A - RA + 2 * RA * t / 100
        b = ybar - a * xbar
        if abs(sy_of(b)) <= W:
            valley.append((sx_of(a), sy_of(b), 0.02))
    tubes("Eje del valle", [valley], 0.009, material("valle", (0.97, 0.97, 0.97), rough=0.3))

    # flechas −∇S en coordenadas de la escena (perpendiculares a las elipses)
    am = arrow_mesh()
    m_ar = material("flecha", (0.02, 0.07, 0.12), rough=0.7)
    am.materials.append(m_ar)
    k = HZ / (SMAX - SMIN)
    G = 11
    for j in range(G):
        for i in range(G):
            xs, ys = -W + 2 * W * (i + 0.5) / G, -W + 2 * W * (j + 0.5) / G
            ga, gb = grad(a_of(xs), b_of(ys))
            dx, dy = -ga * (RA / W) * k, -gb * (RB / W) * k
            mag = math.hypot(dx, dy)
            if mag < 1e-9:
                continue
            ob = link(bpy.data.objects.new(f"g{i}_{j}", am))
            L = 0.16 + 0.17 * min(1.0, mag / 3.5)
            ob.scale = (L, 1.0, 1.0)
            ob.location = (xs - dx / mag * L / 2, ys - dy / mag * L / 2, 0.06)
            ob.rotation_euler = (0, 0, math.atan2(dy, dx))

    gold = material("oro", (0.95, 0.66, 0.18), rough=0.18, metal=1.0)
    sphere("Minimo", (0, 0, 0.08), 0.085, gold)

    ink = material("tinta", (0.04, 0.06, 0.08), rough=0.5)
    accent = material("acento", (0.75, 0.22, 0.17), rough=0.45)
    plane("Marco", W + 0.012, W + 0.012, (0, 0, -0.008), ink)
    for av in range(0, 7):
        xs = sx_of(av)
        if -W <= xs <= W:
            text(str(av), (xs, -W - 0.17, 0.0), 0.13, ink, rot=(0, 0, 0))
    for bv in (300, 500, 700, 900, 1100):
        ys = sy_of(bv)
        if -W <= ys <= W:
            text(str(bv), (-W - 0.1, ys, 0.0), 0.13, ink, rot=(0, 0, 0), align="RIGHT")
    text("pendiente a (ms por grado)", (0, -W - 0.4, 0), 0.15, ink, rot=(0, 0, 0))
    text("intercepto b (ms)", (-W - 0.6, 0, 0), 0.15, ink, rot=(0, 0, math.pi / 2))
    plate((0.95, 0.34, 0.11), 1.75, 0.34, rot=(0, 0, 0))
    text(f"mínimo ({A:.2f}, {B:.1f})", (0.95, 0.34, 0.12), 0.105, accent, rot=(0, 0, 0))
    text("flechas = −gradiente", (W + 0.2, W - 0.1, 0), 0.11, ink, rot=(0, 0, 0), align="LEFT")
    text("(hacia abajo)", (W + 0.2, W - 0.42, 0), 0.11, ink, rot=(0, 0, 0), align="LEFT")
    text("elipses inclinadas", (W + 0.2, W - 1.0, 0), 0.11, ink, rot=(0, 0, 0), align="LEFT")
    text("porque 2Σx ≠ 0", (W + 0.2, W - 1.32, 0), 0.11, ink, rot=(0, 0, 0), align="LEFT")
    text("2Σx = 107 100", (W + 0.2, W - 1.64, 0), 0.11, ink, rot=(0, 0, 0), align="LEFT")
    text("línea blanca:", (W + 0.2, W - 2.2, 0), 0.11, ink, rot=(0, 0, 0), align="LEFT")
    text("b = ȳ − a·x̄", (W + 0.2, W - 2.52, 0), 0.11, ink, rot=(0, 0, 0), align="LEFT")
    area_light("Clave", (-3.5, -4.0, 8.0), 495, 5.0, (0, 0, 0))
    area_light("Relleno", (4.5, 3.0, 6.0), 171, 6.0, (0, 0, 0), (0.92, 0.96, 1.0))

    finish("nivel", "S_nivel_gradiente.png")


# ================================================================= ESCENA 3 · RECTA SOBRE LOS DATOS
def escena_recta():
    global TXT
    TXT = 2.0
    reset()
    setup_render()
    world((0.95, 0.96, 0.97), 0.45)
    SXs, Y0, SY = 1 / 22.5, 300.0, 1 / 400.0             # x: grados → escena,  y: ms → escena
    YMAX = 2500.0
    P = lambda x, y: (x * SXs, 0.0, (y - Y0) * SY)
    cam = camera((4.25, -22.8, 2.95), (4.25, 0, 2.9), lens=58)

    board = material("tablero", (0.975, 0.98, 0.985), rough=0.7)
    plane("Tablero", 30, 30, (4, 0.25, 0), board, rot=(math.pi / 2, 0, 0))
    plane("Piso", 30, 30, (4, 0, -0.35), material("piso", (0.88, 0.9, 0.92), rough=0.6))

    grid = material("cuadricula", (0.80, 0.86, 0.89), rough=0.6)
    ink = material("tinta", (0.04, 0.06, 0.08), rough=0.5)
    for xv in range(0, 181, 30):
        x0, _, _ = P(xv, Y0)
        tubes(f"gx{xv}", [[(x0, 0.2, 0), (x0, 0.2, (YMAX - Y0) * SY)]], 0.008, grid)
        text(f"{xv}°", (x0, 0.1, -0.22), 0.2, ink)
    for yv in range(400, int(YMAX) + 1, 300):
        _, _, z0 = P(0, yv)
        tubes(f"gy{yv}", [[(-0.15, 0.2, z0), (180 * SXs + 0.15, 0.2, z0)]], 0.008, grid)
        text(f"{yv}", (-0.35, 0.1, z0), 0.18, ink, align="RIGHT")
    tubes("Eje x", [[(-0.15, 0.15, 0), (180 * SXs + 0.3, 0.15, 0)]], 0.016, ink)
    tubes("Eje y", [[(-0.15, 0.15, 0), (-0.15, 0.15, (YMAX - Y0) * SY + 0.2)]], 0.016, ink)
    text("ángulo de la R  (grados)", (4.0, 0.1, -0.62), 0.24, ink)
    text("tiempo (ms)", (-1.45, 0.1, 2.75), 0.24, ink, rot=(math.pi / 2, -math.pi / 2, 0))

    # ensayos individuales: un color y una columna fija por participante (el corrimiento es solo visual)
    ids = sorted(set(WHO))
    colores = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4", "#00bcd4", "#f032e6", "#8db600",
               "#ff9ebb", "#008080", "#9a6324", "#800000", "#2fd67a", "#808000", "#ffb300", "#000075", "#8a8a8a"]
    assert len(ids) == len(colores) == 17

    def lineal(hx):
        v = [int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in v)

    mallas = {}
    for k, pid in enumerate(ids):
        m_p = material("color_" + pid, (0, 0, 0), rough=1.0)
        pr = m_p.node_tree.nodes.get("Principled BSDF")
        setin(pr, ["Specular IOR Level", "Specular"], 0.0)
        setin(pr, ["Emission Color", "Emission"], (*lineal(colores[k]), 1))
        setin(pr, ["Emission Strength"], 1.15)
        me = bpy.data.meshes.new("pt_" + pid)
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.045)
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = True
        me.materials.append(m_p)
        mallas[pid] = (k, me, m_p)
    hidden = 0
    for x, y, pid in zip(X, Y, WHO):
        if y > YMAX:
            hidden += 1
            continue
        k, me, _ = mallas[pid]
        ob = link(bpy.data.objects.new("e_" + pid, me))
        px, _, pz = P(x + (k - 8) * 0.65, y)
        ob.location = (px, -0.08, pz)
        ob.visible_shadow = False
    text("persona", (9.95, -0.3, 5.5), 0.13, ink)
    for pid, (k, me, m_p) in mallas.items():
        zz = 5.05 - k * 0.3
        sphere("leyenda_" + pid, (9.55, -0.3, zz), 0.09, m_p, seg=24)
        text(pid, (9.8, -0.3, zz), 0.11, ink, align="LEFT")

    # recta óptima y medias con residuos
    red = material("recta", (0.75, 0.2, 0.15), rough=0.25, coat=0.7)
    tubes("Recta", [[P(-6, A * -6 + B), P(186, A * 186 + B)]], 0.035, red)
    gold = material("media_negra", (0.008, 0.008, 0.01), rough=0.35)
    m_res = material("residuo", (0.1, 0.1, 0.1), rough=0.4)
    for x, yb in MEANS:
        sphere(f"media {x:.0f}", (P(x, yb)[0], -0.25, P(x, yb)[2]), 0.1, gold)
        tubes(f"res {x:.0f}", [[(P(x, yb)[0], -0.25, P(x, yb)[2]), (P(x, A * x + B)[0], -0.25, P(x, A * x + B)[2])]], 0.012, m_res)
    xb, yb = sx / n, sy / n

    accent = material("acento", (0.75, 0.2, 0.15), rough=0.45)
    for x, yb in MEANS:                      # valor de cada media sobre la gráfica
        px, _, pz = P(x, yb)
        px += 0.42 if x == 0 else 0.0
        plate((px, -0.55, pz + 0.52), 0.9, 0.42)
        text(f"{yb:.0f}", (px, -0.57, pz + 0.52), 0.16, ink)
    text(f"ŷ = {A:.4f}·x + {B:.2f}", (1.7, -0.3, 6.35), 0.26, accent)
    text("negro = media de cada ángulo (ms)", (6.3, -0.3, 6.45), 0.12, ink)
    text("colores = cada ensayo, por persona", (6.3, -0.3, 6.05), 0.12, ink)
    text(f"{hidden} ensayos > {int(YMAX)} ms no se ven, pero sí cuentan", (4.0, -0.3, 5.72), 0.09, ink)

    area_light("Clave", (-2.5, -8.0, 7.5), 675, 6.0, (4, 0, 2.2))
    area_light("Relleno", (10.0, -7.0, 3.0), 225, 6.0, (4, 0, 2.2), (0.92, 0.96, 1.0))

    finish("recta", "recta_datos.png")


def finish(tag, png):
    sc = bpy.context.scene
    sc.render.filepath = os.path.join(OUT, png)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blender", f"graficas_v2_{tag}.blend"))
    bpy.ops.render.render(write_still=True)
    print(f"[NeuroCode] listo: {sc.render.filepath}")


for name, fn in (("superficie", escena_superficie), ("nivel", escena_nivel), ("recta", escena_recta)):
    if name in WHICH:
        fn()
