import streamlit as st
from supabase import create_client
import time

# --- Config Supabase ---
URL_SUPABASE = "https://hcyuowvrrjccmvcgebaj.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3NjExOTYsImV4cCI6MjA4OTMzNzE5Nn0.rpMn8jxHagUJsOLjJXW79oV5ogUnGhxv-kr9TGWhj98" 
supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

st.set_page_config(page_title="Beginner Collab", layout="centered")
st.title("🎵 Beginner Collab")

# Inizializzazione session state per il login
if "utente_loggato" not in st.session_state:
    st.session_state.utente_loggato = None

# --- 1. PANNELLO ACCESSO / LOGIN ---
with st.expander("🔑 Accedi per modificare il tuo profilo"):
    nome_login = st.text_input("Inserisci il tuo Nome registrato", key="login_nome")
    if st.button("Accedi"):
        res = supabase.table("utenti").select("*").eq("nome", nome_login).execute()
        if res.data:
            st.session_state.utente_loggato = res.data[0]
            st.success(f"Bentornato {nome_login}! Ora puoi modificare i tuoi dati qui sotto.")
        else:
            st.error("Nome non trovato. Registrati se è la prima volta.")

# --- 2. PANNELLO CREAZIONE O MODIFICA ---
titolo_pannello = "📝 Modifica il tuo Profilo" if st.session_state.utente_loggato else "➕ Crea il tuo profilo"
with st.expander(titolo_pannello, expanded=st.session_state.utente_loggato is not None):
    
    # Pre-compilazione se loggato
    default_nome = st.session_state.utente_loggato["nome"] if st.session_state.utente_loggato else ""
    default_contatto = st.session_state.utente_loggato["contatto"] if st.session_state.utente_loggato else ""
    default_ruolo = st.session_state.utente_loggato["ruolo"] if st.session_state.utente_loggato else "produttore"
    
    nome_input = st.text_input("Nome d'arte / Nome", value=default_nome)
    contatto_input = st.text_input("Contatto (Instagram, email, ecc)", value=default_contatto)
    ruoli = ["produttore", "cantante", "spettatore"]
    ruolo_input = st.selectbox("Chi sei?", ruoli, index=ruoli.index(default_ruolo))
    
    audio_files = st.file_uploader(
        "Carica nuovi audio (Aggiungerà nuovi file a quelli esistenti)",
        type=["mp3"],
        accept_multiple_files=True
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Salva / Aggiorna Profilo"):
            if not nome_input:
                st.warning("Il nome è obbligatorio!")
            else:
                new_audio_urls = []
                # Se l'utente è loggato, manteniamo i vecchi audio
                if st.session_state.utente_loggato:
                    new_audio_urls = st.session_state.utente_loggato.get("audio_url", [])

                # Upload nuovi file se presenti
                if audio_files:
                    for f in audio_files:
                        nome_file_storage = f"{int(time.time())}_{f.name.replace(' ', '_')}"
                        try:
                            supabase.storage.from_("audio").upload(nome_file_storage, f.read(), {"content_type": "audio/mpeg"})
                            url = str(supabase.storage.from_("audio").get_public_url(nome_file_storage))
                            new_audio_urls.append(url)
                        except: pass

                dati_profilo = {
                    "nome": nome_input,
                    "ruolo": ruolo_input,
                    "contatto": contatto_input,
                    "audio_url": new_audio_urls
                }

                if st.session_state.utente_loggato:
                    # UPDATE
                    supabase.table("utenti").update(dati_profilo).eq("id", st.session_state.utente_loggato["id"]).execute()
                    st.success("Profilo aggiornato!")
                else:
                    # INSERT (nuovo utente)
                    supabase.table("utenti").insert(dati_profilo).execute()
                    st.success("Profilo creato!")
                
                st.session_state.utente_loggato = None # Reset dopo il salvataggio
                st.cache_data.clear()
                st.rerun()
    
    with col2:
        if st.session_state.utente_loggato:
            if st.button("Esci senza salvare"):
                st.session_state.utente_loggato = None
                st.rerun()

# --- 3. RICERCA E VISUALIZZAZIONE (Inalterata) ---
st.divider()
st.subheader("🔎 Esplora la community")

@st.cache_data(ttl=10)
def get_utenti():
    try: return supabase.table("utenti").select("*").execute()
    except: return None

response = get_utenti()

if response and response.data:
    c1, c2 = st.columns(2)
    with c1: r_nome = st.text_input("Cerca per nome")
    with c2: f_ruolo = st.selectbox("Filtra per Ruolo", ["tutti", "produttore", "cantante", "spettatore"])

    for u in response.data:
        if r_nome and r_nome.lower() not in u["nome"].lower(): continue
        if f_ruolo != "tutti" and u["ruolo"] != f_ruolo: continue

        with st.container():
            st.markdown(f"### 👤 {u['nome']}")
            st.write(f"**{u['ruolo'].capitalize()}** | 📩 {u.get('contatto', 'N/A')}")
            urls = u.get("audio_url", [])
            if urls:
                for link in urls:
                    if isinstance(link, str) and link.startswith("http"):
                        st.audio(link)
            st.divider()

# --- 4. FEEDBACK ---
st.subheader("💬 Invia un feedback")
f_text = st.text_area("Suggerimenti")
if st.button("Invia feedback"):
    if f_text:
        supabase.table("feedback").insert({"messaggio": f_text, "nome": nome_input if nome_input else "Anonimo"}).execute()
        st.success("Inviato!")



