import streamlit as st
from supabase import create_client
import time

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
    lista_audio_corrente = loggato.get("audio_url", []) if loggato else []
    
    nome_input = st.text_input("Nome d'arte / Nome", value=d_nome)
    pass_input = st.text_input("Password", type="password", value=loggato["password"] if loggato else "")
    contatto_input = st.text_input("Contatto", value=d_contatto)
    
    ruoli = ["produttore", "cantante", "spettatore"]
    ruolo_input = st.selectbox("Chi sei?", ruoli, index=ruoli.index(d_ruolo))
    
    if loggato and lista_audio_corrente:
        st.write("---")
        st.write("🗑️ **Gestisci i tuoi audio caricati:**")
        nuova_lista_audio = lista_audio_corrente.copy()
        
        for i, url in enumerate(lista_audio_corrente):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.audio(url)
            with col_b:
                if st.button(f"Elimina", key=f"del_{i}"):
                    nuova_lista_audio.pop(i)
                    st.session_state.utente_loggato["audio_url"] = nuova_lista_audio
                    st.rerun()
        lista_audio_corrente = nuova_lista_audio
        st.write("---")

    audio_files = st.file_uploader("Aggiungi nuovi audio (MP3)", type=["mp3"], accept_multiple_files=True)

    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("Salva modifiche" if loggato else "Crea Profilo"):
            if not nome_input or not pass_input:
                st.warning("Nome e Password obbligatori!")
            else:
                final_audio_list = lista_audio_corrente.copy()
                if audio_files:
                    for f in audio_files:
                        nome_f = f"{int(time.time())}_{f.name.replace(' ', '_')}"
                        try:
                            supabase.storage.from_("audio").upload(nome_f, f.read(), {"content_type": "audio/mpeg"})
                            url_pub = str(supabase.storage.from_("audio").get_public_url(nome_f))
                            final_audio_list.append(url_pub)
                        except: pass

                payload = {
                    "nome": nome_input,
                    "password": pass_input,
                    "ruolo": ruolo_input,
                    "contatto": contatto_input,
                    "audio_url": final_audio_list
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
            if st.button("Esci"):
                st.session_state.utente_loggato = None
                st.rerun()

# --- 3. SEZIONE ESPLORA (DENTRO EXPANDER) ---
st.divider()

with st.expander("Cerca collaboratori", expanded=False):
    @st.cache_data(ttl=5)
    def get_utenti():
        try: return supabase.table("utenti").select("nome, ruolo, , audio_url").execute()
        except: return None

    res = get_utenti()
    if res and res.data:
        c1, c2 = st.columns(2)
        with c1: r_nome = st.text_input("Cerca nome", key="search_n")
        with c2: f_ruolo = st.selectbox("Filtra ruolo", ["tutti", "produttore", "cantante", "spettatore"], key="search_r")

        st.write("---")
        for u in res.data:
            if r_nome and r_nome.lower() not in u["nome"].lower(): continue
            if f_ruolo != "tutti" and u["ruolo"] != f_ruolo: continue
            
            st.markdown(f"### 👤 {u['nome']}")
            st.caption(f"{u['ruolo'].upper()} | Contatto, {u.get('contatto', 'N/A')}")
            urls = u.get("audio_url", [])
            for link in urls:
                if isinstance(link, str) and link.startswith("http"):
                    st.audio(link)
            st.divider()
    else:
        st.info("Nessun utente registrato al momento.")

# --- 4. FEEDBACK ---
st.subheader("Feedback")
f_text = st.text_area("", key="f_area")
if st.button("Invia"):
    if f_text:
        supabase.table("feedback").insert({"messaggio": f_text, "nome": nome_input if nome_input else "Anonimo"}).execute()
        st.success("Grazie!")
