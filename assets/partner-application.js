const form=document.getElementById('partnerForm'),button=document.getElementById('submitButton'),status=document.getElementById('formStatus');
let sending=false;
form.addEventListener('submit',async event=>{
  event.preventDefault();if(sending||!form.reportValidity())return;
  const payload=Object.fromEntries(new FormData(form));payload.consent=document.getElementById('consent').checked;
  for(const key of ['name','email','phone','profile_url','audience_label','message'])payload[key]=String(payload[key]||'').trim();
  sending=true;button.disabled=true;button.textContent='Enviando…';status.textContent='';status.className='status';
  try{
    const response=await fetch('https://api.nofiodobigode.app.br/api/v1/partner-applications',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify(payload)});
    let result={};try{result=await response.json()}catch(_){}
    if(!response.ok)throw new Error(response.status===429?'Muitas tentativas. Aguarde uma hora antes de tentar novamente.':Object.values(result.errors||{}).flat()[0]||'Não foi possível enviar agora. Seus dados continuam no formulário; tente novamente.');
    form.hidden=true;const success=document.getElementById('success');success.hidden=false;success.focus();
  }catch(error){status.textContent=error.message==='Failed to fetch'?'Não foi possível conectar. Confira sua conexão e tente novamente.':error.message;status.className='status error';}
  finally{sending=false;button.disabled=false;button.textContent='Enviar meu interesse';}
});
