# Motivos extras: bases genéricas novas + itens com nome da thread Missões. Mesmas convenções de motivos_itens.py.
import math
import motivos_itens as MI
from motivos_itens import K, o, TINTS, LAT, COU, MAD, OSS, ACO, FER, glow, diag, rot
def gdot(x, y, r, c): return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" filter="url(#glow)"/>'
VERM = "#7a1612"; PAPEL = ("#e6dcc0", "#c4b48e", "#7a6a4a")

# ---------- bases genéricas ----------
def rosario(t, e):
    L,M,D = t
    beads = "".join(f'<circle cx="{32+20*math.cos(a):.1f}" cy="{26+18*math.sin(a):.1f}" r="3" fill="{M}" {o}/><circle cx="{31+20*math.cos(a):.1f}" cy="{25+18*math.sin(a):.1f}" r="1" fill="{L}"/>' for a in [math.pi*(0.62+i*0.157) for i in range(-8,5)])
    return f'''<ellipse cx="32" cy="26" rx="20" ry="18" fill="none" stroke="{K}" stroke-width="1"/>{beads}
 <path d="M32 44 L32 50" stroke="{K}" stroke-width="1.6"/><path d="M29 50 L35 50 L35 54 L39 54 L39 58 L35 58 L35 63 L29 63 L29 58 L25 58 L25 54 L29 54 Z" fill="{L}" {o}/>{glow("M32 52 L32 61", e, 1.2)}'''
def terco_partido(t, e):
    L,M,D = t
    beads = "".join(f'<circle cx="{32+20*math.cos(a):.1f}" cy="{28+18*math.sin(a):.1f}" r="3" fill="{M}" {o}/>' for a in [math.pi*(0.55+i*0.16) for i in range(0,7)])
    loose = "".join(f'<circle cx="{x}" cy="{y}" r="2.6" fill="{M}" {o}/>' for x,y in ((46,52),(52,46),(40,58)))
    return f'''{beads}{loose}<path d="M26 40 L30 44 M8 30 l-2 -4" stroke="{K}" stroke-width="1"/>
 <path d="M15 42 L19 42 L19 46 L23 46 L23 50 L19 50 L19 58 L15 58 L15 50 L11 50 L11 46 L15 46 Z" fill="{L}" {o}/><path d="M17 44 L17 56" stroke="{D}" stroke-width="1"/>'''
def gazua(t, e):
    L,M,D = t
    return f'''<path d="M10 54 L40 24 L44 26 L50 18 L46 14 L52 10" fill="none" stroke="{K}" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/>
 <path d="M10 54 L40 24 L44 26 L50 18 L46 14 L52 10" fill="none" stroke="{L}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
 <path d="M14 58 L46 32 L50 36 L56 30" fill="none" stroke="{K}" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M14 58 L46 32 L50 36 L56 30" fill="none" stroke="{M}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
 <rect x="6" y="48" width="12" height="12" rx="2" fill="{COU[1]}" {o} transform="rotate(-40 12 54)"/>'''
def couro(t, e):
    L,M,D = t
    return f'''<path d="M10 14 Q20 8 28 14 Q36 6 46 12 Q56 14 54 26 Q60 36 52 44 Q54 56 40 54 Q32 60 22 54 Q8 56 10 44 Q4 34 12 26 Q6 18 10 14 Z" fill="{M}" {o}/>
 <path d="M16 20 Q26 14 34 18 Q44 14 48 22" fill="none" stroke="{L}" stroke-width="1.8"/><path d="M20 40 Q30 36 42 42 M18 30 Q26 28 30 32" fill="none" stroke="{D}" stroke-width="1.6"/>
 {"".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#4a5a2a" stroke="{K}" stroke-width=".8"/>' for x,y,r in ((38,32,2.6),(24,46,2),(46,48,1.6)))}<path d="M12 26 l-4 -2 M52 44 l5 1" stroke="{K}" stroke-width="1.4"/>'''
def sucata(t, e):
    L,M,D = t
    cog = " ".join(f"{20+(11 if (i//2)%2==0 else 8)*math.cos(math.radians(i*22.5)):.1f},{40+(11 if (i//2)%2==0 else 8)*math.sin(math.radians(i*22.5)):.1f}" for i in range(16))
    return f'''<rect x="24" y="8" width="10" height="34" rx="2" fill="{FER[1]}" {o} transform="rotate(30 29 25)"/><path d="M25 10 L25 40" stroke="{FER[0]}" stroke-width="1.4" transform="rotate(30 29 25)"/>
 <rect x="22" y="9" width="14" height="5" fill="{FER[2]}" {o} transform="rotate(30 29 25)"/>
 <polygon points="{cog}" fill="{M}" {o}/><circle cx="20" cy="40" r="3.4" fill="{K}"/>
 <path d="M40 44 Q46 36 52 44 Q58 52 50 56" fill="none" stroke="{K}" stroke-width="3.6"/><path d="M40 44 Q46 36 52 44 Q58 52 50 56" fill="none" stroke="{ACO[1]}" stroke-width="1.8"/>
 <path d="M36 56 l6 -3 l4 4 l-6 3 Z" fill="{LAT[1]}" {o}/><path d="M44 18 l8 0 l0 8 l-8 0 Z" fill="{M}" {o}/><circle cx="48" cy="22" r="1.6" fill="{K}"/>'''
def carne(t, e):
    L,M,D = t
    return f'''<path d="M8 36 Q8 18 26 16 Q42 12 52 22 Q60 32 52 44 Q42 56 24 52 Q8 50 8 36 Z" fill="{M}" {o}/>
 <path d="M14 34 Q18 24 28 22 Q40 20 46 28" fill="none" stroke="{L}" stroke-width="2"/><path d="M20 40 Q30 34 42 40 M24 46 Q34 44 40 48" fill="none" stroke="#d8b8a0" stroke-width="1.6"/>
 <circle cx="40" cy="34" r="5" fill="#e8d8c0" {o}/><circle cx="40" cy="34" r="2" fill="#c8a888"/>
 {"".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#6a7a3a" stroke="{K}" stroke-width=".8"/>' for x,y,r in ((18,30,2.4),(30,48,1.8)))}<path d="M50 14 Q54 10 52 6 M44 12 Q46 8 44 4" fill="none" stroke="#7a806a" stroke-width="1.4"/>'''
def pedra_benta(t, e):
    L,M,D = t
    return f'''<path d="M10 46 L16 18 L36 10 L54 20 L56 44 L40 56 L18 54 Z" fill="{M}" {o}/><path d="M16 18 L36 10 L54 20 L34 26 Z" fill="{L}" {o}/>
 <path d="M34 26 L40 56 M34 26 L10 46" stroke="{D}" stroke-width="1.4"/>
 <path d="M28 30 L32 30 L32 34 L36 34 L36 38 L32 38 L32 48 L28 48 L28 38 L24 38 L24 34 L28 34 Z" fill="#141012" opacity=".55"/>{glow("M30 32 L30 46 M26 36 L34 36", e or "#ffe08a", 1.2)}'''
def cera(t, e):
    L,M,D = t
    stubs = "".join(f'<g transform="translate({x} {y})"><path d="M-6 0 L-6 -{h} Q-3 -{h+3} 0 -{h} Q3 -{h+2} 6 -{h} L6 0 Z" fill="{M}" {o}/><path d="M-4 -{h-2} L-4 -2" stroke="{L}" stroke-width="1.6"/><path d="M0 -{h} L0 -{h+4}" stroke="{K}" stroke-width="1.2"/></g>' for x,y,h in ((18,52,18),(34,56,26),(48,50,12)))
    return f'''<path d="M4 56 Q32 50 60 56 Q58 62 32 62 Q6 62 4 56 Z" fill="{L}" {o}/>{stubs}<path d="M26 40 Q22 48 26 54 M42 46 Q46 50 44 56" fill="none" stroke="{L}" stroke-width="2"/>'''
def bau_faminto(t, e):
    L,M,D = t
    teeth = "".join(f'<path d="M{x} 30 l3 7 l3 -7" fill="#ece2cc" stroke="{K}" stroke-width=".8"/>' for x in range(9,55,6)) + "".join(f'<path d="M{x} 34 l3 -7 l3 7" fill="#ece2cc" stroke="{K}" stroke-width=".8"/>' for x in range(12,52,6))
    return f'''<path d="M6 34 L58 34 L56 60 L8 60 Z" fill="{M}" {o}/><path d="M4 30 Q4 6 32 4 Q60 6 60 30 L56 26 Q32 18 8 26 Z" fill="{M}" {o} transform="rotate(-10 6 30)"/>
 <path d="M8 26 Q32 18 56 26 L58 34 L6 34 Z" fill="#3a0806"/>{teeth}<path d="M18 30 Q32 40 46 30" fill="none" stroke="#9a2a22" stroke-width="3"/>
 {"".join(f'<path d="M8 {y} L56 {y}" stroke="{D}" stroke-width="1.2"/>' for y in (44,52))}<circle cx="22" cy="14" r="3" fill="#ffd040" filter="url(#glow)"/><circle cx="40" cy="12" r="3" fill="#ffd040" filter="url(#glow)"/>
 <circle cx="22" cy="14" r="1.2" fill="{K}"/><circle cx="40" cy="12" r="1.2" fill="{K}"/><path d="M8 60 l-3 3 M56 60 l3 3 M20 60 l-1 3 M44 60 l1 3" stroke="{K}" stroke-width="2"/>'''

# ---------- itens de missão ----------
def bobina(t, e):
    L,M,D = t
    turns = "".join(f'<path d="M{14+i*4.4} 18 Q{16+i*4.4} 32 {14+i*4.4} 46" fill="none" stroke="{K}" stroke-width="4"/><path d="M{14+i*4.4} 18 Q{16+i*4.4} 32 {14+i*4.4} 46" fill="none" stroke="{M if i%2 else L}" stroke-width="2.4"/>' for i in range(9))
    return f'''<rect x="8" y="14" width="6" height="36" rx="2" fill="{MAD[1]}" {o}/><rect x="52" y="14" width="6" height="36" rx="2" fill="{MAD[1]}" {o}/>{turns}
 <path d="M55 50 Q58 58 50 60 Q44 62 46 56" fill="none" stroke="{K}" stroke-width="3.2"/><path d="M55 50 Q58 58 50 60 Q44 62 46 56" fill="none" stroke="{L}" stroke-width="1.6"/>'''
def raiz(t, e):
    L,M,D = t
    return f'''<path d="M30 4 Q24 16 28 28 Q20 36 12 34 M28 28 Q30 42 22 56 M28 28 Q38 36 48 34 Q54 40 56 50 M30 40 Q38 48 36 60 M22 44 Q14 48 10 58" fill="none" stroke="{K}" stroke-width="5.6" stroke-linecap="round"/>
 <path d="M30 4 Q24 16 28 28 Q20 36 12 34 M28 28 Q30 42 22 56 M28 28 Q38 36 48 34 Q54 40 56 50 M30 40 Q38 48 36 60 M22 44 Q14 48 10 58" fill="none" stroke="{L}" stroke-width="3.4" stroke-linecap="round"/>
 <path d="M27 8 Q24 18 27 26" fill="none" stroke="{D}" stroke-width="1"/>{"".join(f'<circle cx="{x}" cy="{y}" r="2.6" fill="#3a2a1a"/>' for x,y in ((34,14),(18,24),(44,46)))}'''
def tigela(t, e):
    L,M,D = t
    return f'''<path d="M6 30 L58 30 Q56 52 40 56 L24 56 Q8 52 6 30 Z" fill="{M}" {o}/><ellipse cx="32" cy="30" rx="26" ry="7" fill="{D}" {o}/>
 <ellipse cx="32" cy="31" rx="22" ry="5" fill="#8a6a3a"/><path d="M18 30 Q24 28 30 31 M36 29 Q42 32 48 30" stroke="#c8a060" stroke-width="1.6" fill="none"/>
 <path d="M38 30 Q44 24 42 18 L40 14 L46 20 Q48 28 42 32 Z" fill="#5a7a2a" {o}/><path d="M10 36 Q14 48 24 52" fill="none" stroke="{L}" stroke-width="2"/>
 {"".join(f'<path d="M{x} 22 Q{x-3} 16 {x} 10 Q{x+3} 6 {x} 2" fill="none" stroke="#c8c0b0" stroke-width="1.6" opacity=".55"/>' for x in (22,32))}<rect x="22" y="56" width="20" height="4" fill="{D}" {o}/>'''
def medalha(t, e):
    L,M,D = t
    return f'''<path d="M10 4 Q20 12 18 22 Q28 30 22 40 L14 34 Q16 26 8 20 Q2 12 10 4 Z" fill="#c84a4a" {o}/>{"".join(f'<circle cx="{x}" cy="{y}" r="1.8" fill="#ece2cc"/>' for x,y in ((10,10),(14,18),(18,28),(10,22)))}
 <path d="M22 34 Q28 30 34 32" fill="none" stroke="{K}" stroke-width="1.6"/><circle cx="40" cy="42" r="15" fill="{M}" {o}/><circle cx="40" cy="42" r="11" fill="none" stroke="{D}" stroke-width="1.4"/>
 <path d="M37 34 L43 34 L43 38 L47 38 L47 43 L43 43 L43 51 L37 51 L37 43 L33 43 L33 38 L37 38 Z" fill="{L}" stroke="{D}" stroke-width="1"/><path d="M28 36 Q32 30 38 28" fill="none" stroke="{L}" stroke-width="1.6"/>
 <path d="M50 50 l3 4" stroke="{D}" stroke-width="2"/>'''
def sebo(t, e):
    L,M,D = t
    return f'''<path d="M14 18 L50 18 L48 56 Q32 60 16 56 Z" fill="#6a7a7a" fill-opacity=".55" {o}/><path d="M16 28 Q32 24 48 28 L47 55 Q32 59 17 55 Z" fill="#d8c060"/>
 <path d="M18 30 Q24 36 22 44 M34 30 Q38 40 34 50" fill="none" stroke="#a8902a" stroke-width="1.6"/><path d="M14 18 L50 18 L48 56 Q32 60 16 56 Z" fill="none" {o}/>
 <rect x="12" y="12" width="40" height="7" fill="{MAD[1]}" {o}/><path d="M20 22 L20 52" stroke="#eef4f8" stroke-width="1.6" opacity=".6"/>{"".join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="#f0e090"/>' for x,y in ((28,40),(40,46),(30,50)))}'''
def badalo(t, e):
    L,M,D = t
    return diag(f'''<rect x="29" y="2" width="6" height="12" rx="2" fill="{FER[1]}" {o}/><circle cx="32" cy="6" r="2" fill="{K}"/>
 <path d="M30 14 L34 14 L35 40 L29 40 Z" fill="{M}" {o}/><path d="M31 15 L31 39" stroke="{L}" stroke-width="1.2"/>
 <ellipse cx="32" cy="50" rx="11" ry="13" fill="{M}" {o}/><path d="M25 44 Q26 38 32 38" fill="none" stroke="{L}" stroke-width="2"/><path d="M36 42 L33 50 L37 56" fill="none" stroke="{K}" stroke-width="1.6"/>''')
def livro(t, e):
    L,M,D = t
    return f'''<path d="M12 10 L46 6 L52 10 L52 58 L18 60 L12 56 Z" fill="{D}" {o}/><path d="M12 10 L46 6 L46 54 L12 56 Z" fill="{M}" {o}/>
 <path d="M46 6 L52 10 L52 58 L46 54 Z" fill="{PAPEL[1]}" {o}/><path d="M48 12 L48 54 M50 12 L50 56" stroke="{PAPEL[2]}" stroke-width=".7"/>
 <path d="M14 12 L44 8" stroke="{L}" stroke-width="1.4"/>{"".join(f'<rect x="{x}" y="{y}" width="5" height="5" fill="{LAT[1]}" {o}/>' for x,y in ((13,11),(40,8),(13,50),(40,49)))}
 <rect x="20" y="20" width="20" height="12" fill="{PAPEL[0]}" {o}/><path d="M23 24 L37 24 M23 28 L34 28" stroke="{PAPEL[2]}" stroke-width="1.2"/>
 <path d="M28 40 L28 50 M24 43 L32 43" stroke="{LAT[1]}" stroke-width="2"/>{glow("M30 22 L30 30", e, 1)}'''
def chave_gancho(t, e):
    L,M,D = t
    return diag(f'''<path d="M32 30 L32 12 Q32 2 24 2 Q16 2 16 10 Q16 16 22 16" fill="none" stroke="{K}" stroke-width="6.4" stroke-linecap="round"/>
 <path d="M32 30 L32 12 Q32 2 24 2 Q16 2 16 10 Q16 16 22 16" fill="none" stroke="{M}" stroke-width="3.6" stroke-linecap="round"/><path d="M20 15 L24 18 L23 13 Z" fill="{L}" {o}/>
 <rect x="29.5" y="28" width="5" height="30" fill="{M}" {o}/><path d="M34 44 L42 44 L42 48 L38 48 L38 52 L42 52 L42 58 L34 58" fill="{M}" {o}/>
 <rect x="36" y="26" width="16" height="9" rx="2" fill="{COU[1]}" {o} transform="rotate(-45 44 30)"/><path d="M30 30 L31 56" stroke="{L}" stroke-width="1"/>''')
def lacre(t, e):
    L,M,D = t
    pts = " ".join(f"{32+(24 if i%2==0 else 20)*math.cos(i*math.pi/10):.1f},{32+(24 if i%2==0 else 20)*math.sin(i*math.pi/10):.1f}" for i in range(20))
    return f'''<polygon points="{pts}" fill="{M}" {o}/><circle cx="32" cy="32" r="15" fill="{D}" stroke="{K}" stroke-width="1.2"/>
 <path d="M20 22 Q26 14 36 14" fill="none" stroke="{L}" stroke-width="2"/>
 <path d="M24 38 L36 26 Q42 22 44 28 Q40 30 38 34 L28 42 Z" fill="{M}" stroke="{K}" stroke-width="1"/><circle cx="23" cy="40" r="3" fill="{M}" stroke="{K}" stroke-width="1"/>
 {glow("M22 32 Q32 20 42 32 Q32 44 22 32", e, 1.4)}'''
def bocal(t, e):
    L,M,D = t
    return diag(f'''<path d="M22 6 Q32 0 42 6 Q40 16 35 20 L34 58 L30 58 L29 20 Q24 16 22 6 Z" fill="{M}" {o}/><ellipse cx="32" cy="6" rx="10" ry="3.6" fill="{D}" {o}/>
 <path d="M26 8 Q28 14 31 18" fill="none" stroke="{L}" stroke-width="1.6"/><path d="M31 22 L31 56" stroke="{L}" stroke-width="1"/>
 <ellipse cx="32" cy="6" rx="7" ry="2.4" fill="{TINTS['chumbo'][1]}" {o}/><path d="M27 6 L37 6" stroke="{TINTS['chumbo'][0]}" stroke-width="1"/>
 <rect x="28" y="40" width="8" height="4" fill="{D}" {o}/>{glow("M24 8 Q32 14 40 8", e, 1.2)}''')
def carta(t, e):
    L,M,D = t
    return f'''<path d="M6 16 L58 16 L58 50 L6 50 Z" fill="{PAPEL[0]}" {o}/><path d="M6 16 L32 36 L58 16" fill="none" stroke="{PAPEL[2]}" stroke-width="1.6"/>
 <path d="M6 50 L26 32 M58 50 L38 32" stroke="{PAPEL[1]}" stroke-width="1.4"/><path d="M14 44 L30 44 M14 40 L24 40" stroke="#4a3a2a" stroke-width="1"/>
 <circle cx="32" cy="36" r="6.5" fill="#6a1a26" {o}/><circle cx="32" cy="36" r="3.4" fill="none" stroke="#9a3040" stroke-width="1"/><path d="M6 16 l4 4 M50 50 l6 -4" stroke="{PAPEL[2]}" stroke-width="1"/>'''
def mapa(t, e):
    L,M,D = t
    return f'''<path d="M4 12 L22 8 L42 14 L60 10 L58 52 L40 56 L22 50 L6 54 Z" fill="{PAPEL[0]}" {o}/><path d="M22 8 L22 50 M42 14 L40 56" stroke="{PAPEL[1]}" stroke-width="1.4"/>
 <path d="M60 10 L54 18 L58 24 L52 32 L58 40" fill="none" stroke="{K}" stroke-width="1.4"/><path d="M10 40 Q20 30 30 34 Q38 38 48 26" fill="none" stroke="#4a3a2a" stroke-width="1.4" stroke-dasharray="3 2"/>
 {"".join(f'<path d="M{x-3} {y-3} L{x+3} {y+3} M{x+3} {y-3} L{x-3} {y+3}" stroke="#9a1e16" stroke-width="2"/>' for x,y in ((14,22),(34,44),(48,24)))}
 <circle cx="28" cy="20" r="3" fill="none" stroke="#4a3a2a" stroke-width="1.2"/><circle cx="27" cy="19.5" r=".7" fill="#4a3a2a"/><circle cx="29" cy="19.5" r=".7" fill="#4a3a2a"/>'''
def relicario_peq(t, e):
    L,M,D = t
    return f'''<path d="M16 22 L48 22 L48 54 L16 54 Z" fill="{M}" {o}/><path d="M12 22 Q12 8 32 8 Q52 8 52 22 Z" fill="{L}" {o}/><path d="M16 22 L48 22" stroke="{K}" stroke-width="2"/>
 <rect x="22" y="28" width="20" height="20" rx="2" fill="#141012" {o}/><path d="M24 46 L40 30" stroke="#3a3436" stroke-width="1.2"/>
 <path d="M30 2 L34 2 L34 6 L38 6 L38 10 L34 10 L34 14 L30 14 L30 10 L26 10 L26 6 L30 6 Z" fill="{L}" {o}/>{"".join(f'<circle cx="{x}" cy="{y}" r="1.6" fill="{L}" stroke="{K}" stroke-width=".7"/>' for x,y in ((19,25),(45,25),(19,51),(45,51)))}
 <path d="M14 56 L50 56 L48 60 L16 60 Z" fill="{D}" {o}/>'''
def pa(t, e):
    L,M,D = t
    return diag(f'''<rect x="30" y="2" width="4.6" height="40" fill="{MAD[1]}" {o}/><path d="M31.2 4 L31.2 40" stroke="{MAD[0]}" stroke-width="1"/>
 <path d="M26 2 L38 2" stroke="{K}" stroke-width="4"/><path d="M26 2 L38 2" stroke="{MAD[0]}" stroke-width="2"/>
 <path d="M24 42 L40 42 L40 54 Q32 64 24 54 Z" fill="{M}" {o}/><path d="M27 44 L27 54" stroke="{L}" stroke-width="1.6"/><path d="M34 50 l3 4" stroke="{D}" stroke-width="2"/>''')
def caixinha(t, e):
    L,M,D = t
    return f'''<path d="M10 34 L54 34 L54 56 L10 56 Z" fill="{M}" {o}/><path d="M10 34 L18 26 L62 26 L54 34 Z" fill="{L}" {o}/><path d="M54 34 L62 26 L62 48 L54 56 Z" fill="{D}" {o}/>
 <path d="M14 40 L50 40 M14 50 L50 50" stroke="{D}" stroke-width="1.2"/><path d="M58 34 Q64 36 62 42" fill="none" stroke="{K}" stroke-width="2"/>
 <path d="M34 26 L34 12" stroke="{K}" stroke-width="1.4"/><path d="M30 20 Q34 16 38 20 L40 26 L28 26 Z" fill="#d8ccb0" {o}/><path d="M28 18 L40 14" stroke="#d8ccb0" stroke-width="1.6"/>
 <path d="M24 18 l1 -4 M44 10 q2 -2 4 0" stroke="{L}" stroke-width="1.2" fill="none"/>'''
def pao(t, e):
    L,M,D = t
    return f'''<path d="M6 40 Q4 22 22 18 Q32 10 44 16 Q60 20 58 38 Q58 52 32 54 Q8 54 6 40 Z" fill="{M}" {o}/>
 <path d="M12 30 Q18 22 28 22" fill="none" stroke="{L}" stroke-width="2"/>{"".join(f'<path d="M{x} {y} q4 -6 8 0" fill="none" stroke="{D}" stroke-width="2"/>' for x,y in ((16,34),(28,30),(40,32)))}
 <path d="M44 40 L52 46 L46 50 Z" fill="#c8a878" {o}/>{"".join(f'<circle cx="{x}" cy="{y}" r=".9" fill="#e8d8b0"/>' for x,y in ((20,42),(30,44),(38,40),(26,38)))}'''
def tonico(t, e):
    L,M,D = t
    return f'''<path d="M26 22 L38 22 L44 30 L44 58 L20 58 L20 30 Z" fill="{M}" fill-opacity=".9" {o}/><rect x="28" y="8" width="8" height="14" fill="{D}" {o}/><rect x="27" y="4" width="10" height="6" rx="1" fill="{MAD[1]}" {o}/>
 <rect x="22" y="36" width="20" height="14" fill="{PAPEL[0]}" {o}/><path d="M25 40 L39 40 M25 44 L35 44" stroke="#4a3a2a" stroke-width="1.2"/><path d="M23 30 L23 56" stroke="#eef4f8" stroke-width="1.6" opacity=".6"/>
 {"".join(f'<circle cx="{x}" cy="{y}" r="1.2" fill="{L}"/>' for x,y in ((30,26),(36,32),(32,54)))}'''
def hostia(t, e):
    L,M,D = t
    return f'''<circle cx="32" cy="34" r="22" fill="{M}" {o}/><circle cx="32" cy="34" r="18" fill="none" stroke="{L}" stroke-width="1.2"/>
 <path d="M30 22 L34 22 L34 30 L42 30 L42 34 L34 34 L34 46 L30 46 L30 34 L22 34 L22 30 L30 30 Z" fill="{D}" stroke="{L}" stroke-width=".8"/>
 <path d="M14 26 Q20 16 32 14" fill="none" stroke="{L}" stroke-width="1.6"/>{gdot(42, 44, 2.6, e or "#9a1410")}<path d="M42 46 Q43 52 41 56" stroke="#7a1612" stroke-width="2" fill="none"/>'''
def bomba_benta(t, e):
    return MI._frasco(t, e, wide=True, cork="#6a6a70") + f'''<path d="M30 40 L34 40 L34 43 L37 43 L37 46 L34 46 L34 52 L30 52 L30 46 L27 46 L27 43 L30 43 Z" fill="#2a2a2a"/>
 <path d="M38 4 Q46 0 48 8 Q50 14 56 12" fill="none" stroke="#c8b890" stroke-width="2"/>{gdot(56,12,2.6,"#ff9a3a")}{"".join(f'<circle cx="{x}" cy="{y}" r="1.2" fill="#ffd070"/>' for x,y in ((59,8),(60,15),(53,7)))}'''
def figo(t, e):
    L,M,D = t
    return f'''<path d="M32 8 Q30 4 34 2 L36 6 Q50 12 52 34 Q54 54 32 58 Q10 54 12 34 Q14 14 32 8 Z" fill="{M}" {o}/>
 <path d="M20 26 Q22 16 32 12" fill="none" stroke="{L}" stroke-width="2"/>{"".join(f'<path d="M{x} {y} q2 4 0 8" fill="none" stroke="{D}" stroke-width="1.6"/>' for x,y in ((24,30),(34,24),(40,36),(28,44)))}
 <path d="M34 2 Q40 0 44 4 Q40 8 36 6" fill="#5a6a2a" {o}/>'''
def papel(t, e):
    return f'''<path d="M14 6 L44 6 L52 14 L52 58 L14 58 Z" fill="{PAPEL[0]}" {o}/><path d="M44 6 L44 14 L52 14" fill="{PAPEL[1]}" {o}/>
 {"".join(f'<path d="M19 {y} L33 {y} M38 {y} L47 {y}" stroke="#4a3a2a" stroke-width="1.2"/>' for y in range(20,52,5))}<path d="M36 18 L36 54" stroke="#9a1e16" stroke-width=".8"/>
 <path d="M18 54 Q30 48 40 56" fill="none" stroke="#7a3a22" stroke-width="2" opacity=".5"/>'''
def pergaminho(t, e):
    L,M,D = t
    return diag(f'''<rect x="22" y="10" width="20" height="44" fill="{PAPEL[0]}" {o}/>{"".join(f'<path d="M26 {y} L38 {y}" stroke="#4a3a2a" stroke-width="1"/>' for y in range(18,48,5))}
 <rect x="18" y="4" width="28" height="8" rx="4" fill="{MAD[1]}" {o}/><rect x="18" y="52" width="28" height="8" rx="4" fill="{MAD[1]}" {o}/>
 <circle cx="32" cy="50" r="5" fill="{M}" {o}/>{gdot(32,50,1.8,e) if e else ''}''')
def tabua(t, e):
    L,M,D = t
    return f'''<path d="M8 12 L56 8 L58 54 L6 58 Z" fill="{M}" {o}/><path d="M10 14 L54 10" stroke="{L}" stroke-width="1.6"/>
 {"".join(f'<path d="M{14} {y} L{50-(y%7)} {y-2}" stroke="{D}" stroke-width="1.8"/>' for y in range(22,52,6))}<path d="M40 30 L44 40 L38 48" fill="none" stroke="{K}" stroke-width="1.4"/>
 {"".join(f'<path d="M{x} 50 l2 -3 l2 3" fill="none" stroke="#9a1e16" stroke-width="1"/>' for x in (16,22,28,34))}'''
def bracadeira(t, e):
    L,M,D = t
    return f'''<path d="M8 22 Q32 12 56 22 L56 44 Q32 34 8 44 Z" fill="{M}" {o}/><path d="M8 22 Q32 12 56 22" fill="none" stroke="{L}" stroke-width="2"/><path d="M8 44 Q32 34 56 44" fill="none" stroke="{D}" stroke-width="2"/>
 {"".join(f'<circle cx="{32+9*math.cos(i*math.pi/4):.1f}" cy="{30+9*math.sin(i*math.pi/4):.1f}" r="2.2" fill="{LAT[1]}" stroke="{K}" stroke-width=".7"/>' for i in range(8))}<circle cx="32" cy="30" r="7.5" fill="{LAT[1]}" {o}/>
 <rect x="30" y="29" width="4" height="7" fill="#ece0bc"/><path d="M32 29 Q30 26 32 23 Q34 26 32 29 Z" fill="{e or '#ff9a3a'}" filter="url(#glow)"/>
 <path d="M10 26 l0 14 M54 26 l0 14" stroke="#c8bca0" stroke-width="1.2" stroke-dasharray="2 2"/>'''
def fita(t, e):
    L,M,D = t
    return f'''<path d="M4 26 Q20 18 34 24 Q46 30 60 22 L60 36 Q46 44 34 38 Q20 32 4 40 Z" fill="{M}" {o}/><path d="M6 28 Q20 20 34 26" fill="none" stroke="{L}" stroke-width="1.6"/>
 <path d="M34 38 L28 58 L34 54 L38 60 L40 40" fill="{D}" {o}/>
 <path d="M18 34 L30 28 Q34 24 38 28 L36 30 L28 33 Z" fill="{e or '#c99a3e'}" stroke="{K}" stroke-width=".8"/><path d="M38 28 l3 -3 M39 30 l4 0" stroke="{e or '#c99a3e'}" stroke-width="1.2" filter="url(#glow)"/>'''
def machado_bonde(t, e):
    L,M,D = t
    return f'''<g transform="{rot(-30)}"><rect x="29.5" y="24" width="5" height="38" fill="{FER[1]}" {o}/><path d="M30.8 25 L30.8 61" stroke="{FER[0]}" stroke-width="1"/><rect x="28" y="56" width="8" height="6" fill="{FER[2]}" {o}/>
 <path d="M8 6 L56 6 L56 30 L8 30 Z" fill="{M}" {o}/><path d="M11 9 L53 9 L53 27 L11 27 Z" fill="none" stroke="#e8e0d0" stroke-width="1.2"/>
 <text x="32" y="22" font-family="Arial Black,Arial" font-weight="900" font-size="12" fill="#e8e0d0" text-anchor="middle">7</text>
 <path d="M8 30 Q4 22 8 6" fill="{ACO[1]}" {o}/><path d="M6 10 Q4 18 6 26" stroke="{ACO[0]}" stroke-width="1.2"/><path d="M44 12 l6 6" stroke="{D}" stroke-width="2"/><circle cx="20" cy="18" r="1.6" fill="{FER[0]}" stroke="{K}" stroke-width=".6"/></g>'''
def cajado_lampiao(t, e):
    L,M,D = t
    ec = e or "#ffe0a0"
    return diag(f'''<rect x="30" y="20" width="4" height="42" fill="{M}" {o}/>{"".join(f'<rect x="28.6" y="{y}" width="6.8" height="2.6" fill="{D}" {o}/>' for y in (30,44,56))}
 <path d="M34 34 Q42 40 36 50" fill="none" stroke="{K}" stroke-width="2.4"/><path d="M34 34 Q42 40 36 50" fill="none" stroke="#b0603a" stroke-width="1"/>
 <path d="M24 20 L40 20 L36 8 L28 8 Z" fill="#2a2226" {o}/><path d="M28 18 L36 18 L34 10 L30 10 Z" fill="{ec}" filter="url(#glow)"/><path d="M26 8 L38 8 L32 2 Z" fill="{L}" {o}/>
 <rect x="23" y="19" width="18" height="3" fill="{L}" {o}/>''')
def foice_penhor(t, e):
    return MI.foice(t, e) + f'''<g transform="{rot(-20)}"><path d="M40 24 L50 30 L46 38 L38 32 Z" fill="#d8ccb0" {o}/><circle cx="41" cy="27" r="1" fill="{K}"/><path d="M42 31 L46 33" stroke="#9a1e16" stroke-width="1.2"/>
 <path d="M38 22 L41 26" stroke="{K}" stroke-width="1"/></g>'''
def adaga_curva(t, e):
    L,M,D = t
    return diag(f'''<path d="M29 40 Q26 26 30 16 Q34 6 42 4 Q36 14 36 24 Q36 32 35 40 Z" fill="{ACO[1]}" {o}/><path d="M31 38 Q29 26 33 16 Q36 10 40 6" fill="none" stroke="{ACO[0]}" stroke-width="1.4"/>
 <path d="M24 40 L40 40 L39 44 L25 44 Z" fill="{M}" {o}/><rect x="29.5" y="44" width="5" height="12" fill="{D}" {o}/><path d="M29.8 47 l4.6 1.4 M29.8 51 l4.6 1.4" stroke="{K}" stroke-width="1"/>
 <circle cx="32" cy="58" r="3" fill="{M}" {o}/><path d="M33 20 Q34 30 33 36" stroke="#9a1410" stroke-width="2" fill="none"/>''')
def amuleto_sino(t, e):
    L,M,D = t
    return f'''<path d="M16 2 Q32 12 48 2" fill="none" stroke="{K}" stroke-width="2.6"/><path d="M16 2 Q32 12 48 2" fill="none" stroke="{COU[0]}" stroke-width="1.2"/>
 <rect x="29" y="8" width="6" height="6" rx="2" fill="{FER[1]}" {o}/><path d="M18 52 Q20 18 32 14 Q44 18 46 52 Z" fill="{M}" {o}/><path d="M14 52 L50 52 L50 56 L14 56 Z" fill="{D}" {o}/>
 <path d="M22 48 Q22 24 30 18" fill="none" stroke="{L}" stroke-width="2"/><circle cx="32" cy="58" r="4" fill="{D}" {o}/><path d="M32 22 L30 32 L34 38 L31 46" fill="none" stroke="{K}" stroke-width="1.4"/>
 {"".join(f'<path d="M{x} {y} q-4 3 -6 0" fill="none" stroke="{L}" stroke-width="1.2" opacity=".6"/>' for x,y in ((12,40),(58,40)))}'''
def lenco(t, e):
    L,M,D = t
    def flor(x, y): return f'<g transform="translate({x} {y})">' + "".join(f'<circle cx="{2.6*math.cos(i*math.pi*2/5):.1f}" cy="{2.6*math.sin(i*math.pi*2/5):.1f}" r="1.8" fill="#ece2cc"/>' for i in range(5)) + '<circle r="1.3" fill="#e0b040"/></g>'
    flores = "".join(flor(x, y) for x,y in ((20,20),(40,18),(30,32),(16,36),(44,34),(32,46)))
    return f'''<path d="M6 10 L58 10 L32 58 Z" fill="{M}" {o}/><path d="M8 12 L56 12" stroke="{L}" stroke-width="1.6"/><path d="M32 58 L28 62 M32 58 L37 62" stroke="{K}" stroke-width="1.6"/>
 {flores}<path d="M6 10 Q20 18 32 10 Q44 18 58 10" fill="none" stroke="{D}" stroke-width="1.6"/>'''
def anel_selo(t, e):
    L,M,D = t
    ec = e or "#c99a3e"
    return f'''<ellipse cx="32" cy="40" rx="17" ry="15" fill="none" stroke="{K}" stroke-width="9"/><ellipse cx="32" cy="40" rx="17" ry="15" fill="none" stroke="{M}" stroke-width="5.6"/>
 <path d="M17 34 Q22 24 32 24" fill="none" stroke="{L}" stroke-width="1.6"/><ellipse cx="32" cy="18" rx="15" ry="12" fill="{D}" {o}/><ellipse cx="32" cy="17" rx="11.5" ry="8.5" fill="{M}" stroke="{K}" stroke-width="1"/>
 <path d="M24 22 L36 13 Q40 10 41 15 Q38 16 37 19 L27 24 Z" fill="{ec}" stroke="{K}" stroke-width=".8"/><path d="M36 12 l4 -3" stroke="{ec}" stroke-width="1.2" filter="url(#glow)"/>'''
def avental(t, e):
    L,M,D = t
    return f'''<path d="M22 4 L42 4 L44 14 L56 20 L52 60 L12 60 L8 20 L20 14 Z" fill="{M}" {o}/><path d="M22 4 L42 4" stroke="{K}" stroke-width="3"/>
 <path d="M8 20 L2 28 M56 20 L62 28" stroke="{K}" stroke-width="3"/><path d="M8 20 L2 28 M56 20 L62 28" stroke="{COU[0]}" stroke-width="1.4"/>
 <path d="M14 24 L12 56" stroke="{L}" stroke-width="2"/><path d="M20 30 Q28 34 26 44 Q34 40 40 48 Q44 38 50 40" fill="none" stroke="#5a0806" stroke-width="4" opacity=".8"/>
 {"".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#4a0604"/>' for x,y,r in ((34,24,3),(44,30,2),(24,50,2.6),(46,54,1.6)))}<path d="M10 40 L54 40" stroke="{D}" stroke-width="1.2" stroke-dasharray="3 2"/>'''
def veu(t, e):
    L,M,D = t
    holes = "".join(f'<circle cx="{x}" cy="{y}" r="1.5" fill="none" stroke="{L}" stroke-width=".6"/>' for x in range(16,50,6) for y in range(20,54,6) if (x-32)**2/400 + (y-34)**2/500 < 1)
    return f'''<path d="M32 4 Q12 10 10 30 Q8 50 4 62 L60 62 Q56 50 54 30 Q52 10 32 4 Z" fill="{M}" fill-opacity=".92" {o}/>{holes}
 <path d="M14 14 Q32 6 50 14" fill="none" stroke="{L}" stroke-width="1.6"/>{"".join(f'<path d="M{x} 6 l0 6" stroke="{FER[0]}" stroke-width="2"/>' for x in (22,32,42))}
 {gdot(26,34,1.6,e or '#bfe6ff')}{gdot(38,34,1.6,e or '#bfe6ff')}<path d="M24 38 Q25 46 23 52 M39 38 Q40 44 38 50" fill="none" stroke="#e8e0cc" stroke-width="1.6"/>
 <path d="M4 62 L10 56 L16 62 L22 56 L28 62 L34 56 L40 62 L46 56 L52 62 L58 56 L60 62" fill="{D}" {o}/>'''
def estilhaco(t, e):
    L,M,D = t
    return f'''<path d="M18 6 L44 10 L56 30 L42 58 L22 52 L8 28 Z" fill="{M}" {o}/><path d="M18 6 L44 10 L36 28 L8 28 Z" fill="{L}" {o}/><path d="M36 28 L42 58 M36 28 L56 30" stroke="{D}" stroke-width="1.4"/>
 {glow("M12 30 L22 50 L40 56", e, 2)}{glow("M20 8 L40 12", e, 1.2)}<path d="M24 36 Q30 40 28 46" fill="none" stroke="{D}" stroke-width="1.6"/>
 <path d="M30 2 Q32 -2 36 2" fill="none" stroke="{K}" stroke-width="2"/><circle cx="32" cy="6" r="2.4" fill="none" stroke="{FER[0]}" stroke-width="1.4"/>'''
def diapasao(t, e):
    L,M,D = t
    return diag(f'''<path d="M22 4 L22 30 Q22 40 32 40 Q42 40 42 30 L42 4 L36 4 L36 30 Q36 34 32 34 Q28 34 28 30 L28 4 Z" fill="{M}" {o}/>
 <path d="M24 6 L24 30" stroke="{L}" stroke-width="1.6"/><rect x="29.5" y="40" width="5" height="18" fill="{M}" {o}/><circle cx="32" cy="59" r="3" fill="{D}" {o}/>
 {"".join(f'<path d="M{x} {y} q-4 4 0 8" fill="none" stroke="{e or "#9fd8ff"}" stroke-width="1.4" filter="url(#glow)"/>' for x,y in ((16,8),(12,6),(48,8)))}''')
def etiqueta(t, e):
    L,M,D = t
    return f'''<path d="M4 6 Q16 14 24 22" fill="none" stroke="{K}" stroke-width="2.4"/><path d="M4 6 Q16 14 24 22" fill="none" stroke="#9a1e16" stroke-width="1.2"/>
 <path d="M22 20 L36 12 L60 44 L40 58 Z" fill="{PAPEL[0]}" {o}/><circle cx="30" cy="20" r="3" fill="{K}"/><circle cx="30" cy="20" r="3" fill="none" stroke="{LAT[1]}" stroke-width="1.2"/>
 <path d="M34 38 L50 34" stroke="#2a2222" stroke-width="2.4"/>{glow("M34 38 L50 34", e, 1)}<path d="M44 52 L56 44" stroke="{PAPEL[2]}" stroke-width="1"/>
 <path d="M26 24 L36 18" stroke="{PAPEL[1]}" stroke-width="1"/>'''
def gancho(t, e):
    L,M,D = t
    return diag(f'''<path d="M32 30 L32 46 Q32 58 22 58 Q12 58 12 48 Q12 42 16 40" fill="none" stroke="{K}" stroke-width="7" stroke-linecap="round"/>
 <path d="M32 30 L32 46 Q32 58 22 58 Q12 58 12 48 Q12 42 16 40" fill="none" stroke="{M}" stroke-width="4.2" stroke-linecap="round"/><path d="M14 42 L18 36 L19 43 Z" fill="{L}" {o}/>
 <path d="M30 34 L30 48" stroke="{L}" stroke-width="1.2"/><path d="M24 4 L40 4 L42 30 L22 30 Z" fill="{COU[1]}" {o}/><path d="M24 10 L40 10 M23 18 L41 18" stroke="{COU[2]}" stroke-width="1.6"/>
 <path d="M26 6 L26 28" stroke="{COU[0]}" stroke-width="1.2"/>''')
def serra_caldeira(t, e):
    L,M,D = t
    teeth = "".join(f'<path d="M{37+(i%2)*2} {6+i*3.4} l4 1.7 l-4 1.7" fill="{L}" stroke="{K}" stroke-width=".6"/>' for i in range(10))
    return f'''<g transform="{rot(-25)}"><path d="M22 4 L38 4 L38 42 L22 42 Z" fill="{M}" {o}/>{teeth}<path d="M25 6 L25 40" stroke="{L}" stroke-width="1.6"/>
 <path d="M24 12 l8 6 M26 26 l6 4" stroke="#5a0806" stroke-width="2.4"/>
 <ellipse cx="24" cy="50" rx="13" ry="10" fill="{TINTS['cobre'][1]}" {o}/><path d="M14 46 Q20 40 30 42" fill="none" stroke="{TINTS['cobre'][0]}" stroke-width="2"/>
 {"".join(f'<circle cx="{x}" cy="{y}" r="1.3" fill="{LAT[0]}" stroke="{K}" stroke-width=".6"/>' for x,y in ((14,50),(34,50),(24,58)))}<circle cx="24" cy="50" r="4" fill="#141012" {o}/>{gdot(24,50,2.2,e or "#ff7a1a")}
 <path d="M10 44 Q4 36 8 28 M8 36 Q2 30 6 22" fill="none" stroke="#c8c0b0" stroke-width="1.8" opacity=".6"/><rect x="36" y="44" width="10" height="16" fill="{FER[2]}" {o}/></g>'''
def cajado_femur(t, e):
    L,M,D = t
    return diag(f'''<path d="M29 14 L35 14 L36 52 L28 52 Z" fill="{M}" {o}/><path d="M31 16 L30 50" stroke="{L}" stroke-width="1.6"/>
 <circle cx="27" cy="12" r="6" fill="{M}" {o}/><circle cx="37" cy="12" r="6" fill="{M}" {o}/><path d="M28 14 L36 14" stroke="{M}" stroke-width="3"/>
 <circle cx="27" cy="55" r="5" fill="{M}" {o}/><circle cx="37" cy="55" r="5" fill="{M}" {o}/><path d="M28 52 L36 52" stroke="{M}" stroke-width="3"/>
 <path d="M26 2 Q32 -2 38 2 Q42 6 38 10 L26 10 Q22 6 26 2 Z" fill="{L}" {o}/><circle cx="29.5" cy="5" r="1.6" fill="{K}"/><circle cx="34.5" cy="5" r="1.6" fill="{K}"/>
 {gdot(29.5,5,1,e or '#bfe6ff')}{gdot(34.5,5,1,e or '#bfe6ff')}<path d="M27 24 L37 26 M27 40 L37 42" stroke="{FER[1]}" stroke-width="2"/>''')
def halo(t, e):
    L,M,D = t
    ec = e or "#ff7a1a"
    spikes = "".join(f'<path d="M{32+20*math.cos(a):.1f} {32+12*math.sin(a):.1f} L{32+29*math.cos(a):.1f} {32+19*math.sin(a):.1f}" stroke="{K}" stroke-width="3.6"/><path d="M{32+20*math.cos(a):.1f} {32+12*math.sin(a):.1f} L{32+28*math.cos(a):.1f} {32+18*math.sin(a):.1f}" stroke="{M}" stroke-width="1.8"/>' for a in [i*math.pi*2/12 for i in range(12)])
    return f'''{spikes}<ellipse cx="32" cy="32" rx="21" ry="13" fill="none" stroke="{ec}" stroke-width="7" filter="url(#glow)" opacity=".75"/>
 <ellipse cx="32" cy="32" rx="20" ry="12" fill="none" stroke="{K}" stroke-width="6"/><ellipse cx="32" cy="32" rx="20" ry="12" fill="none" stroke="{M}" stroke-width="3.6"/>
 <path d="M14 30 Q20 21 32 20" fill="none" stroke="{ec}" stroke-width="1.6" filter="url(#glow)"/><path d="M44 42 L48 36" stroke="{K}" stroke-width="2"/>'''

MOTIVOS = {k: v for k, v in globals().items() if callable(v) and not k.startswith("_") and k not in ("glow", "diag", "rot", "gdot")}
for k in list(MOTIVOS):
    if k in ("math",): MOTIVOS.pop(k)

def casaca(t, e):
    L,M,D = t
    ec = e or "#ff7a1a"
    return f'''<path d="M20 8 L28 6 L32 14 L36 6 L44 8 L54 16 L52 40 L48 38 L48 60 L36 56 L32 60 L28 56 L16 60 L16 38 L12 40 L10 16 Z" fill="{M}" {o}/>
 <path d="M28 6 L32 14 L36 6 L34 58 L30 58 Z" fill="{D}" {o}/>{"".join(f'<circle cx="{x}" cy="{y}" r="1.5" fill="{LAT[0]}" stroke="{K}" stroke-width=".6"/>' for x in (27,37) for y in (22,30,38,46))}
 <path d="M16 20 L14 36 M20 26 L19 54" stroke="{L}" stroke-width="1.4"/><path d="M16 48 L28 52 M36 52 L48 48" stroke="{K}" stroke-width="1.6"/>
 {"".join(f'<path d="M{x-9} 14 Q{x} 6 {x+9} 14 L{x+8} 18 L{x-8} 18 Z" fill="{LAT[1]}" {o}/>' for x in (16,48))}
 {"".join(f'<path d="M{x-8+i*2.6} 18 L{x-8+i*2.6} 24" stroke="{ec}" stroke-width="1.2" filter="url(#glow)"/>' for x in (16,48) for i in range(7))}
 <path d="M40 54 L44 58 L46 54" fill="none" stroke="{K}" stroke-width="1.2"/>'''
def estandarte(t, e):
    L,M,D = t
    return f'''<g transform="{rot(-30)}"><rect x="30" y="8" width="4.4" height="54" fill="{FER[1]}" {o}/><path d="M31.2 10 L31.2 60" stroke="{FER[0]}" stroke-width="1"/>
 <path d="M28 10 L32 0 L36.4 10 Z" fill="{ACO[0]}" {o}/><rect x="27" y="10" width="10.4" height="3.4" fill="{LAT[1]}" {o}/>
 <path d="M34 14 L58 16 L54 26 L58 34 L52 40 L56 48 L34 46 Z" fill="{M}" {o}/><path d="M36 17 L54 19" stroke="{L}" stroke-width="1.4"/>
 <path d="M42 24 L48 24 L50 30 L45 36 L40 30 Z" fill="{LAT[1]}" stroke="{K}" stroke-width=".8"/><circle cx="45" cy="29" r="1.6" fill="{K}"/>
 <path d="M40 40 l6 -2 M50 22 l3 3" stroke="{D}" stroke-width="2"/>{glow("M36 46 L52 47", e, 1.4)}<rect x="28.5" y="56" width="7.4" height="5" fill="{COU[1]}" {o}/></g>'''
MOTIVOS.update(casaca=casaca, estandarte=estandarte)

def espada_larga(t, e):
    L,M,D = t
    return diag(f'''<path d="M25 44 L25 9 L32 1 L39 9 L39 44 Z" fill="{M}" {o}/><path d="M30.5 8 L30.5 41 L33.5 41 L33.5 8 Z" fill="{D}"/>
 <path d="M27 10 L27 43" stroke="{L}" stroke-width="1.6"/><path d="M37.4 10 L37.4 43" stroke="{D}" stroke-width="1.2"/><path d="M28 18 l2 3 M36 30 l-2 3" stroke="{K}" stroke-width="1"/>
 {glow("M32 6 L32 40", e)}<path d="M15 43 L49 43 L46 49 L18 49 Z" fill="{ACO[1]}" {o}/><path d="M17 44.5 L47 44.5" stroke="{ACO[0]}" stroke-width="1"/>
 <circle cx="15" cy="46" r="2.6" fill="{ACO[2]}" {o}/><circle cx="49" cy="46" r="2.6" fill="{ACO[2]}" {o}/>
 <rect x="28.8" y="49" width="6.4" height="10" fill="{COU[1]}" {o}/><path d="M29 51.5 l6 1.6 M29 54.5 l6 1.6" stroke="{COU[2]}" stroke-width="1.2"/>
 <path d="M27 59 L37 59 L35.5 63.5 L28.5 63.5 Z" fill="{ACO[1]}" {o}/>''')
MOTIVOS.update(espada_larga=espada_larga)

def cantil(t, e):
    L,M,D = t
    return f'''<path d="M22 14 Q10 18 10 36 Q10 56 32 58 Q54 56 54 36 Q54 18 42 14 Z" fill="{FER[1]}" {o}/><path d="M14 30 Q14 20 24 18" fill="none" stroke="{FER[0]}" stroke-width="2"/>
 <path d="M12 32 L52 32 L52 46 L12 46 Z" fill="{COU[1]}" {o}/><path d="M12 35 L52 35 M12 43 L52 43" stroke="{COU[2]}" stroke-width="1"/>
 <path d="M26 36 Q32 30 38 36 Q38 42 32 44 Q26 42 26 36 Z" fill="{M}" stroke="{K}" stroke-width=".8"/><path d="M30 37 Q31 35 33 35" fill="none" stroke="{L}" stroke-width="1.2"/>
 <rect x="27" y="4" width="10" height="11" rx="1.5" fill="{MAD[1]}" {o}/><path d="M37 8 Q48 2 54 14" fill="none" stroke="{K}" stroke-width="2.6"/><path d="M37 8 Q48 2 54 14" fill="none" stroke="{COU[0]}" stroke-width="1.2"/>
 <path d="M44 48 l4 4" stroke="{FER[2]}" stroke-width="2"/>'''
MOTIVOS.update(cantil=cantil)
