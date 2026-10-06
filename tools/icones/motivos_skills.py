# Desenhos (SVG 64x64) dos ícones de skills. Cada função recebe E (cor emissiva do elemento) e retorna o símbolo central.
# A moldura e o fundo ficam em moldura() — dourado/osso para Arautos, aço/latão para Vigília.
import math
K = "#0a0808"
o = f'stroke="{K}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"'
ELEM = {  # (emissivo, escuro do fundo)
 "sagrado":("#ffe08a","#3a2a0a"), "sangue":("#ff4a3a","#2e0604"), "fogo":("#ff9a3a","#3a1004"), "veneno":("#a8ff4a","#122a06"),
 "eletrico":("#a8e0ff","#0c2236"), "sombra":("#c084ff","#1a0c26"), "fisico":("#f0dcb0","#2a2018"),
}
OSSO = ("#ece2cc","#bfb398","#776b57"); ACO = ("#d8dce0","#8a9098","#4a5058"); LAT = ("#e6b866","#b07a3a","#5a3a18")
COU = ("#8a6040","#5a3a24","#2e1c10"); FER = ("#7a7a80","#4a4a50","#222226"); VERM = "#8a1a14"
def gl(d, E, w=2.4): return f'<path d="{d}" fill="none" stroke="{E}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" filter="url(#gl)"/>'
def dot(x, y, r, E): return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{E}" filter="url(#gl)"/>'
def raios(cx, cy, r0, r1, n, E, w=1.6, off=0):
    return "".join(gl(f"M{cx+r0*math.cos(a):.1f} {cy+r0*math.sin(a):.1f} L{cx+r1*math.cos(a):.1f} {cy+r1*math.sin(a):.1f}", E, w) for a in [off+2*math.pi*i/n for i in range(n)])
def espada(x=32, y=32, rot=45, s=1.0, E=None, cor=ACO):
    L,M,D = cor
    g = f'''<g transform="translate({x} {y}) rotate({rot}) scale({s}) translate(-32 -32)"><path d="M28.5 44 L28.5 10 L32 3 L35.5 10 L35.5 44 Z" fill="url(#gM)" {o}/>
 <path d="M32 6 L32 43" stroke="{L}" stroke-width="1.4"/>{gl("M32 7 L32 42", E, 1.8) if E else ""}<path d="M21 44 L43 44 L41 48 L23 48 Z" fill="{LAT[1]}" {o}/>
 <rect x="30" y="48" width="4" height="9" fill="{COU[1]}" {o}/><circle cx="32" cy="59" r="2.6" fill="{LAT[1]}" {o}/></g>'''
    return g

def anjo_lamina_veredito(E): return gl("M10 50 Q20 14 54 10", E, 3.4) + espada(34,30,40,1.05,E,("#fff4cc","#e8c46a","#7a5a1e")) + raios(52,12,3,8,6,E,1.2)
def anjo_toque_graca(E):
    return f'''{dot(32,24,9,E)}<path d="M16 60 L18 40 Q14 30 18 28 L22 36 L22 22 Q22 18 26 18 L27 34 L28 16 Q29 12 32 13 L33 33 L35 18 Q36 14 39 15 L39 35 L42 26 Q45 24 46 27 L44 42 Q42 52 44 60 Z" fill="{OSSO[1]}" {o}/>
 <path d="M18 46 L44 42 M18 52 L44 48" stroke="{OSSO[2]}" stroke-width="1.4"/><path d="M24 24 L24 34 M31 18 L31 33" stroke="{OSSO[0]}" stroke-width="1.2"/>
 <path d="M30 44 L34 44 L34 41 M32 38 L32 50" stroke="{VERM}" stroke-width="2"/>{raios(32,24,12,18,8,E,1.4)}'''
def anjo_asas_ascensao(E):
    def asa(sx):
        pen = "".join(f'<path d="M{32+sx*(6+i*4.2):.1f} {26+i*1.2:.1f} Q{32+sx*(10+i*5):.1f} {38+i*3:.1f} {32+sx*(8+i*4.6):.1f} {46+i*2.4:.1f} L{32+sx*(4+i*4.2):.1f} {34+i*1.5:.1f} Z" fill="{["#e6dcc6","#d0c4ac","#bcb096","#a89c84","#948870"][i]}" {o}/>' for i in range(5))
        return f'<path d="M32 30 Q{32+sx*10} 6 {32+sx*30} 4 Q{32+sx*28} 14 {32+sx*30} 22 Q{32+sx*20} 22 {32+sx*12} 32 Z" fill="#ece2cc" {o}/><path d="M{32+sx*12} 24 Q{32+sx*20} 12 {32+sx*28} 8" fill="none" stroke="#fffaf0" stroke-width="1.4"/>' + pen
    return f'''{"".join(gl(f"M{x} 62 L{x} {50-abs(x-32)//3}", E, 1.6) for x in (22,32,42))}{asa(-1)}{asa(1)}
 <path d="M22 30 L42 30" stroke="#5a3a24" stroke-width="3.4"/><path d="M22 30 L42 30" stroke="#8a6040" stroke-width="1.4"/>{dot(32,22,3.4,E)}{raios(32,22,5,9,8,E,1)}'''
def anjo_halo_ardente(E):
    return f'''<ellipse cx="32" cy="34" rx="24" ry="10" fill="none" stroke="{E}" stroke-width="5" filter="url(#gl)" opacity=".7"/>{raios(32,34,14,28,12,E,1.4)}
 <ellipse cx="32" cy="34" rx="20" ry="8" fill="none" stroke="{K}" stroke-width="6"/><ellipse cx="32" cy="34" rx="20" ry="8" fill="none" stroke="{LAT[1]}" stroke-width="3.6"/>
 <ellipse cx="32" cy="34" rx="20" ry="8" fill="none" stroke="{E}" stroke-width="1.2" stroke-dasharray="10 4"/>
 <path d="M46 28 L50 26 M14 38 L18 40" stroke="{K}" stroke-width="3"/>{dot(32,34,4,"#fff8e0")}'''
def anjo_sentenca(E):
    pts = " ".join(f"{32+(14 if i%2 else 18)*math.cos(i*math.pi/8):.1f},{32+(14 if i%2 else 18)*math.sin(i*math.pi/8):.1f}" for i in range(16))
    return f'''{gl("M32 4 L32 12 M32 52 L32 60 M4 32 L12 32 M52 32 L60 32", E, 2)}<polygon points="{pts}" fill="#9a1e16" {o}/><circle cx="32" cy="32" r="11" fill="#7a1410" stroke="#4a0a08" stroke-width="1.4"/>
 <path d="M24 26 Q26 22 30 23" fill="none" stroke="#d84a3a" stroke-width="1.6"/>
 <path d="M26 36 L36 26 M28 26 L38 36" stroke="#3a0604" stroke-width="2.6"/><path d="M27 37 L37 27" stroke="{E}" stroke-width="1.4" filter="url(#gl)"/>
 <path d="M24 48 L18 60 L26 56 L28 62 Z M40 48 L46 60 L38 56 L36 62 Z" fill="#9a1e16" {o}/>'''
def anjo_trombeta_juizo(E):
    return f'''{raios(42,22,14,28,10,E,1.4,0.3)}<path d="M8 50 L36 26 Q44 14 56 10 Q52 22 40 30 L14 56 Z" fill="url(#gO)" {o}/>
 <path d="M36 26 Q46 16 56 10 Q52 22 40 30 Z" fill="#7a5a1e" {o}/><path d="M12 50 L36 29" stroke="#fff4cc" stroke-width="1.4"/>
 <path d="M24 38 L28 42 M18 44 L22 48" stroke="{K}" stroke-width="2"/><path d="M38 28 L30 36 L34 34 L28 42" fill="none" stroke="{K}" stroke-width="1.4"/>
 <circle cx="10" cy="54" r="4" fill="#c99a3e" {o}/>{dot(50,16,4,E)}'''

def cultista_sangria(E):
    return f'''{gl("M8 56 Q20 40 40 22", E, 3)}<path d="M40 8 Q54 26 54 36 Q54 48 42 48 Q30 48 30 36 Q30 26 40 8 Z" fill="url(#gS)" {o}/>
 <path d="M36 30 Q34 38 38 44" fill="none" stroke="#ff9a8a" stroke-width="2"/>{"".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#9a1410" {o}/>' for x,y,r in ((22,46,3),(14,54,2.2),(28,54,1.8)))}'''
def cultista_pacto_rubro(E):
    return f'''<path d="M10 56 L14 18 L46 10 L52 50 Z" fill="#d8ccb0" {o}/><path d="M14 18 L46 10 L48 16 L16 24 Z" fill="#b8ac90"/>
 {"".join(f'<path d="M{18+i*0.6} {30+i*6} L{44+i*0.6} {24+i*6}" stroke="#6a5e48" stroke-width="1"/>' for i in range(4))}
 <path d="M22 50 Q30 40 34 46 Q38 52 46 42" fill="none" stroke="{E}" stroke-width="2.2" filter="url(#gl)"/>
 <path d="M44 4 L58 18 L28 48 L22 50 L24 44 Z" fill="url(#gM)" {o}/><path d="M46 8 L54 16" stroke="{ACO[0]}" stroke-width="1.4"/>
 <path d="M24 44 L28 48" stroke="#9a1410" stroke-width="3"/>{dot(22,56,2.4,E)}'''
def cultista_servo_carne(E):
    return f'''<path d="M10 62 Q12 42 20 36 L44 36 Q52 42 54 62 Z" fill="#6a5048" {o}/><path d="M20 36 Q18 14 32 10 Q46 14 44 36 Z" fill="#8a7068" {o}/>
 <path d="M32 10 L32 60 M20 44 L44 44" stroke="#2a1410" stroke-width="1.2" stroke-dasharray="2.5 2"/><path d="M30 12 l4 2 M30 18 l4 2 M30 24 l4 2 M30 30 l4 2 M30 50 l4 2" stroke="#d8ccb0" stroke-width="1"/>
 <circle cx="26" cy="24" r="3.4" fill="{K}"/><circle cx="38" cy="24" r="3.4" fill="{K}"/>{dot(26,24,1.6,E)}{dot(38,24,1.6,E)}
 <path d="M24 32 L40 32" stroke="{K}" stroke-width="2"/><path d="M26 31 l0 3 M30 31 l0 3 M34 31 l0 3 M38 31 l0 3" stroke="#d8ccb0" stroke-width="1"/>
 <path d="M4 62 Q32 54 60 62" fill="#5a0e0a" {o}/>'''
def cultista_chuva_cinzas(E):
    flakes = "".join(f'<path d="M{x} {y} l2 6" stroke="#9a948c" stroke-width="1.6"/>' for x,y in ((12,28),(20,36),(30,30),(40,38),(50,30),(16,48),(28,46),(44,50),(36,22),(52,46)))
    return f'''<path d="M6 22 Q6 8 20 10 Q26 2 36 6 Q50 2 54 12 Q62 14 58 24 Z" fill="#3a3634" {o}/><path d="M10 18 Q20 12 30 14 Q40 10 52 16" fill="none" stroke="#6a6460" stroke-width="2"/>
 {flakes}{"".join(dot(x,y,1.4,E) for x,y in ((24,40),(46,30),(14,54),(38,56)))}<path d="M4 60 Q32 52 60 60" fill="none" stroke="#6a6460" stroke-width="3"/>'''
def cultista_profecia_sombria(E):
    return f'''<path d="M4 32 Q32 6 60 32 Q32 58 4 32 Z" fill="#141012" {o}/><path d="M10 32 Q32 14 54 32" fill="none" stroke="#3a2e3a" stroke-width="1.6"/>
 <circle cx="32" cy="32" r="12" fill="#5a0a08" stroke="{K}" stroke-width="1.5"/><circle cx="32" cy="32" r="12" fill="none" stroke="{E}" stroke-width="1.6" filter="url(#gl)"/>
 <ellipse cx="32" cy="32" rx="2.6" ry="9" fill="{K}"/><circle cx="28" cy="27" r="2" fill="#ffd0c0"/>
 {"".join(f'<path d="M{32+30*math.cos(a):.1f} {32+30*math.sin(a):.1f} L{32+22*math.cos(a):.1f} {32+22*math.sin(a):.1f}" stroke="#2a1e2a" stroke-width="2"/>' for a in [math.pi*(0.15+0.1*i) for i in range(8)])}'''
def cultista_setimo_selo(E):
    seals = "".join(f'<circle cx="{32+20*math.cos(a):.1f}" cy="{32+20*math.sin(a):.1f}" r="5" fill="#8a1a14" {o}/>' + (dot(f"{32+20*math.cos(a):.1f}", f"{32+20*math.sin(a):.1f}", 2, E) if i < 6 else "") for i,a in enumerate([-math.pi/2+2*math.pi*i/7 for i in range(7)]))
    return f'''<circle cx="32" cy="32" r="26" fill="none" stroke="{E}" stroke-width="1.4" filter="url(#gl)"/><circle cx="32" cy="32" r="20" fill="none" stroke="#5a1a14" stroke-width="1.4"/>
 <polygon points="{" ".join(f"{32+20*math.cos(-math.pi/2+4*math.pi*i/7):.1f},{32+20*math.sin(-math.pi/2+4*math.pi*i/7):.1f}" for i in range(7))}" fill="none" stroke="{E}" stroke-width="1.2" filter="url(#gl)"/>
 {seals}<path d="M24 32 Q32 24 40 32 Q32 40 24 32 Z" fill="#e8dcc0" {o}/><circle cx="32" cy="32" r="3.4" fill="#7a1410"/><circle cx="32" cy="32" r="1.4" fill="{K}"/>'''

def mutante_golpe_purulento(E):
    return f'''{"".join(dot(x,y,r,E) for x,y,r in ((12,50,3),(52,46,2.4),(18,58,2),(46,58,2.6)))}<path d="M14 48 Q32 36 50 48" fill="none" stroke="{E}" stroke-width="2" filter="url(#gl)"/>
 <path d="M18 8 Q34 2 46 10 Q54 20 50 32 L48 44 Q36 50 22 44 L16 30 Q10 18 18 8 Z" fill="#6a7058" {o}/>
 <path d="M20 12 Q32 6 42 12" fill="none" stroke="#9aa078" stroke-width="2"/>{"".join(f'<path d="M{x} 30 L{x} 44" stroke="{K}" stroke-width="1.2"/>' for x in (26,32,38))}
 {"".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{E}" stroke="{K}" stroke-width="1"/>' for x,y,r in ((24,20,3.2),(38,18,2.4),(44,28,2.8),(30,26,1.8)))}
 <path d="M14 38 L50 34" stroke="{FER[1]}" stroke-width="4"/><path d="M14 38 L50 34" stroke="{K}" stroke-width="1" stroke-dasharray="3 3"/>'''
def mutante_carapaca(E):
    plates = "".join(f'<path d="M{x} {y} l7 -4 l7 4 l0 8 l-7 4 l-7 -4 Z" fill="{c}" {o}/>' for x,y,c in ((18,14,"#7a806a"),(32,14,"#6a7058"),(11,26,"#6a7058"),(25,26,"#8a9078"),(39,26,"#6a7058"),(18,38,"#5a604c"),(32,38,"#6a7058")))
    return f'''<path d="M32 4 L56 14 L54 40 Q48 54 32 60 Q16 54 10 40 L8 14 Z" fill="#3a4030" {o}/>{plates}
 {gl("M32 4 L56 14 L54 40 Q48 54 32 60 Q16 54 10 40 L8 14 Z", E, 1.4)}<path d="M26 28 L30 32 L28 36 M42 30 L38 34" stroke="{K}" stroke-width="1.2"/>'''
def mutante_rugido_praga(E):
    return f'''{"".join(f'<path d="M{32-r} {34-r*0.3} Q32 {34-r*1.2} {32+r} {34-r*0.3}" fill="none" stroke="{E}" stroke-width="{2.2-i*0.4}" opacity="{1-i*0.25}" filter="url(#gl)"/>' for i,r in enumerate((22,27,31)))}
 <path d="M14 40 Q14 20 32 18 Q50 20 50 40 Q50 56 32 60 Q14 56 14 40 Z" fill="#6a7058" {o}/>
 <path d="M20 40 Q32 34 44 40 Q42 54 32 56 Q22 54 20 40 Z" fill="#1a0806" {o}/>{"".join(f'<path d="M{x} 40 l2 5 l2 -5" fill="#d8ccb0" stroke="{K}" stroke-width=".8"/>' for x in (22,27,32,37))}
 <rect x="22" y="46" width="20" height="8" rx="3" fill="{FER[1]}" {o}/><circle cx="27" cy="50" r="2" fill="{K}"/><circle cx="37" cy="50" r="2" fill="{K}"/>
 <circle cx="25" cy="30" r="2.6" fill="{E}" filter="url(#gl)"/><circle cx="39" cy="30" r="2.6" fill="{E}" filter="url(#gl)"/><path d="M20 26 L28 28 M44 26 L36 28" stroke="{K}" stroke-width="2"/>'''
def mutante_regeneracao_profana(E):
    return f'''<path d="M32 58 Q8 42 8 24 Q8 10 20 10 Q28 10 32 18 Q36 10 44 10 Q56 10 56 24 Q56 42 32 58 Z" fill="#7a2a22" {o}/>
 <path d="M14 22 Q16 14 24 14" fill="none" stroke="#c05a4a" stroke-width="2"/>
 <path d="M32 18 L28 30 L34 36 L30 48" fill="none" stroke="{K}" stroke-width="2"/>{"".join(f'<path d="M{x-3} {y} L{x+3} {y+1}" stroke="#d8ccb0" stroke-width="1.2"/>' for x,y in ((30,24),(31,32),(32,40)))}
 {"".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{E}" stroke="{K}" stroke-width="1" filter="url(#gl)"/>' for x,y,r in ((20,32,3),(44,26,2.4),(40,42,2),(24,44,1.6)))}{raios(32,32,28,31,12,E,1.2)}'''
def mutante_investida_bestial(E):
    return f'''{"".join(gl(f"M2 {y} L{16+i*3} {y}", E, 1.8) for i,y in enumerate((18,28,38,48)))}
 {raios(50,32,6,14,10,"#fff0c0",1.6)}<path d="M50 20 L54 28 L62 28 L56 34 L60 42 L50 37 L42 42 L46 34 L40 28 L48 28 Z" fill="{E}" filter="url(#gl)" opacity=".8"/>
 <path d="M10 44 Q8 26 20 20 Q30 14 42 20 Q50 24 50 32 Q50 42 42 46 Q30 52 18 50 Q10 50 10 44 Z" fill="#6a7058" {o}/>
 {"".join(f'<rect x="{x}" y="{y}" width="9" height="7" rx="2" fill="#8a9078" {o}/>' for x,y in ((40,22),(42,30),(40,38)))}
 <path d="M14 28 Q22 20 34 20" fill="none" stroke="#9aa078" stroke-width="2.2"/><path d="M16 44 Q26 40 36 44" fill="none" stroke="#3a4030" stroke-width="2"/>
 {"".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{E}" stroke="{K}" stroke-width=".8"/>' for x,y,r in ((22,32,2.6),(30,38,1.8),(18,40,1.6)))}
 <path d="M12 46 L4 58 M20 50 L16 62" stroke="#6a7058" stroke-width="5"/><path d="M12 46 L4 58 M20 50 L16 62" stroke="{K}" stroke-width="1" fill="none"/>'''
def mutante_forma_besta(E):
    return f'''{raios(32,36,24,30,14,E,1.4)}<path d="M8 60 Q6 40 14 30 L8 14 L20 24 Q32 18 44 24 L56 14 L50 30 Q58 40 56 60 Z" fill="#4a5040" {o}/>
 <path d="M14 30 L8 14 L20 24 M50 30 L56 14 L44 24" fill="#d8ccb0" {o}/>
 <path d="M18 38 L28 42 M46 38 L36 42" stroke="{K}" stroke-width="3"/><circle cx="24" cy="40" r="3" fill="{E}" filter="url(#gl)"/><circle cx="40" cy="40" r="3" fill="{E}" filter="url(#gl)"/>
 <path d="M18 50 Q32 58 46 50 L44 56 Q32 62 20 56 Z" fill="#1a0806" {o}/>{"".join(f'<path d="M{x} 51 l2 5 l2 -5" fill="#ece2cc"/>' for x in (22,28,34,40))}
 <path d="M20 28 Q32 24 44 28" fill="none" stroke="#7a806a" stroke-width="2"/>'''

def demonio_garra_abismo(E):
    return "".join(f'''<path d="M{10+i*12} 6 Q{20+i*12} 30 {14+i*12} 58" fill="none" stroke="{K}" stroke-width="6" stroke-linecap="round"/>
 <path d="M{10+i*12} 6 Q{20+i*12} 30 {14+i*12} 58" fill="none" stroke="#3a0804" stroke-width="3.6" stroke-linecap="round"/>{gl(f"M{11+i*12} 8 Q{20+i*12} 30 {14+i*12} 56", E, 1.8)}''' for i in range(3)) + \
        f'<path d="M42 54 Q52 50 56 40 Q60 30 54 26" fill="none" stroke="#3a3436" stroke-width="2" opacity=".8"/>'
def demonio_corrente_danacao(E):
    links = "".join(f'<ellipse cx="{8+i*6}" cy="{56-i*6}" rx="{4 if i%2==0 else 2}" ry="{2.6 if i%2==0 else 4}" transform="rotate(-45 {8+i*6} {56-i*6})" fill="none" stroke="{K}" stroke-width="4"/><ellipse cx="{8+i*6}" cy="{56-i*6}" rx="{4 if i%2==0 else 2}" ry="{2.6 if i%2==0 else 4}" transform="rotate(-45 {8+i*6} {56-i*6})" fill="none" stroke="{E}" stroke-width="2" filter="url(#gl)"/>' for i in range(7))
    return f'''{links}<path d="M46 18 Q46 4 54 6 Q62 8 60 18 Q58 26 50 26" fill="none" stroke="{K}" stroke-width="6" stroke-linecap="round"/>
 <path d="M46 18 Q46 4 54 6 Q62 8 60 18 Q58 26 50 26" fill="none" stroke="{ACO[1]}" stroke-width="3.4" stroke-linecap="round"/><path d="M48 24 L52 30 L54 24 Z" fill="{ACO[0]}" {o}/>'''
def demonio_pele_enxofre(E):
    return f'''<path d="M12 10 Q32 4 52 10 L50 44 Q42 56 32 60 Q22 56 14 44 Z" fill="#2a1a18" {o}/>
 <path d="M32 10 L28 22 L36 30 L30 40 L34 52 M28 22 L18 26 L14 36 M36 30 L46 26 L50 18 M30 40 L20 46 M34 52 L42 46" fill="none" stroke="{K}" stroke-width="3"/>
 {gl("M32 10 L28 22 L36 30 L30 40 L34 52 M28 22 L18 26 L14 36 M36 30 L46 26 L50 18 M30 40 L20 46 M34 52 L42 46", E, 1.6)}
 {"".join(f'<path d="M{x} 8 Q{x-4} 2 {x} -2" fill="none" stroke="#c0b040" stroke-width="1.4" opacity=".6"/>' for x in (20,32,44))}{raios(32,32,28,31,10,E,1.2)}'''
def demonio_passo_sombrio(E):
    return f'''<path d="M8 58 Q6 40 14 30 Q12 18 20 16 Q30 14 30 26 Q34 36 30 58 Z" fill="#1a1014" opacity=".55"/>
 <path d="M28 60 Q26 40 34 28 Q32 14 42 12 Q52 12 52 24 Q56 36 52 60 Z" fill="#141012" {o}/><path d="M36 12 L32 4 L38 10 M48 12 L54 4 L50 12" fill="#3a2e30" {o}/>
 <circle cx="40" cy="22" r="2" fill="{E}" filter="url(#gl)"/><circle cx="47" cy="22" r="2" fill="{E}" filter="url(#gl)"/>
 {"".join(f'<path d="M{x} {y} Q{x-8} {y-4} {x-14} {y+2}" fill="none" stroke="#5a4a5e" stroke-width="2" opacity=".7"/>' for x,y in ((30,34),(28,44),(30,52)))}
 <path d="M14 26 L20 28" stroke="#ff7a1a" stroke-width="1.4" opacity=".5"/>'''
def demonio_banquete(E):
    return f'''<path d="M12 32 Q12 14 32 14 Q52 14 52 32 L52 36 Q32 30 12 36 Z" fill="#3a1410" {o}/><path d="M12 36 Q32 30 52 36 Q50 52 32 54 Q14 52 12 36 Z" fill="#1a0604" {o}/>
 {"".join(f'<path d="M{x} {33-abs(x-32)*0.15} l3 9 l3 -9" fill="#ece2cc" stroke="{K}" stroke-width=".8"/>' for x in (17,23,29,35,41))}
 {"".join(f'<path d="M{x} {50-abs(x-32)*0.2} l3 -7 l3 7" fill="#ece2cc" stroke="{K}" stroke-width=".8"/>' for x in (20,26,32,38))}
 {gl("M24 50 Q22 58 26 62 M40 48 Q42 56 38 62", E, 2)}<path d="M18 22 Q26 18 34 18" fill="none" stroke="#6a2a22" stroke-width="2"/>'''
def demonio_portao_inferno(E):
    return f'''<path d="M10 62 L10 24 Q10 6 32 6 Q54 6 54 24 L54 62 Z" fill="#1d1a1c" {o}/><path d="M16 62 L16 26 Q16 12 32 12 Q48 12 48 26 L48 62 Z" fill="url(#gF)" {o}/>
 {"".join(f'<path d="M{x} 62 Q{x-4} {48-i%2*6} {x+2} {38-i*3} Q{x+6} {48} {x+6} 62 Z" fill="#ffd070" opacity=".85"/>' for i,x in enumerate((19,26,33,40)))}
 {"".join(f'<rect x="{x}" y="16" width="2.6" height="46" fill="{K}"/>' for x in (22,30,38))}<path d="M16 34 L48 34" stroke="{K}" stroke-width="2.6"/>
 <path d="M10 24 L4 14 L14 18 M54 24 L60 14 L50 18" fill="#3a2e30" {o}/>{dot(32,8,2,E)}'''

def humano_tiro_certeiro(E):
    return f'''<circle cx="32" cy="32" r="22" fill="none" stroke="{K}" stroke-width="5"/><circle cx="32" cy="32" r="22" fill="none" stroke="#b8a888" stroke-width="2.4"/>
 <circle cx="32" cy="32" r="12" fill="none" stroke="#b8a888" stroke-width="1.4"/><path d="M32 4 L32 22 M32 42 L32 60 M4 32 L22 32 M42 32 L60 32" stroke="{K}" stroke-width="3.2"/>
 <path d="M32 4 L32 22 M32 42 L32 60 M4 32 L22 32 M42 32 L60 32" stroke="#d8ccb0" stroke-width="1.4"/>{dot(32,32,3.4,E)}{gl("M32 32 L52 12", E, 1.6)}'''
def humano_rajada(E):
    return f'''{"".join(gl(f"M14 50 L{14+40*math.cos(a):.1f} {50-40*math.sin(a):.1f}", E, 1.6) for a in [math.radians(20+i*12.5) for i in range(5)])}
 {"".join(f'<circle cx="{14+40*math.cos(a):.1f}" cy="{50-40*math.sin(a):.1f}" r="2.6" fill="#5e5e64" {o}/>' for a in [math.radians(20+i*12.5) for i in range(5)])}
 <path d="M4 60 Q8 46 18 44 Q24 46 22 54 Q14 60 4 60 Z" fill="#ff9a3a" filter="url(#gl)" opacity=".85"/><circle cx="14" cy="50" r="5" fill="#fff0c0"/>'''
def humano_armadilha_prata(E):
    teeth = "".join(f'<path d="M{x} 32 l3 -8 l3 8" fill="#eef4f8" stroke="{K}" stroke-width="1"/>' for x in range(12,50,6)) + "".join(f'<path d="M{x} 36 l3 8 l3 -8" fill="#eef4f8" stroke="{K}" stroke-width="1"/>' for x in range(15,50,6))
    return f'''<ellipse cx="32" cy="48" rx="26" ry="8" fill="#1a1616" {o}/><path d="M8 34 Q8 14 32 14 Q56 14 56 34 Z" fill="none" stroke="{K}" stroke-width="6"/><path d="M8 34 Q8 14 32 14 Q56 14 56 34" fill="none" stroke="#a8b4bc" stroke-width="3"/>
 <path d="M8 34 Q8 54 32 54 Q56 54 56 34" fill="none" stroke="{K}" stroke-width="6"/><path d="M8 34 Q8 54 32 54 Q56 54 56 34" fill="none" stroke="#8a949c" stroke-width="3"/>{teeth}
 <rect x="26" y="30" width="12" height="8" fill="#5e5e64" {o}/>{"".join(dot(x,y,1.4,E) for x,y in ((14,18),(50,18),(32,10),(56,40)))}'''
def humano_agua_benta_polvora(E):
    return f'''<path d="M10 16 L26 16 L28 22 L28 56 L8 56 L8 22 Z" fill="#8ab8c8" fill-opacity=".7" {o}/><path d="M10 34 L26 34 L26 54 L10 54 Z" fill="{E}" filter="url(#gl)" opacity=".8"/>
 <rect x="13" y="8" width="10" height="8" fill="#6a6a70" {o}/><path d="M16 38 L20 38 M18 36 L18 46" stroke="#eef4f8" stroke-width="1.8"/>
 {"".join(f'<g transform="translate({x} 22) rotate({r})"><rect x="-5" y="0" width="10" height="24" fill="#9a1e16" {o}/><rect x="-5.4" y="20" width="10.8" height="9" fill="#b07a3a" {o}/><path d="M-2.5 2 L-2.5 20" stroke="#d84a3a" stroke-width="1.4"/></g>' for x,r in ((38,-8),(50,8)))}
 {gl("M30 10 Q36 4 44 8 Q50 4 56 10", "#ff9a3a", 1.6)}'''
def humano_rolamento(E):
    return f'''{"".join(gl(f"M{32+20*math.cos(a):.1f} {32+20*math.sin(a):.1f} A20 20 0 0 1 {32+20*math.cos(a+1.6):.1f} {32+20*math.sin(a+1.6):.1f}", E, 2.4 - i*0.4) for i,a in enumerate((0.2, 2.3, 4.4)))}
 <path d="M48 20 L52 28 L44 26 Z" fill="{E}" filter="url(#gl)"/>
 <circle cx="32" cy="32" r="11" fill="#5a3a24" {o}/><path d="M22 28 Q32 18 42 28" fill="#3a2414" {o}/><ellipse cx="32" cy="27" rx="15" ry="4" fill="#4a2c18" {o}/>
 <path d="M24 36 Q32 42 40 36" fill="none" stroke="#3c5468" stroke-width="3"/>
 <path d="M8 56 Q20 50 30 56 Q40 60 56 54" fill="none" stroke="#6a5a48" stroke-width="2" opacity=".7"/>'''
def humano_ultimo_suspiro(E):
    return f'''<path d="M32 58 Q8 42 8 24 Q8 10 20 10 Q28 10 32 18 Q36 10 44 10 Q56 10 56 24 Q56 42 32 58 Z" fill="#3a0806" {o}/>
 <path d="M32 18 L30 26 L36 32 L28 42 L32 58" fill="none" stroke="{K}" stroke-width="3"/>
 {gl("M2 34 L14 34 L18 26 L24 44 L30 20 L36 40 L40 34 L62 34", E, 2.2)}<path d="M14 18 Q18 14 24 14" fill="none" stroke="#7a2a22" stroke-width="2"/>'''

def tecnomancer_arco_voltaico(E):
    return f'''{gl("M6 56 L18 40 L14 36 L28 22 L26 18 L40 10 M28 22 L42 30 L40 34 L56 40 M18 40 L30 48 L28 52 L42 58", E, 2.4)}
 <path d="M6 56 L18 40 L14 36 L28 22 L26 18 L40 10 M28 22 L42 30 L40 34 L56 40 M18 40 L30 48 L28 52 L42 58" fill="none" stroke="#ffffff" stroke-width="1"/>
 {"".join(f'<circle cx="{x}" cy="{y}" r="4.4" fill="#2a2226" {o}/>' for x,y in ((40,10),(56,40),(42,58)))}{"".join(dot(x,y,1.6,E) for x,y in ((40,10),(56,40),(42,58)))}
 <circle cx="6" cy="56" r="5" fill="#b07a3a" {o}/>'''
def tecnomancer_nanoreparo(E):
    def aranha(x, y, s):
        return f'''<g transform="translate({x} {y}) scale({s})"><path d="M-8 -6 L-3 -1 M8 -6 L3 -1 M-9 2 L-3 1 M9 2 L3 1 M-7 9 L-2 3 M7 9 L2 3" stroke="{K}" stroke-width="2.4"/>
 <path d="M-8 -6 L-3 -1 M8 -6 L3 -1 M-9 2 L-3 1 M9 2 L3 1 M-7 9 L-2 3 M7 9 L2 3" stroke="#e6b866" stroke-width="1"/><ellipse cx="0" cy="2" rx="4.4" ry="5" fill="#b07a3a" {o}/><circle cx="0" cy="0" r="1.6" fill="#ff9a3a" filter="url(#gl)"/></g>'''
    return f'''<path d="M32 58 Q8 42 8 24 Q8 10 20 10 Q28 10 32 18 Q36 10 44 10 Q56 10 56 24 Q56 42 32 58 Z" fill="#5a2622" {o} opacity=".9"/>
 <path d="M24 28 L40 28 M24 34 L40 34" stroke="{E}" stroke-width="1.2" stroke-dasharray="2 2" filter="url(#gl)"/>{aranha(22,26,1)}{aranha(40,36,0.9)}{aranha(32,46,0.7)}
 <path d="M24 16 L26 20 M44 14 L42 20" stroke="#ff9a3a" stroke-width="1.4"/>'''
def tecnomancer_torreta_sentinela(E):
    return f'''<path d="M32 40 L12 60 M32 40 L52 60 M32 40 L32 62" stroke="{K}" stroke-width="4.4"/><path d="M32 40 L12 60 M32 40 L52 60 M32 40 L32 62" stroke="#6a6a70" stroke-width="2.4"/>
 <rect x="20" y="24" width="24" height="18" rx="3" fill="#b07a3a" {o}/><path d="M22 26 L42 26" stroke="#e6b866" stroke-width="1.4"/>
 <rect x="42" y="28" width="18" height="5" fill="#4a5058" {o}/><rect x="42" y="34" width="18" height="5" fill="#4a5058" {o}/>
 <circle cx="29" cy="33" r="6" fill="#141012" {o}/>{dot(29,33,3,"#ff9a3a")}<path d="M24 24 L24 12 M24 12 L18 8 M24 12 L30 8" stroke="{K}" stroke-width="2.4"/><path d="M24 24 L24 12" stroke="#d8dce0" stroke-width="1"/>
 {gl("M60 30 L63 31 M60 36 L63 37", E, 1.4)}'''
def tecnomancer_campo_forca(E):
    hexes = "".join(f'<path d="M{x} {y} l5 -3 l5 3 l0 6 l-5 3 l-5 -3 Z" fill="none" stroke="{E}" stroke-width=".9" opacity=".75"/>' for x,y in ((12,28),(22,22),(32,22),(42,28),(17,36),(27,32),(37,32),(47,38),(22,44),(32,42),(12,46)))
    return f'''<path d="M4 54 Q4 8 32 8 Q60 8 60 54 Z" fill="{E}" fill-opacity=".14"/>{hexes}<path d="M4 54 Q4 8 32 8 Q60 8 60 54" fill="none" stroke="{E}" stroke-width="2.4" filter="url(#gl)"/>
 <ellipse cx="32" cy="54" rx="28" ry="5" fill="#1a2a36" {o}/><path d="M20 54 L22 44 L26 54 M38 54 L42 42 L44 54" fill="#141012" {o}/>{dot(48,16,1.4,"#ffffff")}'''
def tecnomancer_pulso_antidivino(E):
    return f'''{"".join(f'<circle cx="32" cy="32" r="{r}" fill="none" stroke="{E}" stroke-width="{2.4-i*0.5}" opacity="{1-i*0.22}" filter="url(#gl)"/>' for i,r in enumerate((14,21,28)))}
 <circle cx="32" cy="32" r="11" fill="#141012" {o}/><path d="M32 22 L32 42 M26 36 L38 36" stroke="#ff9a3a" stroke-width="2.4" filter="url(#gl)" transform="rotate(180 32 32)"/>
 <path d="M14 14 L50 50" stroke="{K}" stroke-width="5"/><path d="M14 14 L50 50" stroke="#d84a3a" stroke-width="2.6"/>'''
def tecnomancer_maquina_juizo_reverso(E):
    return f'''{gl("M14 22 L8 14 L12 12 L4 4 M50 22 L56 14 L52 12 L60 4", E, 1.8)}<path d="M18 62 L22 30 L42 30 L46 62 Z" fill="#b0603a" {o}/>
 <path d="M24 30 L26 14 L38 14 L40 30 Z" fill="#b07a3a" {o}/>{"".join(f'<path d="M{20+i*0.6} {38+i*7} L{44-i*0.6} {38+i*7}" stroke="{K}" stroke-width="1.6"/>' for i in range(3))}
 {"".join(f'<rect x="{x}" y="4" width="5" height="11" rx="2.4" fill="#6a8a9a" fill-opacity=".6" {o}/>' for x in (25,34))}{dot(27.5,9,1.8,"#ff9a3a")}{dot(36.5,9,1.8,"#ff9a3a")}
 <path d="M14 30 Q8 36 14 42 M50 30 Q56 36 50 42" fill="none" stroke="#e09a68" stroke-width="3"/><circle cx="32" cy="46" r="6" fill="#141012" {o}/>
 <path d="M32 50 L32 42 M28 44 L36 44" stroke="{E}" stroke-width="1.8" filter="url(#gl)" transform="rotate(180 32 46)"/>'''

FACCAO = {"anjo":"arautos","cultista":"arautos","demonio":"arautos","humano":"vigilia","mutante":"vigilia","tecnomancer":"vigilia"}
def defs(E, Ed):
    return f'''<defs><filter id="gl" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="1.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <radialGradient id="bg" cx="50%" cy="42%" r="70%"><stop offset="0" stop-color="{Ed}"/><stop offset=".75" stop-color="#0c0a0b"/><stop offset="1" stop-color="#050404"/></radialGradient>
 <radialGradient id="aura" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{E}" stop-opacity=".35"/><stop offset="1" stop-color="{E}" stop-opacity="0"/></radialGradient>
 <linearGradient id="gM" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eef0f2"/><stop offset=".5" stop-color="#9aa0a8"/><stop offset="1" stop-color="#4a5058"/></linearGradient>
 <linearGradient id="gO" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff0b0"/><stop offset=".5" stop-color="#c99a3e"/><stop offset="1" stop-color="#5a3a10"/></linearGradient>
 <linearGradient id="gS" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e04a3a"/><stop offset="1" stop-color="#4a0806"/></linearGradient>
 <linearGradient id="gF" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#ffd070"/><stop offset=".5" stop-color="#ff6a10"/><stop offset="1" stop-color="#3a0804"/></linearGradient>
 <linearGradient id="fA" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4dc90"/><stop offset=".45" stop-color="#a87a2e"/><stop offset="1" stop-color="#3a2408"/></linearGradient>
 <linearGradient id="fV" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#c8d4dc"/><stop offset=".45" stop-color="#5a6a78"/><stop offset="1" stop-color="#1a2028"/></linearGradient></defs>'''
def moldura(classe, conteudo, E, Ed):
    f = FACCAO[classe]; grad = "fA" if f == "arautos" else "fV"
    canto = "#7a1612" if f == "arautos" else "#b07a3a"
    cantos = "".join(f'<path d="M{x} {y} l{6*sx} 0 l{-6*sx} {6*sy} Z" fill="{canto}" stroke="{K}" stroke-width=".8"/>' for x,y,sx,sy in ((3,3,1,1),(61,3,-1,1),(3,61,1,-1),(61,61,-1,-1)))
    rebites = "" if f == "arautos" else "".join(f'<circle cx="{x}" cy="{y}" r="1.1" fill="#e6b866" stroke="{K}" stroke-width=".5"/>' for x,y in ((32,2.6),(32,61.4),(2.6,32),(61.4,32)))
    return f'''<rect x="0" y="0" width="64" height="64" rx="3" fill="{K}"/><rect x="4" y="4" width="56" height="56" fill="url(#bg)"/><circle cx="32" cy="32" r="26" fill="url(#aura)"/>
 <g transform="translate(32 32) scale(.82) translate(-32 -32)">{conteudo}</g>
 <rect x="2" y="2" width="60" height="60" rx="2.4" fill="none" stroke="url(#{grad})" stroke-width="3.2"/><rect x="4.4" y="4.4" width="55.2" height="55.2" fill="none" stroke="{K}" stroke-width="1"/>
 <rect x=".6" y=".6" width="62.8" height="62.8" rx="3" fill="none" stroke="{K}" stroke-width="1.2"/>{cantos}{rebites}
 <path d="M5 5 L59 5" stroke="#ffffff" stroke-opacity=".12" stroke-width="1"/>'''

def humano_corte_largo(E):
    arcos = "".join(gl(f"M{32+r*math.cos(a):.1f} {32+r*math.sin(a):.1f} A{r} {r} 0 0 1 {32+r*math.cos(a+2.2):.1f} {32+r*math.sin(a+2.2):.1f}", E, w) for r, a, w in ((26, 0.3, 3.2), (26, 2.4, 2.4), (26, 4.5, 1.6), (19, 1.2, 1.8), (19, 3.8, 1.2)))
    pontas = "".join(f'<path d="M{32+26*math.cos(a+2.2):.1f} {32+26*math.sin(a+2.2):.1f} l{4*math.cos(a+2.2+1.9):.1f} {4*math.sin(a+2.2+1.9):.1f}" stroke="{E}" stroke-width="2.4" filter="url(#gl)"/>' for a in (0.3, 2.4))
    lam = f'''<g transform="rotate(-35 32 32)"><path d="M28 34 L28 4 L32 -1 L36 4 L36 34 Z" fill="url(#gM)" {o}/><path d="M31 4 L31 32 L33 32 L33 4 Z" fill="#4a5058"/>
 <path d="M20 34 L44 34 L42 38 L22 38 Z" fill="#8a9098" {o}/><rect x="29.5" y="38" width="5" height="9" fill="#5a3a24" {o}/><circle cx="32" cy="49" r="2.6" fill="#8a9098" {o}/></g>'''
    return f'''{arcos}{pontas}{raios(32,32,28,31,16,"#fff0c0",1)}{lam}<ellipse cx="32" cy="54" rx="16" ry="3.6" fill="#000" opacity=".45"/>'''

def humano_arrancada(E):
    def lamina(dx, op, cor="url(#gM)"):
        return f'''<g transform="translate({dx} {-dx}) rotate(45 32 32)" opacity="{op}"><path d="M27 40 L27 6 L32 0 L37 6 L37 40 Z" fill="{cor}" {o}/><path d="M31 6 L31 38 L33 38 L33 6 Z" fill="#4a5058"/>
 <path d="M18 40 L46 40 L43 45 L21 45 Z" fill="#8a9098" {o}/><rect x="29.5" y="45" width="5" height="10" fill="#5a3a24" {o}/><circle cx="32" cy="57" r="2.8" fill="#8a9098" {o}/></g>'''
    return f'''{"".join(gl(f"M{x} {y} L{x+16} {y-16}", E, w) for x,y,w in ((2,46,2.2),(6,58,1.6),(14,62,1.2),(0,36,1.2)))}
 {lamina(-14, .22, "#3a3436")}{lamina(-7, .45, "#5a5458")}{lamina(4, 1)}{raios(54,10,3,9,7,"#fff0c0",1.4)}{gl("M30 34 L52 12", "#ffffff", 1)}'''

# ---------- skills de área do nível 5 ----------
def _leque(cx, cy, r, a0, a1, cor, op=.55):
    p0 = (cx + r*math.cos(math.radians(a0)), cy + r*math.sin(math.radians(a0))); p1 = (cx + r*math.cos(math.radians(a1)), cy + r*math.sin(math.radians(a1)))
    return f'<path d="M{cx} {cy} L{p0[0]:.1f} {p0[1]:.1f} A{r} {r} 0 0 1 {p1[0]:.1f} {p1[1]:.1f} Z" fill="{cor}" opacity="{op}" filter="url(#gl)"/>'
def anjo_leque_juizo(E):
    chamas = ""
    for a in range(-92, 8, 12):
        r = math.radians(a); ux, uy = math.cos(r), math.sin(r); px, py = -uy, ux
        bx, by = 12 + 20*ux, 52 + 20*uy
        chamas += f'<path d="M{bx+3*px:.1f} {by+3*py:.1f} Q{bx+14*ux+5*px:.1f} {by+14*uy+5*py:.1f} {bx+26*ux:.1f} {by+26*uy:.1f} Q{bx+12*ux-5*px:.1f} {by+12*uy-5*py:.1f} {bx-3*px:.1f} {by-3*py:.1f} Z" fill="url(#gO)" stroke="#5a3a10" stroke-width=".8"/>'
        chamas += f'<path d="M{bx+6*ux:.1f} {by+6*uy:.1f} L{bx+18*ux:.1f} {by+18*uy:.1f}" stroke="#fff8e0" stroke-width="1.2"/>'
    return f'''{_leque(12,52,50,-98,12,E,.28)}{chamas}{gl("M12 52 m0 -46 A46 46 0 0 1 58 52", E, 1.8)}
 {espada(20,44,45,0.82,E,("#fff4cc","#e8c46a","#7a5a1e"))}{gl("M4 44 Q14 18 42 10", "#ffffff", 2)}{dot(12,52,3,"#fff8e0")}'''
def cultista_espinhos_sangue(E):
    espinhos = "".join(f'<path d="M{x-3.4*s} {y} L{x} {y-16*s} L{x+3.4*s} {y} Z" fill="url(#gS)" {o}/><path d="M{x-1} {y-2} L{x} {y-13*s}" stroke="#ff9a8a" stroke-width="1"/>' for x,y,s in ((20,44,0.8),(44,44,0.8),(32,40,1.15),(25,52,1),(39,52,1),(32,56,0.7),(14,52,0.6),(50,52,0.6)))
    return f'''<ellipse cx="32" cy="48" rx="26" ry="11" fill="#3a0604" {o}/><ellipse cx="32" cy="48" rx="26" ry="11" fill="none" stroke="{E}" stroke-width="1.6" filter="url(#gl)"/>
 <ellipse cx="32" cy="48" rx="19" ry="8" fill="none" stroke="#9a1410" stroke-width="1.2" stroke-dasharray="3 2"/>{espinhos}
 {"".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#9a1410" {o}/>' for x,y,r in ((12,22,2.4),(52,18,1.8),(46,28,1.4),(18,30,1.4)))}{dot(32,10,3,E)}<path d="M32 13 Q31 20 32 24" stroke="#9a1410" stroke-width="2.4" fill="none"/>'''
def mutante_terremoto_putrido(E):
    rach = "M32 48 L20 54 L10 52 M32 48 L44 56 L54 54 M32 48 L28 60 M32 48 L42 44 L56 44 M32 48 L22 44 L8 46"
    return f'''<ellipse cx="32" cy="48" rx="30" ry="12" fill="none" stroke="#c8b890" stroke-width="2.4" opacity=".7"/><ellipse cx="32" cy="48" rx="22" ry="8" fill="#2a2a1e" {o}/>
 <path d="{rach}" fill="none" stroke="{K}" stroke-width="3"/>{gl(rach, E, 1.6)}{"".join(f'<path d="M{x} {y} l-3 -6 l6 0 Z" fill="#6a5a48" {o}/>' for x,y in ((6,42),(58,42),(14,60),(52,62)))}
 <path d="M22 0 Q20 12 18 22 L48 22 Q44 12 42 0 Z" fill="#5a604c" {o}/><path d="M26 2 Q24 12 23 20" fill="none" stroke="#7a806a" stroke-width="1.6"/>
 <path d="M18 14 L46 12" stroke="{FER[1]}" stroke-width="3"/><path d="M18 14 L46 12" stroke="{K}" stroke-width=".8" stroke-dasharray="2 2"/>
 <path d="M12 30 Q10 20 22 20 L44 20 Q56 20 54 32 L52 42 Q50 48 42 48 L22 48 Q12 48 12 40 Z" fill="#6a7058" {o}/>
 {"".join(f'<ellipse cx="{x}" cy="44" rx="5" ry="4.4" fill="#7a806a" {o}/>' for x in (18,27,36,45))}{"".join(f'<path d="M{x} 40 Q{x+1} 34 {x+2} 28" fill="none" stroke="#3a4030" stroke-width="1.4"/>' for x in (22,31,40))}
 <path d="M18 26 Q30 22 44 24" fill="none" stroke="#9aa078" stroke-width="2"/>{"".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{E}" stroke="{K}" stroke-width="1"/>' for x,y,r in ((22,30,2.6),(36,28,2),(46,34,2.2)))}
 {"".join(dot(x,y,1.6,E) for x,y in ((12,48),(52,50),(30,58)))}'''
def demonio_ceifa_infernal(E):
    return f'''{_leque(32,40,30,180,360,E,.35)}<path d="M4 40 A28 28 0 0 1 60 40" fill="none" stroke="{K}" stroke-width="7"/>{gl("M4 40 A28 28 0 0 1 60 40", E, 4)}{gl("M10 40 A22 22 0 0 1 54 40", "#ffd070", 1.4)}
 {"".join(f'<path d="M{x} 54 Q{x-3} 46 {x+1} 42 Q{x+5} 48 {x+4} 54 Z" fill="#ff9a3a" opacity=".85" filter="url(#gl)"/>' for x in (8,18,28,38,48))}
 <g transform="rotate(-25 32 40)"><rect x="30" y="22" width="4" height="40" fill="#4a2c18" {o}/><path d="M32 22 Q12 14 4 30 Q16 22 32 28 Z" fill="#2e2a2c" {o}/>{gl("M28 23 Q14 18 7 27", E, 1.6)}</g>
 <path d="M4 58 L60 58" stroke="#3a1004" stroke-width="3"/>'''
def humano_coquetel_querosene(E):
    return f'''<ellipse cx="38" cy="50" rx="22" ry="9" fill="#ff7a1a" opacity=".55" filter="url(#gl)"/>{"".join(f'<path d="M{x} 54 Q{x-4} {44-h} {x+1} {38-h} Q{x+6} {46-h} {x+5} 54 Z" fill="{c}" filter="url(#gl)"/>' for x,h,c in ((22,0,"#ff9a3a"),(30,8,"#ffd070"),(38,12,"#ff9a3a"),(46,6,"#ffd070"),(52,0,"#ff7a1a")))}
 {"".join(f'<path d="M{38+20*math.cos(a):.1f} {44+10*math.sin(a):.1f} l{3*math.cos(a):.1f} {2*math.sin(a):.1f}" stroke="#bfe6ff" stroke-width="1.6"/>' for a in [i*0.9 for i in range(7)])}
 <path d="M6 36 Q14 14 30 20" fill="none" stroke="#c8c0b0" stroke-width="1.2" stroke-dasharray="2 3" opacity=".7"/>
 <g transform="rotate(-30 14 26)"><path d="M10 16 L18 16 L18 22 Q22 26 22 34 L22 44 L6 44 L6 34 Q6 26 10 22 Z" fill="#6a8a5a" fill-opacity=".8" {o}/><path d="M7 34 L21 34 L21 43 L7 43 Z" fill="#c8a040" opacity=".8"/>
 <path d="M11 10 L17 10 L17 16 L11 16 Z" fill="#c8bca0" {o}/><path d="M14 10 Q12 4 16 2" fill="none" stroke="#c8bca0" stroke-width="2"/></g>{dot(17,4,2.6,"#ff9a3a")}'''
def tecnomancer_tempestade_bobina(E):
    raios_z = "".join(gl(f"M32 30 L{32+12*math.cos(a):.1f} {30+8*math.sin(a)-4:.1f} L{32+18*math.cos(a+0.25):.1f} {30+13*math.sin(a+0.25):.1f} L{32+27*math.cos(a):.1f} {30+20*math.sin(a):.1f}", E, 1.6) for a in [i*math.pi/4+0.3 for i in range(8)])
    return f'''<circle cx="32" cy="30" r="27" fill="{E}" opacity=".12"/><circle cx="32" cy="30" r="27" fill="none" stroke="{E}" stroke-width="1.4" filter="url(#gl)" stroke-dasharray="4 3"/>{raios_z}
 <rect x="22" y="24" width="20" height="22" rx="4" fill="#b07a3a" {o}/><path d="M24 28 L40 28" stroke="#e6b866" stroke-width="1.4"/>{"".join(f'<rect x="{x}" y="10" width="5" height="16" rx="2" fill="#b0603a" {o}/><path d="M{x} {y} l5 0" stroke="#e09a68" stroke-width="1"/>' for x in (23,36) for y in (14,18,22))}
 {dot(25.5,9,2.6,E)}{dot(38.5,9,2.6,E)}<circle cx="32" cy="36" r="4" fill="#141012" {o}/>{dot(32,36,2,"#ff9a3a")}
 {"".join(f'<path d="M{x} {y} l2 -3 l2 3" fill="none" stroke="#ffffff" stroke-width="1"/>' for x,y in ((6,52),(54,50),(10,14),(50,12)))}'''
