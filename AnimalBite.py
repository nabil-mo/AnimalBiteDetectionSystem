#!/usr/bin/env python
# coding: utf-8

# In[1]:


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

animal_type = st.selectbox("Animal Type", [placeholder, "Dog","Cat","Monkey","Bat","Rodent","Livestock","Unknown"])
bite_location = st.selectbox("Bite Location", [placeholder, "Hand","Face / Neck","Near joint","Leg","Other"])
bite_depth = st.selectbox("Bite Depth", [placeholder, "Superficial","Moderate","Deep"])
time_delay = st.selectbox("Time Delay", [placeholder, "<6 hours","6–12 hours","12 hours"])
tetanus_status = st.selectbox("Tetanus Vaccination", [placeholder, "Up-to-date","Unknown/Incomplete"])
animal_status = st.selectbox("Animal Status", [placeholder, "Healthy & vaccinated","Healthy (not vaccinated)","Unknown / stray","Sick / abnormal behavior"])
clothing = st.selectbox("Clothing Barrier", [placeholder, "Yes","No"])
rabies_vaccination = st.selectbox("Rabies Vaccination", [placeholder, "Up-to-date","Unknown/Incomplete"])

# Validation
all_selected = all([
    animal_type != placeholder,
    bite_location != placeholder,
    bite_depth != placeholder,
    time_delay != placeholder,
    tetanus_status != placeholder,
    animal_status != placeholder,
    clothing != placeholder,
    rabies_vaccination != placeholder,
    patient_name.strip() != "",
    sex != placeholder
])

# Scoring maps
animal_score_map = {"Cat":3,"Dog":2,"Monkey":3,"Bat":3,"Rodent":2,"Livestock":2,"Unknown":3}
location_score_map = {"Hand":3,"Face / Neck":3,"Near joint":3,"Leg":2,"Other":1}
depth_score_map = {"Deep":3,"Moderate":2,"Superficial":1}
delay_score_map = {"12 hours":3,"6–12 hours":2,"<6 hours":1}
tetanus_score_map = {"Unknown/Incomplete":2,"Up-to-date":0}
animal_status_score_map = {"Sick / abnormal behavior":4,"Unknown / stray":3,"Healthy (not vaccinated)":2,"Healthy & vaccinated":0}
clothing_score_map = {"No":1,"Yes":0}

# Button
if st.button("Calculate Risk"):
    if not all_selected:
        st.warning("⚠️ Please complete all required fields")
    else:
        score = (
            animal_score_map[animal_type] +
            location_score_map[bite_location] +
            depth_score_map[bite_depth] +
            delay_score_map[time_delay] +
            tetanus_score_map[tetanus_status] +
            animal_status_score_map[animal_status] +
            clothing_score_map[clothing]
        )

        # Risk Level
        if score <= 6:
            risk_level = "LOW"
        elif 7 <= score <= 13:
            risk_level = "MODERATE"
        else:
            risk_level = "HIGH"

        # -------------------------
        # Visual Risk Bar
        # -------------------------
        st.subheader("📊 Risk Assessment")
        st.metric("Risk Score", score)

        progress_value = min(score / 20, 1.0)
        st.progress(progress_value)

        if risk_level == "HIGH":
            st.error(f"Risk Level: {risk_level}")
        elif risk_level == "MODERATE":
            st.warning(f"Risk Level: {risk_level}")
        else:
            st.success(f"Risk Level: {risk_level}")

        # Decisions
        tetanus_decision = "No booster required" if tetanus_status == "Up-to-date" else "Tetanus booster recommended (+ consider immunoglobulin in high-risk wounds)"

        if animal_type == "Bat":
            rabies_decision = "Rabies PEP REQUIRED"
        elif animal_status in ["Unknown / stray", "Sick / abnormal behavior"]:
            rabies_decision = "Rabies PEP recommended"
        else:
            rabies_decision = "Assess clinically"

        immediate_care = "Wash wound >= 15 min | Irrigation | Debridement"

        if risk_level == "HIGH":
            treatment = "Antibiotics (Amoxicillin-clavulanate) | Tetanus assessment | Rabies PEP"
        elif risk_level == "MODERATE":
            treatment = "Consider antibiotics | Follow-up"
        else:
            treatment = "Clean & observe"

        st.subheader("🩺 Clinical Plan")
        st.info(f"Immediate Care: {immediate_care}")
        st.write(f"Treatment: {treatment}")

        st.subheader("💉 Tetanus Decision")
        st.write(tetanus_decision)

        st.subheader("🦠 Rabies Decision")
        st.write(rabies_decision)

        # -------------------------
        # Professional PDF
        # -------------------------
        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 16)
                self.cell(0, 10, "Animal Bite Medical Report", 0, 1, "C")
                self.ln(2)

        pdf = PDF()
        pdf.add_page()

        def section(title):
            pdf.set_font("Arial", "B", 12)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(0, 8, title, 0, 1, "L", True)
            pdf.ln(1)

        def line(text):
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 6, text)

        # Patient
        section("Patient Information")
        line(f"Name: {patient_name}")
        line(f"Age: {age}")
        line(f"Sex: {sex}")
        line(f"Date: {visit_date}")

        # Clinical
        section("Clinical Details")
        line(f"Animal: {animal_type}")
        line(f"Location: {bite_location}")
        line(f"Depth: {bite_depth}")
        line(f"Delay: {time_delay}")
        line(f"Animal Status: {animal_status}")
        line(f"Clothing Barrier: {clothing}")
        line(f"Rabies Vaccination: {rabies_vaccination}")

        # Risk
        section("Risk Assessment")
        line(f"Score: {score}")
        line(f"Risk Level: {risk_level}")

        # Plan
        section("Clinical Plan")
        line(f"Immediate Care: {immediate_care}")
        line(f"Treatment: {treatment}")

        section("Tetanus")
        line(tetanus_decision)

        section("Rabies")
        line(rabies_decision)

        if additional_notes.strip():
            section("Additional Notes")
            line(additional_notes)

        pdf_file = "report.pdf"
        pdf.output(pdf_file)

        with open(pdf_file, "rb") as f:
            st.download_button("📄 Download Medical Report PDF", f, file_name="Animal_Bite_Report.pdf")

st.markdown("---")
st.caption("By Suez Canal University students")


# In[ ]:




