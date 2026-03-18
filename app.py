
import streamlit as st
from supabase import create_client
url = "https://hcyuowvrrjccmvcgebaj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3NjExOTYsImV4cCI6MjA4OTMzNzE5Nn0.rpMn8jxHagUJsOLjJXW79oV5ogUnGhxv-kr9TGWhj98"
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
