
    st.subheader("🎧 Artisti disponibili")

    for u in response.data:
        if ricerca_nome and ricerca_nome.lower() not in u["nome"].lower():
            continue
        if filtro_ruolo != "tutti" and u["ruolo"] != filtro_ruolo:
            continue

        st.write(f"👤 {u['nome']} - {u['ruolo']}")
        st.write(f"📩 Contatto: {u.get('contatto', 'Non disponibile')}")

        # Riproduzione audio con URL pubblico permanente
        if u.get("audio_url"):
            for nome_file in u["audio_url"]:
                public_url = f"https://{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/object/public/audio/{nome_file}"
                st.audio(public_url)

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
