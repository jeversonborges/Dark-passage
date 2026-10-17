# Familiar do Cultista, 4ª forma (nível 60 do dono): o Líder dos Demônios em escala de pet (~3,3 m).
# Pedido do Jefin (2026-10-17): "a última evolução do pet do cultista será o demônio líder lvl 60".
# Reaproveita o modelo de lider_dos_demonios.py (carne e ferro negro com rachaduras de lava, chifres, asas rasgadas)
# e acrescenta as animações de pet: idle, walk, attack (garra de lava que bate em área), hit e death.
# Uso: blender -b -P render.py -- familiar_lider /tmp/brutos/familiar_lider
import math
import lider_dos_demonios as L
from mrig import merge, lerp_pose, keys_to_frames
from amenti import mote_pose

L.SCALE = 1.8                      # 5,1 m no lorde -> ~3,3 m no pet
INFO = dict(L.INFO, px=448, target_z=1.95, samples=int(L.INFO["samples"]),
            loops=("idle", "walk"), fps={"idle": 6, "walk": 9, "attack": 12, "hit": 12, "death": 9})
def set_variant(name): pass

def build():
    R, _ = L.build()
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
