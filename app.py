import streamlit as st
import pandas as pd

st.title("Er software")
nome = st.text_input("Come ti chiami?")
eta = st.text_input("Quanti anni hai?")
scuola = st.text_input("Che scuola frequenti?")

sesso = st.radio("Sesso", [Maschio, Femmina, Indefinito])
        
if st.button ("salva"):
    if not sesso:
        st.error("Seleziona prima il nome")
    else:
        dati = pd.DataFrame([[nome, eta, scuola, sesso]],
                            colnums=["nome", "età", "scuola", "Sesso"])
        csv = dati.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Scarica il tuo file",
            data=csv,
            fle_name='i_miei_dati.csv',
            mine='text/csv'
            )
        st.success("Puoi scaricare i tuoi dati sul tuo computer!")




