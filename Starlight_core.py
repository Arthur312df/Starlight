import datetime
import json
import os
import random
import re
from sentence_transformers import SentenceTransformer, util
from ddgs import DDGS

print("Inicializando o núcleo da StarLight v1.2 (Memória + Calculadora + Web Search)...")
print("Carregando o modelo de linguagem universal...")

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

MEMORY_FILE = "starlight_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_memory(memory_list):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory_list, f, ensure_ascii=False, indent=4)

def detect_language(text):
    english_keywords = [
        "hi", "hello", "hey", "what", "who", "why", "how", "where", "when", 
        "thank", "thanks", "you", "is", "are", "not", "speaking", "english", 
        "help", "day", "time", "please", "can", "do", "i", "want", "version", "translate", "remember", "search", "google", "web"
    ]
    words = text.lower().split()
    en_count = sum(1 for w in words if w in english_keywords)
    return "en" if en_count > 0 else "pt"

def get_safe_response(resp_obj, lang):
    if isinstance(resp_obj, dict):
        val = resp_obj.get(lang, resp_obj.get("pt", ""))
    else:
        val = resp_obj
    
    if isinstance(val, list):
        return random.choice(val)
    return val

def web_search(query):
    try:
        print("StarLight: 🌐 Pesquisando na internet...")
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                summary = "\n".join([f"- {r.get('title', '')}: {r.get('body', '')}" for r in results])
                return summary
            return "Não encontrei resultados relevantes na web."
    except Exception as e:
        return f"Erro ao acessar a internet: {str(e)}"

def evaluate_math(text):
    match = re.search(r'(\d+[\.\d]*)\s*([\+\-\*\/\x2b\x2d])\s*(\d+[\.\d]*)', text)
    if match:
        num1, op, num2 = match.groups()
        try:
            n1, n2 = float(num1), float(num2)
            if op == '+': res = n1 + n2
            elif op == '-': res = n1 - n2
            elif op in ('*', 'x'): res = n1 * n2
            elif op == '/': res = n1 / n2 if n2 != 0 else "infinito"
            else: return None
            
            if isinstance(res, float) and res.is_integer():
                res = int(res)
            return f"O resultado de {num1} {op} {num2} é **{res}**!"
        except Exception:
            return None
    return None

def smart_translate(text):
    cleaned = text.strip().lower()
    translations = {
        "o my god, i forgot the time": "Oh meu deus, i esqueci a hora",
        "hi, can you tell me a little more about you?": "Oi, você pode me contar um pouco mais sobre você?",
    }
    return translations.get(cleaned, f"[Tradução]: {text}")

long_term_memory = load_memory()

intents = [
    {
        "tag": "cumprimento",
        "patterns": ["oi", "olá", "tudo bem", "como vai", "e aí", "bom dia", "boa tarde", "boa noite", "hi", "hello", "hey"],
        "responses": {
            "pt": [
                "Oi! Tudo ótimo por aqui! Pronta para a versão 1.2. O que vamos fazer hoje?",
                "Olá! Como posso ajudar você nesta sessão da v1.2?",
                "E aí! O sistema está atualizado e pronto."
            ],
            "en": [
                "Hi! Everything is great here! Ready for version 1.2. What are we doing today?",
                "Hello! How can I help you in this v1.2 session?",
                "Hey! The system is updated and ready."
            ]
        }
    },
    {
        "tag": "identidade",
        "patterns": ["quem é você", "qual o seu nome", "o que você é", "who are you", "what is your name"],
        "responses": {
            "pt": ["Sou a StarLight versão 1.2, com calculadora integrada, memória avançada e busca na internet!"],
            "en": ["I am StarLight version 1.2, featuring integrated calculator, advanced memory, and internet search!"]
        }
    },
    {
        "tag": "data_hora",
        "patterns": ["que dia é hoje", "que horas são", "data de hoje", "what day is today", "what time is it"],
        "responses": {"pt": "TIME_QUERY_PT", "en": "TIME_QUERY_EN"}
    },
    {
        "tag": "agradecimento",
        "patterns": ["muito obrigado", "obrigado", "obrigada", "valeu", "thanks", "thank you", "thx", "otimo", "perfeito"],
        "responses": {
            "pt": [
                "Por nada! Estou sempre à disposição para ajudar.",
                "Imagina! Se precisar de mais alguma coisa, é só chamar.",
                "Disponha! Fico feliz em ajudar."
            ],
            "en": [
                "You're welcome! Always happy to help.",
                "Anytime! Let me know if you need anything else.",
                "Glad I could help!"
            ]
        }
    }
]

def process_query(user_input):
    lang = detect_language(user_input)
    user_lower = user_input.lower()

    math_result = evaluate_math(user_input)
    if math_result:
        return math_result

    if "o que você lembra" in user_lower or "listar memórias" in user_lower or "minhas memórias" in user_lower:
        if long_term_memory:
            mem_list = "\n".join([f"- {m}" for m in long_term_memory])
            return f"Aqui está tudo o que tenho salvo na minha memória de longo prazo:\n{mem_list}"
        return "Minha memória de longo prazo ainda está vazia. Use 'lembre-se que [fato]' para me ensinar algo!"

    if user_lower.startswith("lembre-se que") or user_lower.startswith("lembra que") or user_lower.startswith("remember that"):
        fact = user_input.split("que", 1)[-1].strip() if "que" in user_lower else user_input
        if fact:
            long_term_memory.append(fact)
            save_memory(long_term_memory)
            return "Anotado! Salvei essa informação na minha memória permanente."
        return "O que você quer que eu lembre?"

    if "pesquisar" in user_lower or "pesquise" in user_lower or "pesquisa" in user_lower or "busque" in user_lower or "buscar" in user_lower or "procure" in user_lower:
        query = re.sub(r'.*?(pesquisar|pesquise|pesquisa|busque|buscar|procure)\s+(na\s+internet\s+|pra\s+mim\s+|para\s+mim\s+)?(sobre\s+|por\s+|o\s+que\s+é\s+|qual\s+é\s+)?', '', user_input, flags=re.IGNORECASE).strip()
        if not query:
            query = user_input
        return web_search(query)

    if "traduza" in user_lower or "traduzir" in user_lower or "translate" in user_lower:
        match = re.search(r"['\"]{1,2}(.*?)['\"]{1,2}", user_input)
        if match:
            return f"Resultado da tradução: {smart_translate(match.group(1))}"
        return "Coloque o texto entre aspas para eu traduzir."

    corpus_sentences, corpus_mapping = [], []
    for intent in intents:
        for pattern in intent["patterns"]:
            corpus_sentences.append(pattern)
            corpus_mapping.append(intent)

    corpus_embeddings = model.encode(corpus_sentences, convert_to_tensor=True)
    user_embedding = model.encode(user_input, convert_to_tensor=True)
    hits = util.semantic_search(user_embedding, corpus_embeddings, top_k=1)[0]
    
    best_hit = hits[0]
    score = best_hit["score"]
    matched_intent = corpus_mapping[best_hit["corpus_id"]]

    if score >= 0.50:
        response_template = get_safe_response(matched_intent["responses"], lang)
        if response_template == "TIME_QUERY_PT":
            now = datetime.datetime.now()
            return f"📅 Hoje é {now.strftime('%d/%m/%Y')} e agora são {now.strftime('%H:%M:%S')}!"
        elif response_template == "TIME_QUERY_EN":
            now = datetime.datetime.now()
            return f"📅 Today is {now.strftime('%m/%d/%Y')} and it's {now.strftime('%H:%M:%S')}!"
        return response_template

    if long_term_memory:
        memory_embeddings = model.encode(long_term_memory, convert_to_tensor=True)
        mem_hits = util.semantic_search(user_embedding, memory_embeddings, top_k=1)[0]
        if mem_hits[0]["score"] > 0.55:
            return f"Eu me lembro de você ter me dito: '{long_term_memory[mem_hits[0]['corpus_id']]}'"

    if score < 0.30:
        return "Hm, não tenho certeza se entendi. Pode reformular, testar uma conta matemática ou pedir para eu pesquisar na web?"
    
    return get_safe_response(matched_intent["responses"], lang)