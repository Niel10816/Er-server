 

import streamlit as st
from supabase import create_client

url = "https://hcyuowvrrjccmvcgebaj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3NjExOTYsImV4cCI6MjA4OTMzNzE5Nn0.rpMn8jxHagUJsOLjJXW79oV5ogUnGhxv-kr9TGWhj98"
supabase = create_client(url, key)

st.title("Collaboratori Musicali")

nome = st.text_input("Nome")
ruolo = st.selectbox("Chi sei?", ["produttore", "cantante"])
genere = st.selectbox("Genere musicale", ["rock", "jazz", "tecno", "pop","classico", "rap"])

audio_file = st.file_uploader("Carica un audio (mp3)", type=["mp3"])

if st.button("Salva il profilo"):

    audio_url = None

    if audio_file is not None:
        file_bytes = audio_file.read()
        nome_file = f"{nome.lower().replace(' ', '_')}.mp3"

        supabase.storage.from_("audio").upload(nome_file, file_bytes, {"upsert": True})
        audio_url = supabase.storage.from_("audio").get_public_url(nome_file)["publicUrl"]

    supabase.table("utenti").insert({
        "nome": nome,
        "ruolo": ruolo,
        "genere": genere,
        "audio_url": audio_url
    }).execute()

    st.success("Profilo salvato!")

response = supabase.table("utenti").select("*").execute()

if response.data:

    current_user = response.data[-1]

    st.subheader("🔎 Trova collaboratori")

    filtro_ruolo = st.selectbox(
        "Ruolo",
        ["tutti", "produttore", "cantante"]
    )

    filtro_genere = st.selectbox(
        "Genere musicale",
        ["tutti", "rock", "jazz", "tecno", "classico", "rap"]
    )

    st.subheader("🎧 Artisti disponibili")

    for u in response.data:

        if u["nome"] == current_user["nome"]:
            continue

        if filtro_ruolo != "tutti" and u["ruolo"] != filtro_ruolo:
            continue

        if filtro_genere != "tutti":
            if u.get("genere") != filtro_genere:
                continue

        st.write(f"👤 {u['nome']} - {u['ruolo']}-{u['genere']}")

        if u.get("audio_url"):
            st.audio(u["audio_url"])

        st.divider()
