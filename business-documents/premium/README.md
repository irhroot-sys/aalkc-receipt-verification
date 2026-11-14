# AALKC × HMS — Premium Business Documents

Premium redesign of the seven Arabic business documents pack, printed on the **original AALKC letterhead** (header, watermark, and footer unchanged).

## Output

- `AALKC_HMS_7_Business_Documents_Premium_Arabic.pdf` — final 13-page A4 pack

## Rebuild

```bash
python3 build_premium_pdf.py
```

Requires Google Chrome (headless) and system fonts: Noto Naskh Arabic, Noto Kufi Arabic, Carlito/Liberation Sans.

## Design notes

- Letterhead asset: `assets/letterhead.jpg` (exact background from the source PDF)
- Body: navy/gold accent system aligned to AALKC brand colors
- RTL Arabic typography with cleaned punctuation and refined tables / signature blocks
