import {verifyToken} from './verify.mjs';
const status=document.getElementById('status');
const message=document.getElementById('message');
const details=document.getElementById('details');
const token=new URLSearchParams(location.hash.slice(1)).get('r');
async function run(){
  if(!token){status.textContent='Scan your receipt QR';message.textContent='Open this page using the QR printed on your AALKC receipt.';return;}
  try{
    const response=await fetch('./trusted-keys.json',{cache:'no-store',credentials:'omit'});
    if(!response.ok)throw new Error('Registry unavailable');
    const registry=await response.json();
    if(!Array.isArray(registry.keys))throw new Error('Invalid registry');
    const result=await verifyToken(token,registry.keys);
    if(result.state !== 'verified'){
      status.className='failed';
      status.textContent=result.state==='untrusted'?'Signer not recognized':'Receipt could not be verified';
      message.textContent=result.state==='untrusted'?'This signing key is not registered for this company. Contact AALKC to confirm the receipt.':'The QR is damaged, unsupported, or its signed contents have been changed.';
      return;
    }
    status.className='verified';status.textContent='Receipt signature verified';
    message.textContent='Signed by a registered AALKC key. Check that every detail below matches your receipt.';
    const labels={company:'Company',number:'Receipt number',date:'Receipt date',payee:'Payee',amount:'Amount (SAR)',category:'Category',status:'Status when signed',notes:'Details and explanation',vat:'VAT registration',cr:'Commercial registration'};
    for(const [key,label] of Object.entries(labels)){
      const dt=document.createElement('dt');dt.textContent=label;
      const dd=document.createElement('dd');dd.textContent=result.fields[key] || 'Not recorded';
      details.append(dt,dd);
    }
    details.hidden=false;
  }catch{status.textContent='Verification temporarily unavailable';message.textContent='Please try again later. No receipt has been verified.';}
}
run();
