# Desenhos (SVG 64x64) dos ícones de itens do DARK PASSAGE, estilo "Ferrugem Sagrada".
# Cada motivo recebe t = (claro, médio, escuro) do material principal e e = cor emissiva (ou None).
K = "#0a0808"
o = f'stroke="{K}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"'
TINTS = {
 "aco":("#c8ccd0","#8a9098","#4a5058"), "osso":("#e6dcc6","#bfb398","#776b57"), "madeira":("#9a6a40","#6a4428","#3a2414"),
 "ouro":("#f0d080","#c99a3e","#6a4a18"), "vinho":("#9a3040","#6a1a26","#3a0c14"), "sangue":("#c0302a","#7a1612","#3a0806"),
 "ferrugem":("#b06a3a","#6a3a22","#3a1e10"), "placa":("#c83a30","#8a1a14","#4a0a08"), "praga":("#9aaa72","#6a7058","#363c2c"),
 "ferro_negro":("#5a5458","#2e2a2c","#141012"), "brasa":("#ffc070","#ff7a1a","#7a2a08"), "latao":("#e6b866","#b07a3a","#5a3a18"),
 "prata":("#eef4f8","#a8b4bc","#5a646c"), "cobre":("#e09a68","#b0603a","#5a2e18"), "couro":("#8a6040","#5a3a24","#2e1c10"),
 "bronze":("#c89a58","#8a6030","#4a3018"), "ferro":("#9a9aa0","#5e5e64","#2e2e32"), "pano":("#d8ccb0","#a89a7c","#6a5e48"),
 "vermelho":("#d84a3a","#9a1e16","#4a0a08"), "azul":("#7ab8e8","#3c6a90","#1c2a38"), "agua":("#d8f0f8","#8ab8c8","#3a6a7a"),
 "verde":("#c0e870","#6a9a2a","#2a4410"), "lata":("#c8ccc8","#8a8e8a","#4a4e4a"), "cera":("#ece0bc","#c0ac80","#6a5a38"),
 "chumbo":("#9a9aa0","#5e5e64","#2e2e34"), "alma":("#e8f8ff","#9fd8ff","#3a6a8a"), "cinza":("#a8a29c","#6a6460","#3a3634"),
}
LAT = TINTS["latao"]; COU = TINTS["couro"]; MAD = TINTS["madeira"]; OSS = TINTS["osso"]; ACO = TINTS["aco"]; FER = TINTS["ferro"]

def glow(path, e, w=2.2):
    return f'<path d="{path}" fill="none" stroke="{e}" stroke-width="{w}" stroke-linecap="round" filter="url(#glow)"/>' if e else ""
ROT = True  # False = desenho "em pé" para a arte da mochila em grade
def rot(a): return f"rotate({a if ROT else 0} 32 32)"
def diag(inner): return f'<g transform="{rot(45)}">{inner}</g>'

def espada(t, e):
    L,M,D = t
    return diag(f'''<path d="M27.5 45 L27.5 11 L32 3 L36.5 11 L36.5 45 Z" fill="{M}" {o}/>
 <path d="M32 6 L32 44" stroke="{L}" stroke-width="1.8"/><path d="M34.8 12 L34.8 44" stroke="{D}" stroke-width="1.4"/>
 <path d="M29 20 l2 3 M34 30 l-2 2" stroke="{D}" stroke-width="1"/>
 {glow("M32 8 L32 42", e)}
 <path d="M19 44 L45 44 L43 49 L21 49 Z" fill="{LAT[1]}" {o}/><path d="M21 45.5 L43 45.5" stroke="{LAT[0]}" stroke-width="1"/>
 <rect x="29.3" y="49" width="5.4" height="9.5" fill="{COU[1]}" {o}/><path d="M29.5 52 l5 1.5 M29.5 55 l5 1.5" stroke="{COU[2]}" stroke-width="1"/>
 <circle cx="32" cy="60.2" r="3" fill="{LAT[1]}" {o}/>''')

def espada_serra(t, e):
    L,M,D = t
    teeth = "".join(f"L{38.5 if i%2==0 else 36.5} {44-i*3}" for i in range(11))
    return diag(f'''<path d="M27.5 45 L27.5 10 L32 3 L36.5 8 {teeth} Z" fill="{M}" {o}/>
 <path d="M30.5 8 L30.5 44" stroke="{L}" stroke-width="1.6"/>{glow("M30.5 10 L30.5 42", e)}
 <path d="M21 44 L43 44 L45 40 L47 45 L43 49 L21 49 L17 45 L19 40 Z" fill="{FER[2]}" {o}/>
 <rect x="29.3" y="49" width="5.4" height="9.5" fill="{COU[2]}" {o}/><circle cx="32" cy="60.2" r="3" fill="{FER[1]}" {o}/>''')

def adaga(t, e):
    L,M,D = t
    return diag(f'''<path d="M28.5 40 Q27 24 32 12 Q37 24 35.5 40 Z" fill="{M}" {o}/><path d="M32 15 Q30.5 26 31 39" stroke="{L}" stroke-width="1.6" fill="none"/>
 {glow("M32 16 L32 38", e)}
 <path d="M23 40 Q32 44 41 40 L40 43.5 Q32 47 24 43.5 Z" fill="{OSS[1]}" {o}/>
 <rect x="29.5" y="44.5" width="5" height="11" fill="#5a2622" {o}/><path d="M29.8 47.5 l4.6 1.2 M29.8 51 l4.6 1.2" stroke="#2a0e0c" stroke-width="1"/>
 <path d="M28 56 L36 56 L34.5 61 L29.5 61 Z" fill="{OSS[0]}" {o}/><circle cx="31" cy="58" r=".9" fill="{K}"/><circle cx="33" cy="58" r=".9" fill="{K}"/>''')

def lanca(t, e):
    L,M,D = t
    return diag(f'''<rect x="30" y="16" width="4" height="46" fill="{MAD[1]}" {o}/><path d="M31.2 17 L31.2 61" stroke="{MAD[0]}" stroke-width="1"/>
 <path d="M32 1 L37 14 L32 19 L27 14 Z" fill="{ACO[1]}" {o}/><path d="M32 3 L32 17" stroke="{ACO[0]}" stroke-width="1.4"/>
 <rect x="28.5" y="18" width="7" height="4" fill="{LAT[1]}" {o}/>
 <path d="M34 23 Q46 26 44 38 Q40 30 34 32 Z" fill="{L}" {o}/><path d="M36 27 Q42 29 42 34" stroke="{D}" stroke-width="1" fill="none"/>
 <path d="M34 25 L38 25 M34 29 L37 29" stroke="#7a1612" stroke-width="1.4"/>{glow("M32 4 L32 16", e)}''')

def escudo(t, e):
    L,M,D = t
    planks = "".join(f'<path d="M{x} 9 L{x} 56" stroke="{D}" stroke-width="1.2"/>' for x in (22,29,36,43))
    return f'''<path d="M12 8 L52 8 L52 34 Q52 50 32 59 Q12 50 12 34 Z" fill="{M}" {o}/>{planks}
 <path d="M14 10 L50 10" stroke="{L}" stroke-width="1.4"/>
 <path d="M12 8 L52 8 L52 34 Q52 50 32 59 Q12 50 12 34 Z" fill="none" stroke="{FER[1]}" stroke-width="2.6"/>
 <path d="M12 8 L52 8 L52 34 Q52 50 32 59 Q12 50 12 34 Z" fill="none" {o}/>
 <path d="M29 15 L35 15 L35 24 L44 24 L44 30 L35 30 L35 48 L29 48 L29 30 L20 30 L20 24 L29 24 Z" fill="{OSS[1]}" {o}/>
 <path d="M30 16 L30 47 M21 25 L43 25" stroke="{OSS[0]}" stroke-width="1"/>
 {"".join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="{FER[0]}" stroke="{K}" stroke-width=".8"/>' for x,y in ((16,12),(48,12),(16,34),(48,34),(32,54)))}'''

def cajado_osso(t, e):
    L,M,D = t
    verts = "".join(f'<ellipse cx="32" cy="{y}" rx="4.2" ry="2.4" fill="{L if i%2 else M}" {o}/>' for i,y in enumerate(range(60,20,-5)))
    return diag(f'''{verts}
 <path d="M24 12 Q24 2 32 2 Q40 2 40 12 Q40 18 36 19 L36 22 L28 22 L28 19 Q24 18 24 12 Z" fill="{L}" {o}/>
 <ellipse cx="29" cy="12" rx="2.4" ry="3" fill="{K}"/><ellipse cx="35" cy="12" rx="2.4" ry="3" fill="{K}"/>
 <path d="M30 19 L30 22 M32 19 L32 22 M34 19 L34 22" stroke="{K}" stroke-width="1"/>
 {f'<circle cx="29" cy="12" r="1.3" fill="{e}" filter="url(#glow)"/><circle cx="35" cy="12" r="1.3" fill="{e}" filter="url(#glow)"/>' if e else f'<circle cx="29" cy="12.5" r="1" fill="#ff3a2a"/><circle cx="35" cy="12.5" r="1" fill="#ff3a2a"/>'}''')

def grimorio(t, e):
    L,M,D = t
    return f'''<path d="M14 14 L44 10 L50 14 L50 54 L20 58 L14 54 Z" fill="{D}" {o}/>
 <path d="M14 14 L44 10 L44 50 L14 54 Z" fill="{M}" {o}/><path d="M44 10 L50 14 L50 54 L44 50 Z" fill="{OSS[1]}" {o}/>
 <path d="M45.5 14 L45.5 50 M47.5 15 L47.5 52" stroke="{OSS[2]}" stroke-width=".8"/>
 <path d="M16 16 L42 12.5" stroke="{L}" stroke-width="1.2"/>
 <circle cx="29" cy="32" r="8" fill="none" stroke="{OSS[1]}" stroke-width="1.6"/><path d="M29 23 L29 41 M21 34 L37 30" stroke="{OSS[1]}" stroke-width="1.4"/>
 {f'<circle cx="29" cy="32" r="2.6" fill="{e}" filter="url(#glow)"/>' if e else f'<circle cx="29" cy="32" r="2" fill="{OSS[0]}"/>'}
 <path d="M8 40 Q30 30 56 26" fill="none" stroke="{FER[2]}" stroke-width="4.4"/><path d="M8 40 Q30 30 56 26" fill="none" stroke="{FER[0]}" stroke-width="2.4" stroke-dasharray="3.5 2"/>
 <rect x="26" y="31" width="7" height="8" rx="1" fill="{FER[1]}" {o}/><circle cx="29.5" cy="35" r="1" fill="{K}"/>'''

def punhos(t, e):
    L,M,D = t
    return f'''<g transform="{rot(-12)}"><path d="M14 22 Q14 14 22 14 L44 14 Q52 14 52 22 L52 40 Q52 50 42 50 L22 50 Q14 50 14 40 Z" fill="{M}" {o}/>
 {"".join(f'<rect x="{x}" y="10" width="8.5" height="14" rx="3" fill="{FER[1]}" {o}/><path d="M{x+1.5} 12 L{x+1.5} 22" stroke="{FER[0]}" stroke-width="1.2"/>' for x in (14.5,23.5,32.5,41.5))}
 <path d="M14 30 L52 30 M14 38 L52 38" stroke="{K}" stroke-width="2.4"/><path d="M14 30 L52 30 M14 38 L52 38" stroke="#4a4a50" stroke-width="1.2" stroke-dasharray="2 2"/>
 {"".join(f'<path d="M{x} 28 l2 -4 l2 4 M{x+1} 40 l2 4 l2 -4" fill="none" stroke="{ACO[0]}" stroke-width="1.2"/>' for x in (18,28,38,46))}
 <path d="M16 44 L50 44" stroke="{D}" stroke-width="2"/><rect x="22" y="50" width="20" height="8" fill="{COU[1]}" {o}/></g>'''

def machado_placa(t, e):
    L,M,D = t
    pts = " ".join(f"{32+16*__import__('math').cos(__import__('math').radians(22.5+45*i)):.1f},{20+16*__import__('math').sin(__import__('math').radians(22.5+45*i)):.1f}" for i in range(8))
    return f'''<g transform="{rot(-30)}"><rect x="29.5" y="24" width="5" height="38" fill="{FER[1]}" {o}/><path d="M30.8 25 L30.8 61" stroke="{FER[0]}" stroke-width="1"/>
 <polygon points="{pts}" fill="{M}" {o}/><polygon points="{pts}" fill="none" stroke="#e8e0d0" stroke-width="1.4" transform="translate(32 20) scale(.85) translate(-32 -20)"/>
 <text x="32" y="23" font-family="Arial Black,Arial" font-weight="900" font-size="8.5" fill="#e8e0d0" text-anchor="middle">PARE</text>
 <path d="M22 10 L28 16 M42 28 l-4 -3" stroke="{D}" stroke-width="2"/>
 <rect x="28" y="34" width="8" height="4" fill="{FER[2]}" {o}/><path d="M28 50 L36 50 M28 54 L36 54" stroke="#3a2a1a" stroke-width="2"/></g>'''

def cutelo(t, e):
    L,M,D = t
    return diag(f'''<path d="M30 40 L30 6 L44 6 Q47 22 44 40 Z" fill="{M}" {o}/><path d="M42 8 Q44.5 22 42 38" fill="none" stroke="{L}" stroke-width="2"/>
 <circle cx="35" cy="11" r="2" fill="{K}"/><path d="M33 20 l5 4 M32 30 l6 -3" stroke="#5a1a14" stroke-width="2"/>{glow("M43 9 Q45.5 22 43 38", e)}
 <rect x="29.5" y="40" width="5.5" height="20" rx="1.5" fill="{MAD[1]}" {o}/><circle cx="32.2" cy="45" r="1" fill="{LAT[0]}"/><circle cx="32.2" cy="53" r="1" fill="{LAT[0]}"/>''')

def garras(t, e):
    L,M,D = t
    fl = 'filter="url(#glow)"' if e else ""
    claws = "".join(f'<path d="M{x} 30 Q{x-2} 14 {x+6} 4 Q{x+3} 16 {x+6} 30 Z" fill="{OSS[0]}" {o}/>' for x in (16,26,36))
    return f'''{claws}<path d="M10 30 Q10 24 18 26 L48 24 Q56 26 54 36 L50 54 Q40 60 22 58 Q10 52 10 40 Z" fill="{M}" {o}/>
 <path d="M14 34 Q24 30 34 34 Q42 38 50 32" fill="none" stroke="{D}" stroke-width="2"/>
 {"".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{e or "#9cff3a"}" stroke="{K}" stroke-width="1" {fl}/>' for x,y,r in ((20,44,3),(30,50,2.2),(42,42,3.4),(46,52,1.8)))}
 <path d="M18 38 L24 40 M36 54 L40 50" stroke="{L}" stroke-width="1.4"/>'''

def foice(t, e):
    L,M,D = t
    return f'''<g transform="{rot(-20)}"><rect x="35" y="8" width="4.5" height="54" fill="{MAD[1]}" {o}/><path d="M36.2 9 L36.2 61" stroke="{MAD[0]}" stroke-width="1"/>
 <path d="M37 10 Q16 4 4 22 Q18 12 37 17 Z" fill="{M}" {o}/><path d="M33 11 Q18 9 8 19" fill="none" stroke="{L}" stroke-width="1.6"/>
 {glow("M33 12 Q18 9 7 20", e, 2.6)}
 <rect x="33.5" y="9" width="7.5" height="9" fill="{FER[2]}" {o}/><rect x="33.5" y="38" width="7.5" height="4" fill="{COU[1]}" {o}/></g>'''

def corrente(t, e):
    L,M,D = t
    links = "".join(f'<ellipse cx="{12+i*5.4}" cy="{52-i*4.2}" rx="{4 if i%2==0 else 2}" ry="{2.6 if i%2==0 else 3.6}" fill="none" stroke="{K}" stroke-width="3.6"/><ellipse cx="{12+i*5.4}" cy="{52-i*4.2}" rx="{4 if i%2==0 else 2}" ry="{2.6 if i%2==0 else 3.6}" fill="none" stroke="{M}" stroke-width="1.8"/>' for i in range(7))
    return f'''{links}<path d="M46 22 Q46 8 54 8 Q60 8 60 16 Q60 24 52 26 L56 30" fill="none" stroke="{K}" stroke-width="5.6" stroke-linecap="round"/>
 <path d="M46 22 Q46 8 54 8 Q60 8 60 16 Q60 24 52 26 L56 30" fill="none" stroke="{L}" stroke-width="3" stroke-linecap="round"/>
 {glow("M46 22 Q46 8 54 8 Q60 8 60 16 Q60 24 52 26", e, 1.6)}<path d="M54 30 L58 27 L58 33 Z" fill="{L}" {o}/>'''

def besta(t, e):
    L,M,D = t
    return f'''<g transform="{rot(-35)}"><rect x="29" y="14" width="6" height="46" rx="1.5" fill="{M}" {o}/><path d="M30.5 16 L30.5 58" stroke="{L}" stroke-width="1"/>
 <path d="M6 22 Q32 6 58 22" fill="none" stroke="{K}" stroke-width="5"/><path d="M6 22 Q32 6 58 22" fill="none" stroke="{FER[1]}" stroke-width="2.8"/>
 <path d="M7 22 L32 34 L57 22" fill="none" stroke="{OSS[0]}" stroke-width="1"/>
 <path d="M32 2 L32 34" stroke="{K}" stroke-width="2.6"/><path d="M32 3 L32 33" stroke="{ACO[0]}" stroke-width="1.2"/><path d="M29 6 L32 1 L35 6 Z" fill="{ACO[0]}" {o}/>
 <rect x="27.5" y="34" width="9" height="5" fill="{FER[2]}" {o}/><path d="M33 40 L37 46" stroke="{FER[1]}" stroke-width="2"/></g>'''

def escopeta(t, e):
    L,M,D = t
    return f'''<g transform="{rot(-35)}"><rect x="25.5" y="1" width="6.5" height="34" fill="{ACO[2]}" {o}/><rect x="32" y="1" width="6.5" height="34" fill="{ACO[1]}" {o}/>
 <path d="M34 3 L34 33" stroke="{ACO[0]}" stroke-width="1.4"/><path d="M27.5 3 L27.5 33" stroke="{ACO[1]}" stroke-width="1"/>{glow("M28.7 3 L28.7 33 M35.2 3 L35.2 33", e, 1.4)}
 <rect x="25" y="0" width="14" height="3" fill="{K}"/><rect x="24" y="14" width="16" height="10" rx="1" fill="{COU[1]}" {o}/><path d="M24 17 L40 17 M24 21 L40 21" stroke="{COU[2]}" stroke-width="1"/>
 <rect x="24" y="34" width="16" height="9" fill="{FER[1]}" {o}/><circle cx="29" cy="38.5" r="1.4" fill="{FER[0]}"/><path d="M38 42 Q44 46 39 49" fill="none" stroke="{K}" stroke-width="2"/>
 <path d="M24 43 L40 43 L45 63 L27 63 Z" fill="{M}" {o}/><path d="M28 45 L31.5 61" stroke="{L}" stroke-width="1.6"/><path d="M25 53 L42.5 53 M25.6 56.5 L43.4 56.5" stroke="{COU[2]}" stroke-width="2"/></g>'''

def mosquete(t, e):
    L,M,D = t
    return f'''<g transform="{rot(-38)}"><rect x="30" y="0" width="4" height="40" fill="{ACO[1]}" {o}/><path d="M31.2 1 L31.2 39" stroke="{ACO[0]}" stroke-width="1"/>
 {"".join(f'<rect x="29" y="{y}" width="6" height="2.6" fill="{M}" {o}/>' for y in (8,22))}
 <path d="M28 26 L36 26 L36 42 L42 62 L30 62 L28 42 Z" fill="{MAD[1]}" {o}/><path d="M30 28 L30 42 L32 60" stroke="{MAD[0]}" stroke-width="1" fill="none"/>
 <rect x="35" y="34" width="6" height="5" fill="{M}" {o}/><path d="M40 34 L44 30 L45 33" fill="none" stroke="{K}" stroke-width="1.6"/>
 {glow("M32 2 L32 38", e, 1.2)}</g>'''

def cajado_antena(t, e):
    L,M,D = t
    ec = e or "#ff9a3a"
    return diag(f'''<rect x="30" y="24" width="4" height="38" fill="{M}" {o}/>{"".join(f'<rect x="28.5" y="{y}" width="7" height="2.5" fill="{D}" {o}/>' for y in (30,42,54))}
 <path d="M32 24 L32 2" stroke="{K}" stroke-width="2.4"/><path d="M32 24 L32 2" stroke="{L}" stroke-width="1"/>
 <path d="M24 8 L40 8 M26 13 L38 13" stroke="{K}" stroke-width="2.4"/><path d="M24 8 L40 8 M26 13 L38 13" stroke="{L}" stroke-width="1"/>
 <path d="M26 24 Q26 15 32 15 Q38 15 38 24 Z" fill="#6a8a9a" fill-opacity=".55" {o}/>
 <path d="M29.5 23 Q30 18 32 17 Q34 18 34.5 23" fill="none" stroke="{ec}" stroke-width="1.6" filter="url(#glow)"/>
 <rect x="25" y="23" width="14" height="4" fill="{D}" {o}/><circle cx="32" cy="2.5" r="1.6" fill="{ec}" filter="url(#glow)"/>''')

def luva_voltaica(t, e):
    L,M,D = t
    ec = e or "#9fd8ff"
    return f'''<path d="M20 58 L20 34 L16 24 Q15 20 19 20 L23 28 L23 12 Q23 9 26 9 Q29 9 29 12 L29 26 L30 9 Q30 6 33 6 Q36 6 36 9 L36 26 L38 11 Q38 8 41 8 Q44 9 43.5 12 L42 28 L45 18 Q46 15 49 16 Q51 17 50 20 L46 38 L46 58 Z" fill="{COU[1]}" {o}/>
 <path d="M24 13 L24 26 M31 10 L31 26 M39 12 L38.5 26" stroke="{COU[0]}" stroke-width="1.2"/>
 {"".join(f'<rect x="{x}" y="{y}" width="6" height="4" rx="1" fill="{M}" {o}/>' for x,y in ((23,14),(30,11),(38,13),(44,21)))}
 <rect x="19" y="40" width="28" height="9" fill="{M}" {o}/><path d="M21 42 L45 42" stroke="{L}" stroke-width="1.2"/>
 {"".join(f'<circle cx="{x}" cy="44.5" r="2.2" fill="{D}" {o}/>' for x in (25,33,41))}
 <path d="M8 10 L14 16 L10 18 L16 26" fill="none" stroke="{ec}" stroke-width="1.6" filter="url(#glow)"/><path d="M56 6 L50 12 L54 14 L48 20" fill="none" stroke="{ec}" stroke-width="1.6" filter="url(#glow)"/>'''

def pistola_raio(t, e):
    L,M,D = t
    ec = e or "#9fd8ff"
    return f'''<path d="M8 20 L40 20 L40 32 L8 32 Z" fill="{M}" {o}/>{"".join(f'<rect x="{x}" y="18" width="3.4" height="16" rx="1" fill="{TINTS["cobre"][1]}" {o}/>' for x in (14,20,26))}
 <path d="M10 22 L38 22" stroke="{L}" stroke-width="1.2"/>
 <circle cx="47" cy="26" r="8.5" fill="#6a8a9a" fill-opacity=".5" {o}/><path d="M43 26 L46 22 L48 30 L51 26" fill="none" stroke="{ec}" stroke-width="1.6" filter="url(#glow)"/>
 <path d="M4 22 L8 22 L8 30 L4 30 Z" fill="{D}" {o}/><circle cx="3.5" cy="26" r="2" fill="{ec}" filter="url(#glow)"/>
 <path d="M28 32 L40 32 L42 56 L30 56 Z" fill="{MAD[1]}" {o}/><path d="M31 34 L32 54" stroke="{MAD[0]}" stroke-width="1.2"/>
 <path d="M22 32 Q20 40 26 42" fill="none" stroke="{K}" stroke-width="1.8"/><path d="M32 44 l6 0 M32 48 l6 0" stroke="{LAT[0]}" stroke-width="1"/>'''

# ---------- armaduras ----------
def elmo_leve(t, e):
    L,M,D = t
    return f'''<path d="M32 4 Q14 18 12 40 Q10 54 18 60 L46 60 Q54 54 52 40 Q50 18 32 4 Z" fill="{M}" {o}/>
 <path d="M32 6 Q20 18 17 36" fill="none" stroke="{L}" stroke-width="1.6"/>
 <path d="M20 30 Q32 22 44 30 Q46 44 40 54 Q32 58 24 54 Q18 44 20 30 Z" fill="#0e0c0d" {o}/>
 {f'<circle cx="27" cy="38" r="2.4" fill="{e}" filter="url(#glow)"/><circle cx="37" cy="38" r="2.4" fill="{e}" filter="url(#glow)"/><path d="M26 47 L38 47 M28 45 l0 4 M32 45 l0 4 M36 45 l0 4" stroke="{OSS[1]}" stroke-width="1"/>' if e else f'<circle cx="27" cy="38" r="1.2" fill="{OSS[1]}"/><circle cx="37" cy="38" r="1.2" fill="{OSS[1]}"/>'}
 <path d="M14 50 l6 4 M50 50 l-6 4 M26 4 l2 6" stroke="{D}" stroke-width="1.4"/>'''
def elmo_medio(t, e):
    L,M,D = t
    return f'''<ellipse cx="32" cy="40" rx="29" ry="9" fill="{D}" {o}/><path d="M17 38 Q16 16 32 12 Q48 16 47 38 Z" fill="{M}" {o}/>
 <path d="M20 36 Q20 20 30 15" fill="none" stroke="{L}" stroke-width="1.6"/><path d="M17 34 Q32 38 47 34 L47 38 Q32 42 17 38 Z" fill="#7a1612" {o}/>
 {f'<path d="M22 22 L42 22 L42 30 L22 30 Z" fill="{K}"/><circle cx="27" cy="26" r="3" fill="{e}" filter="url(#glow)"/><circle cx="37" cy="26" r="3" fill="{e}" filter="url(#glow)"/>' if e else f'<circle cx="25" cy="26" r="4.6" fill="{LAT[1]}" {o}/><circle cx="25" cy="26" r="2.6" fill="#3a5a6a"/><circle cx="37" cy="26" r="4.6" fill="{LAT[1]}" {o}/><circle cx="37" cy="26" r="2.6" fill="#3a5a6a"/><path d="M29.6 26 L32.4 26" stroke="{K}" stroke-width="1.6"/>'}
 <path d="M8 40 Q32 48 56 40" fill="none" stroke="{L}" stroke-width="1"/>'''
def elmo_pesado(t, e):
    L,M,D = t
    return f'''<path d="M14 54 L14 26 Q14 6 32 6 Q50 6 50 26 L50 54 Q32 60 14 54 Z" fill="{M}" {o}/>
 <path d="M18 50 L18 26 Q18 11 30 10" fill="none" stroke="{L}" stroke-width="2"/><path d="M32 6 L32 56" stroke="{D}" stroke-width="2"/>
 <path d="M18 28 L46 28 L46 33 L18 33 Z" fill="{K}"/>{f'<path d="M20 30.5 L44 30.5" stroke="{e}" stroke-width="2" filter="url(#glow)"/>' if e else ''}
 {"".join(f'<rect x="{x}" y="38" width="2.2" height="9" fill="{K}"/>' for x in (22,26,36,40))}
 <path d="M12 54 Q32 62 52 54" fill="none" stroke="{D}" stroke-width="3"/>{"".join(f'<circle cx="{x}" cy="{y}" r="1.3" fill="{L}" stroke="{K}" stroke-width=".7"/>' for x,y in ((18,20),(46,20),(18,46),(46,46)))}'''
def peito_leve(t, e):
    L,M,D = t
    return f'''<path d="M20 6 L26 4 Q32 10 38 4 L44 6 L56 16 L50 28 L46 24 L48 60 L16 60 L18 24 L14 28 L8 16 Z" fill="{M}" {o}/>
 <path d="M26 4 Q32 10 38 4 L36 14 Q32 18 28 14 Z" fill="{D}" {o}/><path d="M32 16 L32 60" stroke="{D}" stroke-width="1.6"/>
 <path d="M20 10 L16 22 M22 30 L20 58" stroke="{L}" stroke-width="1.4"/>
 <path d="M30 26 L34 26 L34 30 L38 30 L38 34 L34 34 L34 42 L30 42 L30 34 L26 34 L26 30 L30 30 Z" fill="{OSS[1]}" {o}/>{glow("M32 26 L32 42 M26 32 L38 32", e, 1.4)}
 <path d="M18 50 l4 4 M46 52 l-3 3 M40 58 l4 -4" stroke="{D}" stroke-width="1.4"/>'''
def peito_medio(t, e):
    L,M,D = t
    return f'''<path d="M18 6 L28 6 L32 14 L36 6 L46 6 L56 18 L50 32 L48 30 L50 60 L14 60 L16 30 L14 32 L8 18 Z" fill="{M}" {o}/>
 <path d="M28 6 L32 14 L36 6 L34 60 L30 60 Z" fill="#2a2222" {o}/><path d="M20 10 L13 20 M22 24 L20 56" stroke="{L}" stroke-width="1.4"/>
 <path d="M18 14 L46 44" stroke="{K}" stroke-width="5"/><path d="M18 14 L46 44" stroke="{COU[0]}" stroke-width="3"/>
 {"".join(f'<rect x="{18+i*4.6-1.2}" y="{14+i*4.9-2.6}" width="2.4" height="5" fill="{LAT[0]}" transform="rotate(-43 {18+i*4.6} {14+i*4.9})"/>' for i in range(1,6))}
 {"".join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="{LAT[1]}" stroke="{K}" stroke-width=".7"/>' for x,y in ((39,20),(39,26),(26,48),(26,54)))}
 {glow("M40 36 L40 52", e, 1.6)}'''
def peito_pesado(t, e):
    L,M,D = t
    return f'''<path d="M4 18 Q8 6 20 8 L24 16 L40 16 L44 8 Q56 6 60 18 L56 26 L48 22 L48 56 Q32 62 16 56 L16 22 L8 26 Z" fill="{M}" {o}/>
 <path d="M4 18 Q8 6 20 8 L24 16 L16 22 L8 26 Z M60 18 Q56 6 44 8 L40 16 L48 22 L56 26 Z" fill="{D}" {o}/>
 <path d="M24 16 L40 16 L36 24 L28 24 Z" fill="{K}"/><path d="M32 24 L32 58" stroke="{D}" stroke-width="2"/>
 <path d="M20 26 Q20 46 30 54" fill="none" stroke="{L}" stroke-width="2"/><path d="M16 38 Q32 44 48 38 M16 46 Q32 52 48 46" fill="none" stroke="{K}" stroke-width="1.4"/>
 {f'<path d="M26 30 L30 34 L28 38 L33 42 M38 28 L35 33 L38 36" fill="none" stroke="{e}" stroke-width="1.8" filter="url(#glow)"/>' if e else ''}
 {"".join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="{L}" stroke="{K}" stroke-width=".7"/>' for x,y in ((12,16),(52,16),(20,30),(44,30)))}'''
def _luvas(t, e, cuff, knuck):
    L,M,D = t
    g = f'''<path d="M10 58 L12 36 L8 22 Q8 18 12 19 L16 28 L16 12 Q16 9 19 9 Q22 9 22 12 L23 26 L24 10 Q24 7 27 7 Q30 7 30 10 L30 27 L33 14 Q34 11 37 12 Q39 13 38 16 L36 32 Q36 46 32 58 Z" fill="{M}" {o}/>
 <path d="M18 12 L18 26 M25.5 10 L25.5 26" stroke="{L}" stroke-width="1.2"/><rect x="9" y="48" width="25" height="10" fill="{cuff}" {o}/>'''
    if knuck: g += "".join(f'<path d="M{x} {y} l2.5 -3.5 l2.5 3.5 Z" fill="{ACO[0]}" {o}/>' for x,y in ((15.5,30),(22.5,29),(29,30)))
    return g
def luvas_leve(t, e):
    L,M,D = t
    return _luvas(t,e,D,False) + f'<path d="M12 40 L34 36 M12 44 L34 40 M14 32 L34 30" stroke="{OSS[1]}" stroke-width="1.6"/><path d="M20 22 l3 6 M28 20 l-2 8" stroke="#7a1612" stroke-width="1.6"/>' + glow("M16 42 L30 39", e, 1.4) + '<g transform="translate(26 0)">' + _luvas(t,None,D,False) + '</g>'
def luvas_medio(t, e):
    return '<g transform="translate(26 0)">' + _luvas(t,None,LAT[1],True) + '</g>' + _luvas(t,e,LAT[1],True) + glow("M12 52 L32 52", e, 1.4)
def luvas_pesado(t, e):
    L,M,D = t
    plates = "".join(f'<path d="M{10+i*0.3} {36+i*4} Q22 {33+i*4} 36 {34+i*4}" fill="none" stroke="{K}" stroke-width="1.4"/>' for i in range(4))
    one = _luvas(t,None,D,True) + plates
    return '<g transform="translate(26 0)">' + one + '</g>' + one + glow("M14 40 L32 38", e, 1.8)
def _calcas(t, e, belt):
    L,M,D = t
    return f'''<path d="M14 6 L50 6 L54 58 L38 58 L32 22 L26 58 L10 58 Z" fill="{M}" {o}/><rect x="13" y="5" width="38" height="7" fill="{belt}" {o}/>
 <rect x="28" y="5" width="8" height="7" fill="{LAT[1]}" {o}/><path d="M18 14 L14 56 M46 14 L50 56" stroke="{L}" stroke-width="1.4"/><path d="M32 12 L32 22" stroke="{D}" stroke-width="1.6"/>'''
def calcas_leve(t, e):
    L,M,D = t
    return f'''<path d="M16 6 L48 6 L58 60 L6 60 Z" fill="{M}" {o}/><rect x="15" y="5" width="34" height="6" fill="{D}" {o}/>
 <path d="M24 12 L18 58 M32 12 L32 58 M40 12 L46 58" stroke="{D}" stroke-width="1.4"/><path d="M20 12 L12 56" stroke="{L}" stroke-width="1.4"/>
 <path d="M6 60 L10 54 L14 60 L20 55 L26 60 L32 54 L38 60 L44 55 L50 60 L54 54 L58 60" fill="{D}" {o}/>
 <path d="M30 11 L28 30 L32 28 L36 30 L34 11" fill="#7a1612" {o}/>{glow("M30 14 L30 26", e, 1.4)}'''
def calcas_medio(t, e):
    L,M,D = t
    return _calcas(t,e,COU[2]) + f'<rect x="38" y="34" width="9" height="8" fill="{TINTS["pano"][2]}" {o}/><path d="M38 34 l9 8 M47 34 l-9 8" stroke="{K}" stroke-width=".8"/><path d="M16 40 l6 2 M14 50 l8 0" stroke="{D}" stroke-width="1.6"/>' + glow("M18 30 L16 48", e, 1.4)
def calcas_pesado(t, e):
    L,M,D = t
    return _calcas(t,e,FER[2]) + "".join(f'<path d="M{12+i*0.5} {20+i*9} L28 {19+i*9} M{36} {19+i*9} L{52-i*0.3} {20+i*9}" stroke="{K}" stroke-width="1.6"/>' for i in range(4)) + f'<ellipse cx="19" cy="36" rx="6" ry="4" fill="{L}" {o}/><ellipse cx="45" cy="36" rx="6" ry="4" fill="{L}" {o}/>' + glow("M14 46 L28 46 M36 46 L50 46", e, 1.4)
def _bota(x, t, sole, cuff, extra=""):
    L,M,D = t
    return f'''<g transform="translate({x} 0)"><path d="M4 8 L22 8 L22 42 L30 48 Q32 56 28 58 L2 58 Z" fill="{M}" {o}/><rect x="3" y="6" width="20" height="7" fill="{cuff}" {o}/>
 <path d="M2 54 L30 54 Q31 58 28 59 L2 59 Z" fill="{sole}" {o}/><path d="M7 14 L7 50" stroke="{L}" stroke-width="1.4"/>{extra}</g>'''
def botas_leve(t, e):
    L,M,D = t
    ex = f'<path d="M4 22 L22 30 M4 32 L22 40 M4 42 L24 48" stroke="#a89a7c" stroke-width="1.6"/>'
    return _bota(2,t,D,D,ex) + _bota(32,t,D,D,ex) + glow("M8 24 L18 28 M38 24 L48 28", e, 1.2)
def botas_medio(t, e):
    ex = "".join(f'<path d="M20 {y} l-5 2 l5 2" fill="none" stroke="#c0b49a" stroke-width="1"/>' for y in (16,24,32,40))
    return _bota(2,t,"#1d1a1c",LAT[1],ex) + _bota(32,t,"#1d1a1c",LAT[1],ex) + glow("M5 46 L20 46 M35 46 L50 46", e, 1.2)
def botas_pesado(t, e):
    L,M,D = t
    ex = f'<path d="M4 20 L22 20 M4 30 L22 30 M4 40 L24 42" stroke="{K}" stroke-width="1.4"/><path d="M12 12 L16 4 L18 12" fill="{ACO[0]}" {o}/>'
    return _bota(2,t,FER[2],D,ex) + _bota(32,t,FER[2],D,ex) + glow("M6 50 L26 50 M36 50 L56 50", e, 1.4)

# ---------- acessórios ----------
def anel(t, e):
    L,M,D = t
    return f'''<ellipse cx="32" cy="36" rx="18" ry="16" fill="none" stroke="{K}" stroke-width="9"/><ellipse cx="32" cy="36" rx="18" ry="16" fill="none" stroke="{M}" stroke-width="5.6"/>
 <path d="M16 30 Q22 20 34 20" fill="none" stroke="{L}" stroke-width="1.6"/>
 <path d="M26 12 L38 12 L38 16 L34 16 L33 30 L31 30 L30 16 L26 16 Z" fill="{D}" {o}/><path d="M28 13 L36 13" stroke="{L}" stroke-width="1"/>
 <path d="M14 42 l4 2 M46 44 l3 -3" stroke="#6a3a22" stroke-width="2"/>'''
def colar_dentes(t, e):
    L,M,D = t
    teeth = "".join(f'<path d="M{32+20*__import__("math").sin(a)-2.5} {14+24*__import__("math").cos(a)} l2.5 {9-abs(a)*2} l2.5 -{9-abs(a)*2} Z" fill="{L}" {o}/>' for a in (-1.0,-0.65,-0.3,0.05,0.4,0.75))
    return f'''<path d="M8 10 Q10 40 32 40 Q54 40 56 10" fill="none" stroke="{K}" stroke-width="3"/><path d="M8 10 Q10 40 32 40 Q54 40 56 10" fill="none" stroke="{COU[0]}" stroke-width="1.4"/>
 {teeth}<path d="M28 42 L32 58 L36 42 Z" fill="{L}" {o}/><path d="M30 44 L32 54" stroke="{D}" stroke-width="1"/>'''
def amuleto_vigilia(t, e):
    L,M,D = t
    ec = e or "#ff9a3a"
    import math
    cogs = " ".join(f"{32+(19 if i%2==0 else 15)*math.cos(math.radians(i*22.5)):.1f},{38+(19 if i%2==0 else 15)*math.sin(math.radians(i*22.5)):.1f}" for i in range(16))
    return f'''<path d="M16 2 Q32 14 48 2" fill="none" stroke="{K}" stroke-width="2.6"/><path d="M16 2 Q32 14 48 2" fill="none" stroke="{FER[0]}" stroke-width="1.2"/>
 <polygon points="{cogs}" fill="{M}" {o}/><circle cx="32" cy="38" r="10" fill="{K}"/><circle cx="32" cy="38" r="10" fill="none" stroke="{D}" stroke-width="1.6"/>
 <rect x="29" y="36" width="6" height="11" fill="#ece0bc" {o}/><path d="M32 36 Q29 31 32 27 Q35 31 32 36 Z" fill="{ec}" filter="url(#glow)"/>
 <path d="M18 30 Q22 24 28 22" fill="none" stroke="{L}" stroke-width="1.6"/>'''
def amuleto_arautos(t, e):
    L,M,D = t
    ec = e or "#ffe08a"
    return f'''<path d="M18 2 Q32 14 46 2" fill="none" stroke="{K}" stroke-width="2.6"/><path d="M18 2 Q32 14 46 2" fill="none" stroke="#7a1612" stroke-width="1.2"/>
 <path d="M30 12 L34 12 L36 34 Q46 44 50 58 L14 58 Q18 44 28 34 Z" fill="{M}" {o}/><path d="M31 14 L30 34 Q22 42 18 54" fill="none" stroke="{L}" stroke-width="1.6"/>
 <path d="M14 58 L50 58 L46 52 L18 52 Z" fill="{D}" {o}/><path d="M38 36 L46 30 L40 42 Z" fill="#0e0c0d" {o}/>
 <path d="M24 40 Q22 30 28 24 M40 44 Q44 34 38 26" fill="none" stroke="{ec}" stroke-width="1.8" filter="url(#glow)"/>'''

# ---------- consumíveis ----------
def _frasco(t, e, wide=False, cork="#8a6040", label=None):
    L,M,D = t
    body = "M22 22 Q8 30 10 46 Q12 60 32 60 Q52 60 54 46 Q56 30 42 22 Z" if wide else "M26 20 Q14 30 16 46 Q18 58 32 58 Q46 58 48 46 Q50 30 38 20 Z"
    liquid = "M12 38 Q32 34 52 38 Q54 56 32 58 Q10 56 12 38 Z" if wide else "M17 38 Q32 34 47 38 Q47 55 32 56 Q17 55 17 38 Z"
    s = f'''<path d="{body}" fill="#2a3436" fill-opacity=".85" {o}/><path d="{liquid}" fill="{M}"/><path d="{liquid}" fill="none" stroke="{L}" stroke-width="1.2" stroke-dasharray="0 0"/>
 <path d="{body}" fill="none" {o}/><rect x="{24 if wide else 27}" y="8" width="{16 if wide else 10}" height="14" fill="#3a4648" {o}/>
 <rect x="{25 if wide else 28}" y="3" width="{14 if wide else 8}" height="8" rx="1.5" fill="{cork}" {o}/>
 <path d="M{18 if wide else 21} 32 Q{16 if wide else 19} 42 {20 if wide else 22} 50" fill="none" stroke="#eef4f8" stroke-width="2" stroke-opacity=".7"/>
 <circle cx="38" cy="46" r="2" fill="{L}"/><circle cx="30" cy="50" r="1.2" fill="{L}"/>'''
    if label: s += label
    return s
def pocao(t, e): return _frasco(t,e)
def pocao_grande(t, e): return _frasco(t,e,True,label=f'<rect x="20" y="40" width="24" height="10" fill="#c0b49a" {o}/><path d="M24 45 L40 45" stroke="#7a1612" stroke-width="1.4"/>')
def agua_benta(t, e):
    return _frasco(t,e,cork="#6a6a70") + f'<path d="M30 38 L34 38 L34 41 L37 41 L37 44 L34 44 L34 52 L30 52 L30 44 L27 44 L27 41 L30 41 Z" fill="#e8eef2" {o}/><path d="M44 10 Q50 16 46 24" fill="none" stroke="#7a1612" stroke-width="2"/>'
def antidoto(t, e):
    L,M,D = t
    return f'''<path d="M20 14 L44 14 L48 22 L48 58 L16 58 L16 22 Z" fill="#6a5a2a" {o}/><path d="M18 26 L46 26 L46 56 L18 56 Z" fill="{M}" fill-opacity=".8"/>
 <rect x="28" y="4" width="8" height="10" fill="{FER[1]}" {o}/><rect x="20" y="32" width="24" height="16" fill="#c0b49a" {o}/>
 <path d="M26 36 Q32 32 38 36 Q36 44 32 46 Q28 44 26 36 Z" fill="{K}"/><circle cx="29.5" cy="38" r="1.3" fill="#c0b49a"/><circle cx="34.5" cy="38" r="1.3" fill="#c0b49a"/>
 <path d="M20 18 L22 54" stroke="{L}" stroke-width="1.6"/>'''
def bandagem(t, e):
    L,M,D = t
    return f'''<ellipse cx="38" cy="36" rx="18" ry="20" fill="{M}" {o}/><ellipse cx="38" cy="36" rx="7" ry="8" fill="{D}" {o}/>
 <path d="M24 26 Q30 18 40 18 M24 46 Q32 54 44 54" fill="none" stroke="{L}" stroke-width="1.4"/><path d="M26 30 Q26 40 30 46" fill="none" stroke="{D}" stroke-width="1"/>
 <path d="M24 44 L6 56 L10 60 L28 50 Z" fill="{L}" {o}/><path d="M44 28 Q48 34 44 40" fill="none" stroke="#7a1612" stroke-width="3"/><circle cx="16" cy="52" r="2.4" fill="#7a1612"/>'''
def lata(t, e):
    L,M,D = t
    return f'''<path d="M14 18 L50 18 L50 54 Q32 60 14 54 Z" fill="{M}" {o}/><ellipse cx="32" cy="18" rx="18" ry="6" fill="{L}" {o}/><ellipse cx="32" cy="18" rx="13" ry="3.6" fill="none" stroke="{D}" stroke-width="1"/>
 <path d="M14 28 Q32 33 50 28 L50 46 Q32 51 14 46 Z" fill="#6a3a22" {o}/><text x="32" y="42" font-family="Courier New,monospace" font-weight="700" font-size="8" fill="#e6dcc6" text-anchor="middle">RAÇÃO</text>
 <path d="M18 22 L18 52" stroke="#eef4f8" stroke-width="1.4" stroke-opacity=".6"/><path d="M40 20 Q46 8 54 10 L52 14 Q46 12 44 20" fill="{L}" {o}/>'''
def vela(t, e):
    L,M,D = t
    return f'''<ellipse cx="32" cy="56" rx="18" ry="5" fill="{FER[1]}" {o}/><path d="M22 20 L42 20 L42 54 L22 54 Z" fill="{M}" {o}/>
 <path d="M24 22 L24 52" stroke="{L}" stroke-width="2"/><path d="M42 22 Q46 30 42 34 Q40 40 43 46" fill="{M}" {o}/><path d="M22 20 Q26 26 30 22 Q34 28 38 22 Q40 26 42 20" fill="{L}" {o}/>
 <path d="M32 20 L32 14" stroke="{K}" stroke-width="1.4"/><path d="M32 2 Q26 10 32 16 Q38 10 32 2 Z" fill="#ff9a3a" filter="url(#glow)"/><path d="M32 7 Q30 11 32 14 Q34 11 32 7 Z" fill="#fff0c0"/>'''
def balas(t, e):
    L,M,D = t
    return "".join(f'''<g transform="translate({x} {y})"><circle cx="0" cy="0" r="7" fill="{M}" {o}/><path d="M-4 -3 Q-2 -6 2 -5" fill="none" stroke="{L}" stroke-width="1.6"/></g>''' for x,y in ((22,40),(38,42),(30,28),(46,28),(16,26)))
def virotes(t, e):
    L,M,D = t
    return "".join(diag(f'''<g transform="translate({dx} 0)"><rect x="31" y="10" width="2" height="48" fill="{MAD[1]}" {o}/><path d="M32 2 L35.5 12 L28.5 12 Z" fill="{L}" {o}/>
 <path d="M31 48 L26 58 L31 56 M33 48 L38 58 L33 56" fill="#c0b49a" {o}/></g>''') for dx in (-8,0,8))
def cartuchos(t, e):
    L,M,D = t
    return "".join(f'''<g transform="translate({x} {y}) rotate({r})"><rect x="-5" y="-14" width="10" height="20" fill="{M}" {o}/><rect x="-5.6" y="4" width="11.2" height="8" fill="{LAT[1]}" {o}/>
 <path d="M-3 -12 L-3 4" stroke="{L}" stroke-width="1.4"/><circle cx="0" cy="8" r="1.6" fill="{LAT[2]}"/></g>''' for x,y,r in ((20,38,-14),(32,32,0),(44,38,14)))

# ---------- jóias ----------
def joia_lagrima(t, e):
    L,M,D = t
    return f'''<path d="M32 4 Q16 30 16 42 Q16 58 32 58 Q48 58 48 42 Q48 30 32 4 Z" fill="{M}" {o} filter="url(#glow)"/>
 <path d="M32 4 Q16 30 16 42 Q16 58 32 58 Q48 58 48 42 Q48 30 32 4 Z" fill="{M}" {o}/><path d="M32 12 L24 40 L32 54 L40 40 Z" fill="{L}" fill-opacity=".6"/>
 <path d="M24 40 Q22 48 28 52" fill="none" stroke="#fff8e0" stroke-width="2"/><path d="M32 4 L32 58 M16 42 L48 42" stroke="{D}" stroke-width=".8"/>'''
def joia_alma(t, e):
    L,M,D = t
    return f'''<path d="M32 4 L50 22 L44 56 L20 56 L14 22 Z" fill="{M}" filter="url(#glow)"/><path d="M32 4 L50 22 L44 56 L20 56 L14 22 Z" fill="{M}" {o}/>
 <path d="M14 22 L50 22 M32 4 L24 22 L32 56 L40 22 Z" fill="{L}" fill-opacity=".45" stroke="{D}" stroke-width=".8"/>
 <path d="M28 30 Q32 26 36 30 Q38 38 32 44 Q26 38 28 30 Z" fill="#ffffff" fill-opacity=".85"/><circle cx="30.5" cy="33" r="1" fill="{D}"/><circle cx="33.5" cy="33" r="1" fill="{D}"/>'''
def joia_caos(t, e):
    L,M,D = t
    return f'''<path d="M32 4 Q44 14 52 12 Q50 24 58 32 Q48 40 50 54 Q38 50 32 60 Q26 50 14 54 Q16 40 6 32 Q14 24 12 12 Q20 14 32 4 Z" fill="{M}" filter="url(#glow)"/>
 <path d="M32 4 Q44 14 52 12 Q50 24 58 32 Q48 40 50 54 Q38 50 32 60 Q26 50 14 54 Q16 40 6 32 Q14 24 12 12 Q20 14 32 4 Z" fill="{M}" {o}/>
 <path d="M22 22 Q32 16 42 24 Q46 36 36 44 Q24 46 20 34" fill="none" stroke="{L}" stroke-width="2"/><ellipse cx="32" cy="32" rx="7" ry="9" fill="{D}" {o}/><ellipse cx="32" cy="32" rx="2" ry="7" fill="#ffcc40"/>'''
def joia_engrenagem(t, e):
    import math
    L,M,D = t
    ec = e or "#9cff3a"
    cogs = " ".join(f"{32+(26 if (i//2)%2==0 else 20)*math.cos(math.radians(i*15)):.1f},{32+(26 if (i//2)%2==0 else 20)*math.sin(math.radians(i*15)):.1f}" for i in range(24))
    return f'''<polygon points="{cogs}" fill="{M}" {o}/><circle cx="32" cy="32" r="13" fill="{D}" {o}/><circle cx="32" cy="32" r="8" fill="{ec}" filter="url(#glow)"/>
 <path d="M32 26 Q26 32 32 38 Q38 32 32 26" fill="#1a3a08"/><path d="M14 22 Q20 12 30 10" fill="none" stroke="{L}" stroke-width="2"/>'''

# ---------- materiais ----------
def osso(t, e):
    L,M,D = t
    return diag(f'''<path d="M28 14 L36 14 L36 50 L28 50 Z" fill="{M}" {o}/><path d="M30 16 L30 48" stroke="{L}" stroke-width="1.6"/>
 <circle cx="27" cy="11" r="6" fill="{M}" {o}/><circle cx="37" cy="11" r="6" fill="{M}" {o}/><circle cx="27" cy="53" r="6" fill="{M}" {o}/><circle cx="37" cy="53" r="6" fill="{M}" {o}/>
 <path d="M28 14 L36 14 M28 50 L36 50" stroke="{M}" stroke-width="3"/><path d="M33 26 L30 30 L34 33 L31 37" fill="none" stroke="{K}" stroke-width="1.4"/>''')
def pena(t, e):
    L,M,D = t
    barbs = "".join(f'<path d="M32 {y} Q{20-(y-10)*0.05} {y-2} {16+abs(y-32)*0.25} {y+6}" fill="none" stroke="{D}" stroke-width="1"/>' for y in range(12,46,6))
    return diag(f'''<path d="M32 4 Q14 18 16 46 L32 50 L48 46 Q50 18 32 4 Z" fill="{M}" {o}/>{barbs}<path d="M32 4 Q42 20 44 40" fill="none" stroke="{L}" stroke-width="1.6"/>
 <path d="M38 20 L48 24 M18 30 L26 34" stroke="#3a3634" stroke-width="2.4"/><path d="M32 6 L32 62" stroke="{K}" stroke-width="2.2"/><path d="M32 6 L32 62" stroke="{L}" stroke-width="1"/>''')
def engrenagem(t, e):
    import math
    L,M,D = t
    cogs = " ".join(f"{30+(25 if (i//2)%2==0 else 19)*math.cos(math.radians(i*18)):.1f},{34+(25 if (i//2)%2==0 else 19)*math.sin(math.radians(i*18)):.1f}" for i in range(20))
    return f'''<polygon points="{cogs}" fill="{M}" {o}/><circle cx="30" cy="34" r="7" fill="#0e0c0d" {o}/><path d="M16 22 Q22 14 32 12" fill="none" stroke="{L}" stroke-width="2"/>
 <path d="M40 40 l4 6 M22 44 l-4 2 M38 22 l3 -2" stroke="{D}" stroke-width="2.6"/>'''
def retalho(t, e):
    L,M,D = t
    return f'''<path d="M8 14 L30 8 L56 16 L52 34 L58 52 L34 58 L10 52 L14 34 Z" fill="{M}" {o}/><path d="M12 18 L28 12 L52 20" fill="none" stroke="{L}" stroke-width="1.6"/>
 <path d="M14 34 L52 34" stroke="#c0b49a" stroke-width="1.4" stroke-dasharray="3 2"/><path d="M30 8 L34 58" stroke="#c0b49a" stroke-width="1.4" stroke-dasharray="3 2"/>
 <path d="M38 40 Q44 44 42 50" fill="none" stroke="{D}" stroke-width="2.4"/>'''
def dente(t, e):
    L,M,D = t
    return f'''<path d="M14 10 Q32 2 50 10 Q52 22 44 28 Q40 44 32 60 Q30 44 24 32 Q12 24 14 10 Z" fill="{M}" {o}/><path d="M18 12 Q30 6 42 10" fill="none" stroke="{L}" stroke-width="2"/>
 <path d="M24 16 Q22 24 28 30" fill="none" stroke="{L}" stroke-width="1.4"/><circle cx="40" cy="20" r="3" fill="#9cff3a"/><path d="M34 32 Q36 44 32 54" fill="none" stroke="{D}" stroke-width="1.6"/>'''
def cinza(t, e):
    L,M,D = t
    return f'''<path d="M6 54 Q8 40 22 34 Q28 22 36 30 Q50 30 58 54 Z" fill="{M}" {o}/><path d="M14 46 Q22 38 30 40 M36 36 Q44 38 50 46" fill="none" stroke="{L}" stroke-width="1.6"/>
 <circle cx="26" cy="46" r="1.6" fill="#ff7a1a"/><circle cx="40" cy="44" r="1.2" fill="#ff7a1a"/><path d="M30 26 Q26 16 32 10 Q36 4 32 0" fill="none" stroke="{L}" stroke-width="1.6" stroke-opacity=".6"/>'''

# ---------- chaves e baús ----------
def chave(t, e):
    L,M,D = t
    return diag(f'''<circle cx="32" cy="12" r="9" fill="none" stroke="{K}" stroke-width="6.4"/><circle cx="32" cy="12" r="9" fill="none" stroke="{M}" stroke-width="3.6"/>
 <rect x="29.5" y="20" width="5" height="38" fill="{M}" {o}/><path d="M34 44 L42 44 L42 48 L38 48 L38 52 L42 52 L42 58 L34 58" fill="{M}" {o}/><path d="M31 22 L31 56" stroke="{L}" stroke-width="1"/>
 <path d="M26 8 Q28 4 32 4" fill="none" stroke="{L}" stroke-width="1.4"/>''')
def chave_cripta(t, e):
    L,M,D = t
    ec = e or "#ff3a2a"
    return diag(f'''<path d="M22 6 Q22 0 28 2 Q32 4 36 2 Q42 0 42 6 Q42 12 38 14 L36 22 L28 22 L26 14 Q22 12 22 6 Z" fill="{M}" {o}/>
 <circle cx="29" cy="8" r="2.2" fill="{ec}" filter="url(#glow)"/><circle cx="35" cy="8" r="2.2" fill="{ec}" filter="url(#glow)"/>
 <path d="M29 22 L35 22 L34 54 L30 54 Z" fill="{L}" {o}/><circle cx="29" cy="56" r="4" fill="{M}" {o}/><circle cx="35" cy="56" r="4" fill="{M}" {o}/>
 <path d="M34 36 L42 36 L42 40 L38 40 L38 46 L34 46" fill="{M}" {o}/>''')
def _bau(t, e, banded, ornate=False):
    L,M,D = t
    s = f'''<path d="M6 30 L58 30 L56 58 L8 58 Z" fill="{M}" {o}/><path d="M6 30 Q6 10 32 10 Q58 10 58 30 Z" fill="{L if ornate else M}" {o}/>
 <path d="M10 26 Q12 14 32 14" fill="none" stroke="{L}" stroke-width="1.6"/>
 {"".join(f'<path d="M8 {y} L56 {y}" stroke="{D}" stroke-width="1.2"/>' for y in (38,46,52))}'''
    bd = FER if banded else ("#6a6a70","#46464c","#2a2a2e")
    s += f'''<path d="M14 58 L14 30 Q14 12 18 12 M50 58 L50 30 Q50 12 46 12" fill="none" stroke="{K}" stroke-width="5"/><path d="M14 58 L14 30 Q14 13 18 12 M50 58 L50 30 Q50 13 46 12" fill="none" stroke="{bd[0] if banded else bd[1]}" stroke-width="2.6"/>
 <path d="M6 30 L58 30" stroke="{K}" stroke-width="3"/><rect x="26" y="26" width="12" height="14" rx="2" fill="{bd[1]}" {o}/><path d="M32 31 L32 36" stroke="{K}" stroke-width="2"/>'''
    if not banded and not ornate: s += f'<path d="M40 50 l6 -6 M20 40 l-4 4" stroke="#2a2a14" stroke-width="2"/><circle cx="44" cy="40" r="3" fill="#4a5a2a"/>'
    if ornate:
        ec = e or "#ffe08a"
        s += f'<path d="M32 16 L32 24 M28 19 L36 19" stroke="#7a1612" stroke-width="2.4"/><path d="M8 58 L56 58" stroke="{ec}" stroke-width="2" filter="url(#glow)"/><path d="M27 32 L37 32" stroke="{ec}" stroke-width="1.2" filter="url(#glow)"/>'
    return s
def bau_madeira(t, e): return _bau(t,e,False)
def bau_ferro(t, e): return _bau(t,e,True)
def relicario(t, e): return _bau(t,e,True,True)

MOTIVOS = {k:v for k,v in globals().items() if callable(v) and not k.startswith("_") and k not in ("glow","diag")}
