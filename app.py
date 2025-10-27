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

client = genai.Client(api_key=API_KEY)

# --- ISTRUZIONI DI SISTEMA (ADDESTRAMENTO PER I LAVORATORI) ---
SYSTEM_INSTRUCTION = (
    "Sei BiagioBot, l'Assistente Interno dedicato al supporto del personale. "
    "Il tuo compito è fornire risposte precise, professionali e concise, basate esclusivamente sulle regole aziendali e sulle informazioni di seguito. "
    "Il tuo pubblico è il personale interno, quindi usa un tono diretto e orientato all'azione. "
    
    # -----------------------------------------------------------
    # INSERISCI QUI LE INFORMAZIONI SPECIFICHE PER I LAVORATORI:
    # -----------------------------------------------------------
    
    "**Gestione Turni:** I turni di lavoro settimanali vengono pubblicati ogni venerdì alle 17:00 sul portale 'Intranet Lavoratori'. "
    "Per visualizzare il proprio turno, il lavoratore deve accedere con le proprie credenziali. "
    "Le richieste di cambio turno devono essere inviate al caposquadra con almeno 48 ore di anticipo via email. "
    
    "**Procedure di Emergenza:** In caso di emergenza informatica (es. attacco DDoS o interruzione del server principale), "
    "il personale è tenuto a staccare immediatamente la connessione di rete e contattare il Team IT al numero interno 555. "
    "In caso di emergenza medica, chiamare il numero di emergenza 112 e poi avvisare la sicurezza interna. "
    
    "**Politica Ferie/Permessi:** Le richieste di ferie devono essere approvate dal responsabile di reparto e inoltrate tramite il modulo HR online. "
    "Il preavviso minimo per le ferie è di 15 giorni lavorativi. "
    
    # -----------------------------------------------------------
    # FINE INFORMAZIONI SPECIFICHE
    # -----------------------------------------------------------
    
    "**Regola di Limitazione:** Se un lavoratore chiede informazioni non coperte in queste istruzioni (es. retribuzioni esatte, informazioni personali, o argomenti esterni all'azienda), "
    "rispondi sempre con la frase standard: 'Questa informazione non è disponibile nel mio database aziendale. Per assistenza specifica, contatta il Dipartimento Risorse Umane o il tuo Caposquadra.'"
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

            # Chiamata all'API Gemini - USA IL PROMPT DI SISTEMA AGGIORNATO
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
