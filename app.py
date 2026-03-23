import streamlit as st
from supabase import create_client
import time

# --- Config Supabase ---
SUPABASE_URL = "https://hcyuowvrrjccmvcgebaj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3NjExOTYsImV4cCI6MjA4OTMzNzE5Nn0.rpMn8jxHagUJsOLjJXW79oV5ogUnGhxv-kr9TGWhj98"
SUPABASE_PROJECT_ID = "hcyuowvrrjccmvcgebaj"  # serve per URL pubblico diretto
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Beginner Collab")

# --- Input utente ---
nome = st.text_input("Nome")
contatto = st.text_input("Contatto (Instagram, email, ecc)")
ruolo = st.selectbox("Chi sei?", ["produttore", "cantante"])

# Upload multiplo
audio_files = st.file_uploader(
    "Carica uno o più audio (mp3)",
    type=["mp3"],
    accept_multiple_files=True
)

# --- Salvataggio profilo ---
if st.button("Salva il profilo"):
    audio_urls = []

    if audio_files:
        for audio_file in audio_files:
            file_bytes = audio_file.read()
            nome_file = f"{nome.lower().replace(' ', '_')}_{int(time.time())}_{audio_file.name}"

            # Upload con Content-Type corretto
            supabase.storage.from_("audio").upload(
                nome_file,
                file_bytes,
                file_options={"content_type": "audio/mpeg"}
            )

            # Salviamo solo il nome del file nel DB
            audio_urls.append(nome_file)

    # Salva array di nomi file nel DB
    supabase.table("utenti").insert({
        "nome": nome,
        "ruolo": ruolo,
        "contatto": contatto,
        "audio_url": audio_urls
    }).execute()

    st.success("Profilo salvato!")
    st.cache_data.clear()

# --- Funzione per leggere utenti dal DB ---
@st.cache_data
def get_utenti():
    return supabase.table("utenti").select("*").execute()

# --- Visualizzazione collaboratori ---
response = get_utenti()

if response.data:
    st.subheader("🔎 Trova collaboratori")
    ricerca_nome = st.text_input("Cerca per nome")
    filtro_ruolo = st.selectbox("Ruolo", ["tutti", "produttore", "cantante"])

    st.subheader("🎧 Artisti disponibili")

    for u in response.data:
        # Filtri
        if ricerca_nome and ricerca_nome.lower() not in u["nome"].lower():
            continue
        if filtro_ruolo != "tutti" and u["ruolo"] != filtro_ruolo:
            continue

        st.write(f"👤 {u['nome']} - {u['ruolo']}")
        st.write(f"📩 Contatto: {u.get('contatto', 'Non disponibile')}")

        # Mostra tutti gli audio dell'utente
        if u.get("audio_url"):
            for nome_file in u["audio_url"]:
                public_url = f"https://{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/object/public/audio/{nome_file}"
                st.audio(public_url)  # URL pubblico permanente

        st.divider()

# --- Feedback ---
st.subheader("💬 Invia un feedback")
feedback = st.text_area("Scrivi qui il tuo feedback")

if st.button("Invia feedback"):
    supabase.table("feedback").insert({
        "messaggio": feedback,
        "nome": nome
    }).execute()
    st.success("Feedback inviato!")
