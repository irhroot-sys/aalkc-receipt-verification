const encoder = new TextEncoder();
const decoder = new TextDecoder('utf-8', {fatal:true});

// Signing domains: v2 signed receipts only; v3 signs receipts, quotations and vouchers.
const DOMAINS = {2:'AALKC-RECEIPT-SIGNATURE-V2\n', 3:'AALKC-DOCUMENT-SIGNATURE-V3\n'};
const V2_FIELDS = ['company','vat','cr','number','date','payee','amount','currency','category','status','notes'];
const V3_COMMON = ['kind','company','vat','cr','number','date','party','amount','currency'];
export const KIND_FIELDS = {
  receipt:['category','status','notes'],
  quotation:['validUntil','status','subject'],
  voucher:['category','status','notes']
};

export function decode64(value) {
  if (typeof value !== 'string' || value.length > 4096) throw new Error('Invalid encoding');
  return Uint8Array.from(atob(value.replace(/-/g,'+').replace(/_/g,'/')), c=>c.charCodeAt(0));
}
const same = (a,b)=>a.length === b.length && a.every((v,i)=>v===b[i]);
const allStrings = (fields, keys)=>keys.every(k=>typeof fields[k] === 'string');

/// The signed fields in one shape for every version: v2 receipts gain
/// kind 'receipt' and 'party' (their payee).
function normalizedFields(version, fields) {
  if (!fields || typeof fields !== 'object' || fields.currency !== 'SAR') return null;
  if (version === 2) {
    if (!allStrings(fields, V2_FIELDS)) return null;
    return {...fields, kind:'receipt', party:fields.payee};
  }
  if (!allStrings(fields, V3_COMMON) || !Object.hasOwn(KIND_FIELDS, fields.kind)) return null;
  return allStrings(fields, KIND_FIELDS[fields.kind]) ? fields : null;
}

export async function verifyToken(token, trustedKeys, subtle=globalThis.crypto.subtle) {
  try {
    if (typeof token !== 'string' || token.length > 4096) return {state:'invalid'};
    const envelope = JSON.parse(decoder.decode(decode64(token)));
    const domain = DOMAINS[envelope.version];
    if (!domain) return {state:'invalid'};
    const payload = decode64(envelope.payload);
    const digest = decode64(envelope.digest);
    const signature = decode64(envelope.signature);
    const publicKey = decode64(envelope.publicKey);
    if (digest.length !== 32 || signature.length !== 64 || publicKey.length !== 64) return {state:'invalid'};
    // The exact signed bytes are hashed; the payload is never re-serialised.
    if (!same(new Uint8Array(await subtle.digest('SHA-256',payload)),digest)) return {state:'invalid'};
    // CryptoKit rawRepresentation is X || Y; WebCrypto expects SEC1 04 || X || Y.
    const key = await subtle.importKey('raw',new Uint8Array([4,...publicKey]),{name:'ECDSA',namedCurve:'P-256'},false,['verify']);
    const message = new Uint8Array([...encoder.encode(domain),...digest]);
    if (!await subtle.verify({name:'ECDSA',hash:'SHA-256'},key,signature,message)) return {state:'invalid'};
    const fields = normalizedFields(envelope.version, JSON.parse(decoder.decode(payload)));
    if (!fields) return {state:'invalid'};
    // Trust comes only from the separately deployed registry, never from the QR.
    const trusted = trustedKeys.find(k=>k.publicKey === envelope.publicKey && k.enabled === true
      && k.company === fields.company && k.vat === fields.vat && k.cr === fields.cr);
    if (!trusted) return {state:'untrusted', kind:fields.kind};
    return {state:'verified', kind:fields.kind, fields};
  } catch { return {state:'invalid'}; }
}
