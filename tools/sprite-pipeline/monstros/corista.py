# Corista de Osso (adicional da Irmã Celeste, andar 2): esqueleto de menino do coro que virou estátua num nicho
# da capela. Imóvel: batina vermelho-escura apodrecida e sobrepeliz de linho rasgada até o chão, gola de renda,
# crânio pequeno de mandíbula solta, hinário aberto nas duas mãos, coberto de pó de pedra e cera de vela.
# Só fica vulnerável quando canta: os olhos e a boca acendem (luz fria) e a mandíbula canta.
# Animações: idle (estátua, apagada), sing (loop, canta e brilha), hit, death (desmorona em ossos e pano).
# Reaproveita o vestido de painéis e o settle() da Carpideira de Ossos.
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion
from mrig import *
import carpideira_de_ossos as CP
from carpideira_de_ossos import tube, skirt_wave, PANELS, SKB

INFO = {"px": 224, "target_z": .95, "rim": (.6, .7, .9), "colors": 40, "samples": 36,
        "loops": ("idle", "sing"), "fps": {"idle": 2, "sing": 8, "hit": 12, "death": 10}}
def set_variant(name): pass

BONES = {k: v for k, v in CP.BONES.items() if k != "censer"}
BONES["voice"] = ((0, -.05, 1.8), (0, -.05, 1.9), "head")

def build():
    bone = stained("co_osso", (.5, .47, .4), stain=(.2, .19, .17), amount=.6, scale=5, rough=.8,
                   blotch=(.33, .32, .3), blotch_amt=.7, grime=1.2)
    cassock = stained("co_batina", (.13, .03, .03), stain=(.15, .14, .13), amount=.55, scale=3, rough=.9,
                      blotch=(.06, .02, .02), blotch_amt=.6, grime=1.6)
    surplice = stained("co_sobrepeliz", (.36, .34, .29), stain=(.14, .12, .1), amount=.6, scale=3, rough=.95,
                       blotch=(.22, .21, .19), blotch_amt=.7, grime=1.6)
    lace = stained("co_renda", (.42, .4, .34), stain=(.15, .13, .1), amount=.5, scale=6, rough=.9, grime=1.0)
    paper = stained("co_papel", (.42, .36, .25), stain=(.18, .12, .06), amount=.6, scale=6, rough=.9, grime=.8)
    leather = stained("co_couro", (.07, .045, .03), stain=(.1, .1, .09), amount=.4, scale=4, rough=.7, grime=.8)
    wax = stained("co_cera", (.6, .54, .4), stain=(.3, .22, .1), amount=.3, scale=8, rough=.4, grime=.2)
    hole = mat("co_buraco", (.004, .004, .005), 0, .95)
    glow = mat("co_canto", (.7, .85, 1), emit=(.55, .78, 1), strength=18)

    R = Rig("corista_de_osso", BONES, ground=None); P = R.P
    R.gexclude = {"veil1", "veil2", "voice"}
    zs = [1.05, .85, .62, .4, .2, .02]
    sk = tube("batina", cassock, [(0, 0, z) for z in zs], [(.14, .12), (.17, .15), (.2, .17), (.22, .19), (.24, .21), (.27, .24)],
              seg=28, jag=.03, seed=2, holes=.03, thick=.012)
    R.bind(sk, ["hips"] + SKB, power=4)
    sp = tube("sobrepeliz", surplice, [(0, -.004, z) for z in (1.55, 1.42, 1.2, .95, .7)],
              [(.12, .1), (.22, .16), (.25, .19), (.28, .22), (.32, .26)], seg=28, jag=.12, seed=5, holes=.12, thick=.01)
    R.bind(sp, ["chest", "spine", "hips"] + SKB, power=4)
    col = tube("gola", lace, [(0, -.01, 1.6), (0, -.005, 1.53)], [(.075, .065), (.17, .13)], seg=24, jag=.03, seed=8, thick=.006)
    ch = [col]
    for k in range(12):  # babados da gola
        a = 2*math.pi*k/12
        ch.append(prim("primitive_uv_sphere_add", lace, (.16*math.cos(a), .12*math.sin(a), 1.53), (.03, .03, .012), segments=6, ring_count=4))
    # cera de vela escorrida nos ombros (as velas dos nichos pingaram nele por anos)
    rr = random.Random(3)
    for k in range(6):
        x = rr.uniform(-.18, .18); q = Vector((x, rr.uniform(-.05, .05), 1.56 - abs(x)*.4))
        ch.append(along("primitive_cylinder_add", wax, q, q + Vector((0, -.02, -rr.uniform(.08, .2))), .008, vertices=5))
    R.rigid(ch, "chest")
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        d = (el - sh).normalized()
        slv = tube(f"manga.{n}", surplice, [sh - d*.02, sh.lerp(el, .5), el, el + (wr - el)*.4],
                   [(.06, .055), (.07, .065), (.09, .08), (.13, .11)], seg=16, jag=.08, seed=12 + s, holes=.15, thick=.008)
        R.bind(slv, ["chest", f"upper_arm.{n}", f"forearm.{n}"], power=4)
        R.rigid([along("primitive_cylinder_add", bone, el, wr, .012, vertices=6)], f"forearm.{n}")
        o, ax, u, sd = R.frame(f"hand.{n}")
        hp = [prim("primitive_uv_sphere_add", bone, o + ax*.025, (.025, .016, .03), segments=8, ring_count=5)]
        for f in range(4):
            base = o + ax*.045 + sd*(-.024 + .016*f)
            hp.append(along("primitive_cylinder_add", bone, base, base + ax*.05 + u*.02, .006, vertices=5))
        R.rigid(hp, f"hand.{n}")
    # hinário aberto seguro pelas duas mãos (preso ao peito, as mãos o seguram na pose base)
    bc = Vector((0, -.27, 1.32))
    bk = []
    for s in (1, -1):
        cov = prim("primitive_cube_add", leather, bc + Vector((.075*s, .01, 0)), (.075, .006, .1), rot=(-35, 0, -12*s)); bk.append(cov)
        pg = prim("primitive_cube_add", paper, bc + Vector((.07*s, .002, .005)), (.068, .012, .093), rot=(-35, 0, -12*s)); bk.append(pg)
    bk.append(along("primitive_cylinder_add", leather, bc + Vector((0, .015, -.08)), bc + Vector((0, .015, .09)), .012, vertices=6))
    bk.append(along("primitive_cube_add", cassock, bc + Vector((0, -.01, -.06)), bc + Vector((.01, -.02, -.2)), .008))  # fita marcadora
    R.rigid(bk, "chest")
    # crânio de criança, mandíbula, órbitas; olhos e boca acendem só cantando (osso "voice")
    hc = Vector((0, -.03, 1.74))
    hd = [prim("primitive_uv_sphere_add", bone, hc, (.078, .088, .09), segments=14, ring_count=9),
          prim("primitive_uv_sphere_add", bone, hc + Vector((0, -.05, -.04)), (.05, .045, .035), segments=10, ring_count=6)]
    for s in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", hole, hc + Vector((.03*s, -.075, .005)), (.022, .012, .02), segments=8, ring_count=6))
    hd.append(prim("primitive_uv_sphere_add", hole, hc + Vector((0, -.09, -.035)), (.01, .008, .012), segments=6, ring_count=4))
    for k in range(6):
        x = -.025 + .01*k
        hd.append(along("primitive_cone_add", bone, (x, hc.y - .083, hc.z - .055), (x, hc.y - .085, hc.z - .072), .005, vertices=4, radius1=1, radius2=.2))
    R.rigid(hd, "head")
    jw = [prim("primitive_uv_sphere_add", bone, hc + Vector((0, -.05, -.095)), (.045, .04, .016), segments=10, ring_count=6)]
    R.rigid(jw, "jaw")
    gl = []
    for s in (1, -1):
        gl.append(prim("primitive_uv_sphere_add", glow, hc + Vector((.03*s, -.088, .005)), (.016, .01, .014), segments=8, ring_count=6))
    gl.append(prim("primitive_uv_sphere_add", glow, hc + Vector((0, -.085, -.075)), (.024, .014, .02), segments=8, ring_count=6))
    gl.append(prim("primitive_torus_add", glow, hc + Vector((0, .06, .06)), (1, 1, 1), major_radius=.13, minor_radius=.007,
                   major_segments=24, minor_segments=4, rot=(70, 0, 0)))  # auréola de luz fria atrás da cabeça
    R.rigid(gl, "voice")
    R.arm.scale = [1.0]*3
    return R, INFO

G = {"ground": None}
BASE = {"spine": {"x": 2}, "chest": {"x": 0}, "head": {"x": 6},
        "upper_arm.L": {"x": -45, "y": 4, "z": -24}, "upper_arm.R": {"x": -45, "y": -4, "z": 24},
        "forearm.L": {"bend": -70}, "forearm.R": {"bend": -70}, "hand.L": {"x": -10}, "hand.R": {"x": -10}}
AIM0 = {"veil1": (0, .3, -1), "veil2": (0, .22, -1)}

def M(*p): return merge(G, {k: dict(v) for k, v in BASE.items()}, {"root": (0, 0, .0)}, *p)

def finish(frames):
    out = []
    for p in frames:
        p = dict(p); a = dict(AIM0); a.update(p.get("aim") or {}); p["aim"] = a; out.append(p)
    return out

def anims(R):
    off = {"scale": {"voice": .001}}
    idle = [M(skirt_wave(0, 0), off), M(skirt_wave(0, 0), off)]
    sing = []
    for i in range(8):
        t = i/8*2*math.pi; b = math.sin(t)
        sing.append(M(skirt_wave(t, .3), {"jaw": {"x": 22 + 14*math.sin(2*t)}, "head": {"x": -10 + 4*b, "z": 6*math.cos(t)},
                                          "chest": {"x": -4 + 2*b}, "scale": {"voice": .9 + .2*math.sin(2*t)}}))
    hitp = M(skirt_wave(1, .8), {"chest": {"x": -14, "z": 8}, "head": {"x": -16, "z": 12}, "jaw": {"x": 20}, "root": (0, .06, 0)}, off)
    hit = [hitp, lerp_pose(hitp, M(skirt_wave(0, 0), off), .5), M(skirt_wave(0, 0), off)]
    def spread(f, down):
        aim = {}
        for a, ba, bb in PANELS:
            o = Vector((math.cos(a), math.sin(a), 0)); aim[ba] = tuple(o*f + Vector((0, 0, -1))); aim[bb] = tuple(o + Vector((0, 0, -down)))
        return aim
    crack = M(skirt_wave(1, .6), {"chest": {"x": 10, "z": -10}, "head": {"x": 30, "z": 20}, "jaw": {"x": 35}}, off)
    slump = M({"root": (0, 0, -.4), "spine": {"x": 30}, "chest": {"x": 25}, "head": {"x": 40, "z": 25}, "jaw": {"x": 30},
               "upper_arm.L": {"x": 10}, "upper_arm.R": {"x": 15}, "aim": dict(spread(.6, 1.2))}, off)
    pile = M({"root": (0, 0, -.75), "hips": {"x": 25}, "spine": {"x": 45}, "chest": {"x": 30}, "head": {"x": 15, "z": 50}, "jaw": {"x": 35},
              "upper_arm.L": {"x": -30, "y": 20}, "upper_arm.R": {"x": -50, "y": -25}, "aim": dict(spread(1.3, .25))}, off)
    death = keys_to_frames([(0, hitp), (.25, crack), (.55, slump), (.8, pile), (1, pile)], 10)
    death = finish(death); CP.settle(R, death[4:])
    return {"idle": finish(idle), "sing": finish(sing), "hit": finish(hit), "death": death}
