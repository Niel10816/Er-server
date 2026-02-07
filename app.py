import streamlit as st
import pandas as pd

st.title("Er software")
nome = st.text_input("Come ti chiami?")
eta = st.text_input("Quanti anni hai?")
scuola = st.text_input("Che scuola frequenti?")
sesso = st.text_input("Scrivi il tuo sesso. Se non vuoi scriverlo scrivi indefinito")

        
if st.button ("salva"):
        dati = pd.DataFrame([[nome, eta, scuola, sesso]],
                            columns=["nome", "età", "scuola", "Sesso"])
        csv = dati.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Scarica il tuo file",
            data=csv,
            fle_name='i_miei_dati.csv',
            mine='text/csv'
            )
        st.success("Puoi scaricare i tuoi dati sul tuo computer!")







