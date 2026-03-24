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
with st.expander("➕ Aggiungi il tuo profilo / Carica audio"):
    nome_input = st.text_input("Nome d'arte")
    contatto_input = st.text_input("Contatto (Instagram, email, ecc)")
    ruolo_input = st.selectbox("Chi sei?", ["produttore", "cantante"])
    
    audio_files = st.file_uploader(
        "Carica uno o più audio (mp3)",
        type=["mp3"],
        accept_multiple_files=True
    )

    if st.button("Salva il profilo"):
        if not audio_files:
            st.warning("Devi caricare almeno un audio!")
        elif not nome_input:
            st.warning("Inserisci il tuo nome!")
        else:
            audio_urls = []
            for f in audio_files:
                # Generiamo un nome unico per il file nello storage
                nome_file_storage = f"{int(time.time())}_{f.name.replace(' ', '_')}"
                
                try:
                    # Upload su Supabase Storage
                    supabase.storage.from_("audio").upload(
                        path=nome_file_storage,
                        file=f.read(),
                        file_options={"content_type": "audio/mpeg"}
                    )

                    # Ottieni l'URL pubblico permanente
                    public_url = str(supabase.storage.from_("audio").get_public_url(nome_file_storage))
                    audio_urls.append(public_url)
                except Exception as e:
                    st.error(f"Errore durante l'upload di {f.name}: {e}")

            if audio_urls:
                # Inserisce nel Database
                supabase.table("utenti").insert({
                    "nome": nome_input,
                    "ruolo": ruolo_input,
                    "contatto": contatto_input,
                    "audio_url": audio_urls
                }).execute()

                st.success("Profilo salvato correttamente!")
                st.cache_data.clear()
                st.rerun()

# --- 2. LOGICA DI RICERCA E FILTRI ---
st.divider()
st.subheader("🔎 Trova collaboratori")

# Funzione per leggere utenti dal DB
@st.cache_data(ttl=60)
def get_utenti():
    try:
        # Recupera tutti gli utenti (senza .order() per evitare errori di colonne mancanti)
        return supabase.table("utenti").select("*").execute()
    except Exception as e:
        st.error(f"Errore nel caricamento utenti: {e}")
        return None

response = get_utenti()

if response and response.data:
    # Barra di ricerca e filtri
    col1, col2 = st.columns(2)
    with col1:
        ricerca_nome = st.text_input("Cerca per nome")
    with col2:
        filtro_ruolo = st.selectbox("Filtra per Ruolo", ["tutti", "produttore", "cantante"])

    st.subheader("🎧 Artisti disponibili")

    # Ciclo per mostrare gli utenti
    for u in response.data:
        # Applicazione filtri
        nome_db = u.get("nome", "")
        ruolo_db = u.get("ruolo", "")
        
        if ricerca_nome and ricerca_nome.lower() not in nome_db.lower():
            continue
        if filtro_ruolo != "tutti" and ruolo_db != filtro_ruolo:
            continue

        # Layout Utente
        with st.container():
            st.markdown(f"### 👤 {nome_db}")
            st.write(f"**Ruolo:** {ruolo_db.capitalize()} | 📩 **Contatto:** {u.get('contatto', 'Non disponibile')}")

            # Riproduzione Audio
            urls = u.get("audio_url")
            if urls:
                lista_urls = urls if isinstance(urls, list) else [urls]
                for link in lista_urls:
                    # Verifica che il link sia valido prima di passarlo a st.audio
                    if isinstance(link, str) and link.startswith("http"):
                        st.audio(link)
            else:
                st.caption("Nessun audio caricato.")
            
            st.divider()
else:
    st.info("Non ci sono ancora collaboratori registrati.")

# --- 3. AREA FEEDBACK ---
st.subheader("💬 Invia un feedback")
feedback_text = st.text_area("Scrivi qui i tuoi suggerimenti o segnala problemi")

if st.button("Invia feedback"):
    if feedback_text:
        try:
            supabase.table("feedback").insert({
                "messaggio": feedback_text,
                "nome": nome_input
            }).execute()
            st.success("Feedback inviato! Grazie della collaborazione.")
        except Exception as e:
            st.error(f"Errore nell'invio del feedback: {e}")
    else:
        st.warning("Il campo feedback è vuoto!")
