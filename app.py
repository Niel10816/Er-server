import streamlit as st
from supabase import create_client
import time

# --- Config Supabase ---
url = "https://hcyuowvrrjccmvcgebaj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3NjExOTYsImV4cCI6MjA4OTMzNzE5Nn0.rpMn8jxHagUJsOLjJXW79oV5ogUnGhxv-kr9TGWhj98"
supabase = create_client(url, key)

st.title("Beginner Collab")

nome = st.text_input("Nome")
contatto = st.text_input("Contatto (Instagram, email, ecc)")
ruolo = st.selectbox("Chi sei?", ["produttore", "cantante"])

audio_file = st.file_uploader("Carica un audio (mp3)", type=["mp3"])

if st.button("Salva il profilo"):

    audio_url = None

    if audio_file is not None:
        file_bytes = audio_file.read()
        nome_file = f"{nome.lower().replace(' ', '_')}_{int(time.time())}.mp3"

        # Upload
        supabase.storage.from_("audio").upload(nome_file, file_bytes)

        # Genera signed URL valido 1 ora
        signed_file = supabase.storage.from_("audio").create_signed_url(nome_file, 3600)
        if signed_file and "signedUrl" in signed_file:
            audio_url = signed_file["signedUrl"]

    # Salva nel DB
    supabase.table("utenti").insert({
        "nome": nome,
        "ruolo": ruolo,
        "contatto": contatto,
        "audio_url": audio_url
    }).execute()

    st.success("Profilo salvato!")
    st.cache_data.clear()  # 🔥 aggiorna subito i dati

# ✅ CACHE QUI
@st.cache_data
def get_utenti():
    return supabase.table("utenti").select("*").execute()

# --- Mostra collaboratori ---
response = get_utenti()

if response.data:
    current_user = response.data[-1]

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

        if u.get("audio_url"):
            st.audio(u["audio_url"], format="audio/mp3")

        st.divider()

# --- Feedback ---
st.subheader("💬 Invia un feedback")
feedback = st.text_area("Scrivi qui il tuo feedback")

if st.button("Invia feedback"):
    supabase.table("feedback").insert({"messaggio": feedback,"nome":nome}).execute()
    st.success("Feedback inviato!")
