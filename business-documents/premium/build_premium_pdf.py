#!/usr/bin/env python3
"""Build an executive-grade AALKC × HMS Arabic business-document PDF.

Uses each document's exact original letterhead:
  - AALKC letterhead → FW, DEC, EMP, COST
  - HMS letterhead   → EA, AUTH, WP
"""

from __future__ import annotations

import base64
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUT_HTML = ROOT / "premium_documents.html"
OUT_PDF = ROOT / "AALKC_HMS_7_Business_Documents_Premium_Arabic.pdf"
ARTIFACT = Path("/opt/cursor/artifacts/AALKC_HMS_7_Business_Documents_Premium_Arabic.pdf")

# Brand tokens
AALKC = {
    "primary": "#0E335D",
    "primary_soft": "#1A4A78",
    "slate": "#3A4B5C",
    "muted": "#6B7C8F",
    "rule": "#D5DEE8",
    "accent": "#A8895A",
    "tint": "rgba(14, 51, 93, 0.035)",
    "panel": "linear-gradient(180deg, rgba(14,51,93,0.045), rgba(14,51,93,0.015))",
}
HMS = {
    "primary": "#0081A9",
    "primary_soft": "#0A6F92",
    "slate": "#2F3A42",
    "muted": "#5F6E78",
    "rule": "#D2DEE4",
    "accent": "#4A5560",
    "tint": "rgba(0, 129, 169, 0.04)",
    "panel": "linear-gradient(180deg, rgba(0,129,169,0.05), rgba(0,129,169,0.012))",
}


def data_uri(path: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


LH_AALKC = data_uri(ASSETS / "letterhead_aalkc.jpg")
LH_HMS = data_uri(ASSETS / "letterhead_hms.jpg")


def _is_arabic_heavy(text: str) -> bool:
    arabic = sum(1 for ch in text if "\u0600" <= ch <= "\u06FF")
    return arabic >= max(1, len(text) // 5)


def meta_row(label: str, value: str) -> str:
    # DOM order: label then value. With direction:rtl, label sits on the right.
    return f"""
    <div class="meta-row">
      <span class="meta-label">{label}</span>
      <span class="meta-value" dir="ltr">{value}</span>
    </div>"""


def kv_table(rows: list[tuple[str, str]]) -> str:
    cells = []
    for label, value in rows:
        if _is_arabic_heavy(value):
            value_html = f'<div class="kv-value kv-ar">{value}</div>'
        else:
            value_html = (
                f'<div class="kv-value kv-en"><span dir="ltr">{value}</span></div>'
            )
        cells.append(
            f"""
      <div class="kv-row">
        <div class="kv-label">{label}</div>
        {value_html}
      </div>"""
        )
    return f'<div class="kv-table">{"".join(cells)}</div>'


def article(title: str, body_html: str) -> str:
    return f"""
    <section class="article">
      <h2 class="article-title"><span>{title}</span></h2>
      <div class="article-body">{body_html}</div>
    </section>"""


def bullets(items: list[str]) -> str:
    lis = "".join(f"<li>{item}</li>" for item in items)
    return f'<ul class="premium-list">{lis}</ul>'


def sig_block(parties: list[tuple[str, str, str | None]]) -> str:
    cards = []
    for role, name_ar, name_en in parties:
        en = f'<div class="sig-en" dir="ltr">{name_en}</div>' if name_en else ""
        cards.append(
            f"""
      <div class="sig-card">
        <div class="sig-role">{role}</div>
        <div class="sig-line"></div>
        <div class="sig-name">{name_ar}</div>
        {en}
      </div>"""
        )
    cls = "sig-grid single" if len(parties) == 1 else "sig-grid"
    return f'<div class="{cls}">{"".join(cards)}</div>'


def page(inner: str, brand: str, dense: bool = False) -> str:
    extra = " dense" if dense else ""
    return f'<article class="page brand-{brand}{extra}">{inner}</article>'


def doc_header(title: str, metas: list[tuple[str, str]]) -> str:
    meta_html = "".join(meta_row(l, v) for l, v in metas)
    return f"""
    <header class="doc-header">
      <h1 class="doc-title">{title}</h1>
      <div class="meta-panel">{meta_html}</div>
    </header>"""


def lead(text: str) -> str:
    return f'<p class="lead">{text}</p>'


def p(text: str) -> str:
    return f"<p>{text}</p>"


def note(text: str) -> str:
    return f'<p class="note">{text}</p>'


def section_label(text: str) -> str:
    return f'<div class="section-kicker">{text}</div>'


# ── Content (refined formal Arabic; meaning preserved) ──────────────────────

PAGES: list[str] = []

# 1 — Framework (AALKC letterhead)
PAGES.append(
    page(
        doc_header(
            "اتفاقية إطارية للتعاون اللوجستي بين شركتي أمانة الكلمة وإتش إم إس",
            [
                ("رقم المستند", "AALKC-HMS-FW-2026-001"),
                ("تاريخ التحرير", "14/11/2026"),
            ],
        )
        + lead(
            "أُبرمت هذه الاتفاقية لتنظيم التعاون التشغيلي في استلام البضائع وإرسالها ومتابعة مستندات النقل والتسليم بين الطرفين، وتحديد آلية تكليف موظف من شركة أمانة الكلمة بالتنسيق مع شركة إتش إم إس."
        )
        + article(
            "المادة الأولى: أطراف الاتفاقية",
            p(
                "الطرف الأول: شركة أمانة الكلمة، شركة ذات مسؤولية محدودة مسجلة في المملكة العربية السعودية، ومقرها الرئيس في الدمام، ويُشار إليها فيما يلي بـ«الشركة الأصلية»."
            )
            + p(
                "الطرف الثاني: شركة إتش إم إس هيفي ميتال المحدودة، شركة مسجلة في جمهورية بنغلاديش الشعبية، ويُشار إليها فيما يلي بـ«الشركة المستضيفة»."
            )
            + kv_table(
                [
                    ("شركة الطرف الأول", "Amanat Al-Kalima Company (AALKC)"),
                    ("الرقم الوطني الموحد", "7050308233"),
                    ("شركة الطرف الثاني", "HMS Heavy Metal Limited"),
                    ("رقم تأسيس الطرف الثاني", "C-199823/2022"),
                    (
                        "عنوان HMS الحالي",
                        "109, Dinonath Sen Road, Gandaria, Dhaka 1204, Bangladesh",
                    ),
                    (
                        "عنوان HMS السابق",
                        "House-110, Road No. 03, Adabor, Baitul Aman Housing, Dhaka-1207, Bangladesh",
                    ),
                ]
            )
            + note(
                "يُعتمد العنوان الحالي للمراسلات التشغيلية وفق بيانات الشركة المستضيفة. ويُذكر العنوان السابق لأغراض السجل التاريخي للمراسلات فحسب."
            ),
        )
        + article(
            "المادة الثانية: نطاق التعاون",
            p(
                "يتعاون الطرفان في تنسيق استلام وإرسال البضائع لحساب شركة أمانة الكلمة، ومراجعة بيانات الشحن والتسليم والكميات والحالة الظاهرة للبضائع، ومتابعة الجهات الناقلة والمستلمة، وذلك في حدود العمليات المعتمدة من إدارة أمانة الكلمة."
            ),
        ),
        "aalkc",
    )
)

# 2 — Framework continued (AALKC)
PAGES.append(
    page(
        p(
            "لا تنشئ هذه الاتفاقية بذاتها بيعًا أو شراءً أو نقل ملكية أو عمولة أو التزامًا ماليًا جديدًا على أي من الطرفين، ويُنظَّم كل معاملة تجارية مستقلة بمستنداتها المعتمدة."
        )
        + article(
            "المادة الثالثة: التكليف الوظيفي والمواقع",
            p(
                "يجوز تكليف موظف تابع لشركة أمانة الكلمة بتنفيذ مهام التنسيق والاستلام والإرسال وفق ملحق فردي مستقل. ويظل مقر عمله الأصلي في المنطقة الصناعية بالدمام، مع تكليفه — عند الحاجة — بزيارات عمل إلى بنغلاديش للتنسيق الميداني مع شركة إتش إم إس."
            )
            + p(
                "تُحدَّد مواقع الاستلام والإرسال الفعلية لكل مهمة بموجب خطة عمل مستقلة، ولا يُفترض أن عنوان مراسلات الشركة المستضيفة هو موقع المستودع أو التسليم."
            ),
        )
        + article(
            "المادة الرابعة: توزيع المسؤوليات",
            bullets(
                [
                    "تصدر أمانة الكلمة أوامر حركة بضائعها، وتعتمد التكاليف ونتائج المطابقة والقبول النهائي.",
                    "تنسق إتش إم إس استقبال الموظف والوصول إلى المواقع المتاحة ضمن أعمالها، وتوثق الوقائع الميدانية التي تقع في نطاقها.",
                    "يرفع الموظف تقارير الاستلام والإرسال والملاحظات والفروق، دون أن يملك إبرام عقود بيع أو شراء أو نقل ملكية البضائع أو إجراء مدفوعات إلا بتفويض مستقل.",
                ]
            ),
        )
        + article(
            "المادة الخامسة: الإشراف والاتصالات",
            p(
                "يكون السيد هيميل حسن ممثل إتش إم إس المعني باستقبال الموظف والتنسيق التشغيلي وفق قرار التفويض الصادر عن الشركة. وتبقى إدارة العلاقة الوظيفية الأصلية والرواتب والإجازات وإجراءات صاحب العمل لدى أمانة الكلمة."
            ),
        )
        + article(
            "المادة السادسة: التكاليف والسجلات",
            p(
                "تتحمل أمانة الكلمة المصروفات المعتمدة المرتبطة بالتكليف وفق جدول المسؤوليات المالية الملحق. ويحتفظ كل طرف بسجلاته وموافقاته ومستندات المراسلات والشحن ذات الصلة."
            ),
        )
        + article(
            "المادة السابعة: مدة الاتفاقية وإنهاؤها",
            p(
                "تسري الاتفاقية من تاريخ اعتمادها من الطرفين، وتستمر حتى إنهائها باتفاق مكتوب أو بإشعار سابق مدته ستون (60) يومًا. وتُحدَّد مدة تكليف الموظف على حدة في ملحقه الفردي، ويكون أي تمديد لها مكتوبًا."
            ),
        ),
        "aalkc",
    )
)

# 3 — Framework closing (AALKC)
PAGES.append(
    page(
        article(
            "المادة الثامنة: السرية وحدود التفويض",
            p(
                "يحافظ الطرفان على سرية معلومات العمليات والأسعار والموردين والمستندات الداخلية. ولا يجوز لأي طرف إلزام الآخر ماليًا أو تعاقديًا إلا بموافقة صريحة مستقلة من الجهة المخوَّلة."
            ),
        )
        + article(
            "المادة التاسعة: القانون وتسوية المنازعات",
            p(
                "تخضع العلاقة التعاقدية بين الشركتين لأحكام الأنظمة المعمول بها في المملكة العربية السعودية، وتكون المحاكم المختصة في الدمام جهة الفصل في المنازعات التعاقدية بين الطرفين، مع مراعاة الأحكام الآمرة الواجبة التطبيق على الأعمال التي تُنفَّذ في بنغلاديش."
            ),
        )
        + article(
            "المادة العاشرة: الوثائق المرتبطة",
            p(
                "يُعد ملحق تكليف الموظف وخطة العمل وجدول المسؤوليات المالية مستندات تنفيذية مكملة لهذه الاتفاقية، ولا يُعدّل أي منها شروطها العامة إلا باتفاق صريح من الطرفين."
            )
            + kv_table(
                [
                    ("ملحق تكليف الموظف", "AALKC-HMS-EA-2026-001"),
                    ("خطة العمل", "AALKC-HMS-WP-2026-001"),
                    ("جدول التكاليف", "AALKC-HMS-COST-2026-001"),
                ]
            ),
        )
        + section_label("الاعتماد والنفاذ")
        + p(
            "يصبح هذا المستند نافذًا بعد اعتماده من ممثلي الشركتين المخوَّلين وفق صلاحيات كل منهما، ويُعتد بتاريخ الاعتماد الأخير."
        )
        + sig_block(
            [
                (
                    "عن شركة أمانة الكلمة",
                    "شهيد الإسلام عبد الرزاق",
                    "Shahidul Islam Abdur Razzak",
                ),
                ("عن شركة إتش إم إس", "هيميل حسن", "Himel Hasan"),
            ]
        ),
        "aalkc",
    )
)

# 4 — Employee assignment (HMS letterhead)
PAGES.append(
    page(
        doc_header(
            "اتفاقية تكليف موظف وتنسيق استقباله لدى الشركة المستضيفة",
            [
                ("رقم المستند", "AALKC-HMS-EA-2026-001"),
                ("تاريخ التحرير", "14/11/2026"),
                ("الاتفاقية الإطارية", "AALKC-HMS-FW-2026-001"),
            ],
        )
        + lead(
            "تتفق شركة أمانة الكلمة وشركة إتش إم إس على تنظيم المهام المحددة للموظف المبين أدناه وفق الاتفاقية الإطارية بينهما، وبما يحافظ على علاقة العمل الأصلية مع أمانة الكلمة."
        )
        + article(
            "أولاً: بيانات الموظف",
            kv_table(
                [
                    ("الاسم بالعربية", "سالم بن جمل بن جمعان العماري الدوسري"),
                    ("الاسم بالإنجليزية", "ALDOSSARI, SALEM JAMAL J"),
                    ("الجنسية", "سعودي"),
                    ("رقم الهوية الوطنية", "1007982216"),
                    ("تاريخ انتهاء الهوية", "30/12/2033"),
                    ("تاريخ الالتحاق", "01/11/2025"),
                    (
                        "مسمى التكليف",
                        "منسق استلام وإرسال البضائع والتنسيق اللوجستي الدولي",
                    ),
                ]
            )
            + note(
                "تاريخ الالتحاق مذكور بحسب إفادة إدارة أمانة الكلمة. والمسمى المبين أعلاه خاص بهذا التكليف، ولا يُفترض أنه يحل محل المسمى المسجل في عقد العمل الأصلي."
            ),
        )
        + article(
            "ثانيًا: المسؤوليات",
            p(
                "يتولى الموظف — لحساب أمانة الكلمة — متابعة استلام البضائع وإرسالها، ومطابقة أوصافها وكمياتها وحالتها الظاهرة مع المستندات المعتمدة، والتنسيق مع الناقلين وجهات التسليم والاستلام، وإعداد محاضر المتابعة التشغيلية ورفع التقارير إلى إدارة أمانة الكلمة."
            ),
        ),
        "hms",
    )
)

# 5 — Assignment continued (HMS)
PAGES.append(
    page(
        p(
            "تقبل إتش إم إس تنظيم المتابعة الميدانية المرتبطة بعملياتها في بنغلاديش عند وجود مهام تعتمدها الشركتان، وتنسق استقبال الموظف وربطه بالجهات المختصة في تلك العمليات."
        )
        + article(
            "ثالثًا: الموقع وآلية الزيارات",
            p(
                "مقر العمل الأصلي للموظف هو المنطقة الصناعية بالدمام. ويشمل التكليف زيارات عمل متكررة إلى بنغلاديش بحسب العمليات الفعلية وخطط الزيارة المعتمدة. ويُحدَّد موقع كل زيارة ومواعيدها والجهة المستقبِلة في أمر المهمة قبل التنفيذ."
            )
            + kv_table(
                [
                    (
                        "عنوان التنسيق الإداري لدى HMS",
                        "109, Dinonath Sen Road, Gandaria, Dhaka 1204, Bangladesh",
                    )
                ]
            ),
        )
        + article(
            "رابعًا: المدة والتجديد",
            p(
                "المدة الأولية للتكليف اثنا عشر (12) شهرًا تبدأ من تاريخ اعتماد هذا الملحق من الطرفين، ويجوز تمديدها باتفاق مكتوب قبل انتهائها. ولا تُحتسب هذه المدة من تاريخ بدء العمل الأصلي للموظف."
            ),
        )
        + article(
            "خامسًا: الإشراف والسلطات",
            p(
                "يتولى السيد هيميل حسن استقبال الموظف والتنسيق معه من جانب إتش إم إس ضمن التفويض المؤسسي المعتمد. وتحتفظ أمانة الكلمة بصلاحية اعتماد أوامر حركة البضائع والمصروفات والقرارات الوظيفية النهائية."
            )
            + p(
                "لا يشمل التكليف شراء البضائع أو بيعها أو التصرف في ملكيتها أو توقيع عقود ملزمة أو تنفيذ معاملات بنكية إلا بتفويض كتابي مستقل."
            ),
        )
        + article(
            "سادسًا: المصروفات والإجراءات",
            p(
                "تتحمل أمانة الكلمة أجر الموظف ومزاياه والمصروفات المعتمدة المرتبطة بالتكليف، وفق جدول التكاليف المستقل. وتُستكمل وثائق السفر ومتطلبات الدخول والعمل المطبقة قبل مباشرة أي مهمة تستلزمها في بنغلاديش."
            ),
        ),
        "hms",
    )
)

# 6 — Assignment closing (HMS)
PAGES.append(
    page(
        article(
            "سابعًا: الإنهاء",
            p(
                "يجوز إنهاء التكليف الفردي بإشعار مكتوب مدته ثلاثون (30) يومًا، ما لم يتفق الطرفان على خلاف ذلك. ولا يترتب على انتهاء التكليف بذاته إنهاء عقد العمل الأصلي مع أمانة الكلمة."
            ),
        )
        + article(
            "ثامنًا: إقرار الموظف",
            p(
                "يُقر الموظف — عند اعتماده هذا الملحق — باطلاعه على المهام والمواقع وحدود الصلاحيات والالتزامات التشغيلية المقررة، دون تعديل حقوقه الثابتة في علاقة العمل الأصلية."
            )
            + kv_table([("اسم الموظف", "سالم بن جمل بن جمعان العماري الدوسري")]),
        )
        + section_label("الاعتماد والنفاذ")
        + p(
            "يصبح هذا المستند نافذًا بعد اعتماده من ممثلي الشركتين المخوَّلين وفق صلاحيات كل منهما، ويُعتد بتاريخ الاعتماد الأخير."
        )
        + sig_block(
            [
                (
                    "عن شركة أمانة الكلمة",
                    "شهيد الإسلام عبد الرزاق",
                    "Shahidul Islam Abdur Razzak",
                ),
                ("عن شركة إتش إم إس", "هيميل حسن", "Himel Hasan"),
            ]
        ),
        "hms",
    )
)

# 7 — Admin decision (AALKC)
PAGES.append(
    page(
        doc_header(
            "قرار إداري بتكليف موظف بمهام لوجستية دولية",
            [
                ("رقم المستند", "AALKC-HMS-DEC-2026-001"),
                ("تاريخ التحرير", "14/11/2026"),
                ("ملحق التكليف", "AALKC-HMS-EA-2026-001"),
            ],
        )
        + lead(
            "تُكلِّف شركة أمانة الكلمة الموظف المبين أدناه بمتابعة استلام بضائعها وإرسالها ضمن التعاون التشغيلي مع شركة إتش إم إس."
        )
        + kv_table(
            [
                ("الموظف", "سالم بن جمل بن جمعان العماري الدوسري"),
                ("الهوية الوطنية", "1007982216"),
                ("تاريخ الالتحاق", "01/11/2025"),
                (
                    "مسمى التكليف",
                    "منسق استلام وإرسال البضائع والتنسيق اللوجستي الدولي",
                ),
                (
                    "موقع العمل الأصلي",
                    "المنطقة الصناعية بالدمام، المملكة العربية السعودية",
                ),
            ]
        )
        + article(
            "أولاً: المهام المعتمدة",
            bullets(
                [
                    "متابعة استلام وإرسال البضائع حسب أوامر الحركة الصادرة عن أمانة الكلمة.",
                    "مراجعة مستندات النقل والتسليم والكمية والحالة الظاهرة، وتوثيق أي اختلافات.",
                    "تنسيق الزيارات المهنية إلى بنغلاديش عند اقتضاء المهمة المتصلة بأعمال إتش إم إس حضورًا ميدانيًا.",
                    "رفع تقارير التشغيل والملاحظات إلى الإدارة المعنية بأمانة الكلمة.",
                ]
            ),
        )
        + article(
            "ثانيًا: الإشراف وحدود السلطة",
            p(
                "تحتفظ أمانة الكلمة بإدارة علاقة العمل والتكاليف واعتماد حركة البضائع. ويتولى السيد هيميل حسن التنسيق لدى إتش إم إس بموجب تفويضها."
            )
            + p(
                "لا يخوّل هذا القرار بيع البضائع أو شراءها أو نقل ملكيتها أو تحويل الأموال أو توقيع العقود دون تفويض مستقل."
            ),
        )
        + article(
            "ثالثًا: المدة والمصروفات",
            p(
                "يسري التكليف لمدة أولية قدرها اثنا عشر (12) شهرًا من اعتماد ملحقه الفردي، ويجوز تمديده كتابيًا. وتتحمل أمانة الكلمة المصروفات المعتمدة."
            ),
        )
        + section_label("الاعتماد والنفاذ")
        + p(
            "يسري هذا المستند بعد اعتماده من ممثل شركة أمانة الكلمة المخوَّل وفق الصلاحيات المعتمدة لدى الشركة."
        )
        + sig_block(
            [
                (
                    "الممثل المخوَّل",
                    "شهيد الإسلام عبد الرزاق",
                    "Shahidul Islam Abdur Razzak",
                ),
            ]
        ),
        "aalkc",
        dense=True,
    )
)

# 8 — HMS authorization (HMS)
PAGES.append(
    page(
        doc_header(
            "قرار تفويض ممثل شركة إتش إم إس للتنسيق والاستقبال",
            [
                ("رقم المستند", "HMS-AUTH-2026-001"),
                ("تاريخ التحرير", "14/11/2026"),
            ],
        )
        + lead(
            "تصدر شركة إتش إم إس هيفي ميتال المحدودة هذا القرار لتنظيم مسؤولية استقبال الموظف المكلَّف من أمانة الكلمة والتنسيق بشأن أعماله التجارية واللوجستية في بنغلاديش، وفق الصلاحيات المؤسسية المعتمدة."
        )
        + kv_table(
            [
                ("اسم الشركة بالعربية", "شركة إتش إم إس هيفي ميتال المحدودة"),
                ("اسم الشركة بالإنجليزية", "HMS Heavy Metal Limited"),
                ("رقم التأسيس", "C-199823/2022"),
                (
                    "عنوان المراسلات الحالي",
                    "109, Dinonath Sen Road, Gandaria, Dhaka 1204, Bangladesh",
                ),
                (
                    "عنوان المراسلات السابق",
                    "House-110, Road No. 03, Adabor, Baitul Aman Housing, Dhaka-1207, Bangladesh",
                ),
                ("الممثل المكلَّف", "هيميل حسن"),
                ("الاسم بالإنجليزية", "Himel Hasan"),
                ("الموظف المستقبَل", "سالم بن جمل بن جمعان العماري الدوسري"),
            ]
        )
        + article(
            "أولاً: نطاق التفويض",
            bullets(
                [
                    "تنسيق استقبال الموظف وتوجيهه إلى مواقع العمل المحددة في خطط المهام المعتمدة.",
                    "متابعة أعمال استلام البضائع وإرسالها التي تُنفَّذ لصالح أمانة الكلمة ضمن العمليات المنسقة بين الشركتين.",
                    "تنسيق إعداد محاضر الاستلام والتسليم وتبادل المستندات التشغيلية والتقارير مع أمانة الكلمة.",
                    "تمثيل إتش إم إس في اعتماد اتفاقية التعاون وملحق التكليف وخطة العمل وجدول التكاليف ضمن حدود التفويض الصادر من الجهة المختصة.",
                ]
            ),
        ),
        "hms",
    )
)

# 9 — HMS authorization closing (HMS)
PAGES.append(
    page(
        article(
            "ثانيًا: الوثائق المشمولة",
            kv_table(
                [
                    ("الاتفاقية الإطارية", "AALKC-HMS-FW-2026-001"),
                    ("ملحق الموظف", "AALKC-HMS-EA-2026-001"),
                    ("خطة التشغيل", "AALKC-HMS-WP-2026-001"),
                    ("جدول التكاليف", "AALKC-HMS-COST-2026-001"),
                ]
            ),
        )
        + article(
            "ثالثًا: حدود التفويض",
            p(
                "لا يشمل هذا التفويض صلاحية إجراء مدفوعات أو نقل ملكية البضائع أو شراء الأصول أو بيعها أو إنشاء التزامات مالية باسم أمانة الكلمة أو إتش إم إس خارج النطاق المعتمد."
            ),
        )
        + article(
            "رابعًا: سريان القرار",
            p(
                "يسري التفويض بعد اعتماد هذا القرار من الجهة المخوَّلة بتمثيل إتش إم إس وفق وثائق الشركة. ويكون السيد هيميل حسن مسؤول التنسيق والاستقبال في الحدود الواردة أعلاه طوال مدة التكليف، أو إلى حين تعديل التفويض بقرار لاحق."
            ),
        )
        + section_label("الاعتماد والنفاذ")
        + p(
            "يسري هذا المستند بعد اعتماده من صاحب الصلاحية لدى شركة إتش إم إس وفق وثائقها وقراراتها المؤسسية."
        )
        + kv_table(
            [
                (
                    "جهة الاعتماد",
                    "مجلس إدارة شركة إتش إم إس أو من يفوضه وفق وثائق الشركة",
                ),
                ("اسم صاحب صلاحية الاعتماد", "………………………………"),
                ("الصفة", "………………………………"),
                ("تاريخ الاعتماد", "………………………………"),
            ]
        ),
        "hms",
    )
)

# 10 — Employment certificate (AALKC)
PAGES.append(
    page(
        doc_header(
            "شهادة عمل وبيان مهام وظيفية",
            [
                ("رقم المستند", "AALKC-EMP-2026-001"),
                ("تاريخ التحرير", "14/11/2026"),
            ],
        )
        + lead("إلى من يهمه الأمر،")
        + p(
            "تشهد شركة أمانة الكلمة بأن الموظف الموضح أدناه يعمل لديها وفق بيانات العمل المقدمة من إدارة الشركة. وتبين هذه الشهادة طبيعة التكليف الوظيفي المعتمد في إطار أعمالها اللوجستية وتعاونها التجاري مع شركة إتش إم إس."
        )
        + kv_table(
            [
                ("الاسم", "سالم بن جمل بن جمعان العماري الدوسري"),
                ("الهوية الوطنية", "1007982216"),
                ("الجنسية", "سعودي"),
                ("تاريخ الالتحاق", "01/11/2025"),
                (
                    "مقر العمل الأصلي",
                    "المنطقة الصناعية بالدمام، المملكة العربية السعودية",
                ),
                (
                    "مسمى التكليف",
                    "منسق استلام وإرسال البضائع والتنسيق اللوجستي الدولي",
                ),
            ]
        )
        + p(
            "تشمل مهام الموظف متابعة استلام بضائع أمانة الكلمة وإرسالها، ومطابقة بيانات النقل والتسليم والكميات والحالة الظاهرة، والتنسيق بشأن العمليات المعتمدة مع الشركة المستضيفة في بنغلاديش. وقد تتطلب بعض المهام زيارات ميدانية إلى مواقع العمل المعتمدة وفق متطلبات العمليات والخطط الصادرة عن الشركة."
        )
        + p(
            "مدة التكليف الأولية اثنا عشر (12) شهرًا من تاريخ اعتماد ملحق التكليف، مع جواز تمديدها كتابيًا. وتتحمل أمانة الكلمة المصروفات المعتمدة المرتبطة بهذه المهام."
        )
        + section_label("الاعتماد والنفاذ")
        + p(
            "يسري هذا المستند بعد اعتماده من ممثل شركة أمانة الكلمة المخوَّل وفق الصلاحيات المعتمدة لدى الشركة."
        )
        + sig_block(
            [
                (
                    "الممثل المخوَّل",
                    "شهيد الإسلام عبد الرزاق",
                    "Shahidul Islam Abdur Razzak",
                ),
            ]
        ),
        "aalkc",
    )
)

# 11 — Work plan (HMS)
PAGES.append(
    page(
        doc_header(
            "خطة تشغيلية لاستلام البضائع وإرسالها والتنسيق الميداني",
            [
                ("رقم المستند", "AALKC-HMS-WP-2026-001"),
                ("تاريخ التحرير", "14/11/2026"),
                ("ملحق التكليف", "AALKC-HMS-EA-2026-001"),
            ],
        )
        + lead(
            "تنظم هذه الخطة تسلسل المهام المرتبطة بمتابعة استلام بضائع أمانة الكلمة وإرسالها، وتحديد مسؤوليات الموظف المعيَّن والشركة المستضيفة على مستوى كل عملية أو زيارة عمل."
        )
        + article(
            "أولاً: إعداد المهمة",
            bullets(
                [
                    "تصدر أمانة الكلمة أمر المهمة متضمنًا وصف البضاعة أو العملية والجهة المعنية وموقع التنفيذ والمستندات اللازمة.",
                    "تنسق إتش إم إس مع الجهات المستقبِلة أو مواقع الفحص أو التسليم داخل بنغلاديش عند الحاجة إلى زيارة ميدانية.",
                ]
            ),
        )
        + article(
            "ثانيًا: الاستلام",
            bullets(
                [
                    "يتحقق الموظف من الوصف والكميات والحالة الظاهرة للبضائع قياسًا إلى المستندات المعتمدة.",
                    "يُثبت الفروق أو التلفيات أو غياب المستندات في تقرير يُرفع إلى أمانة الكلمة قبل اتخاذ قرار القبول النهائي.",
                ]
            ),
        )
        + article(
            "ثالثًا: الإرسال",
            bullets(
                [
                    "يتابع الموظف تجهيز البضاعة وبيانات الجهة المستلِمة ومستندات التسليم في حدود تعليمات أمانة الكلمة.",
                    "تحتفظ الشركة صاحبة العملية بسجلات الشحن والتسليم والتأكيدات الصادرة من الجهات المعنية.",
                ]
            ),
        )
        + article(
            "رابعًا: التقارير والإشراف",
            p(
                "يرفع الموظف تقريرًا عن كل عملية منفَّذة إلى أمانة الكلمة، ويقوم السيد هيميل حسن بتنسيق المعلومات والمستندات المتعلقة بأنشطة إتش إم إس الفعلية."
            ),
        ),
        "hms",
    )
)

# 12 — Work plan closing (HMS)
PAGES.append(
    page(
        article(
            "خامسًا: برنامج الزيارات",
            p(
                "تُحدَّد كل زيارة إلى بنغلاديش في أمر مهمة منفصل يبيّن الغرض والموقع والأطراف المعنية والتاريخ المتوقع والمستندات المطلوبة. ولا تحدّد هذه الخطة مواعيد رحلات أو عمليات شحن بعينها قبل اعتماد أوامرها."
            )
            + kv_table(
                [
                    (
                        "عنوان تنسيق HMS",
                        "109, Dinonath Sen Road, Gandaria, Dhaka 1204, Bangladesh",
                    ),
                    ("مرجع التفويض", "HMS-AUTH-2026-001"),
                ]
            ),
        )
        + article(
            "سادسًا: الحدود المالية",
            p(
                "تتحمل أمانة الكلمة المصروفات المعتمدة لتنفيذ المهام، ولا يجوز إنشاء التزامات مالية جديدة أو إبرام عقود عن أي من الطرفين من دون صلاحية مستقلة."
            ),
        )
        + section_label("الاعتماد والنفاذ")
        + p(
            "يصبح هذا المستند نافذًا بعد اعتماده من ممثلي الشركتين المخوَّلين وفق صلاحيات كل منهما، ويُعتد بتاريخ الاعتماد الأخير."
        )
        + sig_block(
            [
                (
                    "عن شركة أمانة الكلمة",
                    "شهيد الإسلام عبد الرزاق",
                    "Shahidul Islam Abdur Razzak",
                ),
                ("عن شركة إتش إم إس", "هيميل حسن", "Himel Hasan"),
            ]
        ),
        "hms",
    )
)

# 13 — Cost schedule (AALKC)
PAGES.append(
    page(
        doc_header(
            "جدول توزيع المسؤوليات المالية لتكليف الموظف",
            [
                ("رقم المستند", "AALKC-HMS-COST-2026-001"),
                ("تاريخ التحرير", "14/11/2026"),
                ("ملحق التكليف", "AALKC-HMS-EA-2026-001"),
            ],
        )
        + lead(
            "تتحمل شركة أمانة الكلمة جميع المصروفات المعتمدة المرتبطة بتكليف الموظف ومهامه المحلية والخارجية، بما في ذلك المهام المنسقة مع شركة إتش إم إس في بنغلاديش."
        )
        + article(
            "أولاً: توزيع فئات المصروفات",
            bullets(
                [
                    "الأجر والمزايا الوظيفية الأصلية.",
                    "تذاكر السفر المعتمدة ورسوم الحجز.",
                    "الإقامة أثناء الزيارات المهنية.",
                    "النقل المحلي والتنقل إلى مواقع البضائع.",
                    "التأمين المرتبط بالمهمة.",
                    "رسوم التأشيرات والتصاريح المطلوبة.",
                    "النفقات التشغيلية اللازمة والمعتمدة مسبقًا.",
                ]
            ),
        )
        + article(
            "ثانيًا: إجراءات الموافقة والصرف",
            p(
                "تُدار الأجور والمزايا وفق عقد العمل ونظام الرواتب. وتُعتمد مصروفات التكليف الأخرى مسبقًا بالمستندات المؤيّدة. وإذا تحمّلت إتش إم إس نفقة بموافقة مكتوبة من أمانة الكلمة، تُسوَّى محاسبيًا بين الطرفين."
            )
            + p(
                "لا يُنشئ هذا الجدول عمولة أو أتعاب خدمات مستقلة لصالح أي طرف، ولا يمنح الموظف صلاحية إجراء معاملات بنكية أو صرف مصروفات دون موافقة الإدارة."
            ),
        )
        + article(
            "ثالثًا: المدة والتعديل",
            p(
                "يسري ترتيب التكاليف طوال مدة التكليف الأولية البالغة اثني عشر (12) شهرًا من نفاذ ملحقه الفردي، ويُمدَّد أو يُعدَّل بموجب اتفاق مكتوب بين الطرفين."
            ),
        )
        + section_label("الاعتماد والنفاذ")
        + p(
            "يصبح هذا المستند نافذًا بعد اعتماده من ممثلي الشركتين المخوَّلين وفق صلاحيات كل منهما، ويُعتد بتاريخ الاعتماد الأخير."
        )
        + sig_block(
            [
                (
                    "عن شركة أمانة الكلمة",
                    "شهيد الإسلام عبد الرزاق",
                    "Shahidul Islam Abdur Razzak",
                ),
                ("عن شركة إتش إم إس", "هيميل حسن", "Himel Hasan"),
            ]
        ),
        "aalkc",
        dense=True,
    )
)


def theme_css(prefix: str, t: dict, letterhead: str, pad_top: str, pad_bottom: str) -> str:
    return f"""
.page.brand-{prefix} {{
  background-image: url("{letterhead}");
  padding: {pad_top} 15mm {pad_bottom} 15mm;
  --primary: {t['primary']};
  --primary-soft: {t['primary_soft']};
  --slate: {t['slate']};
  --muted: {t['muted']};
  --rule: {t['rule']};
  --accent: {t['accent']};
  --tint: {t['tint']};
  --panel: {t['panel']};
}}
"""


CSS = f"""
@page {{
  size: A4;
  margin: 0;
}}

* {{ box-sizing: border-box; }}

html, body {{
  margin: 0;
  padding: 0;
  background: #fff;
  color: #3A4B5C;
  font-family: "Noto Naskh Arabic", "Noto Sans Arabic", serif;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}}

.page {{
  width: 210mm;
  height: 297mm;
  page-break-after: always;
  break-after: page;
  position: relative;
  overflow: hidden;
  background-color: #fff;
  background-position: center;
  background-size: 100% 100%;
  background-repeat: no-repeat;
}}

.page:last-child {{
  page-break-after: auto;
  break-after: auto;
}}

{theme_css("aalkc", AALKC, LH_AALKC, "48mm", "52mm")}
{theme_css("hms", HMS, LH_HMS, "57mm", "54mm")}

.doc-header {{ margin-bottom: 2.8mm; }}

.doc-title {{
  margin: 0 0 2.2mm;
  text-align: center;
  color: var(--primary);
  font-family: "Noto Kufi Arabic", "Noto Sans Arabic", sans-serif;
  font-size: 12.2pt;
  font-weight: 700;
  line-height: 1.45;
}}

.meta-panel {{
  border: 0.55pt solid var(--rule);
  background: var(--panel);
  border-radius: 1.8mm;
  padding: 1.2mm 2.8mm;
  display: flex;
  flex-direction: column;
  gap: 0.4mm;
}}

.meta-row {{
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 4mm;
  direction: rtl;
  border-bottom: 0.35pt solid var(--rule);
  padding: 1mm 0;
}}

.meta-row:last-child {{ border-bottom: none; }}

.meta-label {{
  color: var(--primary);
  font-family: "Noto Kufi Arabic", "Noto Sans Arabic", sans-serif;
  font-size: 8.7pt;
  font-weight: 700;
  white-space: nowrap;
}}

.meta-value {{
  color: var(--primary-soft);
  font-family: "Carlito", "Liberation Sans", "Noto Sans", sans-serif;
  font-size: 8.7pt;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-align: left;
  direction: ltr;
  unicode-bidi: isolate;
}}

.lead {{
  margin: 0 0 2.4mm;
  color: var(--primary-soft);
  font-size: 9.7pt;
  line-height: 1.65;
  text-align: justify;
  direction: rtl;
}}

p {{
  margin: 0 0 1.8mm;
  font-size: 9.5pt;
  line-height: 1.65;
  text-align: justify;
  direction: rtl;
  color: var(--slate);
}}

.note {{
  margin-top: 1.6mm;
  padding: 1.8mm 2.6mm;
  background: var(--tint);
  border-right: 1.5pt solid var(--accent);
  border-radius: 0 1mm 1mm 0;
  color: var(--muted);
  font-size: 8.8pt;
  line-height: 1.65;
}}

.article {{ margin: 0 0 1.8mm; }}

.article-title {{
  margin: 0 0 1.2mm;
  direction: rtl;
}}

.article-title span {{
  display: inline-block;
  color: var(--primary);
  font-family: "Noto Kufi Arabic", "Noto Sans Arabic", sans-serif;
  font-size: 9.8pt;
  font-weight: 700;
  padding: 0.3mm 0 0.5mm;
  border-bottom: 1.2pt solid var(--accent);
}}

.article-body {{ direction: rtl; }}

.kv-table {{
  margin: 1.6mm 0 2mm;
  border: 0.55pt solid var(--rule);
  border-radius: 1.8mm;
  overflow: hidden;
  background: rgba(255,255,255,0.78);
}}

.kv-row {{
  display: grid;
  /* With direction:rtl, first column is on the right → Arabic label, then value */
  grid-template-columns: 0.85fr 1.4fr;
  direction: rtl;
  border-bottom: 0.4pt solid var(--rule);
  min-height: 5.8mm;
}}

.kv-row:nth-child(even) {{ background: var(--tint); }}
.kv-row:last-child {{ border-bottom: none; }}

.kv-label {{
  padding: 1.3mm 2.6mm;
  color: var(--primary);
  font-family: "Noto Kufi Arabic", "Noto Sans Arabic", sans-serif;
  font-size: 8.6pt;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  border-left: 0.4pt solid var(--rule);
  background: var(--tint);
  text-align: right;
}}

.kv-value {{
  padding: 1.3mm 2.6mm;
  color: var(--primary-soft);
  font-size: 8.7pt;
  font-weight: 600;
  display: flex;
  align-items: center;
}}

.kv-value.kv-en {{
  font-family: "Carlito", "Liberation Sans", "Noto Sans", sans-serif;
  justify-content: flex-end;
  text-align: left;
  direction: ltr;
}}

.kv-value.kv-ar {{
  font-family: "Noto Naskh Arabic", "Noto Sans Arabic", serif;
  justify-content: flex-start;
  text-align: right;
  direction: rtl;
}}

.premium-list {{
  margin: 0;
  padding: 0 4.5mm 0 0;
  list-style: none;
  direction: rtl;
}}

.premium-list li {{
  position: relative;
  margin: 0 0 1.2mm;
  padding-right: 4.2mm;
  font-size: 9.4pt;
  line-height: 1.58;
  text-align: justify;
  color: var(--slate);
}}

.premium-list li::before {{
  content: "";
  position: absolute;
  right: 0;
  top: 2.2mm;
  width: 1.55mm;
  height: 1.55mm;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 0 0.6mm color-mix(in srgb, var(--accent) 22%, transparent);
}}

.section-kicker {{
  margin: 2.4mm 0 1.4mm;
  text-align: center;
  color: var(--primary);
  font-family: "Noto Kufi Arabic", "Noto Sans Arabic", sans-serif;
  font-size: 10.2pt;
  font-weight: 700;
}}

.section-kicker::before,
.section-kicker::after {{
  content: "";
  display: inline-block;
  width: 12mm;
  height: 0.65pt;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  vertical-align: middle;
  margin: 0 2.5mm;
}}

.sig-grid {{
  margin-top: 2.4mm;
  margin-bottom: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4mm;
  direction: rtl;
}}

.sig-grid.single {{
  grid-template-columns: 1fr;
  max-width: 86mm;
  margin-inline: auto;
}}

.sig-card {{
  border: 0.55pt solid var(--rule);
  border-radius: 1.8mm;
  padding: 2.4mm 3mm 2.8mm;
  background: linear-gradient(180deg, rgba(255,255,255,0.92), var(--tint));
  text-align: center;
}}

.sig-role {{
  color: var(--muted);
  font-family: "Noto Kufi Arabic", "Noto Sans Arabic", sans-serif;
  font-size: 8pt;
  font-weight: 700;
  margin-bottom: 4.2mm;
}}

.sig-line {{
  height: 0.5pt;
  background: var(--rule);
  margin: 0 3.5mm 2.6mm;
}}

.sig-name {{
  color: var(--primary);
  font-family: "Noto Kufi Arabic", "Noto Sans Arabic", sans-serif;
  font-size: 9.8pt;
  font-weight: 700;
}}

.sig-en {{
  margin-top: 0.8mm;
  color: var(--muted);
  font-family: "Carlito", "Liberation Sans", "Noto Sans", sans-serif;
  font-size: 8pt;
  letter-spacing: 0.02em;
  direction: ltr;
}}

/* Dense pages: keep content clear of tall letterhead footers */
.page.dense .doc-header {{ margin-bottom: 2mm; }}
.page.dense .doc-title {{ font-size: 11.6pt; margin-bottom: 1.8mm; }}
.page.dense .lead {{ font-size: 9.2pt; line-height: 1.55; margin-bottom: 1.8mm; }}
.page.dense p {{ font-size: 9.1pt; line-height: 1.55; margin-bottom: 1.4mm; }}
.page.dense .article {{ margin-bottom: 1.4mm; }}
.page.dense .article-title {{ margin-bottom: 0.9mm; }}
.page.dense .article-title span {{ font-size: 9.4pt; }}
.page.dense .kv-row {{ min-height: 5.2mm; }}
.page.dense .kv-label,
.page.dense .kv-value {{ font-size: 8.2pt; padding: 1mm 2.2mm; }}
.page.dense .premium-list li {{ font-size: 9pt; line-height: 1.5; margin-bottom: 0.9mm; }}
.page.dense .section-kicker {{ margin: 1.6mm 0 1mm; font-size: 9.6pt; }}
.page.dense .sig-grid {{ margin-top: 1.6mm; }}
.page.dense .sig-card {{ padding: 1.8mm 2.4mm 2mm; }}
.page.dense .sig-role {{ margin-bottom: 3.2mm; font-size: 7.6pt; }}
.page.dense .sig-name {{ font-size: 9.2pt; }}
.page.dense .note {{ font-size: 8.3pt; padding: 1.2mm 2mm; }}
"""


def build_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8" />
  <title>AALKC × HMS — Premium Business Documents</title>
  <style>{CSS}</style>
</head>
<body>
{"".join(PAGES)}
</body>
</html>
"""


def render_pdf() -> None:
    OUT_HTML.write_text(build_html(), encoding="utf-8")
    if OUT_PDF.exists():
        OUT_PDF.unlink()
    cmd = [
        "timeout",
        "90s",
        "google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={OUT_PDF}",
        OUT_HTML.as_uri(),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if not OUT_PDF.exists():
        raise RuntimeError(
            f"Chrome failed to write PDF (exit={result.returncode}): {result.stderr[-1000:]}"
        )
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_bytes(OUT_PDF.read_bytes())
    print(f"Wrote {OUT_PDF} ({OUT_PDF.stat().st_size} bytes)")
    print(f"Wrote {ARTIFACT}")


if __name__ == "__main__":
    render_pdf()
