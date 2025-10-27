import PyPDF2
import google.generativeai as genai
import json
from urllib.parse import urlparse, unquote 
# --- Função para extrair o texto do PDF ---
def extrair_texto(url_pdf):
    caminho_local = unquote(urlparse(url_pdf).path)  
    if caminho_local.startswith("/") and caminho_local[2] == ":":
        caminho_local = caminho_local[1:] 
    with open(caminho_local, "rb") as f:
        leitor = PyPDF2.PdfReader(f)  # leitor de páginas do PDF
        texto = ""
        for pagina in leitor.pages:
            texto += pagina.extract_text()  # junta o texto de todas as páginas
    return texto


# --- Caminho do arquivo PDF ---
url_pdf = "" # --- Colocar o link do pdf ---
texto = extrair_texto(url_pdf)

# --- Quantidade de perguntas desejada ---
n = int(input("Quantas perguntas serão geradas: "))

# --- Configuração da API do Gemini ---
genai.configure(api_key="") #--- Colocar chave API ---


# --- Função para gerar perguntas com o Gemini ---
def gerarperguntas(texto, n):
    prompt = f""" 
    Gere {n} perguntas de múltipla escolha sobre o texto abaixo.
    Retorne somente em formato JSON, assim:
    [
      {{ 
        "pergunta": "texto da pergunta",
        "alternativas": ["A) ...", "B) ...", "C) ...", "D) ..."],
        "correta": "A",
        "explicacao": "breve explicação"
      }}
    ]

    Texto:
    {texto[:1000]} 
    """
    model = genai.GenerativeModel("gemini-2.5-flash")
    resposta = model.generate_content(prompt)

    # --- Limpeza do texto de resposta ---
    texto_limpo = resposta.text.strip()
    texto_limpo = texto_limpo.replace("json", "").replace("", "").strip()

    try:
        perguntas = json.loads(texto_limpo)
    except Exception as e:
        print("Erro ao converter JSON:", e)
        print("Texto recebido do modelo:\n")
        print(texto_limpo)
        perguntas = []

    return perguntas


# --- Geração das perguntas ---
perguntas = gerarperguntas(texto, n)

# --- Exibe o resultado formatado ---
print(json.dumps(perguntas, indent=2, ensure_ascii=False))

# --- Salva o resultado em um arquivo JSON ---
with open("perguntas.json", "w", encoding="utf-8") as f:
    json.dump(perguntas, f, indent=2, ensure_ascii=False)

print("\n Arquivo 'perguntas.json' gerado com sucesso!")
