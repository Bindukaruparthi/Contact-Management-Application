import re
import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Contact Manager", layout="wide")

# Database connection
conn = sqlite3.connect('contacts.db', check_same_thread=False)
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS contacts
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              first_name TEXT,
              last_name TEXT,
              address TEXT,
              email TEXT UNIQUE,
              phone TEXT)''')
conn.commit()

# UI Header
st.markdown("<h1 style='text-align: center;'>📇 Contact Management App</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Manage your contacts efficiently</p>", unsafe_allow_html=True)

# Sidebar Menu
menu = ["➕ Create", "📄 View", "✏️ Update", "🗑️ Delete"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- CREATE ----------------
if choice == "➕ Create":
    st.markdown("### ➕ Create New Contact")

    col1, col2 = st.columns(2)

    with col1:
        first = st.text_input("First Name")
        email = st.text_input("Email")

    with col2:
        last = st.text_input("Last Name")
        phone = st.text_input("Phone")

    address = st.text_area("Address")

    if st.button("Add Contact"):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not re.match(pattern, email):
            st.error("Invalid email format")
        elif not phone.isdigit():
            st.error("Phone must contain only numbers")
        else:
            try:
                c.execute("INSERT INTO contacts VALUES (NULL,?,?,?,?,?)",
                          (first, last, address, email, phone))
                conn.commit()
                st.success("✅ Contact added successfully")
            except:
                st.error("Email already exists")

# ---------------- VIEW ----------------
elif choice == "📄 View":
    st.markdown("### 📄 View Contacts")
    data = c.execute("SELECT * FROM contacts").fetchall()

    df = pd.DataFrame(data, columns=[
        "ID", "First Name", "Last Name", "Address", "Email", "Phone"
    ])

    st.dataframe(df, use_container_width=True, hide_index=True)

# ---------------- UPDATE ----------------
elif choice == "✏️ Update":
    st.markdown("### ✏️ Update Contact")
    data = c.execute("SELECT * FROM contacts").fetchall()

    if data:
        options = {f"{i[1]} {i[2]} (ID:{i[0]})": i[0] for i in data}
        selected_label = st.selectbox("Select Contact", list(options.keys()))
        selected = options[selected_label]

        record = c.execute("SELECT * FROM contacts WHERE id=?", (selected,)).fetchone()

        first = st.text_input("First Name", record[1])
        last = st.text_input("Last Name", record[2])
        address = st.text_area("Address", record[3])
        email = st.text_input("Email", record[4])
        phone = st.text_input("Phone", record[5])

        if st.button("Update Contact"):
            c.execute("""UPDATE contacts 
                         SET first_name=?, last_name=?, address=?, email=?, phone=? 
                         WHERE id=?""",
                      (first, last, address, email, phone, selected))
            conn.commit()
            st.success("✅ Contact Updated")

    else:
        st.warning("No contacts available to update")

# ---------------- DELETE ----------------
elif choice == "🗑️ Delete":
    st.markdown("### 🗑️ Delete Contact")
    data = c.execute("SELECT * FROM contacts").fetchall()

    if data:
        options = {f"{i[1]} {i[2]} (ID:{i[0]})": i[0] for i in data}
        selected_label = st.selectbox("Select Contact", list(options.keys()))
        selected = options[selected_label]

        st.warning("⚠️ This action cannot be undone")

        if st.button("Delete Contact"):
            c.execute("DELETE FROM contacts WHERE id=?", (selected,))
            conn.commit()
            st.success("✅ Contact Deleted")

    else:
        st.warning("No contacts available to delete")