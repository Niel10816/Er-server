
import streamlit as st
from supabase import create_client
url = "https://hcyuowvrrjccmvcgebaj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3NjExOTYsImV4cCI6MjA4OTMzNzE5Nn0.rpMn8jxHagUJsOLjJXW79oV5ogUnGhxv-kr9TGWhj98"
supabase = create_client(url,key)
st.title("BeginnerCollab")
nome = st.text_input("Email *questa email sarà visibile a tutti gli utenti della piattaforma")
ruolo = st.selectbox("Chi sei?",["produttore", "cantante"])
genere = st.selectbox("genere", ["rock", "rap/trap", "pop", "classico", "tecno/elettro", "jazz"])
audio_file = st.file_uploader("Carica qui la tua traccia audiomp3", type=["mp3"])
if st.button("Salva il profilo"):
    audio_url = None
    if audio_url is None: 
        file_bytes = audio_file.read()
        supabase.storage.from_("audio").upload(
        f"{nome}.mp3",
        file_bytes
    )

    audio_url = supabase.storage.from_("audio").get_public_url(f"{nome}.mp3")

    supabase.table("utenti").insert({
        "nome": nome,
        "genere": genere,
        "ruolo": ruolo
        "audio_url": audio_url
    }).execute()

    st.success("Profilo salvato!")



def match(user, others):
    risultati = []
    for u in others:
        score = 0

        if user["genere"] == u["genere"]:
            score += 50

        if user["ruolo"] != u["ruolo"]:
            score += 50

        risultati.append((u, score))
    risultati = [r for r in risultati if r[1] >= 50]
    return sorted(risultati, key=lambda x: x[1
                ], reverse=True)




response = supabase.table("utenti").select("*").execute()
data = response.data

if data and len(data) > 1:
    current_user = data[-1]

    risultati = match(current_user, data)

    st.subheader("Collaboratori suggeriti")

    for u in response.data:
        st.write(u["nome"])
        st.write(u["ruolo"])
        if u["audio_url"]:
            st.audio(u["audio_url"])
            st.divider()













