import streamlit as st
import json
import os
from uuid import uuid4
from PIL import Image

# إعدادات الصفحة
st.set_page_config(page_title="Prompt Library", layout="wide")

# تفعيل حالة تسجيل الدخول في الـ session_state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- واجهة المستخدم الترحيبية (إذا لمש تسجيل الدخول) ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #4F8BF9;'>🖼️ مرحباً بك في مكتبة البرومبتات الذكية</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>تطبيقك الشخصي لحفظ وتنظيم صورك وبرومبتات الذكاء الاصطناعي</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("---")
        # خيار كلمة مرور بسيطة لحماية مكتبتك (اختياري، يمكنك تغييرها أو جعلها كزر دخول مباشر)
        password = st.text_input("أدخل اسم المستخدم للدخول ):", type="password")
        
        if st.button("🚀 الدخول إلى المكتبة", use_container_width=True):
            # يمكنك وضـع كلمة مرور معينة أو تركها تسمح بالدخول مباشرة
            st.session_state.logged_in = True
            st.rerun()
    
    # إيقاف تنفيذ باقي الكود حتى يسجل الدخول
    st.stop()

# ==========================================
# --- التطبيق الأساسي (بعد تسجيل الدخول) ---
# ==========================================

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .prompt-card {
        background-color: #1a1c23;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# زر تسجيل الخروج في الشريط الجانبي
if st.sidebar.button("🔒 قفل التطبيق (تسجيل خروج)"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🖼️ مكتبة البرومبتات والصور الذكية")
st.markdown("---")

# مسارات التطبيق المطلقة
APP_DIR = os.path.dirname(os.path.abspath(__file__))
SAVED_IMAGES_DIR = os.path.join(APP_DIR, "saved_images")
DATA_FILE = os.path.join(APP_DIR, "prompts_data.json")

os.makedirs(SAVED_IMAGES_DIR, exist_ok=True)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

raw_data = load_data()
if isinstance(raw_data, dict):
    st.session_state.data = [
        {"id": str(uuid4()), "title": "", "image_name": image_name, "prompt": prompt, "note": ""}
        for image_name, prompt in raw_data.items()
    ]
    save_data(st.session_state.data)
else:
    st.session_state.data = [
        {
            "id": item.get("id", str(uuid4())),
            "title": item.get("title", ""),
            "image_name": item["image_name"],
            "prompt": item["prompt"],
            "note": item.get("note", "")
        }
        for item in raw_data
    ]

# --- القائمة الجانبية: إضافة برومبت جديد ---
st.sidebar.header("➕ إضافة برومبت جديد")

if st.sidebar.button("✨ توليد برومبت تلقائي (مساعد الذكاء الاصطناعي)", use_container_width=True):
    st.sidebar.info("💡 تم توليد قالب برومبت احترافي! يمكنك تعديله:")
    default_prompt_suggestion = "A cinematic hyper-realistic portrait of [Subject], dramatic lighting, 8k resolution, Unreal Engine 5 render, highly detailed."
    st.session_state.suggested_prompt = default_prompt_suggestion
else:
    if "suggested_prompt" not in st.session_state:
        st.session_state.suggested_prompt = ""

image_title = st.sidebar.text_input("عنوان أو اسم الصورة:")
uploaded_file = st.sidebar.file_uploader("اختر الصورة", type=["jpg", "jpeg", "png"])

prompt_text = st.sidebar.text_area("اكتب البرومبت هنا:", value=st.session_state.suggested_prompt)
note_text = st.sidebar.text_area("اضف ملاحظة (اختياري):")

if st.sidebar.button("حفظ في المكتبة", use_container_width=True):
    if uploaded_file and prompt_text:
        final_title = image_title.strip() if image_title.strip() else "بدون عنوان"
        
        image_name = f"{uuid4().hex}_{uploaded_file.name}"
        image_path = os.path.join(SAVED_IMAGES_DIR, image_name)
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.session_state.data.append({
            "id": str(uuid4()),
            "title": final_title,
            "image_name": image_name,
            "prompt": prompt_text,
            "note": note_text,
        })
        save_data(st.session_state.data)
        st.sidebar.success("تم الحفظ بنجاح!")
        st.rerun()
    else:
        st.sidebar.error("الرجاء رفع صورة وكتابة البرومبت على الأقل.")

# --- قسم النسخ الاحتياطي في القائمة الجانبية ---
st.sidebar.markdown("---")
st.sidebar.subheader("💾 إدارة النسخ الاحتياطية (للهاتف)")

if st.session_state.data:
    json_string = json.dumps(st.session_state.data, ensure_ascii=False, indent=4)
    st.sidebar.download_button(
        label="📥 تصدير نسختك الاحتياطية",
        data=json_string,
        file_name="prompts_backup.json",
        mime="application/json",
        use_container_width=True
    )

uploaded_backup = st.sidebar.file_uploader("📤 استيراد ملف نسخة احتياطية (JSON)", type=["json"])
if uploaded_backup is not None:
    try:
        imported_data = json.load(uploaded_backup)
        if isinstance(imported_data, list):
            st.session_state.data = imported_data
            save_data(st.session_state.data)
            st.sidebar.success("✅ تم استيراد البيانات بنجاح!")
            st.rerun()
        else:
            st.sidebar.error("ملف النسخة الاحتياطية غير صالح.")
    except Exception as e:
        st.sidebar.error("حدث خطأ أثناء قراءة الملف.")

# --- شريط البحث والفلترة ---
search_query = st.text_input("🔍 ابحث في مكتبتك (بالعنوان، البرومبت، أو الملاحظات):", "")

filtered_data = [
    item for item in st.session_state.data 
    if search_query.lower() in item.get("title", "").lower() or 
       search_query.lower() in item["prompt"].lower() or 
       search_query.lower() in item.get("note", "").lower()
]

st.markdown("### 📚 معرض الصور المحفوظة")

if not filtered_data:
    st.info("لا توجد نتائج مطابقة للبحث أو المكتبة فارغة.")
else:
    cols = st.columns(3)
    for index, item in enumerate(filtered_data):
        col = cols[index % 3]
        img_path = os.path.join(SAVED_IMAGES_DIR, item["image_name"])

        if os.path.exists(img_path):
            image = Image.open(img_path)
            with col:
                with st.container(border=True):
                    current_title = item.get('title', '')
                    if current_title:
                        st.markdown(f"**📌 {current_title}**")
                    else:
                        st.markdown("**⚠️ بدون عنوان**")

                    st.image(image, use_container_width=True)
                    st.code(item["prompt"], language="text")
                    
                    if item.get("note"):
                        st.caption(f"📝 ملاحظة: {item['note']}")

                    with st.expander("⚙️ خيارات التعديل وتوليد المتغيرات"):
                        
                        st.markdown("---")
                        st.markdown("#### 🔀 توليد متغيرات سريعة للبرومبت")
                        
                        lighting_option = st.selectbox("اختر نمط الإضاءة:", ["بدون تغيير", "Dramatic Lighting", "Soft Studio Lighting", "Neon Glowing Light", "Golden Hour Sunlight"], key=f"light_{item['id']}")
                        style_option = st.selectbox("اختر النمط الفني:", ["بدون تغيير", "Cyberpunk Style", "Oil Painting Style", "Anime Illustration", "Photorealistic 8k"], key=f"style_{item['id']}")
                        
                        if st.button("دمج وتوليد البرومبت الجديد", key=f"gen_var_{item['id']}", use_container_width=True):
                            base_prompt = item["prompt"]
                            modified_prompt = base_prompt
                            
                            if lighting_option != "بدون تغيير":
                                modified_prompt += f", {lighting_option}"
                            if style_option != "بدون تغيير":
                                modified_prompt += f", {style_option}"
                            
                            st.info("👇 البرومبت الجديد بعد دمج المتغيرات:")
                            st.code(modified_prompt, language="text")

                        st.markdown("---")
                        with st.form(key=f"edit_form_{item['id']}"):
                            title_input = st.text_input("تعديل العنوان:", current_title, key=f"title_{item['id']}")
                            note_input = st.text_area("تعديل الملاحظة:", item.get("note", ""), key=f"note_{item['id']}")
                            save_changes = st.form_submit_button("حفظ التعديلات", use_container_width=True)
                            
                            if save_changes:
                                item["title"] = title_input.strip() if title_input.strip() else "بدون عنوان"
                                item["note"] = note_input
                                save_data(st.session_state.data)
                                st.success("تم التعديل بنجاح!")
                                st.rerun()
                        
                        if st.button("🗑️ حذف الصورة والبرومبت", key=f"delete_{item['id']}", type="primary", use_container_width=True):
                            if os.path.exists(img_path):
                                os.remove(img_path)
                            
                            st.session_state.data = [d for d in st.session_state.data if d["id"] != item["id"]]
                            save_data(st.session_state.data)
                            st.toast("تم الحذف بنجاح!")
                            st.rerun()