# Familiar do Cultista, 4ª forma (nível 60 do dono): o Líder dos Demônios em escala de pet (~3,3 m).
# Pedido do Jefin (2026-10-17): "a última evolução do pet do cultista será o demônio líder lvl 60".
# Reaproveita o modelo de lider_dos_demonios.py (carne e ferro negro com rachaduras de lava, chifres, asas rasgadas)
# e acrescenta as animações de pet: idle, walk, attack (garra de lava que bate em área), hit e death.
# Uso: blender -b -P render.py -- familiar_lider /tmp/brutos/familiar_lider
import math
import lider_dos_demonios as L
from mrig import merge, lerp_pose, keys_to_frames
from amenti import mote_pose, couro, aco, lava, glow, blade, spike, rest_uv
from base_rig import along
from mathutils import Vector

L.SCALE = 1.8                      # 5,1 m no lorde -> ~3,3 m no pet
INFO = dict(L.INFO, px=448, target_z=1.95, samples=int(L.INFO["samples"]),
            loops=("idle", "walk"), fps={"idle": 6, "walk": 9, "attack": 12, "hit": 12, "death": 9})
def set_variant(name): pass

def espadao(R):
    """Espadão infernal (pedido do Jefin, 0.9.8): lâmina reta de ferro negro com rachaduras de lava, runas gravadas
    em brasa e chamas nas bordas, presa na manopla direita. Cai reto da mão até quase o chão, como o Líder arrastando
    a arma. Tudo na cor de lava do próprio Líder (um só emissivo)."""
    o_, ax, u, sd = R.frame("hand.R")
    d = (Vector((0, 0, -1)) + ax*.3).normalized()        # lâmina para baixo, puxada para fora
    side = Vector((0, 1, 0)); side = (side - d*side.dot(d)).normalized()
    nrm = d.cross(side).normalized()
    g0 = o_ + ax*.06                                     # punho dentro da manopla
    cabo = couro("fl_cabo", rgb=(.12, .05, .03), rough=.5)
    guarda = aco("fl_guarda", rgb=(.2, .17, .15), rough=.45, dirt=.7)
    ferro, s_fer = lava("fl_lamina", base=(.3, .29, .28), crack=L.LAVA, amount=.45, cscale=5.0, width=.02, seed=5.0,
                        metal=.9, rough=.3, worn=(.55, .52, .5))
    runa = glow("fl_runa", L.LAVA, 6.0)
    chama = glow("fl_chama", L.LAVA, 3.0)
    R.glow.append((s_fer, s_fer.default_value))
    for m in (runa, chama):
        sk_ = m.node_tree.nodes["Emission"].inputs["Strength"]; R.glow.append((sk_, sk_.default_value))
    pegada = g0 + d*.14
    g_c = pegada + d*.02                                 # linha do guarda
    peças = [along("primitive_cylinder_add", cabo, g0, pegada, .03, vertices=12)]
    for k in range(3):                                   # enrolado de couro no cabo
        c = g0 + d*(.02 + .035*k)
        peças.append(along("primitive_cylinder_add", cabo, c - side*.03, c + side*.03, .03, vertices=10))
    peças.append(along("primitive_cylinder_add", guarda, g_c - side*.26, g_c + side*.26, .028, vertices=10))
    for s in (-1, 1):                                    # pontas do guarda em espinho
        ponta = g_c + side*.26*s
        peças.append(spike(guarda, ponta, ponta + side*.09*s + d*.05, .03, verts=5))
    peças.append(prim_sphere(guarda, g_c, .03))          # pomo do guarda
    peças.append(blade("fl_lamina_obj", ferro, g_c + d*.03, d, side, .95, .075, .045, th=.02, n=18, tipf=.2))
    # runas: traços em brasa gravados na lâmina, cruzando o fio
    runas = []
    for k, t in enumerate((.12, .26, .4, .54, .68)):
        c = g_c + d*(.03 + .95*t)
        larg = .06 if k % 2 == 0 else .042
        runas.append(along("primitive_cylinder_add", runa, c - side*larg, c + side*larg, .009, vertices=6))
        runas.append(along("primitive_cylinder_add", runa, c - d*.035, c + d*.035, .008, vertices=6))
    # chamas infernais: línguas curvas nas bordas da lâmina, no terço de cima
    chamas = []
    for t, s in ((.45, -1), (.62, 1), (.78, -1)):
        base = g_c + d*(.03 + .95*t) + side*(.035*s*(1 - t*.5))
        chamas.append(L.flame_spike(f"fl_chama{int(t*100)}", chama, base, d, side*s, .16, .028, curl=.5, n=8))
    for o in peças + runas + chamas: rest_uv(o)
    R.rigid(peças + runas + chamas, "hand.R")

def prim_sphere(m, c, r):
    return L.prim("primitive_uv_sphere_add", m, c, (r, r, r), segments=10, ring_count=6)

def build():
    R, _ = L.build()
    espadao(R)
    return R, INFO

def anims(R):
    A, breath, wg = L.A, L.breath, L.wg
    EN = [b for b in R.B if b.startswith("em")]
    def mp(t): return mote_pose(EN, t, rise=.6, drift=.08, seed=13)
    idle = [A(breath(i/8), mp(i/8)) for i in range(8)]
    # andar: passo pesado e arrogante; o punho esquerdo continua na cintura, as asas balançam
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t); th = 20*s
        walk.append(A({"thigh.L": {"x": -th}, "thigh.R": {"x": th},
                       "shin.L": {"bend": 6 + 40*max(0, c)**1.3}, "shin.R": {"bend": 6 + 40*max(0, -c)**1.3},
                       "foot.L": {"x": .3*th - 8*max(0, c)}, "foot.R": {"x": -.3*th - 8*max(0, -c)},
                       "hips": {"z": 5*s, "y": 2*c}, "chest": {"z": -6*s, "x": 2*abs(c)}, "head": {"z": 3*s},
                       "upper_arm.R": {"x": -.7*th},
                       "tf1": {"x": 8*s}, "tf2": {"x": 10*math.sin(t - 1)}, "tb1": {"x": -8*s}, "tb2": {"x": -10*math.sin(t - 1)},
                       "glow": {"v": 1 + .1*abs(s)}},
                      wg(4*c, -3*s, 3*c, 2*s), mp(i/8)))
    # ataque: ergue a garra direita e a crava no chão (explosão de lava em área); asas abrem
    UP = {"upper_arm.R": {"x": -150, "y": 15, "z": 10}, "forearm.R": {"bend": -40}, "hand.R": {"x": -20},
          "chest": {"x": -12, "z": 14}, "spine": {"x": -6}, "head": {"x": -4},
          "thigh.L": {"x": -16}, "shin.L": {"bend": 16}, "root": (0, .06, 0), "glow": {"v": .4}}
    SLAM = {"upper_arm.R": {"x": -12, "y": 4}, "forearm.R": {"bend": -8}, "hand.R": {"x": 30},
            "chest": {"x": 30, "z": -10}, "spine": {"x": 16}, "head": {"x": 10},
            "thigh.L": {"x": -34}, "shin.L": {"bend": 36}, "thigh.R": {"x": 14}, "shin.R": {"bend": 14},
            "root": (0, -.14, -.08), "glow": {"v": 1.0}}
    WO = wg(16, -6, -8, -14)
    keys = [(0, {}), (.32, merge(UP, WO)), (.44, merge(UP, WO, {"upper_arm.R": {"x": -8}})), (.56, merge(SLAM, WO)),
            (.78, merge(SLAM, {"chest": {"x": -6}})), (1, {})]
    fr = keys_to_frames(keys, 10)
    attack = [A(fr[i], breath(i/10, .4), mp(i/10)) for i in range(10)]
    # dano: tranco para trás, sem perder a pose
    hp = {"chest": {"x": -14, "z": 8}, "spine": {"x": -6}, "head": {"x": -14, "z": -10},
          "upper_arm.R": {"x": 16, "y": -10}, "root": (0, .05, 0), "glow": {"v": .6}}
    hit = [A(hp, mp(0)), A(lerp_pose(hp, {}, .5), mp(.1)), A(mp(.2))]
    # morte (só se algo forçar; o pet é invulnerável): cai de joelhos, curva o tronco, asas caem, a lava esfria
    kneel = {"thigh.L": {"x": -70}, "thigh.R": {"x": -45}, "shin.L": {"bend": 100}, "shin.R": {"bend": 90},
             "chest": {"x": 18}, "head": {"x": 16}, "upper_arm.R": {"x": -30}, "forearm.R": {"bend": -10}, "glow": {"v": -.15}}
    slump = merge(kneel, {"spine": {"x": 18}, "chest": {"x": 34}, "neck": {"x": 14}, "head": {"x": 26, "z": -12},
                          "upper_arm.R": {"x": 10, "y": -8}, "forearm.R": {"bend": -4}, "glow": {"v": -.4}}, wg(-24, 12, 14, 14))
    fd = keys_to_frames([(0, hp), (.35, kneel), (.7, slump), (1, merge(slump, {"head": {"x": 6}, "glow": {"v": -.5}}))], 8)
    death = [A(f) for f in fd]
    return {"idle": idle, "walk": walk, "attack": attack, "hit": hit, "death": death}
