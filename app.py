import streamlit as st
from supabase import create_client
import time
import requests  # necessario per scaricare audio dai link

# --- Config Supabase ---
url = "https://hcyuowvrrjccmvcgebaj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3NjExOTYsImV4cCI6MjA4OTMzNzE5Nn0.rpMn8jxHagUJsOLjJXW79oV5ogUnGhxv-kr9TGWhj98"
supabase = create_client(url, key)

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

    if not audio_files:
        st.warning("Devi caricare almeno un audio!")
    else:
        audio_urls = []

        for audio_file in audio_files:
            file_bytes = audio_file.read()
            if len(file_bytes) == 0:
                st.error(f"{audio_file.name} è vuoto!")
                continue

            # Nome unico
            nome_file = f"{nome.lower().replace(' ', '_')}_{int(time.time())}_{audio_file.name}"

            # Upload con Content-Type corretto
            supabase.storage.from_("audio").upload(
                nome_file,
                file_bytes,
                file_options={"content_type": "audio/mpeg"}
            )

            # URL pubblico permanente
            public_file = supabase.storage.from_("audio").get_public_url(nome_file)
            if public_file and "publicUrl" in public_file:
                audio_urls.append(public_file["publicUrl"])

        if audio_urls:
            # Inserisce nel DB come array di URL pubblici permanenti
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
        if ricerca_nome and ricerca_nome.lower() not in u["nome"].lower():
            continue
        if filtro_ruolo != "tutti" and u["ruolo"] != filtro_ruolo:
            continue

        st.write(f"👤 {u['nome']} - {u['ruolo']}")
        st.write(f"📩 Contatto: {u.get('contatto', 'Non disponibile')}")

        # Riproduzione multipla degli audio scaricati come bytes
        if u.get("audio_url"):
            for url in u["audio_url"]:
                try:
                    r = requests.get(url)
                    r.raise_for_status()  # errore se file non raggiungibile
                    st.audio(r.content, format="audio/mp3")
                except Exception as e:
                    st.error(f"Impossibile caricare {url}: {e}")

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
