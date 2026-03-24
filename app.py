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

# --- 1. Funzione di recupero dati pulita ---
@st.cache_data(ttl=10) # Cache breve per vedere subito i nuovi inserimenti
def get_utenti():
    try:
        # Se "created_at" ti dava errore, usiamo una query semplice senza ordinamento
        return supabase.table("utenti").select("*").execute()
    except Exception as e:
        st.error(f"Errore database: {e}")
        return None

# --- 2. Mostra i risultati ---
response = get_utenti()

if response and response.data:
    st.subheader("🎧 Collaboratori Disponibili")
    
    # Filtri opzionali (opzionali, puoi anche toglierli per testare)
    ricerca = st.text_input("Filtra per nome").lower()

    for u in response.data:
        # Salta se non corrisponde alla ricerca
        if ricerca and ricerca not in u.get("nome", "").lower():
            continue

        # Box dell'utente
        with st.container():
            st.markdown(f"### 👤 {u.get('nome', 'Senza nome')}")
            st.write(f"**Ruolo:** {u.get('ruolo', 'N/A')} | **Contatto:** {u.get('contatto', 'N/A')}")

            # GESTIONE AUDIO (Il punto critico)
            audio_data = u.get("audio_url")
            
            if audio_data:
                # Trasformiamo in lista in ogni caso (gestisce sia stringa singola che array)
                lista_urls = audio_data if isinstance(audio_data, list) else [audio_data]
                
                for link in lista_urls:
                    if link and isinstance(link, str) and link.startswith("http"):
                        # Usiamo un expander per non occupare troppo spazio se sono molti
                        st.audio(link)
                    else:
                        st.caption("⚠️ Link audio non valido")
            else:
                st.info("Questo utente non ha caricato audio.")
            
            st.divider()
else:
    st.write("Nessun utente trovato nel database.")
