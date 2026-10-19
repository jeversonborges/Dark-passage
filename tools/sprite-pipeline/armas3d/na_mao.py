# Arma na mão do personagem: monta a arma 3D na mão direita (osso hand.R) de um personagem com animação
# (idle e ataque do próprio glb) e gera PNG parado e GIFs animados, em vista frontal.
#
# A arma segue o osso por um Copy Transforms: um Empty acompanha a mão em posição e rotação, e a arma é filha desse
# Empty com um deslocamento fixo (OFFSET_LOC / OFFSET_ROT), que é o encaixe da pegada na mão.
#
# Uso: /root/bpy42/bin/python na_mao.py -- <personagem.glb> <arma.glb> <saida_dir> <nome>
import bpy, math, os, sys
from mathutils import Vector, Euler, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib

OFFSET_LOC = tuple(float(v) for v in os.environ.get("OFF_LOC", "0,0,0").split(","))
OFFSET_ROT = tuple(float(v) for v in os.environ.get("OFF_ROT", "0,0,0").split(","))   # graus; arma na vertical
RES = int(os.environ.get("RES", 320))
AMOSTRAS = int(os.environ.get("AMOSTRAS", 24))
# Duas mãos: ponto do cabo (no sistema da arma) onde a mão esquerda segura; vazio = uma mão só.
ALVO_MAO_ESQ = os.environ.get("ALVO_MAO_ESQ")
DUAS_MAOS = ALVO_MAO_ESQ is not None
# Arma diagonal cruzando o corpo, uma mão no meio do cabo e a outra solta (referência do machado).
DIAGONAL = os.environ.get("DIAGONAL") == "1"
# Ponto no mundo onde fica o cabo na pegada de duas mãos (frente do peito, mão direita no topo do cabo).
PONTO_ARMA = tuple(float(v) for v in os.environ.get("PONTO_ARMA", "0,-0.3,1.0").split(","))

def importa(caminho):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=caminho)
    return [o for o in bpy.data.objects if o not in antes]

def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    personagem, arma, out, nome = argv[0], argv[1], argv[2], argv[3]
    os.makedirs(out, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # o .blend traz materiais e ações; o glb perde os materiais na importação
    if personagem.endswith(".blend"):
        bpy.ops.wm.open_mainfile(filepath=personagem)
        for o in list(bpy.data.objects):
            if o.type == 'CAMERA':
                bpy.data.objects.remove(o)   # usa a câmera do print, não a do .blend
        novos = list(bpy.data.objects)
    else:
        novos = importa(personagem)
    arm = next(o for o in novos if o.type == 'ARMATURE')
    for o in novos:
        if o.type == 'MESH' and o.name == 'Icosphere':   # sombra de chão do sprite, fora do print
            o.hide_render = True
    # empty que acompanha a mão: a matriz é atualizada a cada quadro (ver loop de render)
    mao = bpy.data.objects.new("mao_arma", None)
    bpy.context.scene.collection.objects.link(mao)
    osso_nome = "hand.R"

    # arma: importa o glb e prende ao empty, sem deslocamento próprio
    armas = importa(arma)
    raiz = [o for o in armas if o.parent is None]
    for o in raiz:   # mantém a transformação que cada peça tem ao ser importada (o glb guarda uma por nó)
        mundo = o.matrix_world.copy()
        o.parent = mao
        o.matrix_parent_inverse.identity()
        o.matrix_basis = mundo

    # quadro de repouso: a arma fica com OFFSET_ROT (vertical = 0,0,0) e acompanha o movimento da mão depois
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    osso_repouso = arm.matrix_world @ arm.pose.bones[osso_nome].matrix
    inv_repouso = osso_repouso.inverted()
    w_repouso = Matrix.Translation(osso_repouso.translation + Vector(OFFSET_LOC)) @ Euler(
        tuple(math.radians(v) for v in OFFSET_ROT)).to_matrix().to_4x4()
    def posiciona_arma():
        bpy.context.view_layer.update()
        if DUAS_MAOS or DIAGONAL:
            return   # pegada de duas mãos: arma parada na frente do peito, as mãos seguem por IK
        osso = arm.matrix_world @ arm.pose.bones[osso_nome].matrix
        mao.matrix_world = osso @ inv_repouso @ w_repouso
    if DUAS_MAOS or DIAGONAL:
        # arma parada, vertical, na frente do peito (PONTO_ARMA). Mão direita no cabo (origem da arma) e
        # mão esquerda mais embaixo no cabo (ALVO_MAO_ESQ). IK com três ossos (antebraço, braço e mão).
        mao.matrix_world = Matrix.Translation(Vector(PONTO_ARMA)) @ Euler(
            tuple(math.radians(v) for v in OFFSET_ROT)).to_matrix().to_4x4()
        pontos_ik = [("hand.R", tuple(float(v) for v in os.environ.get("PONTO_MAO_DIR", "0,0,0").split(",")))]
        if DUAS_MAOS:
            pontos_ik.append(("hand.L", tuple(float(v) for v in ALVO_MAO_ESQ.split(","))))
        for osso_nome_ik, ponto in pontos_ik:
            alvo_mao = bpy.data.objects.new(f"alvo_{osso_nome_ik}", None)
            bpy.context.scene.collection.objects.link(alvo_mao)
            alvo_mao.parent = mao
            alvo_mao.location = ponto
            ik = arm.pose.bones[osso_nome_ik].constraints.new('IK')
            ik.target = alvo_mao
            ik.chain_count = 3
            ik.use_tail = True
            ik.use_stretch = False
            ik.iterations = 500
            ik.influence = 1.0
    lib_objs = [o for o in armas if o.type == "MESH"]

    cena = bpy.context.scene
    cena.render.engine = 'CYCLES'; cena.cycles.device = 'CPU'; cena.cycles.samples = AMOSTRAS
    cena.cycles.use_denoising = False
    cena.render.film_transparent = True
    cena.render.resolution_x = cena.render.resolution_y = RES
    cena.render.image_settings.file_format = 'PNG'; cena.render.image_settings.color_mode = 'RGBA'
    world = bpy.data.worlds.new("mundo"); cena.world = world; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.01, 0.01, 0.012, 1)
    sol = bpy.data.lights.new("sol", 'SUN'); sol.energy = 2.2
    so = bpy.data.objects.new("sol", sol); cena.collection.objects.link(so)
    so.rotation_euler = (math.radians(55), 0, math.radians(35))
    cd = bpy.data.cameras.new("cam"); cd.type = 'ORTHO'; cd.ortho_scale = 2.4
    cam = bpy.data.objects.new("cam", cd); cena.collection.objects.link(cam); cena.camera = cam
    alvo = Vector((0, 0, 0.95))
    cam.location = alvo + Vector((0, -6.0, 1.7))
    cam.rotation_euler = (alvo - cam.location).to_track_quat('-Z', 'Y').to_euler()

    quadros = {}
    for anim, frames in (("idle", 4), ("attack", 8)):
        act = bpy.data.actions.get(anim) or bpy.data.actions.get(f"{anim}_mutante")
        arm.animation_data_create()
        arm.animation_data.action = act
        arquivos = []
        for k in range(frames):
            cena.frame_set(int(act.frame_range[0]) + k)
            posiciona_arma()
            arq = os.path.join(out, f"{nome}_{anim}_{k}.png")
            cena.render.filepath = arq
            bpy.ops.render.render(write_still=True)
            arquivos.append(arq)
        quadros[anim] = arquivos

    # PNG parado (primeiro quadro do idle) e GIFs
    from PIL import Image
    def gif(arquivos, caminho, duracao):
        ims = [Image.open(a).convert("RGBA") for a in arquivos]
        fundo = [Image.new("RGBA", im.size, (14, 14, 18, 255)) for im in ims]
        quadros_gif = []
        for f, im in zip(fundo, ims):
            f.alpha_composite(im)
            quadros_gif.append(f.convert("P", palette=Image.ADAPTIVE))
        quadros_gif[0].save(caminho, save_all=True, append_images=quadros_gif[1:], duration=duracao, loop=0,
                            disposal=2)
    Image.open(quadros["idle"][0]).save(os.path.join(out, f"{nome}_na_mao.png"))
    gif(quadros["idle"], os.path.join(out, f"{nome}_idle.gif"), 250)
    gif(quadros["attack"], os.path.join(out, f"{nome}_ataque.gif"), 83)
    for arqs in quadros.values():
        for a in arqs:
            os.remove(a)
    print("ok", out, nome)

if __name__ == "__main__":
    main()
