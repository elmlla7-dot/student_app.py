"""صفحة الطالب للنشر على streamlit.io — تقرأ public_data.json فقط."""
import hashlib, html, json
import streamlit as st

# ---- تنسيق RTL (مضمّن في الملف حتى لا يعتمد على ملف خارجي) ----
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
.stApp, .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp li,
.stApp input, .stApp textarea, .stApp button, .stApp td, .stApp th, .stApp [role="tab"],
.stApp [data-baseweb="select"] { font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif !important; }
.stApp { direction: rtl; }

/* شريط ستريملت العلوي الثابت كان يغطي أعلى العنوان فيقطع النص — نخفيه */
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
.block-container { max-width: 1150px; padding: 1rem 1rem 2rem; }

.stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp li,
.stApp [data-testid="stWidgetLabel"], .stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="stAlert"] { text-align: right; }
[data-testid="stWidgetLabel"], [data-testid="stCheckbox"] label, [data-testid="stRadio"] label { justify-content: flex-start; }
[data-testid="stSidebar"] { direction: rtl; }
[data-testid="stSidebar"] input, input[type="password"], input[type="number"] { direction: ltr; text-align: left; }
[data-testid="stTextInput"] input { text-align: right; }
[data-testid="stSidebar"] [data-testid="stTextInput"] input { text-align: left; }

/* التبويبات: كلها في صف واحد، بلا أشرطة تمرير داخلية */
[data-testid="stTabs"], [data-testid="stTabs"] * { scrollbar-width: none; }
[data-testid="stTabs"] *::-webkit-scrollbar { display: none; }
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: .3rem; flex-wrap: nowrap; overflow: visible !important; }
[data-testid="stTabs"] [role="tab"] { flex: 1 1 0; height: auto; min-height: 2.6rem; padding: .35rem .4rem;
  white-space: normal; justify-content: center; text-align: center; font-weight: 600; }
[data-testid="stTabs"] [role="tab"] p { text-align: center; line-height: 1.5; }

[data-testid="stDataFrame"], [data-testid="stDataEditor"] { direction: ltr; }
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button { border-radius: 8px; font-weight: 600; }
h2, h3 { color: #4a6fa5; }

/* الجداول: تتمدد على عرض الصفحة وتلتف نصوصها، بلا تمرير أفقي */
table.rt { width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 8px; overflow: hidden; margin-bottom: .6rem; }
.rt th { background: rgba(74,111,165,.18); font-weight: 700; }
.rt td, .rt th { direction: rtl; text-align: right; padding: 7px 10px; border: 1px solid rgba(128,128,128,.3); overflow-wrap: anywhere; }

/* الترويسة */
.hdr { background: #4a6fa5; color: #fff; padding: 14px 16px; border-radius: 12px; margin-bottom: 14px; text-align: center; overflow: visible; }
.hdr .u { font-size: 1.3rem; font-weight: 700; line-height: 1.9; }
.hdr .d { font-size: .95rem; opacity: .95; line-height: 1.9; }
.hdr h1 { margin: 0; padding: .15rem 0 0; font-size: 1.2rem; line-height: 1.9; color: #fff; text-align: center; overflow: visible; }
#MainMenu, footer { visibility: hidden; }

@media (prefers-color-scheme: dark) { h2, h3, .rt td::before { color: #8fb0dc; } }

/* الهاتف: كل صف في الجدول يتحول إلى بطاقة (اسم الحقل ← قيمته) */
@media (max-width: 640px) {
  .block-container { padding: .6rem .6rem 2rem; }
  .hdr { padding: 10px 8px; }
  .hdr .u { font-size: 1.1rem; }
  .hdr .d { font-size: .85rem; }
  .hdr h1 { font-size: 1rem; }
  [data-testid="stTabs"] [role="tab"] { padding: .3rem .2rem; }
  [data-testid="stTabs"] [role="tab"] p { font-size: .8rem; }
  table.rt, .rt tbody, .rt tr, .rt td { display: block; width: 100%; }
  .rt thead { display: none; }
  table.rt { border-radius: 0; overflow: visible; }
  .rt tr { margin-bottom: .6rem; border: 1px solid rgba(128,128,128,.3); border-radius: 10px; overflow: hidden; }
  .rt td { display: flex; justify-content: space-between; align-items: flex-start; gap: .8rem;
           border: 0; border-bottom: 1px solid rgba(128,128,128,.18); padding: 6px 10px; }
  .rt td:last-child { border-bottom: 0; }
  .rt td::before { content: attr(data-label); font-weight: 700; color: #4a6fa5; flex: 0 0 auto; }
  .rt td > span { text-align: left; min-width: 0; }
}
</style>
"""


def apply():
    st.markdown(CSS, unsafe_allow_html=True)


def header():
    st.markdown('<div class="hdr"><div class="u">جامعة بنغازي</div>'
                '<div class="d">قسم اللغة الإنجليزية — كلية الآداب والعلوم سلوق</div>'
                '<h1>منظومة تسجيل المواد وعرض النتائج</h1></div>', unsafe_allow_html=True)


def tbl(heads, body):
    """جدول HTML (RTL) من رؤوس وصفوف جاهزة (كل صف: (لون الخلفية أو "", [خلايا HTML]))."""
    th = "".join(f"<th>{h}</th>" for h in heads)
    tr = "".join(f'<tr style="{f"background:{bg}" if bg else ""}">'
                 + "".join(f'<td data-label="{h}"><span>{c}</span></td>' for h, c in zip(heads, cells)) + "</tr>"
                 for bg, cells in body)
    st.markdown(f'<table class="rt"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>', unsafe_allow_html=True)
# ---- نهاية التنسيق ----

st.set_page_config(page_title="جامعة بنغازي - منظومة تسجيل المواد وعرض النتائج", initial_sidebar_state="collapsed")
apply()
header()

ST = {"passed": ("rgba(34,160,80,.30)", "مجتازة"), "current": ("rgba(40,120,220,.30)", "مسجلة هذا الفصل"),
      "available": ("rgba(240,170,20,.35)", "متاحة لك"), "locked": ("rgba(128,128,128,.18)", "غير متاحة")}
RES = {"passed": ("rgba(34,160,80,.30)", "ناجح"), "failed": ("rgba(220,60,60,.30)", "راسب"),
       "pending": ("rgba(128,128,128,.18)", "لم تُرصد بعد")}
try:
    data = json.load(open("public_data.json", encoding="utf-8"))
except FileNotFoundError:
    st.error("لم يُرفع ملف البيانات بعد."); st.stop()

sid = st.text_input("رقم القيد").strip()
pin = st.text_input("الرمز السري", type="password").strip()

if st.button("عرض") and sid and pin:
    r = data["students"].get(hashlib.sha256(f"{sid}:{pin}".encode()).hexdigest())
    if not r:
        st.error("رقم القيد أو الرمز السري غير صحيح.")
    else:
        st.header(r["name"])
        st.write(f"المواد المجتازة: **{r['done']}** — المواد المتبقية: **{r['left']}** — الفصل الحالي: {data['term']}")
        t_cur, t_plan, t_res = st.tabs(["📚 مواد الفصل الحالي", "🗂️ سجل الطالب", "📊 نتائج الفصل"])

        # ---- 1) مواد الفصل الحالي ----
        with t_cur:
            st.subheader(f"المواد المسجلة — {data['term']}")
            cur = r.get("current")
            if cur is None:
                st.info("هذه البيانات لا تتضمن مواد الفصل بعد؛ سيتم تحديثها قريباً.")
            elif not cur:
                st.info("لا توجد مواد مسجلة لك في هذا الفصل.")
            else:
                tbl(["الرمز", "المقرر", "الأستاذ", "القاعة", "الساعات", "الموعد"],
                    [("", [html.escape(x["code"]), html.escape(x["name"]), html.escape(x.get("teacher") or "—"),
                           html.escape(str(x.get("room") or "—")), html.escape(str(x["hours"])),
                           html.escape(x["when"]) + (" ⚠️ تعارض مع مادة أخرى" if x["clash"] else "")]) for x in cur])
                try:
                    st.caption(f"عدد المواد: {len(cur)} — مجموع الساعات: {sum(int(x['hours']) for x in cur)}")
                except ValueError:
                    st.caption(f"عدد المواد: {len(cur)}")

        # ---- 2) سجل الطالب (كشف المقررات) ----
        with t_plan:
            st.markdown('<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:.4rem">'
                        + "".join(f'<span style="background:{c};padding:3px 10px;border-radius:99px">{t}</span>'
                                  for c, t in ST.values()) + '</div>', unsafe_allow_html=True)
            if not data["published"]:
                st.info("نتائج الفصل الحالي لم تُعلن بعد.")
            for sem in sorted({x["sem"] for x in r["courses"]}):
                st.subheader(f"الفصل الدراسي {sem}")
                tbl(["الرمز", "المقرر", "الساعات", "الحالة", "تفاصيل"],
                    [(ST[x["status"]][0], [html.escape(x["code"]), html.escape(x["name"]), html.escape(str(x["hours"])),
                                           f'<b>{ST[x["status"]][1]}</b>', html.escape(x["detail"])])
                     for x in r["courses"] if x["sem"] == sem])

        # ---- 3) نتائج الفصل ----
        with t_res:
            st.subheader(f"نتائج {data['term']}")
            if not data["published"]:
                st.info("نتائج الفصل الحالي لم تُعلن بعد.")
            elif not r.get("results"):
                st.info("لا توجد نتائج لك في هذا الفصل.")
            else:
                res = r["results"]
                tbl(["الرمز", "المقرر", "الساعات", "التقدير", "النتيجة"],
                    [(RES[x["status"]][0], [html.escape(x["code"]), html.escape(x["name"]), html.escape(str(x["hours"])),
                                            f'<b dir="ltr" style="unicode-bidi:isolate">{html.escape(x["grade"]) or "—"}</b>',
                                            f'<b>{RES[x["status"]][1]}</b>']) for x in res])
                n = lambda k: sum(1 for x in res if x["status"] == k)
                st.caption(f"ناجح: {n('passed')} — راسب: {n('failed')}" + (f" — لم تُرصد بعد: {n('pending')}" if n("pending") else ""))
