window.extra = function(){
  // esconde o rastreador de missões quando a janela abre
  document.querySelectorAll('div').forEach(d=>{ if(d.style.left=='1046px') d.style.display='none'; });
  const X=document.getElementById('extra');
  const C=30; // célula da mochila
  const M='icones/itens/mochila_2x/';
  const cell=(c,r,w,h,id,cls='')=>`<div class="item ${cls}" style="left:${c*C+1}px;top:${r*C+1}px;width:${w*C-1}px;height:${h*C-1}px"><img src="${M}${id}.png" style="width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 2px 2px #000)"></div>`;
  const eq=(x,y,w,h,lbl,icon,vb,glow)=>`<div class="eq" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;${glow?'box-shadow:inset 0 0 0 1px #000,inset 0 0 0 2px #c99a3e,inset 0 0 0 3px #120c08,inset 0 0 16px rgba(255,170,60,.35)':''}">${icon?`<img src="${M}${icon}.png" style="width:84%;height:84%;object-fit:contain;filter:drop-shadow(0 2px 2px #000)">`:''}<span class="lbl">${lbl}</span></div>`;
  X.innerHTML = `
  <div class="iron" style="left:856px;top:118px;width:414px;height:494px;z-index:20">
    <div class="rivet" style="left:6px;top:6px"></div><div class="rivet" style="right:6px;top:6px"></div><div class="rivet" style="left:6px;bottom:6px"></div><div class="rivet" style="right:6px;bottom:6px"></div>
    <div class="plate" style="left:100px;top:-12px;width:214px;height:28px"><span class="title">Equipamento</span></div>
    <div class="abs" style="right:12px;top:10px;width:18px;height:18px;background:linear-gradient(#5a1410,#2a0606);box-shadow:inset 0 0 0 1px #000,0 0 0 1px #8a6530;color:#f0dcae;font-family:Cinzel;font-weight:700;font-size:12px;line-height:18px;text-align:center">×</div>

    <!-- boneco -->
    <div class="leather" style="left:14px;top:24px;width:386px;height:214px;box-shadow:inset 0 0 0 1px #000,inset 0 0 30px #000">
      <div class="abs" style="left:143px;top:6px;width:100px;height:200px;background:url(corpo_humano.png) center/contain no-repeat;filter:drop-shadow(0 0 10px rgba(0,0,0,.9))"></div>
      <div class="abs" style="left:133px;top:170px;width:120px;height:30px;border-radius:50%;background:radial-gradient(rgba(106,168,224,.18),transparent 70%)"></div>
      ${eq(70,10,52,52,'CABEÇA','couro_sobrevivente_cabeca')}
      ${eq(264,10,52,52,'ROSTO','')}
      ${eq(8,10,54,112,'ARMA','escopeta_cano_duplo','',true)}
      ${eq(70,74,52,70,'PEITO','couro_sobrevivente_peito')}
      ${eq(324,10,54,112,'2ª MÃO','')}
      ${eq(264,80,52,52,'AMULETO','colar_dentes')}
      ${eq(8,160,36,36,'ANEL','anel_prego_caixao')}
      ${eq(52,160,36,36,'ANEL','')}
      ${eq(264,148,52,52,'BOTAS','couro_sobrevivente_botas')}
      ${eq(330,148,48,48,'LUVAS','couro_sobrevivente_luvas')}
    </div>

    <!-- atributos -->
    <div class="abs" style="left:14px;top:246px;width:386px;height:44px;display:grid;grid-template-columns:repeat(4,1fr);gap:4px">
      ${[['FOR','48'],['AGI','112','#9fd8ff'],['VIT','46'],['ESP','14']].map(a=>`<div style="background:rgba(0,0,0,.5);box-shadow:inset 0 0 0 1px #3a2a1a;text-align:center;padding-top:3px"><div style="font-family:Cinzel;font-size:9px;letter-spacing:2px;color:#8f8570">${a[0]}</div><div class="out" style="font-family:Cinzel;font-weight:700;font-size:16px;color:${a[2]||'#e8d6b0'}">${a[1]}</div></div>`).join('')}
    </div>
    <div class="abs" style="left:18px;top:296px;width:380px;display:flex;justify-content:space-between;font-size:13px;color:#b8ae96">
      <span>Dano <b style="font-family:Cinzel;color:#e8d6b0">8–14</b></span><span>Defesa <b style="font-family:Cinzel;color:#e8d6b0">38</b></span><span>Res. Sagrada <b style="font-family:Cinzel;color:#e8d6b0">4%</b></span>
    </div>

    <!-- mochila -->
    <div class="plate" style="left:120px;top:318px;width:174px;height:22px"><span class="title" style="font-size:11px">Mochila</span></div>
    <div class="grid" style="left:27px;top:346px;width:361px;height:121px">
      ${cell(0,0,1,2,'adaga_ossuario')}
      ${cell(1,0,3,2,'besta_sucata','cursed')}
      ${cell(4,0,2,2,'coro_mudo_cabeca')}
      ${cell(6,0,1,1,'badalo_de_guerra','rare')}
      ${cell(8,0,1,1,'pocao_vida_p')}${cell(9,0,1,1,'pocao_vida_p')}${cell(10,0,1,1,'pocao_recurso_p')}${cell(11,0,1,1,'antidoto_querosene')}
      ${cell(6,1,1,1,'anel_ferro_cripta')}${cell(7,1,1,1,'cartuchos_sal')}${cell(8,1,1,1,'vela_retorno')}
      ${cell(9,1,1,2,'leitura_hino_carpideiras')}
      ${cell(0,2,1,1,'agua_benta')}${cell(1,2,1,1,'virotes_prata')}
      ${cell(4,2,2,2,'couro_sobrevivente_calcas')}
    </div>
    <div class="abs" style="left:28px;top:472px;font-size:13px;color:#b8ae96;display:flex;gap:6px;align-items:center">
      <b style="font-family:Cinzel;color:#ffc65a">4.812</b>
      <span style="margin-left:200px">Peso <b style="font-family:Cinzel;color:#e8d6b0">38/60</b></span>
    </div>
  </div>

  <!-- tooltip do item -->
  <div class="tooltip" style="left:572px;top:300px;width:276px;z-index:21">
    <div style="display:flex;gap:10px;align-items:center;margin-bottom:6px">
      <img src="icones/itens/40/badalo_de_guerra.png" width="40" height="40" style="box-shadow:0 0 0 1px #000,0 0 0 2px #c99a3e">
      <div><div class="out" style="font-family:Cinzel;font-weight:700;font-size:15px;color:#ffc65a">Badalo de Guerra</div>
      <div style="font-size:12px;color:#c99a3e;font-style:italic">Amuleto · Raro</div></div>
    </div>
    <div style="height:1px;background:linear-gradient(90deg,#6a5030,transparent);margin-bottom:6px"></div>
    <div style="color:#9fd8ff">+3 Vitalidade</div>
    <div style="color:#9fd8ff">+2 Força</div>
    <div style="color:#7ad06a;margin-top:3px">Ao receber um golpe crítico, emite uma badalada que atordoa inimigos próximos por 1 s <span style="color:#8f8570">(recarga 30 s)</span>.</div>
    <div style="color:#8f8570;margin-top:4px">Requer Nv. 5 · Vigília</div>
    <div style="height:1px;background:linear-gradient(90deg,#6a5030,transparent);margin:6px 0"></div>
    <div style="margin-top:2px;font-size:12px;color:#8f8570;display:flex;justify-content:space-between"><span>Vende por</span><span style="color:#ffc65a;font-family:Cinzel;font-weight:700">320</span></div>
  </div>`;
};
