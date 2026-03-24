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
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        nome_login = st.text_input("Nome registrato", key="login_nome")
    with col_l2:
        pass_login = st.text_input("Password", type="password", key="login_pass")
    
    if st.button("Accedi"):
        # Cerchiamo l'utente che ha quel nome E quella password
        res = supabase.table("utenti").select("*").eq("nome", nome_login).eq("password", pass_login).execute()
        
        if res.data:
            st.session_state.utente_loggato = res.data[0]
            st.success(f"Bentornato {nome_login}! Modifica i tuoi dati qui sotto.")
            st.rerun()
        else:
            st.error("Nome o Password errati. Riprova.")

# --- 2. PANNELLO CREAZIONE O MODIFICA ---
loggato = st.session_state.utente_loggato
titolo_pannello = "📝 Modifica il tuo Profilo" if loggato else "➕ Crea il tuo profilo"

with st.expander(titolo_pannello, expanded=loggato is not None):
    
    # Valori di default
    d_nome = loggato["nome"] if loggato else ""
    d_contatto = loggato["contatto"] if loggato else ""
    d_ruolo = loggato["ruolo"] if loggato else "produttore"
    
    nome_input = st.text_input("Nome d'arte / Nome", value=d_nome)
    pass_input = st.text_input("Scegli una Password", type="password", help="Ti servirà per modificare il profilo in futuro")
    contatto_input = st.text_input("Contatto (Instagram, email, ecc)", value=d_contatto)
    
    ruoli = ["produttore", "cantante", "spettatore"]
    ruolo_input = st.selectbox("Chi sei?", ruoli, index=ruoli.index(d_ruolo))
    
    audio_files = st.file_uploader(
        "Carica audio (MP3)",
        type=["mp3"],
        accept_multiple_files=True
    )

    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        testo_bottone = "Aggiorna Profilo" if loggato else "Crea Profilo"
        if st.button(testo_bottone):
            if not nome_input or not pass_input:
                st.warning("Nome e Password sono obbligatori!")
            else:
                lista_audio = loggato.get("audio_url", []) if loggato else []

                # Upload nuovi file
                if audio_files:
                    for f in audio_files:
                        nome_f = f"{int(time.time())}_{f.name.replace(' ', '_')}"
                        try:
                            supabase.storage.from_("audio").upload(nome_f, f.read(), {"content_type": "audio/mpeg"})
                            url = str(supabase.storage.from_("audio").get_public_url(nome_f))
                            lista_audio.append(url)
                        except: pass

                # Dati da inviare
                payload = {
                    "nome": nome_input,
                    "password": pass_input, # Salviamo la password
                    "ruolo": ruolo_input,
                    "contatto": contatto_input,
                    "audio_url": lista_audio
                }

                if loggato:
                    supabase.table("utenti").update(payload).eq("id", loggato["id"]).execute()
                    st.success("Profilo aggiornato!")
                else:
                    supabase.table("utenti").insert(payload).execute()
                    st.success("Profilo creato!")
                
                st.session_state.utente_loggato = None
                st.cache_data.clear()
                st.rerun()
    
    with col_btn2:
        if loggato:
            if st.button("Esci senza salvare"):
                st.session_state.utente_loggato = None
                st.rerun()

# --- 3. RICERCA E VISUALIZZAZIONE ---
st.divider()
st.subheader("🔎 Community")

@st.cache_data(ttl=10)
def get_utenti():
    try: return supabase.table("utenti").select("nome, ruolo, contatto, audio_url").execute()
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
            st.caption(f"**{u['ruolo'].upper()}** | 📩 {u.get('contatto', 'N/A')}")
            urls = u.get("audio_url", [])
            if urls:
                for link in urls:
                    if isinstance(link, str) and link.startswith("http"):
                        st.audio(link)
            st.divider()

# --- 4. FEEDBACK ---
st.subheader("💬 Feedback")
f_text = st.text_area("Suggerimenti", key="feedback_area")
if st.button("Invia"):
    if f_text:
        supabase.table("feedback").insert({"messaggio": f_text, "nome": nome_input if nome_input else "Anonimo"}).execute()
        st.success("Grazie!")
