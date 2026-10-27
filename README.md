# verify.aalkc.com

Static verifier for AALKC **receipts, quotations and payment vouchers** signed by the Aalkc macOS app. Tax invoices and tax credit notes never carry this QR; they carry only the ZATCA Phase 1 QR. The app stays offline: it signs on the Mac, and checking happens in the visitor's browser.

The page source, tests and protocol notes live in the Aalkc app repository (`ReceiptVerificationWebsite/`). `script/publish_verify_site.sh /path/to/this/checkout` copies them here, runs the tests, builds the Worker and smoke-tests it.

## Production hosting

Production URL: https://verify.aalkc.com/  
Cloudflare Worker: `aalkc-receipt-verify` (custom domain `verify.aalkc.com`, `aalkc.com` zone).

Cloudflare serves a **bundled copy** of this repository (`dist/worker.js`) with the security headers in `scripts/build-worker.mjs`. Cloudflare manages DNS for this hostname with a proxied record for the Worker custom domain. Do not replace it with a GitHub Pages CNAME while the Worker is attached.

**To publish an update:** `node --test verify.test.mjs`, `node scripts/build-worker.mjs`, `node --check dist/worker.js`, then redeploy `dist/worker.js` to the Worker (`wrangler deploy dist/worker.js --name aalkc-receipt-verify`, or Cloudflare dashboard › Workers › aalkc-receipt-verify › Edit code › paste › Deploy). Pushing to GitHub alone does NOT update the live site.

## Trusted signing keys

1. In Aalkc: **Settings › Security › Export verification key…**. This saves `trusted-keys.json` with this Mac's public key once per company, using the exact `company`, `vat` and `cr` values the documents carry.
2. Replace `trusted-keys.json` here with it, rebuild and redeploy.

The committed registry may be empty; then no signer is trusted (fail closed). Only register a key you exported from your own Aalkc. Never register a key just because a document contains it, and never publish a private key. Disable a compromised key with `enabled:false`. Keep old keys if documents printed with them should still verify.

## Protocol

The QR opens `https://verify.aalkc.com/#r=TOKEN`. The fragment is not sent to the server, but anyone holding the QR can read the signed details, just as they can read the paper. Verification confirms the signed snapshot, not current payment or revocation status.

Base64url JSON envelope `{version, payload, digest, signature, publicKey}` (inner values standard base64). SHA-256 hashes the exact `payload` bytes (never reserialise). P-256/SHA-256 signs the UTF-8 domain string followed by the 32-byte digest. CryptoKit public keys are 64-byte X||Y; WebCrypto adds the SEC1 `04` prefix.

- **v3 (current):** domain `AALKC-DOCUMENT-SIGNATURE-V3\n`; payload strings `kind` (`receipt` | `quotation` | `voucher`), `company`, `vat`, `cr`, `number`, `date`, `party`, `amount`, `currency` (`SAR`), plus receipt `category` `status` `notes`; quotation `validUntil` `status` `subject`; voucher `category` `status` `notes`.
- **v2 (receipts printed before v3):** domain `AALKC-RECEIPT-SIGNATURE-V2\n`, receipt fields with `payee`. Still accepted.

## Tests

`node --test verify.test.mjs`. `fixtures/app-signed-v3.json` holds tokens signed by the Aalkc app itself, so the browser verifier is checked against real CryptoKit output.
