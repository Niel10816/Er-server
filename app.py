import streamlit as st
from supabase import create_client
import time
import datetime

# --- Config Supabase ---
URL_SUPABASE = "https://hcyuowvrrjccmvcgebaj.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3NjExOTYsImV4cCI6MjA4OTMzNzE5Nn0.rpMn8jxHagUJsOLjJXW79oV5ogUnGhxv-kr9TGWhj98" 
supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

st.set_page_config(page_title="Beginner Collab", layout="centered")
st.title("🎸 Beginner Collab")

# Inizializzazione session state
if "utente_loggato" not in st.session_state:
    st.session_state.utente_loggato = None

# --- LOGICA DI ACCESSO (UNICA COSA VISIBILE ALL'INIZIO) ---
if st.session_state.utente_loggato is None:
    tab1, tab2 = st.tabs(["Accedi", "Registrati"])
    
    with tab1:
        n_log = st.text_input("nome")
        p_log = st.text_input("Password", type="password")
        if st.button("Entra"):
            res = supabase.table("utenti").select("*").eq("nome", n_log).eq("password", p_log).execute()
            if res.data:
                st.session_state.utente_loggato = res.data[0]
                st.rerun()
            else: st.error("Dati errati")
            
    with tab2:
        n_reg = st.text_input("Scegli nome")
        p_reg = st.text_input("Scegli Password", type="password")
        c_reg = st.text_input("Contatto (IG/Telegram)")
        r_reg = st.selectbox("Ruolo", ["produttore", "cantante", "spettatore"])
        not_reg = st.text_input("Nota del giorno (24h)", max_chars=60)
        
        if st.button("Crea Account"):
            if n_reg and p_reg:
                ora = datetime.datetime.now(datetime.timezone.utc).isoformat() if not_reg else None
                payload = {"nome": n_reg, "password": p_reg, "contatto": c_reg, "ruolo": r_reg, "nota": n_reg, "nota_timestamp": ora, "audio_url": []}
                supabase.table("utenti").insert(payload).execute()
                st.success("Profilo creato! Ora accedi.")
                time.sleep(1.5)
                st.rerun()
    st.stop() # BLOCCA TUTTO IL RESTO SE NON SEI LOGGATO

# --- DA QUI IN POI TUTTO È RISERVATO AGLI UTENTI LOGGATI ---
loggato = st.session_state.utente_loggato

# Sidebar per uscire o vedere il proprio nome
st.sidebar.write(f"Logged as: **{loggato['nome']}**")
if st.sidebar.button("Logout"):
    st.session_state.utente_loggato = None
    st.rerun()

# --- SEZIONE PROFILO ---
with st.expander("⚙️ Gestisci Profilo e Audio"):
    # (Qui resta il codice per caricare/eliminare audio e aggiornare la nota che abbiamo già scritto)
    # [Per brevità non lo riscrivo tutto, ma va qui dentro]
    pass

# --- SEZIONE ESPLORA ---
st.header("🔎 Esplora la Community")
@st.cache_data(ttl=2)
def get_data():
    u = supabase.table("utenti").select("*").execute()
    l = supabase.table("likes").select("*").execute()
    return u.data, l.data

utenti, tutti_i_likes = get_data()

for u in utenti:
    if u['nome'] == loggato['nome']: continue # Non mostrare te stesso
    
    with st.container():
        st.subheader(f"👤 {u['nome']}")
        # Controllo Nota 24h
        if u.get('nota') and u.get('nota_timestamp'):
            t_nota = datetime.datetime.fromisoformat(u['nota_timestamp'].replace('Z', '+00:00'))
            if (datetime.datetime.now(datetime.timezone.utc) - t_nota).total_seconds() < 86400:
                st.info(f"🗨️ {u['nota']}")
        
        st.caption(f"Ruolo: {u['ruolo']} | Contatto: {u['contatto']}")
        
        for url in u.get('audio_url', []):
            st.audio(url)
            # CONTEGGIO LIKE UNIVOCI
            likes_per_questo_audio = [lk for lk in tutti_i_likes if lk['audio_url'] == url]
            n_likes = len(likes_per_questo_audio)
            
            # Controllo se IO ho già messo like
            gia_messo = any(lk['utente_che_vota'] == loggato['nome'] for lk in likes_per_questo_audio)
            
            if gia_messo:
                st.button(f"❤️ {n_likes} (Hai già votato)", key=f"lk_{url}", disabled=True)
            else:
                if st.button(f"🤍 {n_likes} Metti Like", key=f"lk_{url}"):
                    supabase.table("likes").insert({"utente_che_vota": loggato['nome'], "audio_url": url}).execute()
                    st.rerun()
        st.divider()

# --- SEZIONE FEEDBACK ---
st.header("💬 Feedback")
f_msg = st.text_area("Cosa ne pensi del sito?", key="f_area")
if st.button("Invia"):
    if f_msg:
        # Inserimento automatico del nome dell'utente loggato
        supabase.table("feedback").insert({"messaggio": f_msg, "nome": loggato['nome']}).execute()
        st.success("Feedback inviato a tuo nome!")


