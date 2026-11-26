"""Render the original Fio do Bigode presentation (typographic motion graphics).
Run from the repository root: python scripts/render-presentation.py
Requires Pillow, NumPy and ffmpeg. No external media, voices or stock music.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np, subprocess, math, wave, json
ROOT=Path(__file__).resolve().parent.parent; OUT=ROOT/'assets/video';OUT.mkdir(parents=True,exist_ok=True)
W,H,FPS,DURATION=1280,720,24,44
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
fonts={}
def font(n,b=False):
 key=(n,b)
 if key not in fonts:fonts[key]=ImageFont.truetype(BOLD if b else FONT,n)
 return fonts[key]
def ease(v):v=max(0,min(1,v));return 1-(1-v)**3
GOLD=(239,192,78);WHITE=(248,247,241);MUTED=(180,183,173)
SCENES=[
 dict(start=0,end=6,kicker='PALAVRA. REGISTRO. CONFIANÇA.',title=['Negócio bom','tem palavra.'],body=['E o combinado merece registro.']),
 dict(start=6,end=11,kicker='CONHEÇA O FIO DO BIGODE',title=['O acordo é seu.','O histórico também.'],body=['Organize o que foi combinado,','da proposta ao acompanhamento.']),
 dict(start=11,end=18,kicker='TRÊS PILARES. UMA VISÃO.',title=['Cada acordo,','no seu tempo.'],pillars=True),
 dict(start=18,end=25,kicker='DO ENCONTRO À FORMALIZAÇÃO',title=['Defina. Convide.','Formalize.'],body=['Propostas e contrapropostas.','Identidade verificada e assinatura eletrônica.'],chips=['CLASSIFICADOS','CONVITE DIRETO','DOCUMENTOS']),
 dict(start=25,end=31,kicker='O COMBINADO CONTINUA',title=['Cada parcela.','Cada registro.'],body=['Comprovantes, confirmações e histórico.','Quitação e reputação na jornada do acordo.']),
 dict(start=31,end=37,kicker='REDE JURÍDICA POR CONVITE',title=['Quando precisar,','peça apoio.'],body=['Autorize o compartilhamento do dossiê.','O admin encaminha o caso ao escritório.'],note='Atendimento combinado entre cliente e escritório.'),
 dict(start=37,end=44,kicker='FIO DO BIGODE',title=['Seu próximo acordo','começa aqui.'],body=['Acesse pelo navegador.'],cta=True),
]
# Background remains restrained; type and the real brand mark carry the story.
y,x=np.mgrid[0:H,0:W];rad=np.exp(-(((x-1130)/690)**2+((y-110)/560)**2));base=np.stack([15+rad*22,17+rad*18,17+rad*7],axis=2).astype(np.uint8);BACKGROUND=Image.fromarray(base)
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(ROOT/'assets/icon.svg'),'-vf','scale=104:104','-frames:v','1',str(OUT/'logo-render.png')],check=True)
logo=Image.open(OUT/'logo-render.png').convert('RGBA')
def line(draw,xy,text,size=40,b=False,color=WHITE):
 f=font(size,b)
 while draw.textlength(text,font=f)>W-144 and size>18:size-=1;f=font(size,b)
 draw.text(xy,text,font=f,fill=color)
def render(t):
 scene=next(s for s in SCENES if s['start']<=t<s['end']);local=t-scene['start'];duration=scene['end']-scene['start'];alpha=min(1,local/.4,(duration-local)/.35);alpha=max(0,alpha)
 image=BACKGROUND.copy();d=ImageDraw.Draw(image)
 # A light orbit suggests continuity without resembling a financial chart.
 for r in [265,355,450]:d.arc((1070-r,155-r,1070+r,155+r),-50+local*2,85+local*2,fill=(54,52,37),width=1)
 image.paste(logo,(55,27),logo);d=ImageDraw.Draw(image);line(d,(174,64),'FIO DO BIGODE',28,True,GOLD)
 d.line((72,132,1208,132),fill=(61,61,49),width=1)
 layer=Image.new('RGBA',(W,H));q=ImageDraw.Draw(layer);offset=int(28*(1-ease(local/.7)))
 line(q,(74,175+offset),scene['kicker'],22,True,GOLD)
 if scene.get('pillars'):
  line(q,(74,223+offset),'Três caminhos para organizar o combinado.',37,True)
  cards=[('Veículos e bens','Disponível agora',True),('Imóveis','Em preparação',False),('Dinheiro','Em preparação',False)]
  for i,(title,status,live) in enumerate(cards):
   xx=74+i*383;yy=315+int(18*(1-ease((local-i*.12)/.6)))
   q.rounded_rectangle((xx,yy,xx+359,yy+214),radius=21,fill=(30,32,28),outline=GOLD if live else (78,80,66),width=2)
   q.rounded_rectangle((xx+22,yy+25,xx+337,yy+67),radius=12,fill=(71,61,31)if live else(44,46,40))
   line(q,(xx+36,yy+32),status,23,True,GOLD if live else MUTED)
   line(q,(xx+23,yy+109),title,31,True)
  line(q,(74,584),'Hoje: comece por veículos e bens.',30,False,GOLD)
 else:
  for i,text in enumerate(scene['title']):line(q,(72,225+i*86+offset),text,66,True,GOLD if i==1 else WHITE)
  for i,text in enumerate(scene.get('body',[])):line(q,(76,445+i*49+offset),text,31,False,MUTED)
  if scene.get('chips'):
   xx=75
   for chip in scene['chips']:
    ww=int(q.textlength(chip,font=font(19,True)))+32;q.rounded_rectangle((xx,572,xx+ww,613),radius=11,fill=(43,44,36));line(q,(xx+16,581),chip,19,True,GOLD);xx+=ww+18
  if scene.get('note'):line(q,(76,584),scene['note'],23,False,MUTED)
  if scene.get('cta'):
   q.rounded_rectangle((73,521,987,597),radius=13,fill=GOLD);line(q,(99,538),'nofiodobigode.app.br',40,True,(25,26,22));line(q,(77,620),'@fiodobigodeapp',23,False,MUTED)
 layer.putalpha(layer.getchannel('A').point(lambda v:int(v*alpha)));image=Image.alpha_composite(image.convert('RGBA'),layer).convert('RGB');d=ImageDraw.Draw(image)
 d.line((74,682,1206,682),fill=(58,57,45),width=3);d.line((74,682,74+int(1132*t/DURATION),682),fill=GOLD,width=3)
 return image
# Original, low-key instrumental bed, composed from synthesized tones.
SR=44100;audio=np.zeros(int(DURATION*SR),dtype=np.float32);beat=60/90;chords=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]
for bar in range(17):
 start=bar*4*beat
 for note in chords[bar%4]:
  n=int(min(4*beat+1,DURATION-start)*SR)
  if n<=0:continue
  tt=np.arange(n)/SR;freq=440*2**((note-69)/12);env=np.minimum(1,tt/.3)*np.exp(-tt/2.4)
  tone=(np.sin(2*np.pi*freq*tt)+.22*np.sin(2*np.pi*freq*2*tt))*env*.018
  at=int(start*SR);audio[at:at+n]+=tone[:len(audio[at:at+n])]
 for b in [0,2]:
  at=int((start+b*beat)*SR);n=min(int(.2*SR),len(audio)-at)
  if n>0:
   tt=np.arange(n)/SR;audio[at:at+n]+=.035*np.sin(2*np.pi*(60*tt-18*tt**2))*np.exp(-tt*35)
 for b in [1,3]:
  at=int((start+b*beat)*SR);n=min(int(.65*SR),len(audio)-at)
  if n>0:
   tt=np.arange(n)/SR;freq=440*2**((chords[bar%4][b%3]+12-69)/12);audio[at:at+n]+=.023*np.sin(2*np.pi*freq*tt)*np.exp(-tt*6)
fade=np.minimum(1,np.arange(len(audio))/(SR*1.5))*np.minimum(1,(len(audio)-np.arange(len(audio)))/(SR*2));audio*=fade
with wave.open(str(OUT/'trilha-original.wav'),'w')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(np.int16(np.clip(audio,-1,1)*32767).tobytes())
video=OUT/'fio-do-bigode-apresentacao.mp4'
cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(OUT/'trilha-original.wav'),'-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p','-af','loudnorm=I=-20:TP=-2:LRA=7','-c:a','aac','-b:a','96k','-movflags','+faststart','-shortest',str(video)]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for frame in range(DURATION*FPS):
 t=frame/FPS;p.stdin.write(render(t).tobytes())
 if frame%(FPS*6)==0:print(f'Render {t:.0f}/{DURATION}s',flush=True)
p.stdin.close();assert p.wait()==0
render(2.5).save(OUT/'capa-apresentacao.jpg',quality=92)
# Internal contact sheet for verification.
board=Image.new('RGB',(960,270*4),(18,18,18))
for i,t in enumerate([2,8,14,21,28,34,40]):board.paste(render(t).resize((480,270)),((i%2)*480,(i//2)*270))
board.save('/tmp/fdb-video-contact-sheet.jpg',quality=90)
(OUT/'logo-render.png').unlink();(OUT/'trilha-original.wav').unlink()
(OUT/'storyboard.json').write_text(json.dumps(SCENES,ensure_ascii=False,indent=2))
print('Finished',video,video.stat().st_size,flush=True)
