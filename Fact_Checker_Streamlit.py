# Do "Get started with the Gemini API: Python"

import streamlit as st
from PIL import Image

import textwrap
import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

autentication_type = st.sidebar.radio(
    "Choose autentication type:",
    ("password", "my own OPENAI_API_KEY")
    )
if "autentication" not in st.session_state:
    st.session_state.autentication = autentication_type
st.session_state.autentication = autentication_type
pwd = st.sidebar.text_input("type your password or APY key", type="password")
if st.session_state.autentication == "password":
    if pwd == st.secrets["PASSWORD"]:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    GOOGLE_API_KEY = pwd

# CONFIGURAÇÂO PARA BUSCA NA INTENET

from googlesearch import search # Biblioteca não oficial para dusca no Google: https://pypi.org/project/googlesearch-python/
import requests # Biblioteca para carregar páginas da internet: https://pypi.org/project/requests/
from bs4 import BeautifulSoup # Biblioteca para manipular arquivos HTML e XML baixados da internet: https://beautiful-soup-4.readthedocs.io/en/latest/


# Definir os domínios de busca. Esta configuração é importante pois são as fontes que vão determinar
# a qualidade da informação utilizada. É importante que as fontes sejam variadas para dar um equilíbrio
# nos diferentes viéses, partindo-se do princpipio que não há jornalismo ou informação sem viés.
# Entretanto, é importante evitar sites de jornalísmo com forte viés ideológico.

NUMERO_DE_DOMINIOS = 5 # Numeros de dominios de busca para usar (quanto mais, melhor, porém mais demorado e com maior consumo de tokens)
MAX_REPETICAO = 2 # Numero máximos de repetições aceitas de links em mesmo domínio. Pouco adianta comparar 5 notícias de um mesmo portal.

# DOMÍNIOS DE BUSCA
DOMINIOS_DE_BUSCA = [
    "https://exame.com/",
    "https://www.cnnbrasil.com.br/",
    "https://www.cartacapital.com.br/",
    "https://www.poder360.com.br/",
    "https://www.bbc.com/",
    "https://g1.globo.com/",
    "https://www.poder360.com.br/", # Até aqui coloquei sites de notícias abertos
    "https://www.in.gov.br/",
    "https://www12.senado.leg.br/",
    "https://www.camara.leg.br/",
    "https://www.gov.br",
    "https://www.cnj.jus.br/", # Até aqui inclui sites oficiais mais importantes do governo federal.
    "https://agenciabrasil.ebc.com.br/",
    "https://noticias.uol.com.br/confere/",
    "https://checamos.afp.com/",
    "https://lupa.uol.com.br/",
    "https://www.boatos.org/",
    "https://projetocomprova.com.br/",
    "https://www.e-farsas.com/" # Até aqui incluí portais de verifcações de fatos profissionais, para caso a notícia já tenha sido verificada.
]

# Função busca de links relacionados ao critério de busca 'resultados'
def listar_links(results, dominios=DOMINIOS_DE_BUSCA, n=NUMERO_DE_DOMINIOS):
  """
  A Função executa busca no Google Search usando a variável 'resultados'
  Busca restrita aos domínios = lista de dominios
  n = numero de links a retornar, se 0 ele usa a quantidade de dominios listados
  Retorna lista de links
  """
  if n == 0:
    n = len(dominios)
  links = []
  for result in results:
    # Verificar contagem de dominio repetitivo para não ultrapassar limite estabelecido
    if verify_domains_max(result, links):
      links.append(result)
      n = n - 1
      if n == 0 :
        break
  return links

# verifica a contagens de dominios já utilizados para evitar repetições
def verify_domains_max(result, links):
  """
  retorna TRUE ou FALSE se a quantidade de dominios passou do limite
  """
  #identificar dominio
  the_domain = "new_domain"
  for domain in DOMINIOS_DE_BUSCA:
    if domain in result:
      the_domain = domain
      break
  # Contar quantas vezes dominio aparece em links
  c = 0
  for link in links:
    if the_domain in link:
      c = c + 1
  # Verifica ontagem
  if c >= MAX_REPETICAO:
    return False
  elif the_domain == "new_domain":
    return False
  else:
    return True

def ler_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    texto_da_publicacao = soup.find('div', class_='publicacao-texto')
    try:
      # Tente executar o comando
      # Nos testes vi que muitos sites não tem título definido desta forma...
      title = soup.title.string
      msg = ("   -> Notícia encontrada:", title)
    except Exception as error:
      # Se ocorrer um erro, execute a ação alternativa
      msg = "  -> :ERRO Menor: Noticia sem titulo - deixar titulo como 'noticia'"
      title = "Noticia"
    text_soup = soup.getText()
    return text_soup, title, msg

def interpretar_noticias(text_soup, title, noticias):
    try:
      gen_response = model.generate_content(
          "Transcrever o artigo principa em meio à sopa de letras e codigos:" + text_soup,
          generation_config=genai.types.GenerationConfig(
            candidate_count=1,
            temperature=0) # Temperatura zero pois a rede não deve criar, apenas transcrever
          ).text
      noticias.append({"title": title, "news": gen_response, "source": url})
      msg = "   -> OK para '", title, "'"
    except Exception as error:
      msg = "   -> ERRO: NOK para '", title, "'"
    return noticias, msg

# Define string de busca do google search para sites de noticias
def news(fact):
  """
  Busca as notícias e retorna query para busca de referencias
  fact deve ser um link válido
  """
  # inicializa notocias
  news = []
  # Buscar notícia
  #print("\n:Status: Buscando notícia fornecida...")
  response = requests.get(fact)
  soup = BeautifulSoup(response.content, 'html.parser')
  texto_da_publicacao = soup.find('div', class_='publicacao-texto')
  try:
    # Tente executar o comando
    # Nos testes vi que muitos sites não tem título definido desta forma...
    title = soup.title.string
    #print("   -> Notícia encontrada:", title)
  except Exception as error:
    # Se ocorrer um erro, execute a ação alternativa
    #print(f"  -> :ERRO Menor: Noticia sem titulo - deixar titulo como 'noticia'")
    title = "Noticia"
  text_soup = soup.getText()
  # Ler notícia
  #print(":Status: Lendo a notícia...")
  response = model.generate_content(
      "Transcrever a seguinte sopa de letrinhas no formato do artigo principal contido nela:" + text_soup,
      generation_config=genai.types.GenerationConfig(
        candidate_count=1,
        temperature=0)
      ).text
  news.append({"title": title, "news": response, "source": fact})
  #print("   -> OK")
  # Gemini cria query para buscar noticias
  #print(":Status: Gerando palavras chave para busca...")
  palavras_chave = model.generate_content(
      "Criar um query com palavras-chave para buscar no google search mais notícias relacionadas a este mesmo assunto. Retorne apenas um query, sem nenhum comentário ou explicação. NOTÍCIA:" + response,
      generation_config=genai.types.GenerationConfig(
        candidate_count=1,
        temperature=0.3)
      ).text
  #print("   -> Palavras-chave:", palavras_chave)
  return palavras_chave, news

#Define string de busca para fatos relatados
def fact(fact):
  """
  Cria um query com base na descrição do fato
  """
  #print("\n:Status: Criando query para '" + fact +"' ...")
  palavras_chave = model.generate_content(
      "Criar um query com palavras-chave para buscar no google search notícias relacionadas a este assunto. Retorne apenas um query, sem nenhum comentário ou explicação. ASSUNTO:" + fact,
      generation_config=genai.types.GenerationConfig(
        candidate_count=1,
        temperature=0.3)
      ).text
  #print("   -> Palavras-chave:", palavras_chave)
  return palavras_chave, []


# Progrma principal
def create_query(fact_2_check):
  if fact_2_check[0:4] == "http":
    query, noticias = news(fact_2_check)
    fact_2_check = noticias[0]['title']
  else:
    query, noticias = fact(fact_2_check)
  return query, noticias, fact_2_check

def buscar_noticias(query):
  # Busca de noticias
  results = search(query, num_results=250)
  links = listar_links(results)
  return links

def avaliar_noticias(noticias):
  # Com todas as notícias compiladas na lista notícias, fazer a comparação final
  #print("\n:Status: Comparando fatos")
  prompt = "Baseado nos diferentes textos do campo 'news' e 'title' dos artigos da lista a seguir, você pode opinar sobre se fatos '" + fact_2_check + "' são ou não verdadeiros? Verifique se há consistência entre estes fatos e os damais textos 'news' fornecidos para formar sua opinião. Por favor justificar sua resposta e citar as fontes sempre que possível. Lista: " + str(noticias)
  gen_response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
          candidate_count=1,
          temperature=1.0)
        ).text
  return gen_response

#MAIN PAGE
st.write("⬅ Insira a chave do API do Google AI Studio na barra lateral ou entre com a senha correta")

# FIXED SITE HEADER
col1, col2 = st.columns([0.2,0.8])
image = Image.open("header.bmp")

with col1:
   st.write('##')
   st.image(image)
with col2:
    st.title("GEMINI-powered Fact Checker")
    st.write("Verifiqu fatos narrados ou por links de notícias. O GEMINI fact checker usa a tecnologia de busca e de interpretação de linguagem natural do Google para verificar os fatos contra sites consolidados e verificados, te dando um resumo do que é verificado, do que pode estar errado e te passando os links de referência.")

# IF KEY IS AVAILABLE

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    #Inicialização do modelo
    model = genai.GenerativeModel('gemini-1.0-pro')

    fact_2_check = st.text_area()

    # React to user input
    if fact_2_check != "":

        # RUN POHATODA
        # Criar Query
        query, noticias, fact_2_check = create_query(fact_2_check)
        st.markdown("   -> Buca por: " + query )
        
        # buscar noticias
        links = buscar_noticias(query)
        st.markdown("   -> " + str(len(links)) + " notícias serão verificadas ...")

        # para cada link encontrado
        for url in links:
            # buscar noticias
            st.markdown("**:Status:** Lendo informação: " + url)
            text_soup, title, msg = ler_url(url)
            st.markdown(msg)
           
            #interpretar noticias
            noticias, msg = interpretar_noticias(text_soup, title, noticias) #noticias vazia ou com previa do inicio do main
            st.markdown(msg)
        
        st.markdown("**:Status:** Comparando fatos ...")
        chat_response = avaliar_noticias(noticias)

        st.markdown(chat_response)

# in case API key unavailable
else:
    st.markdown("please provide a valid password or a valid GOOGLE API key to start your therapy - *see sidebar on '>' top left screen*")

