# AALKC × HMS — Premium Business Documents

Executive-grade redesign of the seven Arabic business documents pack.

## Letterhead assignment (matches source PDF)

| Document | ID | Letterhead |
|----------|----|------------|
| Framework agreement | AALKC-HMS-FW-2026-001 | AALKC |
| Employee assignment annex | AALKC-HMS-EA-2026-001 | HMS |
| Administrative decision | AALKC-HMS-DEC-2026-001 | AALKC |
| HMS authorization | HMS-AUTH-2026-001 | HMS |
| Employment certificate | AALKC-EMP-2026-001 | AALKC |
| Work plan | AALKC-HMS-WP-2026-001 | HMS |
| Cost schedule | AALKC-HMS-COST-2026-001 | AALKC |

Letterhead assets are exact extracts from the source PDF (`assets/letterhead_aalkc.jpg`, `assets/letterhead_hms.jpg`). Safe content margins avoid header/footer overlap.

## Rebuild

```bash
python3 build_premium_pdf.py
```

Requires Google Chrome (headless) and fonts: Noto Naskh Arabic, Noto Kufi Arabic, Carlito/Liberation Sans.
