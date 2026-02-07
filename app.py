import streamlit as st
import pandas as pd

if 'dati' not in st.session_state:
    st.session_state.dati = pd.DataFrame(columns=["Nome", "Età", "Scuola", "Sesso"])

nome = st.text_input("Nome")
eta = st.text_input("Età")
scuola = st.text_input("Scuola")
sesso = st.radio("Sesso", ["Maschio", "Femmina", "Nessuno dei due"])

if st.button("Aggiungi alla tabella"):
    if nome and eta and scuola and sesso:
        nuova_riga = pd.DataFrame([[nome, eta, scuola, sesso]],
                                  columns=["Nome", "Età", "Scuola", "Sesso"])
        st.session_state.dati = pd.concat([st.session_state.dati, nuova_riga],
                                          ignore_index=True)
    else:
        st.error("Compila tutti i campi!")

st.dataframe(st.session_state.dati)

if st.button("Mostra dati copiabili"):
    st.code(st.session_state.dati.to_csv(index=False, sep="\t"), language='text')
    st.info("Seleziona il testo sopra per copiarlo e incollarlo dove vuoi!")

