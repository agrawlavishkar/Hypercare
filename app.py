# app.py
import streamlit as st
from logic import classify_risk, get_contraindications, decide_treatment_group, get_dose_recommendations


st.set_page_config(page_title="HyperCare", layout="centered")
st.title("🩺 HyperCare: Hypertension Management Assistant")

st.header("Step 1: Patient Profile & Lifestyle")

name = st.text_input("Full Name")
age = st.number_input("Age", min_value=1, max_value=120)
gender = st.selectbox("Gender", ["Male", "Female", "Other"])
weight = st.number_input("Weight (kg)", min_value=1.0)
height = st.number_input("Height (cm)", min_value=50.0)
alcohol = st.selectbox("Alcohol Consumption", ["None", "Moderate", "Heavy"])
smoking = st.selectbox("Smoking Status", ["Non-Smoker", "Ex-Smoker", "Current Smoker"])
physical_activity = st.selectbox("Physical Activity", ["Sedentary", "Moderate", "Active"])

st.header("Step 2: BP Recordings")

st.subheader("First Recording")
sbp1 = st.number_input("Systolic BP 1", min_value=50)
dbp1 = st.number_input("Diastolic BP 1", min_value=30)
hr1 = st.number_input("Heart Rate 1", min_value=30)

st.subheader("Second Recording")
sbp2 = st.number_input("Systolic BP 2", min_value=50)
dbp2 = st.number_input("Diastolic BP 2", min_value=30)
hr2 = st.number_input("Heart Rate 2", min_value=30)

st.header("Step 3: Comorbidities")

cva = st.checkbox("Prior CVA (paralysis or sudden vision loss)")
cad = st.checkbox("Coronary Artery Disease / Heart Attack")
hf = st.checkbox("Heart Failure")
diabetes = st.checkbox("Diabetes (or unsure)")
pregnancy = st.checkbox("Currently Pregnant")
lung_disease = st.checkbox("Asthma / COPD / Inhalers use")

st.header("Step 4: Symptom-Based Screening")

chest_pain = st.checkbox("Chest pain on walking/exertion?")
breathlessness = st.checkbox("Breathlessness?")
nyha_class = "Minor NYHA"

if breathlessness:
    st.markdown("#### NYHA Classification")
    breathless_100m = st.checkbox("Breathlessness on walking 100 meters?")
    breathless_stairs = st.checkbox("Breathlessness on climbing one flight of stairs?")
    
    if breathless_100m or breathless_stairs:
        nyha_class = "Major NYHA"

leg_swelling = st.checkbox("Leg swelling?")
dry_cough = st.checkbox("Dry Cough?")

st.header("Step 5: Blood Tests")

st.subheader("HbA1c")
hba1c = st.number_input("HbA1c (%)", min_value=3.0, max_value=15.0)

st.subheader("Lipid Profile")
total_chol = st.number_input("Total Cholesterol (mg/dL)")
hdl = st.number_input("HDL Cholesterol (mg/dL)")
ldl = st.number_input("LDL Cholesterol (mg/dL)")
triglycerides = st.number_input("Triglycerides (mg/dL)")

st.subheader("Kidney Function")
albumin = st.number_input("Serum Albumin (g/dL)")
creatinine = st.number_input("Serum Creatinine (mg/dL)")
acr_result = st.radio("Albumin/Creatinine Ratio (ACR):", ["Not done", "Normal", "Abnormal"])
egfr_calc = st.checkbox("Calculate eGFR using Cockcroft-Gault")

sodium = st.number_input("Serum Sodium (mmol/L)")
potassium = st.number_input("Serum Potassium (mmol/L)")
uric_acid = st.number_input("Uric Acid (mg/dL)")

st.subheader("TSH (Optional)")
tsh_level = st.number_input("TSH Level (mIU/L)")
tsh_status = st.radio("TSH Interpretation:", ["Normal", "High", "Low"])

if st.button("Run HyperCare Logic"):
    egfr = ((140 - age) * weight) / (72 * creatinine)
    if gender == "Female":
        egfr *= 0.85

st.header("Step 6: Imaging & Echocardiography")

renal_doppler = st.radio("Renal Artery Doppler", ["Not done", "Normal", "Abnormal"])

st.subheader("2D Echo Findings")
cad_echo = st.radio("Coronary Artery Disease (Echo):", ["Absent", "Present"])
ejection_fraction = st.number_input("Ejection Fraction (EF%)", min_value=10, max_value=80)

# EF interpretation
if ejection_fraction < 40:
    ef_type = "HFrEF"
elif 40 <= ejection_fraction <= 60 and cad_echo == "Absent":
    ef_type = "HFpEF"
elif ejection_fraction > 40 and cad_echo == "Present":
    ef_type = "CAD"
else:
    ef_type = "Normal EF"

st.header("Step 7: Decision Support Output")

if st.button("Generate Treatment Recommendation"):

    # eGFR Calculation
    if egfr_calc:
        egfr = ((140 - age) * weight) / (72 * creatinine)
        if gender == "Female":
            egfr *= 0.85
    else:
        egfr = 0  # Or assume known CKD if data not available

    # Risk Summary (basic placeholder for now)
    high_risk_flags = []
    if cva:
        high_risk_flags.append("Prior CVA")
    if cad or cad_echo == "Present":
        high_risk_flags.append("CAD")
    if hf or ef_type == "HFrEF":
        high_risk_flags.append("Heart Failure")
    if egfr < 60:
        high_risk_flags.append("CKD")
    
    risk_level = "High Risk" if high_risk_flags else "Low Risk"
    
    # Contraindications (updated location)
    contraindications = []
    if creatinine > 2.5 or potassium > 5.5:
        contraindications += ["ACE inhibitors (A1)", "ARBs (A2)", "MRAs (D3)"]
    if hr1 < 60:
        contraindications.append("Beta-blockers (B)")
    if dry_cough:
        contraindications.append("ACE inhibitors (A1)")
    if uric_acid > 9:
        contraindications.append("Thiazides (D1)")

    # Determine Treatment Group
    treatment_group = decide_treatment_group(
        ef=ejection_fraction,
        egfr=egfr,
        cad=(cad or cad_echo == "Present"),
        cva=cva,
        diabetes=diabetes,
        pregnant=pregnancy,
        age=age
    )

    # Get Drug Dose Recommendations based on the treatment group
    drug_doses = get_dose_recommendations(treatment_group)

    # Output Section
    st.subheader("🧠 Clinical Summary")
    st.subheader("📘 Assigned Treatment Group")
    st.write(treatment_group)
    
    st.subheader("💊 Drug Dose Recommendations")
    for dose in drug_doses:
        st.markdown(f"- {dose}")

    st.write(f"eGFR: {egfr:.1f} mL/min" if egfr > 0 else "eGFR: Not calculated")
    st.write(f"Risk Level: {risk_level}")
    
    if high_risk_flags:
        st.write("Flags:", ", ".join(high_risk_flags))

    st.subheader("🚫 Contraindicated Drug Classes")
    st.write(", ".join(contraindications) if contraindications else "None")

    st.subheader("💊 Treatment Recommendation")
    
    if "Group 1" in treatment_group:
        st.markdown("- Start: E (Isosorbide + Hydralazine) + D2 (Furosemide)")
        st.markdown("- Add: B (Beta-blocker) cautiously")
    elif "Group 2" in treatment_group:
        st.markdown("- Start: A3 (Sacubitril + Valsartan) + B (Beta-blocker)")
        st.markdown("- Add: D3 (Spironolactone), D2 (Furosemide) if volume overloaded")
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
        st.markdown("- Avoid: ACE inhibitors, ARBs, MRAs, Thiazides")
    elif "Group 9" in treatment_group:
        st.markdown("- Start: C (Calcium Channel Blocker)")
    elif "Group 10" in treatment_group:
        st.markdown("- Lifestyle modification")
        st.markdown("- Review after 3 months")
        st.markdown("- If BP >140/90 → Start C (Calcium Channel Blocker)")
    else:
        st.markdown("- Custom physician review required")