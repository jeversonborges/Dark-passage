# Pisos do Novo Éden (kit "Gênesis", 15/10/2026). Uso: python eden_tiles.py <saida> [tipo ...]
#   relva_eden     relva e trevo com florzinhas brancas e douradas (o chão do jardim)
#   musgo_pedra    lajes velhas de pedra engolidas pelo musgo (Viveiro, caminhos, a Nascente)
#   margem_rio     areia clara e seixos da beira dos quatro rios
#   terra_jardim   terra escura revolvida dos canteiros da Enxertia
#   trilha_eden    terra batida clara das estradinhas, com lajes chatas de passo (17/10: "para entender onde é estrada")
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit as K
from kit import N, L, ramp, mix, math_, noise, voronoi, bump
from mathutils import Vector

def relva(nt, b, v, w, seed):
    n = noise(nt, v, w, 1.6, 8, .6, seed); n2 = noise(nt, v, w, 14, 5, .55, seed + 4)
    r = ramp(nt, [(.3, (.012, .045, .012)), (.55, (.03, .09, .025)), (.8, (.07, .16, .05))]); L(nt, n.outputs["Fac"], r.inputs[0])
    col = mix(nt, r.outputs[0], n2.outputs["Color"], .3, 'OVERLAY')
    tv = voronoi(nt, v, w, 26, 'F1', seed + 5)               # tufos de trevo
    tr = ramp(nt, [(0, (1, 1, 1)), (.2, (0, 0, 0))]); L(nt, tv.outputs["Distance"], tr.inputs[0])
    col = mix(nt, col, (.09, .2, .07), math_(nt, 'MULTIPLY', tr.outputs[0], .7))
    tm = noise(nt, v, w, 2.4, 4, .5, seed + 15)              # terra entre a relva
    tmr = ramp(nt, [(.6, (0, 0, 0)), (.68, (1, 1, 1))]); L(nt, tm.outputs["Fac"], tmr.inputs[0])
    col = mix(nt, col, (.035, .025, .015), math_(nt, 'MULTIPLY', tmr.outputs[0], .6))
    fv = voronoi(nt, v, w, 9, 'F1', seed + 9)                 # florzinhas
    fr = ramp(nt, [(0, (1, 1, 1)), (.08, (0, 0, 0))]); L(nt, fv.outputs["Distance"], fr.inputs[0])
    fm = noise(nt, v, w, 1.4, 3, .5, seed + 12)
    fmr = ramp(nt, [(.45, (0, 0, 0)), (.55, (1, 1, 1))]); L(nt, fm.outputs["Fac"], fmr.inputs[0])
    fc = mix(nt, (.6, .58, .45), (.7, .5, .12), math_(nt, 'GREATER_THAN', n2.outputs["Fac"], .55))
    col = mix(nt, col, fc, math_(nt, 'MULTIPLY', fr.outputs[0], fmr.outputs[0]))
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .9
    bump(nt, b, math_(nt, 'ADD', math_(nt, 'MULTIPLY', n.outputs["Fac"], .6), math_(nt, 'MULTIPLY', tr.outputs[0], .5)), .5, .04)

def musgo_pedra(nt, b, v, w, seed):
    vo = voronoi(nt, v, w, 2.2, 'DISTANCE_TO_EDGE', seed, .6); vc = voronoi(nt, v, w, 2.2, 'F1', seed, .6)
    gap = ramp(nt, [(.0, (0, 0, 0)), (.06, (1, 1, 1))]); L(nt, vo.outputs["Distance"], gap.inputs[0])
    n = noise(nt, v, w, 3, 7, .6, seed + 2); n2 = noise(nt, v, w, 11, 4, .5, seed + 3)
    r = ramp(nt, [(.3, (.06, .058, .052)), (.6, (.12, .115, .1)), (.85, (.19, .18, .16))]); L(nt, n.outputs["Fac"], r.inputs[0])
    col = mix(nt, r.outputs[0], vc.outputs["Color"], .18, 'OVERLAY')
    col = mix(nt, col, n2.outputs["Color"], .15, 'OVERLAY')
    mn = noise(nt, v, w, 2.0, 5, .6, seed + 7)                # musgo engolindo as lajes (nas juntas e em manchas)
    mr = ramp(nt, [(.42, (0, 0, 0)), (.6, (1, 1, 1))]); L(nt, mn.outputs["Fac"], mr.inputs[0])
    musgo = math_(nt, 'MAXIMUM', mr.outputs[0], math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', 1.0, gap.outputs[0]), .9))
    mc = mix(nt, (.025, .07, .015), (.06, .13, .03), n2.outputs["Fac"])
    col = mix(nt, col, mc, musgo)
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .85
    bump(nt, b, math_(nt, 'SUBTRACT', math_(nt, 'ADD', gap.outputs[0], math_(nt, 'MULTIPLY', n2.outputs["Fac"], .3)), math_(nt, 'MULTIPLY', musgo, .3)), .7, .06)

def margem(nt, b, v, w, seed):
    n = noise(nt, v, w, 2.0, 8, .6, seed); n2 = noise(nt, v, w, 16, 4, .5, seed + 4)
    r = ramp(nt, [(.3, (.08, .07, .055)), (.6, (.17, .15, .11)), (.85, (.26, .23, .17))]); L(nt, n.outputs["Fac"], r.inputs[0])
    col = mix(nt, r.outputs[0], n2.outputs["Color"], .2, 'OVERLAY')
    pv = voronoi(nt, v, w, 14, 'F1', seed + 5, .9)            # seixos
    pr = ramp(nt, [(0, (1, 1, 1)), (.18, (0, 0, 0))]); L(nt, pv.outputs["Distance"], pr.inputs[0])
    pc = mix(nt, (.09, .09, .085), (.2, .19, .17), pv.outputs["Color"])
    pm = noise(nt, v, w, 1.6, 3, .5, seed + 8); pmr = ramp(nt, [(.48, (0, 0, 0)), (.58, (1, 1, 1))]); L(nt, pm.outputs["Fac"], pmr.inputs[0])
    seixo = math_(nt, 'MULTIPLY', pr.outputs[0], pmr.outputs[0])
    col = mix(nt, col, pc, seixo)
    mn = noise(nt, v, w, 3.0, 4, .5, seed + 11); mr = ramp(nt, [(.58, (0, 0, 0)), (.68, (1, 1, 1))]); L(nt, mn.outputs["Fac"], mr.inputs[0])
    col = mix(nt, col, (.03, .07, .02), math_(nt, 'MULTIPLY', mr.outputs[0], .6))   # musgo da umidade
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .8
    bump(nt, b, math_(nt, 'ADD', math_(nt, 'MULTIPLY', n2.outputs["Fac"], .3), math_(nt, 'MULTIPLY', seixo, 1.0)), .6, .05)

def terra_jardim(nt, b, v, w, seed):
    n = noise(nt, v, w, 2.2, 8, .6, seed); n2 = noise(nt, v, w, 18, 4, .5, seed + 4)
    r = ramp(nt, [(.3, (.018, .013, .009)), (.6, (.045, .032, .02)), (.85, (.085, .065, .04))]); L(nt, n.outputs["Fac"], r.inputs[0])
    col = mix(nt, r.outputs[0], n2.outputs["Color"], .25, 'OVERLAY')
    wv = N(nt, "ShaderNodeTexWave", wave_type='BANDS', bands_direction='X'); wv.inputs["Scale"].default_value = 3.0; wv.inputs["Distortion"].default_value = 4.0
    L(nt, v, wv.inputs["Vector"])                              # sulcos do rastelo
    col = mix(nt, col, (.012, .009, .006), math_(nt, 'MULTIPLY', wv.outputs["Fac"], .35))
    bv = voronoi(nt, v, w, 7, 'F1', seed + 9); br = ramp(nt, [(0, (1, 1, 1)), (.1, (0, 0, 0))]); L(nt, bv.outputs["Distance"], br.inputs[0])
    bm = noise(nt, v, w, 1.5, 3, .5, seed + 13); bmr = ramp(nt, [(.5, (0, 0, 0)), (.6, (1, 1, 1))]); L(nt, bm.outputs["Fac"], bmr.inputs[0])
    col = mix(nt, col, (.08, .18, .05), math_(nt, 'MULTIPLY', br.outputs[0], bmr.outputs[0]))   # brotos
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .95
    bump(nt, b, math_(nt, 'ADD', math_(nt, 'MULTIPLY', n2.outputs["Fac"], .5), math_(nt, 'MULTIPLY', wv.outputs["Fac"], .5)), .6, .05)

def trilha(nt, b, v, w, seed):
    # terra batida cor de palha, bem mais clara e quente que a relva: o olho acha o caminho de longe
    n = noise(nt, v, w, 1.8, 8, .6, seed); n2 = noise(nt, v, w, 20, 4, .5, seed + 4)
    r = ramp(nt, [(.3, (.2, .15, .095)), (.6, (.32, .25, .16)), (.85, (.44, .35, .23))]); L(nt, n.outputs["Fac"], r.inputs[0])
    col = mix(nt, r.outputs[0], n2.outputs["Color"], .18, 'OVERLAY')
    gv = voronoi(nt, v, w, 40, 'F1', seed + 3, 1.0)           # grão de areia e cascalho miúdo
    gr = ramp(nt, [(0, (1, 1, 1)), (.25, (0, 0, 0))]); L(nt, gv.outputs["Distance"], gr.inputs[0])
    col = mix(nt, col, mix(nt, (.08, .06, .04), (.34, .29, .2), gv.outputs["Color"]), math_(nt, 'MULTIPLY', gr.outputs[0], .5))
    lv = voronoi(nt, v, w, 3.2, 'F1', seed + 7, .8)            # lajes chatas de passo, gastas, espalhadas
    le = voronoi(nt, v, w, 3.2, 'DISTANCE_TO_EDGE', seed + 7, .8)
    lr = ramp(nt, [(.08, (0, 0, 0)), (.13, (1, 1, 1))]); L(nt, le.outputs["Distance"], lr.inputs[0])
    lsel = ramp(nt, [(.55, (0, 0, 0)), (.6, (1, 1, 1))]); L(nt, lv.outputs["Color"], lsel.inputs[0])
    laje = math_(nt, 'MULTIPLY', lr.outputs[0], lsel.outputs[0])
    lc = mix(nt, (.34, .3, .23), (.46, .41, .32), n2.outputs["Fac"])
    col = mix(nt, col, lc, math_(nt, 'MULTIPLY', laje, .85))
    rn = noise(nt, v, w, 2.6, 4, .5, seed + 11)                # sulcos de pés e rodas, mais escuros
    rr = ramp(nt, [(.62, (0, 0, 0)), (.7, (1, 1, 1))]); L(nt, rn.outputs["Fac"], rr.inputs[0])
    col = mix(nt, col, (.13, .095, .06), math_(nt, 'MULTIPLY', rr.outputs[0], .4))
    tv = voronoi(nt, v, w, 11, 'F1', seed + 13)                # tufos raros de trevo que resistem ao pisoteio
    tr = ramp(nt, [(0, (1, 1, 1)), (.12, (0, 0, 0))]); L(nt, tv.outputs["Distance"], tr.inputs[0])
    tm = noise(nt, v, w, 1.7, 3, .5, seed + 15); tmr = ramp(nt, [(.6, (0, 0, 0)), (.66, (1, 1, 1))]); L(nt, tm.outputs["Fac"], tmr.inputs[0])
    col = mix(nt, col, (.04, .09, .025), math_(nt, 'MULTIPLY', tr.outputs[0], tmr.outputs[0]))
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .92
    bump(nt, b, math_(nt, 'ADD', math_(nt, 'MULTIPLY', n2.outputs["Fac"], .3), math_(nt, 'MULTIPLY', laje, .5)), .5, .05)

K.EXTRA_GROUND.update({"relva_eden": relva, "musgo_pedra": musgo_pedra, "margem_rio": margem, "terra_jardim": terra_jardim, "trilha_eden": trilha})

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    out = argv[0]; os.makedirs(out, exist_ok=True)
    kinds = argv[1:] or ["relva_eden", "musgo_pedra", "margem_rio", "terra_jardim", "trilha_eden"]
    Nn = 4; P = Nn*K.T
    for kind in kinds:
        sc = K.reset(); sc.render.film_transparent = False
        cam = K.make_cam(); K.lights(False)
        bpy.ops.mesh.primitive_plane_add(size=P*3, location=(P/2, P/2, 0))
        pl = bpy.context.object
        pl.data.materials.append(K.mat_ground(kind, (P, P), 1.0))
        corners = [Vector((x, y, 0)) for x in (-K.T, P + K.T) for y in (-K.T, P + K.T)]
        meta = K.render_asset(f"{out}/{kind}", [], anchor=(0, 0, 0), samples=int(os.environ.get("SAMPLES", 64)), pad=0, shadows=False, extra=corners)
        centers = {}
        for i in range(Nn):
            for j in range(Nn):
                x, y = K.screen_xy(((i + .5)*K.T, (j + .5)*K.T, 0)); ax, ay = K.screen_xy((0, 0, 0))
                centers[f"{i}_{j}"] = [meta["anchor"][0] + (x - ax)*K.PX_M, meta["anchor"][1] - (y - ay)*K.PX_M]
        meta["centers"] = centers
        json.dump(meta, open(f"{out}/{kind}.json", "w")); print("OK", kind, flush=True)
