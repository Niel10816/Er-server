import streamlit as st
from supabase import create_client
import time
import datetime

# --- Config Supabase ---
URL_SUPABASE = "https://hcyuowvrrjccmvcgebaj.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3NjExOTYsImV4cCI6MjA4OTMzNzE5Nn0.rpMn8jxHagUJsOLjJXW79oV5ogUnGhxv-kr9TGWhj98" 
supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

st.set_page_config(page_title="Beginner Collab", layout="centered")

# Inizializzazione session state
if "utente_loggato" not in st.session_state:
    st.session_state.utente_loggato = None

# --- 1. SCHERMATA DI ACCESSO (LOGIN/REGISTRAZIONE) ---
if st.session_state.utente_loggato is None:
    st.title("🎸 Beginner Collab")
    tab1, tab2 = st.tabs(["Accedi", "Registrati"])
    
    with tab1:
        n_log = st.text_input("Nome", key="l_n")
        p_log = st.text_input("Password", type="password", key="l_p")
        if st.button("Entra"):
            res = supabase.table("utenti").select("*").eq("nome", n_log).eq("password", p_log).execute()
            if res.data:
                st.session_state.utente_loggato = res.data[0]
                st.rerun()
            else: st.error("Dati errati")
            
    with tab2:
        n_reg = st.text_input("Scegli Nome", key="r_n")
        p_reg = st.text_input("Scegli Password", type="password", key="r_p")
        c_reg = st.text_input("Contatto (IG/Telegram)", key="r_c")
        r_reg = st.selectbox("Ruolo", ["produttore", "cantante", "spettatore"], key="r_r")
        if st.button("Crea Account"):
            payload = {"nome": n_reg, "password": p_reg, "contatto": c_reg, "ruolo": r_reg, "audio_url": [], "nota": None}
            supabase.table("utenti").insert(payload).execute()
            st.success("🎉 Profilo creato! Ora accedi.")
            time.sleep(1.5); st.rerun()
    st.stop()

# --- AREA RISERVATA ---
loggato = st.session_state.utente_loggato
st.sidebar.title(f"Ciao {loggato['nome']}")
if st.sidebar.button("Logout"):
    st.session_state.utente_loggato = None
    st.rerun()

st.title("🎸 Beginner Collab")

# --- 2. GESTIONE PROFILO E AUDIO (Pannello Funzionante) ---
with st.expander("⚙️ Gestisci il tuo Profilo e i tuoi Audio"):
    # Caricamento Nuovi Audio
    st.subheader("Carica nuovi MP3")
    audio_files = st.file_uploader("Seleziona file", type=["mp3"], accept_multiple_files=True)
    
    # Gestione Nota
    st.write("---")
    nota_att = loggato.get("nota", "")
    nuova_nota = st.text_input("Aggiorna la tua nota (24h):", value=nota_att if nota_att else "")
    
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        if st.button("Salva modifiche profilo"):
            final_audio = loggato.get("audio_url", [])
            if audio_files:
                for f in audio_files:
                    nome_f = f"{int(time.time())}_{f.name.replace(' ', '_')}"
                    supabase.storage.from_("audio").upload(nome_f, f.read(), {"content_type": "audio/mpeg"})
                    url_pub = str(supabase.storage.from_("audio").get_public_url(nome_f))
                    final_audio.append(url_pub)
            
            ora = datetime.datetime.now(datetime.timezone.utc).isoformat()
            payload = {"audio_url": final_audio, "nota": nuova_nota, "nota_timestamp": ora}
            supabase.table("utenti").update(payload).eq("id", loggato["id"]).execute()
            st.success("Profilo aggiornato!")
            time.sleep(1); st.rerun()
            
    # Visualizzazione ed eliminazione audio esistenti
    st.write("---")
    st.subheader("I tuoi audio:")
    miei_audio = loggato.get("audio_url", [])
    for i, url in enumerate(miei_audio):
        c1, c2 = st.columns([3, 1])
        with c1: st.audio(url)
        with c2:
            if st.button("Elimina", key=f"del_{i}"):
                miei_audio.pop(i)
                supabase.table("utenti").update({"audio_url": miei_audio}).eq("id", loggato["id"]).execute()
                st.rerun()

# --- 3. SEZIONE FEEDBACK (Spostata sopra) ---
st.header("💬 Feedback")
f_msg = st.text_area("Suggerimenti per il sito?", key="f_area")
if st.button("Invia Feedback"):
    if f_msg:
        supabase.table("feedback").insert({"messaggio": f_msg, "nome": loggato['nome']}).execute()
        st.success("Grazie per il feedback!")

# --- 4. SEZIONE ESPLORA (Con Ricerca e Filtri) ---
st.divider()
st.header("🔎 Esplora Collaboratori")

@st.cache_data(ttl=2)
def get_data():
    try:
        u = supabase.table("utenti").select("*").execute()
        l = supabase.table("likes").select("*").execute()
        return u.data, l.data
    except: return [], []

utenti, tutti_i_likes = get_data()

# Barra di ricerca e Filtro
c_search, c_filter = st.columns(2)
with c_search:
    search_query = st.text_input("Cerca per nome...", key="search_bar")
with c_filter:
    filter_role = st.selectbox("Filtra per ruolo", ["Tutti", "produttore", "cantante", "spettatore"])

for u in utenti:
    # Filtri logici
    if u['nome'] == loggato['nome']: continue
    if search_query and search_query.lower() not in u['nome'].lower(): continue
    if filter_role != "Tutti" and u['ruolo'] != filter_role: continue
    
    with st.container():
        st.subheader(f"👤 {u['nome']} ({u['ruolo']})")
        
        # Nota 24h
        n_testo = u.get("nota")
        n_time = u.get("nota_timestamp")
        if n_testo and n_time:
            t_nota = datetime.datetime.fromisoformat(n_time.replace('Z', '+00:00'))
            if (datetime.datetime.now(datetime.timezone.utc) - t_nota).total_seconds() < 86400:
                st.info(f"🗨️ {n_testo}")
        
        st.write(f"🔗 Contatto: {u.get('contatto', 'N/A')}")
        
        for url in u.get('audio_url', []):
            st.audio(url)
            
            # Like e Un-like
            likes_audio = [lk for lk in tutti_i_likes if lk.get('audio_url') == url]
            n_likes = len(likes_audio)
            gia_votato = any(lk.get('utente_che_vota') == loggato['nome'] for lk in likes_audio)
            
            if gia_votato:
                if st.button(f"❤️ {n_likes}", key=f"unlk_{url}"):
                    supabase.table("likes").delete().eq("utente_che_vota", loggato['nome']).eq("audio_url", url).execute()
                    st.cache_data.clear(); st.rerun()
            else:
                if st.button(f"🤍 {n_likes}", key=f"lk_{url}"):
                    supabase.table("likes").insert({"utente_che_vota": loggato['nome'], "audio_url": url}).execute()
                    st.cache_data.clear(); st.rerun()
        st.divider()


