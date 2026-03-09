import asyncio
import os
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_mcp import MCPToolkit
from langgraph.prebuilt import create_react_agent

from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import argparse
import time

# Ajouter un argument en ligne de commande pour choisir entre Mistral et Gemini
parser = argparse.ArgumentParser(description="Choisir entre Mistral et Gemini pour les clés API.")
parser.add_argument("--api", type=str, choices=["mistral", "gemini"], default="gemini", help="Choisir entre Mistral et Gemini pour les clés API.")
args = parser.parse_args()


load_dotenv()

prompt = "Tu es un assistant RH polyvalent. Utilise exclusivement 'consulter_politiques_rh_SE' pour les questions sur le règlement et les autres outils des employés de la société SE Engineering et 'consulter_politiques_rh_SMA' pour les questions sur le règlement et les autres outils des employés de la société SMA pour les données personnelles des employés. " \
    "Le tool get_user_societe te permet de récupérer la société du user."

if args.api == "mistral":
    embeddings = MistralAIEmbeddings(mistral_api_key=os.getenv("MISTRAL_API_KEY"))
else:
    embeddings = GoogleGenerativeAIEmbeddings(google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-embedding-001")

# Chargement et indexation (à faire une seule fois au démarrage)
documents_SE = []
for file in ["data_SE/politique_teletravail.pdf", "data_SE/guide_conges.pdf"]:
    if os.path.exists(file):
        loader = PyPDFLoader(file)
        documents_SE.extend(loader.load())

if documents_SE:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits_SE = text_splitter.split_documents(documents_SE)
    vectorstore_SE = FAISS.from_documents(documents=splits_SE, embedding=embeddings)
    retriever_SE = vectorstore_SE.as_retriever()
else:
    retriever_SE = None
    print("⚠️ PDF non trouvés. L'outil RAG SE Engineering sera inactif.")

documents_SMA = []
for file in ["data_SMA/politique_teletravail.pdf", "data_SMA/guide_conges.pdf"]:
    if os.path.exists(file):
        loader = PyPDFLoader(file)
        documents_SMA.extend(loader.load())

if documents_SMA:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits_SMA = text_splitter.split_documents(documents_SMA)
    vectorstore_SMA = FAISS.from_documents(documents=splits_SMA, embedding=embeddings)
    retriever_SMA = vectorstore_SMA.as_retriever()
else:
    retriever_SMA = None
    print("⚠️ PDF non trouvés. L'outil RAG SMA sera inactif.")

# --- 2. DÉFINITION MANUELLE DE L'OUTIL ---
@tool
def consulter_politiques_rh_SE(query: str) -> str:
    """
    Recherche des informations dans les documents officiels RH (télétravail, congés, etc.) de la société SE Engineering.
    Utilise cet outil pour répondre aux questions sur les règles de l'entreprise.
    """
    if not retriever_SE:
        return "Erreur : La base de documents RH n'est pas disponible."

    # On récupère les documents pertinents
    docs = retriever_SE.invoke(query)
    # On fusionne le contenu pour l'agent
    return "\n\n".join([d.page_content for d in docs])

@tool
def consulter_politiques_rh_SMA(query: str) -> str:
    """
    Recherche des informations dans les documents officiels RH (télétravail, congés, etc.) de la société SMA.
    Utilise cet outil pour répondre aux questions sur les règles de l'entreprise.
    """
    if not retriever_SMA:
        return "Erreur : La base de documents RH n'est pas disponible."
    
    # On récupère les documents pertinents
    docs = retriever_SMA.invoke(query)
    # On fusionne le contenu pour l'agent
    return "\n\n".join([d.page_content for d in docs])

async def run():
    # 1. Configuration du serveur
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )

    # 2. Gestion de la connexion
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialisation de la session MCP
            await session.initialize()
            toolkit = MCPToolkit(session=session) 
            await toolkit.initialize()
            
            # 4. Récupération des outils
            mcp_tools = toolkit.get_tools()
            all_tools = mcp_tools + [consulter_politiques_rh_SE, consulter_politiques_rh_SMA]
            
            # 5. Configuration de l'agent
            if args.api == "mistral":
                model = ChatMistralAI(
                    model="mistral-small-latest",
                    mistral_api_key=os.getenv("MISTRAL_API_KEY")
                ).bind_tools(all_tools, parallel_tool_calls=False)
            else:
                model=ChatGoogleGenerativeAI(
                    model="gemini-flash-latest",
                    google_api_key=os.getenv("GOOGLE_API_KEY"),
                    temperature=0
                )
            agent = create_react_agent(model, all_tools, prompt=prompt)
            time.sleep(1)

            print("Veuillez entrer vos questions (une par ligne). Appuyez sur Entrée pour terminer :")
            while True:
                query = input("Question : ")
                if query.strip() == "":
                    break

                print(f"\nQuestion : {query}")
                result = await agent.ainvoke({
                    "messages": [("user", query)]
                })
                # Extraire la valeur de 'text' à partir des réponses du LLM
                if args.api == "mistral":
                    text_content = result["messages"][-1].content
                else:
                    text_content = result["messages"][-1].content[0]["text"]
                print(f"Réponse : {text_content}")
                print("-" * 50)
                time.sleep(1)

if __name__ == "__main__":
    asyncio.run(run())