import streamlit as st
from supabase import create_client
import time
import datetime

# --- Config Supabase ---
URL_SUPABASE = "https://hcyuowvrrjccmvcgebaj.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3NjExOTYsImV4cCI6MjA4OTMzNzE5Nn0.rpMn8jxHagUJsOLjJXW79oV5ogUnGhxv-kr9TGWhj98" 
supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

st.set_page_config(page_title="Beginner Collab", layout="centered")
st.title("Beginner Collab")

# Inizializzazione session state
if "utente_loggato" not in st.session_state:
    st.session_state.utente_loggato = None

# --- 1. PANNELLO ACCESSO / LOGIN ---
with st.expander("Accedi"):
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        nome_login = st.text_input("Nome registrato", key="login_nome")
    with col_l2:
        pass_login = st.text_input("Password", type="password", key="login_pass")
    
    if st.button("Accedi"):
        res = supabase.table("utenti").select("*").eq("nome", nome_login).eq("password", pass_login).execute()
        if res.data:
            st.session_state.utente_loggato = res.data[0]
            st.success(f"Bentornato {nome_login}!")
            st.rerun()
        else:
            st.error("Dati errati.")

# --- 2. PANNELLO CREAZIONE O MODIFICA ---
loggato = st.session_state.utente_loggato
titolo_pannello = "Modifica il tuo Profilo" if loggato else "Registrati"

with st.expander(titolo_pannello, expanded=loggato is not None):
    d_nome = loggato["nome"] if loggato else ""
    d_contatto = loggato["contatto"] if loggato else ""
    d_ruolo = loggato["ruolo"] if loggato else "produttore"
    d_nota = loggato.get("nota", "") if loggato else ""
    lista_audio_corrente = loggato.get("audio_url", []) if loggato else []
    
    nome_input = st.text_input("Nome d'arte / Nome", value=d_nome)
    pass_input = st.text_input("Password", type="password", value=loggato["password"] if loggato else "")
    contatto_input = st.text_input("Contatto", value=d_contatto)
    
    ruoli = ["produttore", "cantante", "spettatore"]
    ruolo_input = st.selectbox("Chi sei?", ruoli, index=ruoli.index(d_ruolo))

    # --- Sezione Nota (Sia per Registrazione che per Modifica) ---
    st.write("---")
    st.subheader("📝 Nota del Giorno (24h)")
    nota_input = st.text_input("Cosa hai in mente? (Opzionale)", value=d_nota, max_chars=60)
    
    if loggato:
        c_n1, c_n2 = st.columns(2)
        with c_n1:
            if st.button("Aggiorna solo Nota"):
                ora_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                supabase.table("utenti").update({"nota": nota_input, "nota_timestamp": ora_iso}).eq("id", loggato["id"]).execute()
                st.success("Nota aggiornata!")
                st.rerun()
        with c_n2:
            if st.button("Cancella Nota"):
                supabase.table("utenti").update({"nota": None, "nota_timestamp": None}).eq("id", loggato["id"]).execute()
                st.success("Nota rimossa!")
                st.rerun()

    if loggato and lista_audio_corrente:
        st.write("---")
        st.write("🗑️ **Gestisci i tuoi audio:**")
        nuova_lista_audio = lista_audio_corrente.copy()
        for i, url in enumerate(lista_audio_corrente):
            col_a, col_b = st.columns([3, 1])
            with col_a: st.audio(url)
            with col_b:
                if st


