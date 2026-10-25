# verify.aalkc.com

Static HTTPS receipt verifier. Deploy this directory as the site root and connect `verify.aalkc.com` using the hosting provider's DNS instructions. No backend, analytics, external scripts or private signing keys are required.

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
