import {test} from 'node:test';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
import {verifyToken} from './verify.mjs';
const subtle=webcrypto.subtle;
const b64=b=>Buffer.from(b).toString('base64');
const token=e=>Buffer.from(JSON.stringify(e)).toString('base64url');
async function fixture(){
  const fields={company:'AALKC Sample',vat:'',cr:'',number:'REC-1',date:'2026-10-25',payee:'Sample Payee',amount:'1000',currency:'SAR',category:'Advance',status:'Pending',notes:'Full explanation'};
  const payload=Buffer.from(JSON.stringify(fields));
  const digest=new Uint8Array(await subtle.digest('SHA-256',payload));
  const keys=await subtle.generateKey({name:'ECDSA',namedCurve:'P-256'},true,['sign','verify']);
  const raw=new Uint8Array(await subtle.exportKey('raw',keys.publicKey)).slice(1);
  const signature=await subtle.sign({name:'ECDSA',hash:'SHA-256'},keys.privateKey,Buffer.concat([Buffer.from('AALKC-RECEIPT-SIGNATURE-V2\n'),digest]));
  const envelope={version:2,payload:b64(payload),digest:b64(digest),signature:b64(signature),publicKey:b64(raw)};
  const trusted=[{publicKey:envelope.publicKey,company:fields.company,vat:'',cr:'',enabled:true}];
  return {envelope,trusted,fields};
}
test('trusted signature returns exact signed receipt details',async()=>{const f=await fixture();assert.deepEqual(await verifyToken(token(f.envelope),f.trusted,subtle),{state:'verified',fields:f.fields});});
test('changed receipt payload fails',async()=>{const f=await fixture();f.envelope.payload=b64(Buffer.from(JSON.stringify({...f.fields,amount:'9999'})));assert.equal((await verifyToken(token(f.envelope),f.trusted,subtle)).state,'invalid');});
test('altered signature fails',async()=>{const f=await fixture();f.envelope.signature=b64(Buffer.alloc(64));assert.equal((await verifyToken(token(f.envelope),f.trusted,subtle)).state,'invalid');});
test('unregistered signer never verifies',async()=>{const f=await fixture();assert.equal((await verifyToken(token(f.envelope),[],subtle)).state,'untrusted');});
test('revoked key never verifies',async()=>{const f=await fixture();f.trusted[0].enabled=false;assert.equal((await verifyToken(token(f.envelope),f.trusted,subtle)).state,'untrusted');});
test('key approved for another company never verifies',async()=>{const f=await fixture();f.trusted[0].company='Other';assert.equal((await verifyToken(token(f.envelope),f.trusted,subtle)).state,'untrusted');});
test('malformed and oversized input fail',async()=>{for(const value of ['bad','x'.repeat(5000),token({version:9})])assert.equal((await verifyToken(value,[],subtle)).state,'invalid');});
