import streamlit as st

st.title("Er software")

nome = st.text_input("Inserisci il tuo nome:")

if st.button("Saluta"):
    st.write(f"Ciao {nome}, benvenuto dentro ar software!")
