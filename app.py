import streamlit as st
import csv
import os

st.title("Er software")

email = st.text_input("Inserisci la tua email")

if email:
    nome_file = email.replace("@","_").replace(".","_") + ".csv"

    nome = st.text_input("Come ti chiami?")
    età = st.text_input("Quanti anni hai?")
    scuola = st.text_input("Che scuola frequenti?")

    if st.button("Sono di sesso maschile"):
        sesso = ("Maschio")
    if st.button("Sono di sesso femminile"):
        sesso = ("Femmina")
    if st.button("Preferisco non rispondere"):
        sesso = ("Indefinito")
        
    if st.button ("salva"):
        with open(nome_file, "a", newline="") as f:
            writer= csv.writer(f)
            writer.writerow([nome, età, scuola, sesso])
            st.success("Dati salvati")
    if os.path.exsists(nome_file):
        st.write("I tuoi dati salvati:")
        with open(nome_file, "r") as f:
            st.text(f.read())

