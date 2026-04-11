#!/usr/bin/env python
# coding: utf-8

# In[2]:


import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Animal Bite Risk Assessment", layout="centered")

st.title("🐾 Animal Bite Risk Assessment Tool")

# Helper placeholder
placeholder = "-- Select --"

# Inputs (no default selections)
animal_type = st.selectbox("Animal Type", [placeholder, "Dog","Cat","Monkey","Rat","Camel","Bat","Unknown"])
bite_location = st.selectbox("Bite Location", [placeholder, "Hand","Face","Leg","Other"])
bite_depth = st.selectbox("Bite Depth", [placeholder, "Superficial","Deep"])
time_delay = st.selectbox("Time Delay", [placeholder, "<6h",">6h"])
tetanus_status = st.selectbox("Tetanus Vaccination", [placeholder, "Up-to-date","Unknown/Incomplete"])
animal_status = st.selectbox("Animal Status", [placeholder, "Healthy","Suspected","Unknown"])

# Check if all inputs selected
all_selected = all([
    animal_type != placeholder,
    bite_location != placeholder,
    bite_depth != placeholder,
    time_delay != placeholder,
    tetanus_status != placeholder,
    animal_status != placeholder
])

# Scoring maps
animal_score_map = {"Cat":3,"Dog":2,"Monkey":3,"Rat":2,"Camel":2,"Bat":3,"Unknown":3}
location_score_map = {"Hand":3,"Face":2,"Leg":1,"Other":1}
depth_score_map = {"Deep":2,"Superficial":1}
delay_score_map = {">6h":2,"<6h":1}

if st.button("Calculate Risk"):
    if not all_selected:
        st.warning("⚠️ Please fill all fields before calculation")
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

        # Tetanus Decision
        if tetanus_status == "Up-to-date":
            tetanus_decision = "No booster required"
        else:
            tetanus_decision = "Tetanus booster recommended (+ consider immunoglobulin in high-risk wounds)"

        # Rabies Decision
        if animal_type == "Bat":
            rabies_decision = "Rabies PEP REQUIRED"
        elif animal_status in ["Unknown","Suspected"]:
            rabies_decision = "Rabies PEP recommended"
        elif animal_type in ["Dog","Cat"] and animal_status == "Healthy":
            rabies_decision = "Assess - may not require PEP"
        else:
            rabies_decision = "Assess clinically"

        # Clinical Plan
        immediate_care = "Wash wound >= 15 min | Irrigation | Debridement"

        if risk_level == "HIGH":
            treatment = "Antibiotics (Amoxicillin-clavulanate) | Tetanus assessment | Rabies PEP"
        elif risk_level == "MODERATE":
            treatment = "Consider antibiotics | Follow-up"
        else:
            treatment = "Clean & observe"

        # Display
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

        # PDF Generation
        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 16)
                self.cell(0, 10, "Animal Bite Medical Report", 0, 1, "C")

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(0,10,f"Animal: {animal_type}", ln=True)
        pdf.cell(0,10,f"Location: {bite_location}", ln=True)
        pdf.cell(0,10,f"Depth: {bite_depth}", ln=True)
        pdf.cell(0,10,f"Delay: {time_delay}", ln=True)
        pdf.cell(0,10,f"Score: {score}", ln=True)
        pdf.cell(0,10,f"Risk Level: {risk_level}", ln=True)
        pdf.ln(5)

        pdf.multi_cell(0,10,f"Immediate Care: {immediate_care}")
        pdf.multi_cell(0,10,f"Treatment: {treatment}")
        pdf.multi_cell(0,10,f"Tetanus: {tetanus_decision}")
        pdf.multi_cell(0,10,f"Rabies: {rabies_decision}")

        pdf_output = "report.pdf"
        pdf.output(pdf_output)

        with open(pdf_output, "rb") as f:
            st.download_button("📄 Download Medical Report PDF", f, file_name="Animal_Bite_Report.pdf")

st.markdown("---")
st.caption("For educational purposes only")


# In[ ]:




