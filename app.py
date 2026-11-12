import streamlit as st
import urllib.request
import urllib.parse
import csv
import io

st.set_page_config(page_title="Khoon - Lahore Blood Connect", page_icon="🩸")
st.title("Khoon - Lahore Blood Connect")
st.warning("This is a student project, NOT an emergency service. For emergency, call Rescue 1122.")

# Direct button to your Google Form
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd3krS-WmWd_lShF0ERhxWOzqUmDhXoEZpE5gnjm0FRC2UNYQ/viewform"
st.link_button("Register as a Blood Donor", FORM_URL)

# Paste your Published Google Sheet CSV URL below (must end with output=csv)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRNWmE82wF1xjM6mShGRd9DdSu8LHJnl1RjAZqQ-h8TR0L4k7o9IvMknZ-5t0Ra9onsAC9KOPXzHuFE/pub?gid=302994287&single=true&output=csv"

# Blood compatibility chart (Recipient : [Compatible Donor Blood Groups])
COMPATIBILITY = {
    "O-": ["O-"],
    "O+": ["O+", "O-"],
    "A-": ["A-", "O-"],
    "A+": ["A+", "A-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "AB-": ["AB-", "A-", "B-", "O-"],
    "AB+": ["AB+", "AB-", "A+", "A-", "B+", "B-", "O+", "O-"]
}

@st.cache_data(ttl=60)
def load_donors():
    if SHEET_CSV_URL.startswith("http"):
        response = urllib.request.urlopen(SHEET_CSV_URL)
        lines = response.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(lines))
        return list(reader)
    return []

# Exact question headers from your Google Form
COL_NAME = "Name?"
COL_AGE = "Are you 18+?"
COL_WILLING = "Are you willing to donate?"
COL_BLOOD = "Blood Group - O+, O-, A+, A-, B+, B-, AB+, AB-"
COL_AREA = "Area - DHA, Johar Town, Model Town, Gulberg, Cantt, Other"
COL_LAST = "When did you last donate? - Never / More than 3 months ago / Less than 3 months ago"
COL_PHONE = "WhatsApp Number:"
COL_CONSENT = "Do you agree to register?"

donors = load_donors()
st.write("Total rows loaded:", len(donors))
st.write("First row data:", donors[0] if donors else "EMPTY")

safe_donors = []

for d in donors:
    is_18 = str(d.get(COL_AGE, "")).strip().lower() == "yes"
    is_willing = str(d.get(COL_WILLING, "")).strip().lower() == "yes"
    has_consent = str(d.get(COL_CONSENT, "")).strip().lower() == "yes"
    last_don = str(d.get(COL_LAST, "")).strip()
    is_safe_time = last_don in ["Never", "More than 3 months ago"]
    # Works whether your column is named Approved or APPROVED
    approved_val = d.get("Approved") or d.get("APPROVED") or ""
    is_approved = str(approved_val).strip().lower() == "yes"

    if is_18 and is_willing and has_consent and is_safe_time and is_approved:
        safe_donors.append(d)

st.success(f"Total Safe Donors Available: {len(safe_donors)}")

blood = st.selectbox("Select Required Blood Group", list(COMPATIBILITY.keys()))
area = st.selectbox("Select Area", ["DHA", "Johar Town", "Model Town", "Gulberg", "Cantt", "Other"])

if st.button("Search Donors"):
    compatible_types = COMPATIBILITY[blood]
    found = [
        d for d in safe_donors
        if str(d.get(COL_BLOOD, "")).strip() in compatible_types and str(d.get(COL_AREA, "")).strip() == area
    ]

    # Put exact blood group matches at the top
    found.sort(key=lambda x: str(x.get(COL_BLOOD, "")).strip() != blood)

    if len(found) == 0:
        st.error("No safe compatible donor found in this area. Try another area.")
    else:
        for d in found:
            donor_blood = str(d.get(COL_BLOOD, "")).strip()
            match_label = "Exact Match" if donor_blood == blood else f"Compatible ({donor_blood})"
            st.write(f"**{d[COL_NAME]}** - {match_label} - {d[COL_AREA]}")

            phone = str(d[COL_PHONE]).replace("-", "").replace(" ", "").strip()
            if phone.startswith("0"):
                phone = "92" + phone[1:]

            msg = urllib.parse.quote(
                f"Assalam-o-Alaikum {d[COL_NAME]}, I found your contact on Khoon Lahore Blood Connect. "
                f"We need {blood} blood in {area}."
            )
            st.link_button(f"WhatsApp {d[COL_NAME]}", f"https://wa.me{phone}?text={msg}")
