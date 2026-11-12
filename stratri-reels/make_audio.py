"""Ücretsiz, sentezlenmiş ses izi (telif yok). 120 BPM. Çıktı: output/audio.wav
Zamanlamalar index.html'deki çekimlerle eşleşir; değiştirirseniz buradaki saniyeleri de güncelleyin."""
import numpy as np, wave, os
SR=44100; DUR=27.0; N=int(SR*DUR)
L=np.zeros(N); R=np.zeros(N); rng=np.random.default_rng(7)
def add(sig,t,gain=1.0,pan=0.0):
    i=int(t*SR); j=min(N,i+len(sig)); s=sig[:j-i]*gain
    L[i:j]+=s*(1-max(0,pan)); R[i:j]+=s*(1+min(0,pan))
def env(n,a=.002,d=.2):
    tt=np.arange(n)/SR; return np.minimum(1,tt/a)*np.exp(-tt/d)
def lp(x,k):  # basit alçak geçiren
    return np.convolve(x,np.ones(k)/k,mode='same')
def kick(): n=int(.45*SR); tt=np.arange(n)/SR; f=45+80*np.exp(-tt*28); return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,.001,.16)
def hat(): n=int(.06*SR); x=rng.standard_normal(n); x=x-lp(x,6); return x*env(n,.0005,.018)
def click(): n=int(.025*SR); return (rng.standard_normal(n)-lp(rng.standard_normal(n),3))*env(n,.0003,.006)
def whoosh(l=.35): n=int(l*SR); x=lp(rng.standard_normal(n),18); tt=np.linspace(0,1,n); return x*np.sin(np.pi*tt)**2*3
def impact(): n=int(1.2*SR); tt=np.arange(n)/SR; return np.sin(2*np.pi*48*tt)*np.exp(-tt/.35)+lp(rng.standard_normal(n),4)*np.exp(-tt/.05)*.6
def tapestop(): n=int(.5*SR); tt=np.arange(n)/SR; f=260*(1-tt/.5)**2+25; x=np.sign(np.sin(2*np.pi*np.cumsum(f)/SR)); return lp(x,8)*.5*(1-tt/.5)
def riser(l): n=int(l*SR); tt=np.linspace(0,1,n); f=200+900*tt**2; return np.sin(2*np.pi*np.cumsum(f)/SR)*tt**2*.25+lp(rng.standard_normal(n),10)*tt**3*.6
def ping(f=880): n=int(.5*SR); tt=np.arange(n)/SR; return (np.sin(2*np.pi*f*tt)+.4*np.sin(2*np.pi*f*1.5*tt))*np.exp(-tt/.12)
def bass(f,l): n=int(l*SR); tt=np.arange(n)/SR; x=np.sin(2*np.pi*f*tt)+.3*np.sin(2*np.pi*2*f*tt); return x*np.minimum(1,tt/.01)*np.exp(-tt/.25)
def pad(freqs,l): n=int(l*SR); tt=np.arange(n)/SR; x=sum(np.sin(2*np.pi*f*tt+i) for i,f in enumerate(freqs))/len(freqs); return x*np.minimum(1,tt/1.2)*np.minimum(1,(l-tt)/1.0)
# 0–2: yazma tıkları + yükselen gerilim
for k in range(18): add(click(),.05+k*.05,.35,pan=rng.uniform(-.3,.3))
add(riser(1.0),1.0,.6)
# 2.05: DUR — teyp durması + darbe
add(tapestop(),1.95,.7); add(impact(),2.05,1.0)
# kesme geçişleri
for t in [2.75,4.5,6.0,9.0,11.5,14.5,20.5,23.5]: add(whoosh(),t-.18,.35)
# ritim: 2.75–20.5 kick her vuruşta, hat ara vuruşlarda (6.0'dan sonra)
b=2.75
while b<20.5:
    if not (4.5<=b<6.0) or b%1==0: add(kick(),b,.9)
    if b>=6.0: add(hat(),b+.25,.25,pan=.3)
    b+=.5
# bas çizgisi (D – D – Bb – C)
notes=[73.4,73.4,58.3,65.4]
for i,t in enumerate(np.arange(6.0,20.5,1.0)): add(bass(notes[(i//2)%4],.9),t,.45)
# vurgular
for t in [3.3,8.0,10.3,12.6,17.0]: add(impact(),t,.55)
# onay alarmı
for t in np.arange(17.3,20.4,.5): add(ping(988 if int(t*2)%2 else 740),t,.18)
# 20.5: cevap — sessizlik, sonra üç vuruş
for t in [22.0,22.5,23.0]: add(kick(),t,1.0); add(impact(),t,.4)
# kapanış pedi
add(pad([146.8,220,293.7,370],3.6),23.4,.35); add(kick(),23.5,.8)
for t in np.arange(24.0,26.6,.5): add(hat(),t,.12)
mix=np.stack([L,R],1); mix/=np.max(np.abs(mix))*1.12
fade=np.ones(N); fn=int(.6*SR); fade[-fn:]=np.linspace(1,0,fn); mix*=fade[:,None]
os.makedirs('output',exist_ok=True)
with wave.open('output/audio.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype('<i2').tobytes())
print('output/audio.wav hazır')
