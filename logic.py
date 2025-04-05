# logic.py

def classify_risk(cva, cad, ef, diabetes, egfr):
    if cva:
        return "High Risk: Prior CVA"
    if cad:
        return "High Risk: CAD"
    if ef < 40:
        return "High Risk: HFrEF"
    if diabetes and egfr < 60:
        return "High Risk: DM with CKD"
    if egfr < 60:
        return "High Risk: CKD"
    return "Low Risk"

def get_contraindications(creatinine, potassium, pulse, dry_cough, uric_acid):
    contraindications = []
    if creatinine > 2.5 or potassium > 5.5:
        contraindications += ["ACE inhibitors (A1)", "ARBs (A2)", "MRAs (D3)"]
    if pulse < 60:
        contraindications.append("Beta-blockers (B)")
    if dry_cough:
        contraindications.append("ACE inhibitors (A1)")
    if uric_acid > 9:
        contraindications.append("Thiazides (D1)")
    return contraindications

def decide_treatment_group(ef, egfr, cad, cva, diabetes, pregnant, age):
    if ef < 40:
        if egfr < 60:
            return "Group 1: HFrEF + CKD"
        else:
            return "Group 2: HFrEF without CKD"
    elif 40 <= ef <= 60:
        if cad and egfr < 60:
            return "Group 3: HFpEF with CAD + CKD"
        elif not cad and egfr > 60:
            return "Group 4: HFpEF without CAD + Normal KFT"
    elif cad and egfr > 60:
        return "Group 5: CAD with normal KFT"
    elif cva and egfr > 60:
        return "Group 6: Prior CVA with normal KFT"
    elif diabetes and egfr > 60:
        return "Group 7: Diabetes with normal KFT"
    elif pregnant:
        return "Group 8: Pregnancy"
    elif egfr > 60 and age > 80:
        return "Group 9: Elderly with normal KFT"
    elif egfr > 60:
        return "Group 10: Lifestyle first, then C"
    return "Custom Plan Needed"

def get_dose_recommendations(group):
    dose_dict = {
        "Group 1": [
            "E = Isosorbide 10–20 mg TDS + Hydralazine 25 mg TDS",
            "D2 = Furosemide 20–40 mg OD",
            "B = Metoprolol XL 12.5–25 mg OD (if HR > 60)"
        ],
        "Group 2": [
            "A3 = Sacubitril/Valsartan 24/26 mg BD",
            "B = Bisoprolol 2.5–5 mg OD",
            "D3 = Spironolactone 25 mg OD",
            "D2 = Furosemide 20 mg OD (if required)"
        ],
        "Group 3": ["C = Amlodipine 5 mg OD", "D2 = Furosemide 20 mg OD"],
        "Group 4": ["A1 = Enalapril 2.5 mg BD", "D3 = Spironolactone 25 mg OD"],
        "Group 5": ["A = Ramipril 2.5 mg OD", "B = Metoprolol XL 25 mg OD"],
        "Group 6": ["A = Enalapril 2.5 mg BD", "D1 = Chlorthalidone 12.5 mg OD"],
        "Group 7": ["A = Perindopril 4 mg OD", "D1 = Chlorthalidone 12.5 mg OD"],
        "Group 8": ["Methyldopa 250 mg BD", "or Labetalol 100 mg BD"],
        "Group 9": ["C = Amlodipine 2.5–5 mg OD"],
        "Group 10": ["Lifestyle changes for 3 months", "Then: C = Amlodipine 5 mg OD"]
    }
    return dose_dict.get(group.split(":")[0], ["Custom physician review needed"])
