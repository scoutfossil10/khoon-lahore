import streamlit as st
import csv
from datetime import date

st.set_page_config(page_title="Khoon - Lahore Blood Connect")
st.title("Khoon - Lahore Blood Connect")
st.warning("This is a student project, NOT an emergency service. For emergency, call Rescue 1122.")

donors = []
with open('donors.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        donors.append(row)

safe_donors = []
today = date.today()
for d in donors:
    if d['LastDonation'] == 'Never' or d['LastDonation'] == '':
        safe_donors.append(d)
    else:
        try:
            y,m,dd = map(int, d['LastDonation'].split('-'))
            last = date(y,m,dd)
            diff = (today - last).days
            if diff >= 90:
                safe_donors.append(d)
        except:
            pass

st.success(f"Total Safe Donors Available: {len(safe_donors)}")

blood = st.selectbox("Select Blood Group", ["O+","O-","A+","A-","B+","B-","AB+","AB-"])
area = st.selectbox("Select Area", ["DHA","Johar Town","Model Town","Gulberg","Cantt","Other"])

if st.button("Search Donors"):
    found = []
    for d in safe_donors:
        if d['BloodGroup'] == blood and d['Area'] == area:
            found.append(d)
    
    if len(found) == 0:
        st.error("No safe donor found in this area. Try another area.")
    else:
        for d in found:
            st.write(f"**{d['Name']}** - {d['BloodGroup']} - {d['Area']}")
            phone = d['Phone']
            if phone.startswith('0'):
                phone = '92' + phone[1:]
            st.link_button(f"WhatsApp {d['Name']}", f"https://wa.me/{phone}")