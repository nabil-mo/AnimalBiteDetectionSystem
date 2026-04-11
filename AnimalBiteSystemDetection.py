import streamlit as st
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Animal Bite Risk Assessment", layout="centered")

st.title("🐾 Animal Bite Risk Assessment Tool")

# -------------------------
# Patient Details Section
# -------------------------
st.subheader("👤 Patient Details")

col1, col2 = st.columns(2)
with col1:
    patient_name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
with col2:
    sex = st.selectbox("Sex", ["-- Select --", "Male", "Female"])
    visit_date = st.date_input("Visit Date", value=datetime.today())

additional_notes = st.text_area("Additional Notes (optional)")

# -------------------------
# Clinical Inputs
# -------------------------
st.subheader("🧾 Clinical Inputs")

placeholder = "-- Select --"

animal_type = st.selectbox("Animal Type", [placeholder, "Dog","Cat","Monkey","Rat","Camel","Bat","Unknown"])
bite_location = st.selectbox("Bite Location", [placeholder, "Hand","Face","Leg","Other"])
bite_depth = st.selectbox("Bite Depth", [placeholder, "Superficial","Deep"])
time_delay = st.selectbox("Time Delay", [placeholder, "<6h",">6h"])
tetanus_status = st.selectbox("Tetanus Vaccination", [placeholder, "Up-to-date","Unknown/Incomplete"])
animal_status = st.selectbox("Animal Status", [placeholder, "Healthy","Suspected","Unknown"])

# Validation
all_selected = all([
    animal_type != placeholder,
    bite_location != placeholder,
    bite_depth != placeholder,
    time_delay != placeholder,
    tetanus_status != placeholder,
    animal_status != placeholder,
    patient_name.strip() != "",
    sex != placeholder
])

# Scoring maps
animal_score_map = {"Cat":3,"Dog":2,"Monkey":3,"Rat":2,"Camel":2,"Bat":3,"Unknown":3}
location_score_map = {"Hand":3,"Face":2,"Leg":1,"Other":1}
depth_score_map = {"Deep":2,"Superficial":1}
delay_score_map = {">6h":2,"<6h":1}

# Button
if st.button("Calculate Risk"):
    if not all_selected:
        st.warning("⚠️ Please complete all required fields")
    else:
        score = (
            animal_score_map[animal_type] +
            location_score_map[bite_location] +
            depth_score_map[bite_depth] +
            delay_score_map[time_delay]
        )

        # Risk Level
        if score <= 3:
            risk_level = "LOW"
        elif 4 <= score <= 6:
            risk_level = "MODERATE"
        else:
            risk_level = "HIGH"

        # Decisions
        tetanus_decision = "No booster required" if tetanus_status == "Up-to-date" else "Tetanus booster recommended (+ consider immunoglobulin in high-risk wounds)"

        if animal_type == "Bat":
            rabies_decision = "Rabies PEP REQUIRED"
        elif animal_status in ["Unknown","Suspected"]:
            rabies_decision = "Rabies PEP recommended"
        elif animal_type in ["Dog","Cat"] and animal_status == "Healthy":
            rabies_decision = "Assess - may not require PEP"
        else:
            rabies_decision = "Assess clinically"

        immediate_care = "Wash wound >= 15 min | Irrigation | Debridement"

        if risk_level == "HIGH":
            treatment = "Antibiotics (Amoxicillin-clavulanate) | Tetanus assessment | Rabies PEP"
        elif risk_level == "MODERATE":
            treatment = "Consider antibiotics | Follow-up"
        else:
            treatment = "Clean & observe"

        # -------------------------
        # Display
        # -------------------------
        st.subheader("📊 Risk Assessment")
        st.metric("Risk Score", score)

        if risk_level == "HIGH":
            st.error(f"Risk Level: {risk_level}")
        elif risk_level == "MODERATE":
            st.warning(f"Risk Level: {risk_level}")
        else:
            st.success(f"Risk Level: {risk_level}")

        st.subheader("🩺 Clinical Plan")
        st.info(f"Immediate Care: {immediate_care}")
        st.write(f"Treatment: {treatment}")

        st.subheader("💉 Tetanus Decision")
        st.write(tetanus_decision)

        st.subheader("🦠 Rabies Decision")
        st.write(rabies_decision)

        # -------------------------
        # PDF Generation
        # -------------------------
        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 16)
                self.cell(0, 10, "Animal Bite Medical Report", 0, 1, "C")

        pdf = PDF()
        pdf.add_page()

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0,10,"Patient Information", ln=True)

        pdf.set_font("Arial", size=11)
        pdf.cell(0,8,f"Name: {patient_name}", ln=True)
        pdf.cell(0,8,f"Age: {age}", ln=True)
        pdf.cell(0,8,f"Sex: {sex}", ln=True)
        pdf.cell(0,8,f"Date: {visit_date}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0,10,"Clinical Details", ln=True)
        pdf.set_font("Arial", size=11)

        pdf.cell(0,8,f"Animal: {animal_type}", ln=True)
        pdf.cell(0,8,f"Location: {bite_location}", ln=True)
        pdf.cell(0,8,f"Depth: {bite_depth}", ln=True)
        pdf.cell(0,8,f"Delay: {time_delay}", ln=True)
        pdf.cell(0,8,f"Score: {score}", ln=True)
        pdf.cell(0,8,f"Risk Level: {risk_level}", ln=True)
        pdf.ln(5)

        pdf.multi_cell(0,8,f"Immediate Care: {immediate_care}")
        pdf.multi_cell(0,8,f"Treatment: {treatment}")
        pdf.multi_cell(0,8,f"Tetanus: {tetanus_decision}")
        pdf.multi_cell(0,8,f"Rabies: {rabies_decision}")

        if additional_notes.strip() != "":
            pdf.ln(3)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0,10,"Additional Notes", ln=True)
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0,8, additional_notes)

        pdf_output = "report.pdf"
        pdf.output(pdf_output)

        with open(pdf_output, "rb") as f:
            st.download_button("📄 Download Medical Report PDF", f, file_name="Animal_Bite_Report.pdf")

st.markdown("---")
st.caption("For educational purposes only")
