import streamlit as st
from supabase import create_client
import time

url = "https://hcyuowvrrjccmvcgebaj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Mzc2MTE5NiwiZXhwIjoyMDg5MzM3MTk2fQ.hwuG0YMFLSfSheNa460wTuVxu2TQyCpvj7doyHHB4pg"
supabase = create_client(url, key)

st.title("Beginner Collab")

nome = st.text_input("Nome")
contatto = st.text_input("Contatto (Instagram, email, ecc)")
ruolo = st.selectbox("Chi sei?", ["produttore", "cantante"])

audio_files = st.file_uploader("Carica audio (mp3)", type=["mp3"], accept_multiple_files=True)

if st.button("Salva il profilo"):

    audio_urls = []

    if audio_files:
        for audio_file in audio_files:
            file_bytes = audio_file.read()
            nome_file = f"{nome.lower().replace(' ', '_')}_{int(time.time())}_{audio_file.name}"

            supabase.storage.from_("audio").upload(nome_file, file_bytes)

            url_file = supabase.storage.from_("audio").get_public_url(nome_file)

            audio_urls.append(url_file)

    supabase.table("utenti").insert({
        "nome": nome,
        "ruolo": ruolo,
        "contatto": contatto,
        "audio_url": audio_urls
    }).execute()

    st.success("Profilo salvato!")

response = supabase.table("utenti").select("*").execute()

if response.data:

    current_user = response.data[-1]

    st.subheader("🔎 Trova collaboratori")

    ricerca_nome = st.text_input("Cerca per nome")

    filtro_ruolo = st.selectbox(
        "Ruolo",
        ["tutti", "produttore", "cantante"]
    )

    st.subheader("🎧 Artisti disponibili")

    for u in response.data:

    
        if ricerca_nome:
            if ricerca_nome.lower() not in u["nome"].lower():
                continue

        if filtro_ruolo != "tutti" and u["ruolo"] != filtro_ruolo:
            continue

        st.write(f"👤 {u['nome']} - {u['ruolo']}")
        st.write(f"📩 Contatto: {u.get('contatto', 'Non disponibile')}")

        if u.get("audio_url"):
            for audio in u["audio_url"]:
                st.audio(audio)

        st.divider()

st.subheader("💬 Invia un feedback")

feedback = st.text_area("Scrivi qui il tuo feedback")

if st.button("Invia feedback"):

    supabase.table("feedback").insert({
        "messaggio": feedback,
        "nome": nome
    }).execute()

    st.success("Feedback inviato!")
