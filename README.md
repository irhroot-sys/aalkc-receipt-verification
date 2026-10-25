# verify.aalkc.com

## Production hosting — 25 October 2026

Production URL: https://verify.aalkc.com/  
GitHub source: https://github.com/irhroot-sys/aalkc-receipt-verification  
Cloudflare Worker: `aalkc-receipt-verify` (custom domain `verify.aalkc.com`, `aalkc.com` zone).

Cloudflare serves a **bundled copy** of the audited GitHub source. Cloudflare manages DNS for this hostname using a proxied `AAAA` record with the Worker custom domain. Do not replace it with a GitHub Pages CNAME while the Worker is attached. The standalone GitHub Pages site is not the production HTTPS endpoint.

**To publish a source or trust-registry update:** run `node --test verify.test.mjs`, `node scripts/build-worker.mjs`, and `node --check dist/worker.js`, then redeploy `dist/worker.js` to the Cloudflare Worker. Pushing to GitHub alone will NOT update the live Worker.

**Signing key registration:** unlock the AALKC macOS app vault, open Receipt QR Verification, choose **Copy Public Signing Key**, independently match the public key to the intended production signer and exact `company`, `vat`, and `cr` values used by Swift, then populate `trusted-keys.json`. The initial empty registry is fail-closed: no signer is trusted until registered. Never publish the private key.

---

Static HTTPS receipt verifier. The public hostname is routed to the Cloudflare Worker described above; GitHub stores the versioned source. No backend, analytics, external scripts or private signing keys are required.

## Before publishing

Populate `trusted-keys.json` with the real public signing key from the unlocked Aalkc installation and its approved company identity:

```json
{"keys":[{"publicKey":"BASE64_CRYPTOKIT_RAW_PUBLIC_KEY","company":"EXACT_COMPANY_NAME","vat":"EXACT_VAT_OR_EMPTY","cr":"EXACT_CR_OR_EMPTY","enabled":true}]}
```

Independently confirm the public key belongs to the company. Never register a key merely because a receipt contains it. The empty registry deliberately verifies no issuer. Private keys remain in the app vault. Disable a compromised key with `enabled:false`; keep old approved keys if historical receipts should remain verifiable.

The QR opens `https://verify.aalkc.com/#r=TOKEN`. The fragment is not sent to the web server. It contains the receipt details, digest, public key and signature, so anyone with the QR can read those details. Browser verification confirms an issued snapshot, not current payment/revocation status. Users must compare the displayed details with the printed document.

Protocol v2: base64url-encoded JSON envelope, with `version:2` and standard-base64 `payload`, `digest`, `signature`, `publicKey`. SHA-256 hashes the exact payload bytes. P-256/SHA-256 signs UTF-8 `AALKC-RECEIPT-SIGNATURE-V2\n` followed by the 32-byte digest. CryptoKit uses 64-byte X||Y public keys and 64-byte r||s signatures; WebCrypto adds the SEC1 04 prefix when importing the key. Never reserialize the payload before hashing it.

Serve over HTTPS with `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, and `Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'`. Do not cache the trust registry.

Run verification checks with `node --test verify.test.mjs`.
