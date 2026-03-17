
import streamlit as st
from supabase import create_client
url = "https://kjqncgasirjzilovibat.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtqcW5jZ2FzaXJqemlsb3ZpYmF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI0NjkyNTgsImV4cCI6MjA4ODA0NTI1OH0.qDVawy4rq8QCO9fP5tJsTSVN8PrgZW5BKwFOWxX2ECI"
supabase = create_client(url,key)
st.title("BeginnerCollab")
nome = st.text_input("Email *questa email sarà visibile a tutti gli utenti della piattaforma")
ruolo = st.selectbox("Chi sei?",["produttore", "cantante", "entrambi"])
genere = st.selectbox("genere", ["rock", "rap/trap", "pop", "classico", "tecno/elettro", "jazz"])
if st.button("Salva il profilo"):
    supabase.table("utenti").insert({
        "nome": nome,
        "genere": genere,
        "ruolo": ruolo
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

    for u, score in risultati:
        if u["nome"] != current_user["nome"]:
            st.write(f"{u['nome']} → compatibilità: {score}%")
















