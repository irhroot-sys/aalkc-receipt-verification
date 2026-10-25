const encoder = new TextEncoder();
const decoder = new TextDecoder('utf-8', {fatal:true});
export function decode64(value) {
  if (typeof value !== 'string' || value.length > 4096) throw new Error('Invalid encoding');
  return Uint8Array.from(atob(value.replace(/-/g,'+').replace(/_/g,'/')), c=>c.charCodeAt(0));
}
const same = (a,b)=>a.length === b.length && a.every((v,i)=>v===b[i]);
export async function verifyToken(token, trustedKeys, subtle=globalThis.crypto.subtle) {
  try {
    if (typeof token !== 'string' || token.length > 4096) return {state:'invalid'};
    const envelope = JSON.parse(decoder.decode(decode64(token)));
    if (envelope.version !== 2) return {state:'invalid'};
    const payload = decode64(envelope.payload);
    const digest = decode64(envelope.digest);
    const signature = decode64(envelope.signature);
    const publicKey = decode64(envelope.publicKey);
    if (digest.length !== 32 || signature.length !== 64 || publicKey.length !== 64) return {state:'invalid'};
    if (!same(new Uint8Array(await subtle.digest('SHA-256',payload)),digest)) return {state:'invalid'};
    // CryptoKit rawRepresentation is X || Y; WebCrypto expects SEC1 04 || X || Y.
    const key = await subtle.importKey('raw',new Uint8Array([4,...publicKey]),{name:'ECDSA',namedCurve:'P-256'},false,['verify']);
    const message = new Uint8Array([...encoder.encode('AALKC-RECEIPT-SIGNATURE-V2\n'),...digest]);
    if (!await subtle.verify({name:'ECDSA',hash:'SHA-256'},key,signature,message)) return {state:'invalid'};
    const fields = JSON.parse(decoder.decode(payload));
    const required=['company','vat','cr','number','date','payee','amount','currency','category','status','notes'];
    if (!fields || required.some(k=>typeof fields[k] !== 'string') || fields.currency !== 'SAR') return {state:'invalid'};
    // Trust comes only from the separately deployed registry, never from the QR.
    const trusted = trustedKeys.find(k=>k.publicKey === envelope.publicKey && k.enabled === true
      && k.company === fields.company && k.vat === fields.vat && k.cr === fields.cr);
    if (!trusted) return {state:'untrusted'};
    return {state:'verified',fields};
  } catch { return {state:'invalid'}; }
}
