import streamlit as st
from supabase import create_client
import time

# --- Config Supabase ---
# Sostituisci con le tue credenziali reali
URL_SUPABASE = "https://hcyuowvrrjccmvcgebaj.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjeXVvd3ZycmpjY212Y2dlYmFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3NjExOTYsImV4cCI6MjA4OTMzNzE5Nn0.rpMn8jxHagUJsOLjJXW79oV5ogUnGhxv-kr9TGWhj98" 
supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

st.set_page_config(page_title="Beginner Collab", layout="centered")
st.title("Beginner Collab")

# --- Input utente ---
with st.expander("Accedi"):
    nome = st.text_input("Nome")
    contatto = st.text_input("Contatto (IG, Email, ecc.)")
    ruolo = st.selectbox("Il tuo ruolo", ["produttore", "cantante"])
    audio_files = st.file_uploader("Carica i tuoi beat o le tue voci (MP3)", type=["mp3"], accept_multiple_files=True)

    if st.button("Aggiungi profilo"):
        if not nome or not audio_files:
            st.error("Inserisci almeno il nome e un file audio!")
        else:
            urls_caricati = []
            for f in audio_files:
                # Generiamo un nome file unico per evitare sovrascritture
                estensione = f.name.split('.')[-1]
                nome_pulito = f"{int(time.time())}_{f.name.replace(' ', '_')}"
                
                try:
                    # 1. Upload su Storage
                    supabase.storage.from_("audio").upload(
                        path=nome_pulito,
                        file=f.read(),
                        file_options={"content_type": "audio/mpeg"}
                    )
                    
                    # 2. Ottieni URL Pubblico
                    res_url = supabase.storage.from_("audio").get_public_url(nome_pulito)
                    # Forziamo il risultato a stringa (alcune versioni tornano un oggetto)
                    public_url = str(res_url)
                    urls_caricati.append(public_url)
                except Exception as e:
                    st.error(f"Errore upload {f.name}: {e}")

            if urls_caricati:
                # 3. Salvataggio nel database
                supabase.table("utenti").insert({
                    "nome": nome,
                    "ruolo": ruolo,
                    "contatto": contatto,
                    "audio_url": urls_caricati # Salvato come array JSON
                }).execute()
                
                st.success("Profilo creato con successo!")
                st.cache_data.clear()
                st.rerun()

# --- Visualizzazione ---
st.divider()
st.subheader("🔎 Esplora Collaboratori")

@st.cache_data(ttl=60) # Aggiorna ogni minuto
def carica_utenti():
    return supabase.table("utenti").select("*").order("created_at", desc=True).execute()

data = carica_utenti().data

if data:
    for utente in data:
        with st.container():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**{utente['nome']}**")
                st.caption(f"Role: {utente['ruolo']}")
                st.caption(f"Contact: {utente['contatto']}")
            
            with col2:
                links = utente.get("audio_url", [])
                # Se per errore è una stringa singola, la mettiamo in lista
                if isinstance(links, str):
                    links = [links]
                
                if links:
                    for l in links:
                        # TRUCCO CRUCIALE: se l'URL contiene spazi o caratteri strani,
                        # Streamlit potrebbe fallire. Il link deve essere una stringa pulita.
                        if l and isinstance(l, str) and l.startswith("http"):
                            st.audio(l)
                else:
                    st.write("Nessun audio disponibile")
            st.divider()
else:
    st.info("Non ci sono ancora artisti. Sii il primo!")
