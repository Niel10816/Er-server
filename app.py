

import streamlit as st
from supabase import create_client

# --------------------
# Configurazione Supabase
# --------------------
url = "https://hcyuowvrrjccmvcgebaj.supabase.co"  # sostituisci con il tuo URL
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3NjExOTYsImV4cCI6MjA4OTMzNzE5Nn0.rpMn8jxHagUJsOLjJXW79oV5ogUnGhxv-kr9TGWhj98"                        # sostituisci con la tua chiave
supabase = create_client(url, key)

# --------------------
# Titolo
# --------------------
st.title("Collaboratori Musicali")

# --------------------
# Profilo utente
# --------------------
nome = st.text_input("Nome")
ruolo = st.selectbox("Chi sei?", ["produttore", "cantante",])
genere = st.selectbox("Genere", [ "pop", "tecno", "rap", "classico", "rock", "jazz"])

# Caricamento audio MP3
audio_file = st.file_uploader("Carica un audio (mp3)", type=["mp3"])

if st.button("Salva il profilo"):
    audio_url = None
    if audio_file is not None:
        file_bytes = audio_file.read()
        nome_file = f"{nome.lower().replace(' ', '_')}.mp3"
        supabase.storage.from_("audio").upload(nome_file, file_bytes, {"upsert": True})
        audio_url = supabase.storage.from_("audio").get_public_url(nome_file)["publicUrl"]


    # Inserimento nella tabella 'utenti'
    supabase.table("utenti").insert({
        "nome": nome,
        "ruolo": ruolo,
        "genere": genere,
        "audio_url": audio_url
    }).execute()

    st.success("Profilo salvato!")

# --------------------
# Funzione di matching collaboratori
# --------------------
def match(user, others):
    risultati = []
    for u in others:
        score = 0
        if user["genere"] == u["genere"]:
            score += 50
        if user.get("bpm") and u.get("bpm"):
            if abs(user["bpm"] - u["bpm"]) < 10:
                score += 30
        if user["ruolo"] != u["ruolo"]:
            score += 20
        risultati.append((u, score))
    return sorted(risultati, key=lambda x: x[1], reverse=True)

# --------------------
# Recupera utenti da Supabase
# --------------------
response = supabase.table("utenti").select("*").execute()

if response.data:
    current_user = response.data[-1]  # ultimo inserito
    risultati = match(current_user, response.data)

    # --------------------
    # Barra di ricerca collaboratori
    # --------------------
       # Barra di ricerca collaboratori
    # --------------------
    st.subheader("🔎 Trova collaboratori")

# Filtri
filtro_ruolo = st.selectbox(
    "Ruolo",
    ["tutti", "produttore", "cantante",]
)

filtro_genere = st.selectbox(
    "Genere musicale",
    ["tutti", "pop", "tecno", "rap", "classico", "rock", "jazz"]
)

st.subheader("🎧 Artisti disponibili")

for u in response.data:

    # NON mostrare se stesso
    if u["nome"] == current_user["nome"]:
        continue

    # filtro ruolo
    if filtro_ruolo != "tutti" and u["ruolo"] != filtro_ruolo:
        continue

    # filtro genere musicale
       if filtro_genere != "tutti":
    generi_utente = u.get("generi")

    # se è una lista (tipo ['trap'])
    if isinstance(generi_utente, list):
        if filtro_genere not in generi_utente:
            continue

    # se è una stringa normale
    else:
        if filtro_genere.lower() not in str(generi_utente).lower():
            continue

    # stampa utente
    st.write(f"👤 {u['nome']} - {u['ruolo']} -{u['genere']}")

    # player audio
    if u.get("audio_url"):
        st.audio(u["audio_url"])

    st.divider()

