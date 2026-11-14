#!/usr/bin/env python3
"""Build a premium AALKC business-document PDF on the original letterhead."""

from __future__ import annotations

import base64
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUT_HTML = ROOT / "premium_documents.html"
OUT_PDF = ROOT / "AALKC_HMS_7_Business_Documents_Premium_Arabic.pdf"
ARTIFACT = Path("/opt/cursor/artifacts/AALKC_HMS_7_Business_Documents_Premium_Arabic.pdf")

NAVY = "#0A2745"
NAVY_SOFT = "#1B3A5A"
SLATE = "#3D4F63"
MUTED = "#6B7C8F"
RULE = "#D5DEE8"
GOLD = "#A8895A"
BG_TINT = "rgba(10, 39, 69, 0.035)"


def letterhead_data_uri() -> str:
    data = (ASSETS / "letterhead.jpg").read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(data).decode("ascii")


def meta_row(label: str, value: str) -> str:
    return f"""
    <div class="meta-row">
      <span class="meta-value" dir="ltr">{value}</span>
      <span class="meta-label">{label}</span>
    </div>"""


def _is_arabic_heavy(text: str) -> bool:
    arabic = sum(1 for ch in text if "\u0600" <= ch <= "\u06FF")
    return arabic >= max(1, len(text) // 5)


def kv_table(rows: list[tuple[str, str]]) -> str:
    cells = []
    for label, value in rows:
        if _is_arabic_heavy(value):
            value_html = f'<div class="kv-value kv-ar">{value}</div>'
        else:
            value_html = f'<div class="kv-value kv-en"><span dir="ltr">{value}</span></div>'
        cells.append(
            f"""
      <div class="kv-row">
        {value_html}
        <div class="kv-label">{label}</div>
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
        en = f'<div class="sig-en">{name_en}</div>' if name_en else ""
        cards.append(
            f"""
      <div class="sig-card">
        <div class="sig-role">{role}</div>
        <div class="sig-line"></div>
        <div class="sig-name">{name_ar}</div>
        {en}
      </div>"""
        )
    return f'<div class="sig-grid">{"".join(cards)}</div>'


def page(inner: str, page_class: str = "") -> str:
    return f'<article class="page {page_class}">{inner}</article>'


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


# ── Document content (cleaned Arabic, original meaning preserved) ────────────

PAGES: list[str] = []

# Page 1 — Framework Agreement
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
            "أبرمت هذه الاتفاقية لتنظيم التعاون التشغيلي في استلام البضائع وإرسالها ومتابعة مستندات النقل والتسليم بين الطرفين، وتحديد آلية تكليف موظف من شركة أمانة الكلمة بالتنسيق مع شركة إتش إم إس."
        )
        + article(
            "المادة الأولى: أطراف الاتفاقية",
            p(
                "الطرف الأول: شركة أمانة الكلمة، شركة ذات مسؤولية محدودة مسجلة في المملكة العربية السعودية، ومقرها الرئيس في الدمام، ويشار إليها فيما يلي بالشركة الأصلية."
            )
            + p(
                "الطرف الثاني: شركة إتش إم إس هيفي ميتال المحدودة، شركة مسجلة في جمهورية بنغلاديش الشعبية، ويشار إليها فيما يلي بالشركة المستضيفة."
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
                "يُعتمد العنوان الحالي للمراسلات التشغيلية وفق بيانات الشركة المستضيفة. ويُذكر العنوان السابق لأغراض سجل المراسلات التاريخية فحسب."
            ),
        )
        + article(
            "المادة الثانية: نطاق التعاون",
            p(
                "يتعاون الطرفان في تنسيق استلام وإرسال البضائع لحساب شركة أمانة الكلمة، ومراجعة بيانات الشحن والتسليم والكميات والحالة الظاهرة للبضائع، ومتابعة الجهات الناقلة والمستلمة في حدود العمليات المعتمدة من إدارة أمانة الكلمة."
            ),
        )
    )
)

# Page 2 — Framework continued
PAGES.append(
    page(
        p(
            "لا تنشئ هذه الاتفاقية بذاتها بيعًا أو شراءً أو نقل ملكية أو عمولة أو التزامًا ماليًا جديدًا على أي من الطرفين، ويُنظَّم كل معاملة تجارية مستقلة بمستنداتها المعتمدة."
        )
        + article(
            "المادة الثالثة: التكليف الوظيفي والمواقع",
            p(
                "يجوز تكليف موظف تابع لشركة أمانة الكلمة بتنفيذ مهام التنسيق والاستلام والإرسال وفق ملحق فردي مستقل. ويظل مقر عمله الأصلي في المنطقة الصناعية بالدمام، مع تكليفه عند الحاجة بزيارات عمل إلى بنغلاديش للتنسيق الميداني مع شركة إتش إم إس."
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
                    "يرفع الموظف تقارير الاستلام والإرسال والملاحظات والفروق دون أن يملك إبرام عقود بيع أو شراء أو نقل ملكية البضائع أو إجراء مدفوعات دون تفويض مستقل.",
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
                "تسري الاتفاقية من تاريخ اعتمادها من الطرفين، وتستمر حتى إنهائها باتفاق مكتوب أو بإشعار سابق مدته ستون يومًا. وتُحدَّد مدة تكليف الموظف على حدة في ملحقه الفردي، ويكون تمديده مكتوبًا."
            ),
        )
    )
)

# Page 3 — Framework closing
PAGES.append(
    page(
        article(
            "المادة الثامنة: السرية وحدود التفويض",
            p(
                "يحافظ الطرفان على سرية معلومات العمليات والأسعار والموردين والمستندات الداخلية. ولا يجوز لأي طرف إلزام الآخر ماليًا أو تعاقديًا إلا بموافقة صريحة مستقلة من الجهة المخولة."
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
            "يصبح هذا المستند نافذًا بعد اعتماده من ممثلي الشركتين المخولين وفق صلاحيات كل منهما، ويُعتد بتاريخ الاعتماد الأخير."
        )
        + sig_block(
            [
                ("عن شركة أمانة الكلمة", "شهيد الإسلام عبد الرزاق", "Shahidul Islam Abdur Razzak"),
                ("عن شركة إتش إم إس", "هيميل حسن", "Himel Hasan"),
            ]
        )
    )
)

# Page 4 — Employee assignment
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
                "تاريخ الالتحاق مذكور بحسب إفادة إدارة أمانة الكلمة. والمسمى المبين أعلاه خاص بهذا التكليف ولا يُفترض أنه يحل محل المسمى المسجل في عقد العمل الأصلي."
            ),
        )
        + article(
            "ثانيًا: المسؤوليات",
            p(
                "يتولى الموظف لحساب أمانة الكلمة متابعة استلام البضائع وإرسالها، ومطابقة أوصافها وكمياتها وحالتها الظاهرة مع المستندات المعتمدة، والتنسيق مع الناقلين وجهات التسليم والاستلام، وإعداد محاضر المتابعة التشغيلية ورفع التقارير إلى إدارة أمانة الكلمة."
            ),
        )
    )
)

# Page 5 — Assignment continued
PAGES.append(
    page(
        p(
            "تقبل إتش إم إس تنظيم المتابعة الميدانية المرتبطة بعملياتها في بنغلاديش عند وجود مهام تعتمدها الشركتان، وتنسق استقبال الموظف وربطه بالجهات المختصة في تلك العمليات."
        )
        + article(
            "ثالثًا: الموقع وآلية الزيارات",
            p(
                "مقر العمل الأصلي للموظف هو المنطقة الصناعية بالدمام. ويشمل التكليف زيارات عمل متكررة إلى بنغلاديش بحسب العمليات الفعلية وخطط الزيارة المعتمدة. ويُحدَّد موقع كل زيارة ومواعيدها والجهة المستقبلة في أمر المهمة قبل التنفيذ."
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
                "المدة الأولية للتكليف اثنا عشر شهرًا تبدأ من تاريخ اعتماد هذا الملحق من الطرفين، ويجوز تمديدها باتفاق مكتوب قبل انتهائها. ولا تُحتسب هذه المدة من تاريخ بدء العمل الأصلي للموظف."
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
        )
    )
)

# Page 6 — Assignment closing
PAGES.append(
    page(
        article(
            "سابعًا: الإنهاء",
            p(
                "يجوز إنهاء التكليف الفردي بإشعار مكتوب مدته ثلاثون يومًا، ما لم يتفق الطرفان على خلاف ذلك. ولا يترتب على انتهاء التكليف بذاته إنهاء عقد العمل الأصلي مع أمانة الكلمة."
            ),
        )
        + article(
            "ثامنًا: إقرار الموظف",
            p(
                "يُقر الموظف، عند اعتماده هذا الملحق، باطلاعه على المهام والمواقع وحدود الصلاحيات والالتزامات التشغيلية المقررة، دون تعديل حقوقه الثابتة في علاقة العمل الأصلية."
            )
            + kv_table([("اسم الموظف", "سالم بن جمل بن جمعان العماري الدوسري")]),
        )
        + section_label("الاعتماد والنفاذ")
        + p(
            "يصبح هذا المستند نافذًا بعد اعتماده من ممثلي الشركتين المخولين وفق صلاحيات كل منهما، ويُعتد بتاريخ الاعتماد الأخير."
        )
        + sig_block(
            [
                ("عن شركة أمانة الكلمة", "شهيد الإسلام عبد الرزاق", "Shahidul Islam Abdur Razzak"),
                ("عن شركة إتش إم إس", "هيميل حسن", "Himel Hasan"),
            ]
        )
    )
)

# Page 7 — Admin decision
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
            "تُكلِّف شركة أمانة الكلمة الموظف المبين أدناه بمتابعة استلام بضائعها وإرسالها ضمن التعاون التشغيلي مع إتش إم إس."
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
                "تحتفظ أمانة الكلمة بإدارة علاقة العمل والتكاليف واعتماد حركة البضائع. ويتولى هيميل حسن التنسيق لدى إتش إم إس بموجب تفويضها."
            )
            + p(
                "لا يخول هذا القرار بيع البضائع أو شراءها أو نقل ملكيتها أو تحويل الأموال أو توقيع العقود دون تفويض مستقل."
            ),
        )
        + article(
            "ثالثًا: المدة والمصروفات",
            p(
                "يسري التكليف لمدة أولية 12 شهرًا من اعتماد ملحقه الفردي، ويجوز تمديده كتابيًا. وتتحمل أمانة الكلمة المصروفات المعتمدة."
            ),
        )
        + section_label("الاعتماد والنفاذ")
        + p(
            "يسري هذا المستند بعد اعتماده من ممثل شركة أمانة الكلمة المخول وفق الصلاحيات المعتمدة لدى الشركة."
        )
        + sig_block(
            [
                ("الممثل المخول", "شهيد الإسلام عبد الرزاق", "Shahidul Islam Abdur Razzak"),
            ]
        )
    )
)

# Page 8 — HMS authorization
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
            "تصدر شركة إتش إم إس هيفي ميتال المحدودة هذا القرار لتنظيم مسؤولية استقبال الموظف المكلف من أمانة الكلمة والتنسيق بشأن أعماله التجارية واللوجستية في بنغلاديش، وفق الصلاحيات المؤسسية المعتمدة."
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
                ("الممثل المكلف", "هيميل حسن"),
                ("الاسم بالإنجليزية", "Himel Hasan"),
                ("الموظف المستقبَل", "سالم بن جمل بن جمعان العماري الدوسري"),
            ]
        )
        + article(
            "أولاً: نطاق التفويض",
            bullets(
                [
                    "تنسيق استقبال الموظف وتوجيهه إلى مواقع العمل المحددة في خطط المهام المعتمدة.",
                    "متابعة أعمال استلام البضائع وإرسالها التي تنفذ لصالح أمانة الكلمة ضمن العمليات المنسقة بين الشركتين.",
                    "تنسيق إعداد محاضر الاستلام والتسليم وتبادل المستندات التشغيلية والتقارير مع أمانة الكلمة.",
                    "تمثيل إتش إم إس في اعتماد اتفاقية التعاون وملحق التكليف وخطة العمل وجدول التكاليف ضمن حدود التفويض الصادر من الجهة المختصة.",
                ]
            ),
        )
    )
)

# Page 9 — HMS authorization closing
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
                "يسري التفويض بعد اعتماد هذا القرار من الجهة المخولة بتمثيل إتش إم إس وفق وثائق الشركة. ويكون السيد هيميل حسن مسؤول التنسيق والاستقبال في الحدود الواردة أعلاه طوال مدة التكليف أو إلى حين تعديل التفويض بقرار لاحق."
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
                ("اسم صاحب صلاحية الاعتماد", "……………………"),
                ("الصفة", "……………………"),
                ("تاريخ الاعتماد", "……………………"),
            ]
        )
    )
)

# Page 10 — Employment certificate
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
            "مدة التكليف الأولية اثنا عشر شهرًا من تاريخ اعتماد ملحق التكليف، مع جواز تمديدها كتابيًا. وتتحمل أمانة الكلمة المصروفات المعتمدة المرتبطة بهذه المهام."
        )
        + section_label("الاعتماد والنفاذ")
        + p(
            "يسري هذا المستند بعد اعتماده من ممثل شركة أمانة الكلمة المخول وفق الصلاحيات المعتمدة لدى الشركة."
        )
        + sig_block(
            [
                ("الممثل المخول", "شهيد الإسلام عبد الرزاق", "Shahidul Islam Abdur Razzak"),
            ]
        )
    )
)

# Page 11 — Work plan
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
            "تنظم هذه الخطة تسلسل المهام المرتبطة بمتابعة استلام بضائع أمانة الكلمة وإرسالها، وتحديد مسؤوليات الموظف المعين والشركة المستضيفة على مستوى كل عملية أو زيارة عمل."
        )
        + article(
            "أولاً: إعداد المهمة",
            bullets(
                [
                    "تصدر أمانة الكلمة أمر المهمة متضمنًا وصف البضاعة أو العملية والجهة المعنية وموقع التنفيذ والمستندات اللازمة.",
                    "تنسق إتش إم إس مع الجهات المستقبلة أو مواقع الفحص أو التسليم داخل بنغلاديش عند الحاجة إلى زيارة ميدانية.",
                ]
            ),
        )
        + article(
            "ثانيًا: الاستلام",
            bullets(
                [
                    "يتحقق الموظف من الوصف والكميات والحالة الظاهرة للبضائع قياسًا إلى المستندات المعتمدة.",
                    "يثبت الفروق أو التلفيات أو غياب المستندات في تقرير يرفع إلى أمانة الكلمة قبل اتخاذ قرار القبول النهائي.",
                ]
            ),
        )
        + article(
            "ثالثًا: الإرسال",
            bullets(
                [
                    "يتابع الموظف تجهيز البضاعة وبيانات الجهة المستلمة ومستندات التسليم في حدود تعليمات أمانة الكلمة.",
                    "تحتفظ الشركة صاحبة العملية بسجلات الشحن والتسليم والتأكيدات الصادرة من الجهات المعنية.",
                ]
            ),
        )
        + article(
            "رابعًا: التقارير والإشراف",
            p(
                "يرفع الموظف تقريرًا عن كل عملية منفذة إلى أمانة الكلمة، ويقوم السيد هيميل حسن بتنسيق المعلومات والمستندات المتعلقة بأنشطة إتش إم إس الفعلية."
            ),
        )
    )
)

# Page 12 — Work plan closing
PAGES.append(
    page(
        article(
            "خامسًا: برنامج الزيارات",
            p(
                "تحدد كل زيارة إلى بنغلاديش في أمر مهمة منفصل يبين الغرض والموقع والأطراف المعنية والتاريخ المتوقع والمستندات المطلوبة. ولا تحدد هذه الخطة مواعيد رحلات أو عمليات شحن بعينها قبل اعتماد أوامرها."
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
            "يصبح هذا المستند نافذًا بعد اعتماده من ممثلي الشركتين المخولين وفق صلاحيات كل منهما، ويُعتد بتاريخ الاعتماد الأخير."
        )
        + sig_block(
            [
                ("عن شركة أمانة الكلمة", "شهيد الإسلام عبد الرزاق", "Shahidul Islam Abdur Razzak"),
                ("عن شركة إتش إم إس", "هيميل حسن", "Himel Hasan"),
            ]
        )
    )
)

# Page 13 — Cost schedule
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
                    "الأجر والمزايا الوظيفية الأصلية",
                    "تذاكر السفر المعتمدة ورسوم الحجز",
                    "الإقامة أثناء الزيارات المهنية",
                    "النقل المحلي والتنقل إلى مواقع البضائع",
                    "التأمين المرتبط بالمهمة",
                    "رسوم التأشيرات والتصاريح المطلوبة",
                    "النفقات التشغيلية اللازمة والمعتمدة مسبقًا",
                ]
            ),
        )
        + article(
            "ثانيًا: إجراءات الموافقة والصرف",
            p(
                "تُدار الأجور والمزايا وفق عقد العمل ونظام الرواتب. وتُعتمد مصروفات التكليف الأخرى مسبقًا بالمستندات المؤيدة. وإذا تحملت إتش إم إس نفقة بموافقة مكتوبة من أمانة الكلمة، تُسوَّى محاسبيًا بين الطرفين."
            )
            + p(
                "لا ينشئ هذا الجدول عمولة أو أتعاب خدمات مستقلة لصالح أي طرف، ولا يمنح الموظف صلاحية إجراء معاملات بنكية أو صرف مصروفات دون موافقة الإدارة."
            ),
        )
        + article(
            "ثالثًا: المدة والتعديل",
            p(
                "يسري ترتيب التكاليف طوال مدة التكليف الأولية البالغة اثني عشر شهرًا من نفاذ ملحقه الفردي، ويُمدَّد أو يُعدَّل بموجب اتفاق مكتوب بين الطرفين."
            ),
        )
        + section_label("الاعتماد والنفاذ")
        + p(
            "يصبح هذا المستند نافذًا بعد اعتماده من ممثلي الشركتين المخولين وفق صلاحيات كل منهما، ويُعتد بتاريخ الاعتماد الأخير."
        )
        + sig_block(
            [
                ("عن شركة أمانة الكلمة", "شهيد الإسلام عبد الرزاق", "Shahidul Islam Abdur Razzak"),
                ("عن شركة إتش إم إس", "هيميل حسن", "Himel Hasan"),
            ]
        )
    )
)


CSS = f"""
@page {{
  size: A4;
  margin: 0;
}}

* {{
  box-sizing: border-box;
}}

html, body {{
  margin: 0;
  padding: 0;
  background: #fff;
  color: {SLATE};
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
  background: #fff url("{letterhead_data_uri()}") center / 100% 100% no-repeat;
  padding: 37.5mm 15.5mm 31mm 15.5mm;
}}

.page:last-child {{
  page-break-after: auto;
  break-after: auto;
}}

.doc-header {{
  margin-bottom: 4.2mm;
}}

.doc-title {{
  margin: 0 0 3.2mm;
  text-align: center;
  color: {NAVY};
  font-family: "Noto Kufi Arabic", "Noto Sans Arabic", sans-serif;
  font-size: 13.2pt;
  font-weight: 700;
  line-height: 1.55;
  letter-spacing: 0;
}}

.meta-panel {{
  border: 0.6pt solid {RULE};
  background: linear-gradient(180deg, rgba(10,39,69,0.04), rgba(10,39,69,0.015));
  border-radius: 2mm;
  padding: 1.6mm 3mm;
  display: flex;
  flex-direction: column;
  gap: 0.8mm;
}}

.meta-row {{
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 4mm;
  direction: rtl;
  border-bottom: 0.4pt solid {RULE};
  padding: 1.1mm 0;
}}

.meta-row:last-child {{
  border-bottom: none;
}}

.meta-label {{
  color: {NAVY};
  font-family: "Noto Kufi Arabic", "Noto Sans Arabic", sans-serif;
  font-size: 9pt;
  font-weight: 700;
  white-space: nowrap;
}}

.meta-value {{
  color: {NAVY_SOFT};
  font-family: "Carlito", "Liberation Sans", "Noto Sans", sans-serif;
  font-size: 9pt;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-align: left;
  direction: ltr;
  unicode-bidi: isolate;
}}

.lead {{
  margin: 0 0 3.5mm;
  color: {NAVY_SOFT};
  font-size: 10.4pt;
  line-height: 1.75;
  text-align: justify;
  direction: rtl;
}}

p {{
  margin: 0 0 2.6mm;
  font-size: 10.2pt;
  line-height: 1.78;
  text-align: justify;
  direction: rtl;
  color: {SLATE};
}}

.note {{
  margin-top: 2mm;
  padding: 2.2mm 3mm;
  background: {BG_TINT};
  border-right: 1.6pt solid {GOLD};
  border-radius: 0 1.2mm 1.2mm 0;
  color: {MUTED};
  font-size: 9.3pt;
  line-height: 1.7;
}}

.article {{
  margin: 0 0 3.4mm;
}}

.article-title {{
  margin: 0 0 2mm;
  direction: rtl;
}}

.article-title span {{
  display: inline-block;
  color: {NAVY};
  font-family: "Noto Kufi Arabic", "Noto Sans Arabic", sans-serif;
  font-size: 10.6pt;
  font-weight: 700;
  padding: 0.6mm 0 0.8mm;
  border-bottom: 1.4pt solid {GOLD};
}}

.article-body {{
  direction: rtl;
}}

.kv-table {{
  margin: 2mm 0 2.5mm;
  border: 0.6pt solid {RULE};
  border-radius: 2mm;
  overflow: hidden;
  background: rgba(255,255,255,0.72);
}}

.kv-row {{
  display: grid;
  grid-template-columns: 1.35fr 0.9fr;
  direction: rtl;
  border-bottom: 0.45pt solid {RULE};
  min-height: 7.2mm;
}}

.kv-row:nth-child(even) {{
  background: rgba(10, 39, 69, 0.028);
}}

.kv-row:last-child {{
  border-bottom: none;
}}

.kv-label {{
  padding: 1.6mm 3mm;
  color: {NAVY};
  font-family: "Noto Kufi Arabic", "Noto Sans Arabic", sans-serif;
  font-size: 9pt;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  border-left: 0.45pt solid {RULE};
  background: rgba(10, 39, 69, 0.035);
}}

.kv-value {{
  padding: 1.6mm 3mm;
  color: {NAVY_SOFT};
  font-size: 9pt;
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
  padding: 0 5mm 0 0;
  list-style: none;
  direction: rtl;
}}

.premium-list li {{
  position: relative;
  margin: 0 0 2mm;
  padding-right: 4.5mm;
  font-size: 10.1pt;
  line-height: 1.72;
  text-align: justify;
  color: {SLATE};
}}

.premium-list li::before {{
  content: "";
  position: absolute;
  right: 0;
  top: 2.4mm;
  width: 1.7mm;
  height: 1.7mm;
  border-radius: 50%;
  background: {GOLD};
  box-shadow: 0 0 0 0.7mm rgba(168, 137, 90, 0.18);
}}

.section-kicker {{
  margin: 4mm 0 2.2mm;
  text-align: center;
  color: {NAVY};
  font-family: "Noto Kufi Arabic", "Noto Sans Arabic", sans-serif;
  font-size: 11pt;
  font-weight: 700;
  letter-spacing: 0.04em;
}}

.section-kicker::before,
.section-kicker::after {{
  content: "";
  display: inline-block;
  width: 14mm;
  height: 0.7pt;
  background: linear-gradient(90deg, transparent, {GOLD}, transparent);
  vertical-align: middle;
  margin: 0 3mm;
}}

.sig-grid {{
  margin-top: 4mm;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 5mm;
  direction: rtl;
}}

.sig-grid:has(.sig-card:only-child) {{
  grid-template-columns: 1fr;
  max-width: 88mm;
  margin-inline: auto;
}}

.sig-card {{
  border: 0.6pt solid {RULE};
  border-radius: 2mm;
  padding: 3.5mm 3.5mm 4mm;
  background: linear-gradient(180deg, rgba(255,255,255,0.88), rgba(10,39,69,0.03));
  text-align: center;
}}

.sig-role {{
  color: {MUTED};
  font-family: "Noto Kufi Arabic", "Noto Sans Arabic", sans-serif;
  font-size: 8.5pt;
  font-weight: 700;
  margin-bottom: 6mm;
}}

.sig-line {{
  height: 0.55pt;
  background: {RULE};
  margin: 0 4mm 3mm;
}}

.sig-name {{
  color: {NAVY};
  font-family: "Noto Kufi Arabic", "Noto Sans Arabic", sans-serif;
  font-size: 10.2pt;
  font-weight: 700;
}}

.sig-en {{
  margin-top: 1mm;
  color: {MUTED};
  font-family: "Carlito", "Liberation Sans", "Noto Sans", sans-serif;
  font-size: 8.4pt;
  letter-spacing: 0.02em;
  direction: ltr;
}}
"""


def build_html() -> str:
    body = "\n".join(PAGES)
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8" />
  <title>AALKC × HMS — Premium Business Documents</title>
  <style>{CSS}</style>
</head>
<body>
{body}
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
    print(f"Wrote {OUT_PDF}")
    print(f"Wrote {ARTIFACT}")
    print(f"Size: {OUT_PDF.stat().st_size} bytes")


if __name__ == "__main__":
    render_pdf()
