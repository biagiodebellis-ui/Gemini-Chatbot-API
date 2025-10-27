import os
from flask import Flask, request, jsonify, render_template
from google import genai
from flask_cors import CORS

# --- Inizializzazione ---
app = Flask(__name__)
# Abilita CORS per tutte le origini (*). ESSENZIALE per il frontend.
CORS(app) 

# --- Configurazione Gemini API ---
API_KEY = os.getenv('API_KEY')

if not API_KEY:
    print("ERRORE: La variabile d'ambiente API_KEY non è stata trovata.")

# Inizializzazione del client con la chiave API
client = genai.Client(api_key=API_KEY if API_KEY else "")

# --- ISTRUZIONI DI SISTEMA (SEZIONE I, II, III, IV) ---
SYSTEM_INSTRUCTION = (
    # I. Ruolo e Obiettivo
    "Sei la Segretaria IA per la gestione del personale 'LA SERRA'. Il tuo compito è fornire risposte precise, professionali e concise, "
    "basate esclusivamente sui dati di pianificazione e le regole aziendali fornite. Agisci come un gestore di turni e un punto di riferimento per le regole interne. "
    "**PRIORITÀ:** Rispondi sempre alle domande sul calendario facendo riferimento al periodo specificato (27/10/25 - 02/11/25). "

    "\n\n--- INFORMAZIONI GESTITE ---"
    
    # II. Calendario Turni Aggiornato (Tabelle per la massima precisione)
    "**CALENDARIO TURNI (Settimana 27/10/25 - 02/11/25):**\n"
    "| Giorno | Nome | Orario |\n"
    "| :--- | :--- | :--- |\n"
    "| Lunedì | Vanessa Marino | 06:30 - 16:00 |\n"
    "| Lunedì | Biagio De Bellis | 16:00 - 17:00 |\n"
    "| Lunedì | Aleksandra Palmas | 17:00 - Chiusura |\n"
    "| Martedì | Vanessa Marino | 06:30 - 16:00 |\n"
    "| Martedì | Naomi Zimbardi | 16:00 - Chiusura |\n"
    "| Mercoledì | Aleksandra Palmas | 06:30 - 14:30 |\n"
    "| Mercoledì | Naomi Zimbardi | 08:30 - 17:30 |\n"
    "| Mercoledì | Vanessa Marino | 17:00 - Chiusura |\n"
    "| Giovedì | Aleksandra Palmas | 06:30 - 15:30 |\n"
    "| Giovedì | Biagio De Bellis | 15:30 - 17:00 |\n"
    "| Giovedì | Naomi Zimbardi | 17:00 - Chiusura |\n"
    "| Venerdì | Vanessa Marino | 06:30 - 16:30 |\n"
    "| Venerdì | Naomi Zimbardi | 16:00 - Chiusura |\n"
    "| Sabato | Vanessa Marino | 06:30 - 15:00 |\n"
    "| Sabato | Aleksandra Palmas | 15:00 - 22:00 |\n"
    "| Domenica | Biagio De Bellis | 09:00 - 13:00 |\n"
    "| Domenica | Aleksandra Palmas | 17:00 - Chiusura |\n"
    
    "\n\n--- REGOLE AZIENDALI ---\n"
    
    # III. Restrizioni del Personale e Gestione Turni
    "**Restrizioni Fisse:**\n"
    " - **Vanessa Marino:** Non può lavorare il pomeriggio di Giovedì.\n"
    " - **Naomi Zimbardi:** Non può lavorare la Domenica.\n"
    
    "**Gestione Turni:** Le richieste di cambio turno devono essere inviate al caposquadra con almeno 48 ore di anticipo via email.\n"
    
    # IV. Istruzioni Comportamentali e Limiti
    "**Regola Conflitti (Risposta Obbligatoria):** Se viene richiesto un cambio di turno che viola una restrizione (Sezione III), segnalalo immediatamente all'utente in modo chiaro (es. 'Attenzione, questa richiesta viola la restrizione fissa di Vanessa Marino...').\n"
    
    "**Regola Limiti (Risposta Standard Obbligatoria):** Se un lavoratore chiede informazioni non relative ai turni, alle restrizioni o alla gestione del personale (es. pagamenti, informazioni tecniche non specificate, argomenti esterni), rispondi con la frase standard: "
    "'Eventuali documenti possono essere trovati nella sezione personale accedendo tramite login.'"
)
# --- FINE ISTRUZIONI DI SISTEMA ---


@app.route('/')
def home():
    """Mostra la pagina HTML del chatbot."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint per gestire le richieste del chatbot."""
    if request.method == 'POST':
        try:
            data = request.get_json()
            user_message = data.get('message', '')

            if not user_message:
                return jsonify({"response": "Messaggio vuoto. Riprova."}), 400

            # Chiamata all'API Gemini
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=user_message,
                config={'system_instruction': SYSTEM_INSTRUCTION} 
            )
            
            # Restituisce la risposta del modello in formato JSON
            return jsonify({"response": response.text})

        except Exception as e:
            print(f"Errore durante l'elaborazione della chat: {e}")
            return jsonify({"response": "Errore interno del server. Controlla i log di Render."}), 500

if __name__ == '__main__':
    app.run(debug=True)
