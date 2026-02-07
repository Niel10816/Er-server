import streamlit as st
import csv
import os

st.title("Er software")

email = st.text_input("Inserisci la tua email")

if email:
    nome_file = email.replace("@","_").replace(".","_") + ".csv"

    nome = st.text_input("Come ti chiami?")
    eta = st.text_input("Quanti anni hai?")
    scuola = st.text_input("Che scuola frequenti?")

    sesso = None
    col1, col2, col3 = st.columns(3)
    if col1.button("Sono di sesso maschile"):
        sesso = ("Maschio")
    if col2.button("Sono di sesso femminile"):
        sesso = ("Femmina")
    if col3.button("Preferisco non rispondere"):
        sesso = ("Indefinito")
        
    if st.button ("salva"):
        if sesso is None:
            st.error("Seleziona prima il nome")
        else:
            with open(nome_file, "a", newline="") as f:
                writer= csv.writer(f)
                writer.writerow([nome, eta, scuola, sesso])
                st.success("Dati salvati")
        
    if os.path.exsists(nome_file):
        st.write("I tuoi dati salvati:")
        with open(nome_file, "r") as f:
            st.text(f.read())




