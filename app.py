import streamlit as st
from supabase import create_client
import time
import datetime

# --- Config Supabase ---
URL_SUPABASE = "https://hcyuowvrrjccmvcgebaj.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3NjExOTYsImV4cCI6MjA4OTMzNzE5Nn0.rpMn8jxHagUJsOLjJXW79oV5ogUnGhxv-kr9TGWhj98" 
supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

st.set_page_config(page_title="Beginner Collab", layout="centered")

if "utente_loggato" not in st.session_state:
    st.session_state.utente_loggato = None

# --- 1. LOGIN / REGISTRAZIONE ---
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
        n_reg = st.text_input("Scegli il tuo Nome", key="r_n")
        p_reg = st.text_input("Scegli Password", type="password", key="r_p")
        c_reg = st.text_input("Contatto (IG/Telegram)", key="r_c")
        r_reg = st.selectbox("Ruolo", ["produttore", "cantante", "spettatore"], key="r_r")
        if st.button("Crea Account"):
            if n_reg and p_reg:
                payload = {"nome": n_reg, "password": p_reg, "contatto": c_reg, "ruolo": r_reg, "audio_url": [], "nota": None}
                supabase.table("utenti").insert(payload).execute()
                st.success("🎉 Profilo creato!")
                time.sleep(1.5); st.rerun()
    st.stop()

loggato = st.session_state.utente_loggato
st.sidebar.title(f"Ciao {loggato['nome']}")
if st.sidebar.button("Logout"):
    st.session_state.utente_loggato = None
    st.rerun()

# --- 2. GESTIONE ACCOUNT ---
with st.expander("⚙️ Gestisci il tuo Account"):
    nuovo_nome = st.text_input("Cambia Nome", value=loggato['nome'])
    nuova_pass = st.text_input("Cambia Password", value=loggato['password'], type="password")
    nuovo_contatto = st.text_input("Cambia Contatto", value=loggato.get('contatto', ''))
    nota_att = loggato.get("nota", "")
    nuova_nota = st.text_input("Nota del giorno", value=nota_att if nota_att else "", max_chars=60)
    audio_files = st.file_uploader("Carica MP3", type=["mp3"], accept_multiple_files=True)
    
    if st.button("Salva modifiche"):
        final_audio = loggato.get("audio_url", []) if loggato.get("audio_url") else []
        if audio_files:
            for f in audio_files:
                nome_f = f"{int(time.time())}_{f.name.replace(' ', '_')}"
                supabase.storage.from_("audio").upload(nome_f, f.read(), {"content_type": "audio/mpeg"})
                url_pub = str(supabase.storage.from_("audio").get_public_url(nome_f))
                final_audio.append(url_pub)
        ora = datetime.datetime.now(datetime.timezone.utc).isoformat()
        payload = {"nome": nuovo_nome, "password": nuova_pass, "contatto": nuovo_contatto, "nota": nuova_nota, "nota_timestamp": ora, "audio_url": final_audio}
        supabase.table("utenti").update(payload).eq("id", loggato["id"]).execute()
        st.session_state.utente_loggato.update(payload)
        st.success("Aggiornato!")
        time.sleep(1); st.rerun()

    st.write("---")
    miei_audio = loggato.get("audio_url", []) if loggato.get("audio_url") else []
    for i, url in enumerate(miei_audio):
        c1, c2 = st.columns([3, 1])
        with c1: st.audio(url)
        with c2:
            if st.button("Elimina", key=f"del_{i}"):
                miei_audio.pop(i)
                supabase.table("utenti").update({"audio_url": miei_audio}).eq("id", loggato["id"]).execute()
                st.session_state.utente_loggato["audio_url"] = miei_audio
                st.rerun()

# --- 3. FEEDBACK ---
st.header("💬 Feedback")
f_msg = st.text_area("Suggerimenti?", key="f_area")
if st.button("Invia"):
    if f_msg:
        supabase.table("feedback").insert({"messaggio": f_msg, "nome": loggato['nome']}).execute()
        st.success("Grazie!")

# --- 4. ESPLORA CON RANKING (CORRETTO) ---
st.divider()
st.header("🔎 Esplora Collaboratori")

@st.cache_data(ttl=2)
def get_ranked_data():
    try:
        u_res = supabase.table("utenti").select("*").execute()
        l_res = supabase.table("likes").select("*").execute()
        utenti = u_res.data if u_res.data else []
        likes = l_res.data if l_res.data else []
        
        for u in utenti:
            # Fix: se audio_url è None, usa lista vuota
            lista_url = u.get("audio_url") if u.get("audio_url") else []
            punti_audio = len(lista_url) * 2
            punti_likes = sum(1 for lk in likes if lk.get("audio_url") in lista_url)
            u["score_invisibile"] = punti_audio + punti_likes
            
        return sorted(utenti, key=lambda x: x.get("score_invisibile", 0), reverse=True), likes
    except Exception as e:
        return [], []

utenti_finali, tutti_i_likes = get_ranked_data()

search_query = st.text_input("Cerca per nome...", key="search_bar")
filter_role = st.selectbox("Filtra per ruolo", ["Tutti", "produttore", "cantante", "spettatore"])

if not utenti_finali:
    st.info("Caricamento utenti in corso o nessun utente trovato.")
else:
    for u in utenti_finali:
      
        if search_query and search_query.lower() not in u['nome'].lower(): continue
        if filter_role != "Tutti" and u['ruolo'] != filter_role: continue
        
        with st.container():
            st.subheader(f"👤 {u['nome']} ({u['ruolo']})")
            n_testo, n_time = u.get("nota"), u.get("nota_timestamp")
            if n_testo and n_time:
                try:
                    t_nota = datetime.datetime.fromisoformat(n_time.replace('Z', '+00:00'))
                    if (datetime.datetime.now(datetime.timezone.utc) - t_nota).total_seconds() < 86400:
                        st.info(f"🗨️ {n_testo}")
                except: pass
            
            st.write(f"🔗 Contatto: **{u.get('contatto', 'N/A')}**")
            
            urls = u.get('audio_url') if u.get('audio_url') else []
            for url in urls:
                st.audio(url)
                l_audio = [lk for lk in tutti_i_likes if lk.get('audio_url') == url]
                n_l = len(l_audio)
                gia = any(lk.get('utente_che_vota') == loggato['nome'] for lk in l_audio)
                
                if gia:
                    if st.button(f"❤️ {n_l}", key=f"u_{u['id']}_{url}"):
                        supabase.table("likes").delete().eq("utente_che_vota", loggato['nome']).eq("audio_url", url).execute()
                        st.cache_data.clear(); st.rerun()
                else:
                    if st.button(f"🤍 {n_l}", key=f"l_{u['id']}_{url}"):
                        supabase.table("likes").insert({"utente_che_vota": loggato['nome'], "audio_url": url}).execute()
                        st.cache_data.clear(); st.rerun()
            st.divider()


