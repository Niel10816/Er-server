import streamlit as st
import pandas as pd

st.title("Er software")
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
        dati = pd.DataFrame([[nome, eta, scuola, sesso]],
                            colnums=["nome", "età", "scuola", "Sesso"])
        csv = dati.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Scarica il tuo file",
            data=csv,
            fle_name='i_miei_dati.csv'
            mine='text/csv'
            )
        st.success("Puoi scaricare i tuoi dati sul tuo computer!")

