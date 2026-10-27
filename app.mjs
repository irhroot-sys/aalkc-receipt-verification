import {verifyToken} from './verify.mjs';
const status=document.getElementById('status');
const message=document.getElementById('message');
const details=document.getElementById('details');
let currentRun=0;

const NOUNS={receipt:'Receipt',quotation:'Quotation',voucher:'Payment voucher'};
const COMMON_BEFORE={company:'Company',vat:'VAT registration',cr:'Commercial registration'};
const LABELS={
  receipt:{number:'Receipt number',date:'Receipt date',party:'Paid to',amount:'Amount',category:'Category',status:'Status when signed',notes:'Details and explanation'},
  quotation:{number:'Quotation number',date:'Quotation date',party:'Customer',amount:'Total incl. VAT',validUntil:'Valid until',subject:'Subject',status:'Status when signed'},
  voucher:{number:'Voucher number',date:'Voucher date',party:'Payee',amount:'Amount paid',category:'Category',status:'Status when signed',notes:'Notes'}
};

// Amounts use the official Saudi riyal symbol, never the text "SAR".
function amountValue(amount){
  const dd=document.createElement('dd');
  const symbol=document.createElement('img');
  symbol.src='riyal.svg';symbol.alt='Saudi riyal';symbol.className='riyal';
  const value=Number(amount);
  dd.append(symbol,Number.isFinite(value)?value.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2}):amount);
  return dd;
}

function show(fields,kind){
  for(const [key,label] of Object.entries({...COMMON_BEFORE,...LABELS[kind]})){
    const dt=document.createElement('dt');dt.textContent=label;
    let dd;
    if(key==='amount'){dd=amountValue(fields.amount);}
    else{dd=document.createElement('dd');dd.textContent=fields[key] || 'Not recorded';}
    details.append(dt,dd);
  }
  details.hidden=false;
}

async function run(){
  const runId=++currentRun;
  const token=new URLSearchParams(location.hash.slice(1)).get('r');
  status.className='';
  details.replaceChildren();
  details.hidden=true;
  if(!token){status.textContent='Scan your document QR';message.textContent='Open this page using the QR printed on an AALKC receipt, quotation or payment voucher.';return;}
  status.textContent='Checking document…';
  message.textContent='Verifying the digital signature.';
  try{
    const response=await fetch(`./trusted-keys.json?nonce=${Date.now()}`,{cache:'no-store',credentials:'omit'});
    if(!response.ok)throw new Error('Registry unavailable');
    const registry=await response.json();
    if(!Array.isArray(registry.keys))throw new Error('Invalid registry');
    const result=await verifyToken(token,registry.keys);
    if(runId!==currentRun)return;
    const noun=NOUNS[result.kind] || 'Document';
    if(result.state !== 'verified'){
      status.className='failed';
      status.textContent=result.state==='untrusted'?'Signer not recognized':`${noun} could not be verified`;
      message.textContent=result.state==='untrusted'?'This signing key is not registered for this company. Contact AALKC to confirm the document.':'The QR is damaged, unsupported, or its signed contents have been changed.';
      return;
    }
    status.className='verified';status.textContent=`${noun} signature verified`;
    message.textContent='Signed by a registered AALKC key. Check that every detail below matches the printed document.';
    show(result.fields,result.kind);
  }catch{if(runId!==currentRun)return;status.textContent='Verification temporarily unavailable';message.textContent='Please try again later. No document has been verified.';}
}
window.addEventListener('hashchange',run);
run();
