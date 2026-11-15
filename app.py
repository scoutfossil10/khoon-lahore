import streamlit as st
import urllib.request
import urllib.parse
import csv
import io

st.set_page_config(page_title="Khoon - Lahore Blood Connect", page_icon="🩸")
st.title("Khoon - Lahore Blood Connect")
st.warning("This is a student project, NOT an emergency service. For emergency, call Rescue 1122.")
st.footer("To get yourself removed message +923344448421")
# Direct button to your Google Form
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd3krS-WmWd_lShF0ERhxWOzqUmDhXoEZpE5gnjm0FRC2UNYQ/viewform"
st.link_button("Register as a Blood Donor", FORM_URL)

# Paste your Published Google Sheet CSV URL below
SHEET_CSV_URL = st.secrets["SHEET_CSV_URL"]


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

# Helper function to find column value regardless of spaces or line breaks
def get_val(row, keyword):
    for k, v in row.items():
        if k and keyword.lower() in k.lower():
            return str(v).strip()
    return ""

donors = load_donors()
safe_donors = []

for d in donors:
    name = get_val(d, "Name")
    is_18 = get_val(d, "18+").lower() == "yes"
    is_willing = get_val(d, "willing to donate").lower() == "yes"
    has_consent = get_val(d, "agree to register").lower() == "yes"
    last_don = get_val(d, "last donate")
    is_safe_time = last_don in ["Never", "More than 3 months ago"]
    is_approved = get_val(d, "approved").lower() == "yes"

    if name and is_18 and is_willing and has_consent and is_safe_time and is_approved:
        safe_donors.append({
            "Name": name,
            "BloodGroup": get_val(d, "Blood Group"),
            "Area": get_val(d, "Area"),
            "Phone": get_val(d, "WhatsApp")
        })

st.success(f"Total Safe Donors Available: {len(safe_donors)}")

blood = st.selectbox("Select Required Blood Group", list(COMPATIBILITY.keys()))
area = st.selectbox("Select Area", ["DHA", "Johar Town", "Model Town", "Gulberg", "Cantt", "Other"])

if st.button("Search Donors"):
    compatible_types = COMPATIBILITY[blood]
    found = [
        d for d in safe_donors
        if d["BloodGroup"] in compatible_types and d["Area"] == area
    ]

    # Put exact blood group matches at the top
    found.sort(key=lambda x: x["BloodGroup"] != blood)

    if len(found) == 0:
        st.error("No safe compatible donor found in this area. Try another area.")
    else:
        for d in found:
            match_label = "Exact Match" if d["BloodGroup"] == blood else f"Compatible ({d['BloodGroup']})"
            st.write(f"**{d['Name']}** - {match_label} - {d['Area']}")

            phone = d["Phone"].replace("-", "").replace(" ", "").strip()
            if phone.startswith("0"):
                phone = "92" + phone[1:]

            msg = urllib.parse.quote(
                f"Assalam-o-Alaikum {d['Name']}, I found your contact on Khoon Lahore Blood Connect. "
                f"We need {blood} blood in {area}."
            )
            st.link_button(f"WhatsApp {d['Name']}", f"https://wa.me/{phone}?text={msg}")
