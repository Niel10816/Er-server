import streamlit as st
from supabase import create_client
import time

# --- Config Supabase ---
URL_SUPABASE = "https://hcyuowvrrjccmvcgebaj.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3NjExOTYsImV4cCI6MjA4OTMzNzE5Nn0.rpMn8jxHagUJsOLjJXW79oV5ogUnGhxv-kr9TGWhj98"  # Inserisci la tua chiave corretta
supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

st.set_page_config(page_title="Beginner Collab", layout="centered")
st.title("🎵 Beginner Collab")

# --- 1. AREA INPUT UTENTE ---
with st.expander("➕ Crea il tuo profilo (Artisti o Spettatori)"):
    nome_input = st.text_input("Nome d'arte / Nome")
    contatto_input = st.text_input("Contatto (Instagram, email, ecc)")
    ruolo_input = st.selectbox("Chi sei?", ["produttore", "cantante", "spettatore"])
    
    audio_files = st.file_uploader(
        "Carica i tuoi audio (Opzionale - solo per artisti)",
        type=["mp3"],
        accept_multiple_files=True
    )

    if st.button("Salva il profilo"):
        if not nome_input:
            st.warning("Inserisci almeno il tuo nome!")
        else:
            audio_urls = []
            
            # Se ci sono file, esegui l'upload
            if audio_files:
                for f in audio_files:
                    nome_file_storage = f"{int(time.time())}_{f.name.replace(' ', '_')}"
                    try:
                        supabase.storage.from_("audio").upload(
                            path=nome_file_storage,
                            file=f.read(),
                            file_options={"content_type": "audio/mpeg"}
                        )
                        public_url = str(supabase.storage.from_("audio").get_public_url(nome_file_storage))
                        audio_urls.append(public_url)
                    except Exception as e:
                        st.error(f"Errore durante l'upload di {f.name}: {e}")

            # Salva il profilo (anche se audio_urls è vuota)
            try:
                supabase.table("utenti").insert({
                    "nome": nome_input,
                    "ruolo": ruolo_input,
                    "contatto": contatto_input,
                    "audio_url": audio_urls  # Sarà [] se non ci sono audio
                }).execute()

                st.success("Profilo salvato correttamente!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Errore nel salvataggio del profilo: {e}")

# --- 2. LOGICA DI RICERCA E FILTRI ---
st.divider()
st.subheader("🔎 Esplora la community")

@st.cache_data(ttl=60)
def get_utenti():
    try:
        return supabase.table("utenti").select("*").execute()
    except Exception as e:
        st.error(f"Errore nel caricamento: {e}")
        return None

response = get_utenti()

if response and response.data:
    col1, col2 = st.columns(2)
    with col1:
        ricerca_nome = st.text_input("Cerca per nome")
    with col2:
        filtro_ruolo = st.selectbox("Filtra per Ruolo", ["tutti", "produttore", "cantante", "spettatore"])

    st.subheader("👥 Utenti disponibili")

    for u in response.data:
        nome_db = u.get("nome", "")
        ruolo_db = u.get("ruolo", "")
        
        if ricerca_nome and ricerca_nome.lower() not in nome_db.lower():
            continue
        if filtro_ruolo != "tutti" and ruolo_db != filtro_ruolo:
            continue

        with st.container():
            st.markdown(f"### 👤 {nome_db}")
            st.write(f"**Ruolo:** {ruolo_db.capitalize()} | 📩 **Contatto:** {u.get('contatto', 'Non disponibile')}")

            # Mostra audio solo se presenti
            urls = u.get("audio_url")
            if urls and len(urls) > 0:
                lista_urls = urls if isinstance(urls, list) else [urls]
                for link in lista_urls:
                    if isinstance(link, str) and link.startswith("http"):
                        st.audio(link)
            
            st.divider()
else:
    st.info("Nessun utente registrato.")

# --- 3. AREA FEEDBACK ---
st.subheader("💬 Invia un feedback")
feedback_text = st.text_area("Suggerimenti o segnalazioni")

if st.button("Invia feedback"):
    if feedback_text:
        try:
            supabase.table("feedback").insert({
                "messaggio": feedback_text,
                "nome": nome_input if nome_input else "Anonimo"
            }).execute()
            st.success("Feedback inviato!")
        except Exception as e:
            st.error(f"Errore invio feedback: {e}")
