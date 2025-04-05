import streamlit as st
from PIL import Image
import base64
from logic import decide_treatment_group, get_dose_recommendations, get_contraindications

# --- Config ---
st.set_page_config(page_title="HyperCare", page_icon="favicon.png", layout="wide")

# --- Logo ---
theme = st.get_option("theme.base") if st.get_option("theme.base") else "light"
logo_path = "logo_dark.png" if theme == "dark" else "logo_clean.png"
with open(logo_path, "rb") as f:
    logo_data = f.read()
logo_base64 = base64.b64encode(logo_data).decode("utf-8")
st.markdown(
    f"<div style='text-align:center'><img src='data:image/png;base64,{logo_base64}' width='180'/></div>",
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align:center; color:#2E86C1;'>HyperCare: Hypertension Assistant</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border:1px solid #ccc;'/>", unsafe_allow_html=True)

# --- Layout ---
st.subheader("🧾 Patient Profile")
with st.expander("➤ Personal Details", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=1, max_value=120, value=50)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    with col2:
        weight = st.number_input("Weight (kg)", min_value=1.0, value=70.0)
        height = st.number_input("Height (cm)", min_value=50.0, value=170.0)

st.subheader("📈 BP & Pulse Recordings")
with st.expander("➤ Blood Pressure & Heart Rate", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        sbp1 = st.number_input("Systolic BP 1", min_value=50, value=130)
        dbp1 = st.number_input("Diastolic BP 1", min_value=30, value=85)
        hr1 = st.number_input("Heart Rate 1", min_value=30, value=70)
    with col2:
        sbp2 = st.number_input("Systolic BP 2", min_value=50, value=128)
        dbp2 = st.number_input("Diastolic BP 2", min_value=30, value=80)
        hr2 = st.number_input("Heart Rate 2", min_value=30, value=72)

st.subheader("🩺 Medical History")
with st.expander("➤ Comorbidities", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        cva = st.checkbox("Prior CVA")
        hf = st.checkbox("Heart Failure")
    with col2:
        cad = st.checkbox("CAD / MI")
        diabetes = st.checkbox("Diabetes")
    with col3:
        pregnancy = st.checkbox("Currently Pregnant")
        lung_disease = st.checkbox("Asthma / COPD")

st.subheader("🧠 Symptoms")
with st.expander("➤ Presenting Complaints", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        chest_pain = st.checkbox("Chest pain on exertion")
        breathlessness = st.checkbox("Breathlessness")
    with col2:
        leg_swelling = st.checkbox("Leg swelling")
        dry_cough = st.checkbox("Dry cough")

st.subheader("🧪 Lab Investigations")
with st.expander("➤ Biochemistry", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        hba1c = st.number_input("HbA1c (%)", min_value=3.0, max_value=15.0, value=5.5)
        creatinine = st.number_input("Creatinine (mg/dL)", min_value=0.1, value=1.0)
        uric_acid = st.number_input("Uric Acid (mg/dL)", min_value=1.0, value=5.5)
    with col2:
        potassium = st.number_input("Potassium (mmol/L)", min_value=2.5, value=4.2)
        sodium = st.number_input("Sodium (mmol/L)", min_value=120.0, value=138.0)
        egfr_calc = st.checkbox("Calculate eGFR")

if egfr_calc:
    egfr = ((140 - age) * weight) / (72 * creatinine)
    if gender == "Female":
        egfr *= 0.85
else:
    egfr = 0

st.subheader("🖼️ Imaging")
with st.expander("➤ Echocardiogram", expanded=True):
    cad_echo = st.radio("CAD on Echo", ["Absent", "Present"])
    ef = st.number_input("Ejection Fraction %", min_value=10.0, max_value=80.0, value=60.0)
    if ef < 40:
        ef_type = "HFrEF"
    elif 40 <= ef <= 60 and cad_echo == "Absent":
        ef_type = "HFpEF"
    elif ef > 40 and cad_echo == "Present":
        ef_type = "CAD"
    else:
        ef_type = "Normal EF"

st.markdown("<hr style='border:1px solid #ccc;'/>", unsafe_allow_html=True)
st.subheader("🧾 Final Recommendation")
if st.button("🧮 Generate Treatment Recommendation"):
    high_risk_flags = []
    if cva: high_risk_flags.append("Prior CVA")
    if cad or cad_echo == "Present": high_risk_flags.append("CAD")
    if hf or ef_type == "HFrEF": high_risk_flags.append("Heart Failure")
    if egfr_calc and egfr < 60: high_risk_flags.append("CKD")

    risk_level = "High Risk" if high_risk_flags else "Low Risk"

    treatment_group = decide_treatment_group(
        ef=ef,
        egfr=egfr,
        cad=(cad or cad_echo == "Present"),
        cva=cva,
        diabetes=diabetes,
        pregnant=pregnancy,
        age=age
    )

    contraindications = get_contraindications(
        creatinine=creatinine,
        potassium=potassium,
        pulse=hr1,
        dry_cough=dry_cough,
        uric_acid=uric_acid
    )
    drug_doses = get_dose_recommendations(treatment_group)

    with st.container():
        st.success("### ✅ Personalized Clinical Summary")
        st.markdown(f"👤 **Name:** `{name if name else 'Anonymous'}`")
        st.markdown(f"🧮 **eGFR:** {egfr:.1f} mL/min" if egfr_calc else "eGFR not calculated")
        st.markdown(f"⚠️ **Risk Level:** `{risk_level}`")
        if high_risk_flags:
            st.markdown(f"🧠 **Flags:** {', '.join(high_risk_flags)}")
        st.markdown(f"📘 **Treatment Group:** `{treatment_group}`")

        st.markdown("💊 **Recommended Drug Doses:**")
        for d in drug_doses:
            st.markdown(f"- {d}")

        st.markdown("🚫 **Contraindicated Drug Classes:**")
        st.markdown(", ".join(contraindications) if contraindications else "None")

        st.markdown("🧾 **Treatment Plan Suggestion:**")
        if "Group 1" in treatment_group:
            st.markdown("- Start: E (Isosorbide + Hydralazine) + D2 (Furosemide)")
            st.markdown("- Add: B (Beta-blocker) cautiously")
        elif "Group 2" in treatment_group:
            st.markdown("- Start: A3 (Sacubitril + Valsartan) + B (Beta-blocker)")
            st.markdown("- Add: D3 (Spironolactone), D2 if volume overloaded")
        elif "Group 3" in treatment_group:
            st.markdown("- Start: C + D2 or B + D2")
        elif "Group 4" in treatment_group:
            st.markdown("- Start: A1 (ACE Inhibitor) + D3 (Spironolactone)")
        elif "Group 5" in treatment_group:
            st.markdown("- Start: A + B (ACE Inhibitor + Beta-blocker)")
        elif "Group 6" in treatment_group:
            st.markdown("- Start: A + D1 (ACE Inhibitor + Thiazide)")
        elif "Group 7" in treatment_group:
            st.markdown("- Start: A + D1 (ACE Inhibitor + Thiazide)")
        elif "Group 8" in treatment_group:
            st.markdown("- Start: Alpha-methyldopa or Labetalol")
            st.markdown("- Avoid: ACEi, ARBs, MRAs, Thiazides")
        elif "Group 9" in treatment_group:
            st.markdown("- Start: C (Calcium Channel Blocker)")
        elif "Group 10" in treatment_group:
            st.markdown("- Lifestyle modification")
            st.markdown("- Review in 3 months")
            st.markdown("- If BP >140/90 → Start C")
        else:
            st.warning("Custom physician-led treatment advised")
