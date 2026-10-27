import {test} from 'node:test';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
import {readFileSync, existsSync} from 'node:fs';
import {verifyToken} from './verify.mjs';
const subtle=webcrypto.subtle;
const b64=b=>Buffer.from(b).toString('base64');
const token=e=>Buffer.from(JSON.stringify(e)).toString('base64url');
const DOMAIN={2:'AALKC-RECEIPT-SIGNATURE-V2\n',3:'AALKC-DOCUMENT-SIGNATURE-V3\n'};

async function signed(fields,version,domainVersion=version){
  const payload=Buffer.from(JSON.stringify(fields));
  const digest=new Uint8Array(await subtle.digest('SHA-256',payload));
  const keys=await subtle.generateKey({name:'ECDSA',namedCurve:'P-256'},true,['sign','verify']);
  const raw=new Uint8Array(await subtle.exportKey('raw',keys.publicKey)).slice(1);
  const signature=await subtle.sign({name:'ECDSA',hash:'SHA-256'},keys.privateKey,Buffer.concat([Buffer.from(DOMAIN[domainVersion]),digest]));
  const envelope={version,payload:b64(payload),digest:b64(digest),signature:b64(signature),publicKey:b64(raw)};
  const trusted=[{publicKey:envelope.publicKey,company:fields.company,vat:fields.vat,cr:fields.cr,enabled:true}];
  return {envelope,trusted,fields};
}
const company={company:'AALKC Sample',vat:'312345678900003',cr:'7050308233',currency:'SAR'};
const v2Fields={...company,number:'REC-1',date:'2026-10-25',payee:'Sample Payee',amount:'1000',category:'Advance',status:'Pending',notes:'Full explanation'};
const v3={
  receipt:{...company,kind:'receipt',number:'REC-2',date:'2026-10-27',party:'Sample Payee',amount:'250.5',category:'Advance',status:'Paid',notes:'Explanation'},
  quotation:{...company,kind:'quotation',number:'QUO-7',date:'2026-10-27',party:'Energia',amount:'11500',validUntil:'2026-11-26',status:'Sent',subject:'Supply of panels'},
  voucher:{...company,kind:'voucher',number:'EXP-3',date:'2026-10-27',party:'Fuel Station',amount:'80',category:'Fuel',status:'Paid',notes:''}
};

// v2 receipts printed before v3 keep verifying.
test('v2 receipt verifies and is shown as a receipt',async()=>{const f=await signed(v2Fields,2);assert.deepEqual(await verifyToken(token(f.envelope),f.trusted,subtle),{state:'verified',kind:'receipt',fields:{...v2Fields,kind:'receipt',party:'Sample Payee'}});});
test('changed v2 payload fails',async()=>{const f=await signed(v2Fields,2);f.envelope.payload=b64(Buffer.from(JSON.stringify({...v2Fields,amount:'9999'})));assert.equal((await verifyToken(token(f.envelope),f.trusted,subtle)).state,'invalid');});

for(const kind of Object.keys(v3)){
  test(`v3 ${kind} verifies with its kind and exact fields`,async()=>{const f=await signed(v3[kind],3);assert.deepEqual(await verifyToken(token(f.envelope),f.trusted,subtle),{state:'verified',kind,fields:v3[kind]});});
}
test('v3 payload with a changed kind fails',async()=>{const f=await signed(v3.quotation,3);f.envelope.payload=b64(Buffer.from(JSON.stringify({...v3.quotation,kind:'receipt'})));assert.equal((await verifyToken(token(f.envelope),f.trusted,subtle)).state,'invalid');});
test('v3 unknown kind is invalid even when signed',async()=>{const f=await signed({...v3.receipt,kind:'invoice'},3);assert.equal((await verifyToken(token(f.envelope),f.trusted,subtle)).state,'invalid');});
test('v3 missing kind field is invalid',async()=>{const {validUntil,...rest}=v3.quotation;const f=await signed(rest,3);assert.equal((await verifyToken(token(f.envelope),f.trusted,subtle)).state,'invalid');});
test('a v2 signature presented as v3 fails',async()=>{const f=await signed(v3.receipt,3,2);assert.equal((await verifyToken(token(f.envelope),f.trusted,subtle)).state,'invalid');});
test('altered signature fails',async()=>{const f=await signed(v3.receipt,3);f.envelope.signature=b64(Buffer.alloc(64));assert.equal((await verifyToken(token(f.envelope),f.trusted,subtle)).state,'invalid');});
test('unregistered signer never verifies',async()=>{const f=await signed(v3.voucher,3);assert.equal((await verifyToken(token(f.envelope),[],subtle)).state,'untrusted');});
test('revoked key never verifies',async()=>{const f=await signed(v3.voucher,3);f.trusted[0].enabled=false;assert.equal((await verifyToken(token(f.envelope),f.trusted,subtle)).state,'untrusted');});
test('key approved for another company never verifies',async()=>{const f=await signed(v3.receipt,3);f.trusted[0].company='Other';assert.equal((await verifyToken(token(f.envelope),f.trusted,subtle)).state,'untrusted');});
test('malformed and oversized input fail',async()=>{for(const value of ['bad','x'.repeat(5000),token({version:9})])assert.equal((await verifyToken(value,[],subtle)).state,'invalid');});

// A token signed by the Aalkc app (Swift/CryptoKit), so both sides agree on bytes.
const fixturePath=new URL('./fixtures/app-signed-v3.json',import.meta.url);
test('app-signed v3 tokens verify in the browser verifier',{skip:!existsSync(fixturePath)},async()=>{
  const fixture=JSON.parse(readFileSync(fixturePath,'utf8'));
  for(const item of fixture.tokens){
    const result=await verifyToken(item.token,[{...fixture.trustedKey,enabled:true}],subtle);
    assert.equal(result.state,'verified',item.kind);
    assert.equal(result.kind,item.kind);
    assert.deepEqual(result.fields,item.fields);
  }
});
