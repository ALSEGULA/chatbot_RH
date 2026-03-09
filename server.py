from mcp.server.fastmcp import FastMCP
import sqlite3
import os

# Initialisation du serveur FastMCP
mcp = FastMCP("HR_Data_Service")

DB_PATH = "database/hr_bot.db"

def get_db_connection():
    """Helper pour la connexion à la BDD avec support des noms de colonnes."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 1. Liste de tous les champs de votre BDD (Statiques + Dynamiques)
FIELDS = [
    "nom", "prenom", "matricule", "date_embauche", "date_sortie",
    "telephone", "telephone_portable", "email", "email_notification", "bureau",
    "departement", "form_label_pays", "business_unit", "societe", 
    "etablissement", "fonction_generique_groupe", "poste", "specialite",
    "responsable_hierarchique", "responsable_valideur", "rrh",
    "jours_conges_restants", "credit_swile", "heures_supp_semaine",
    "teletravail_eligible", "derniere_formation_securite"
]

@mcp.tool()
def get_login_from_name(nom: str, prenom:str) -> str:
    """
    Récupère le login de l'utilisateur à partir de son nom et son prénom'.
    """
    try:
        with get_db_connection() as conn:
            user = conn.execute("SELECT * FROM users WHERE nom = ? AND prenom = ?", (nom,prenom)).fetchone()
            if user:
                # On transforme le Row en dictionnaire pour une lecture propre par l'IA
                data = dict(user)
                return f"login de {data['prenom']} {data['nom']} trouvé : {data['login']}"
            return f"Erreur : Login de  {data['prenom']} {data['nom']}' introuvable."
    except Exception as e:
        return f"Erreur lors de la lecture BDD : {str(e)}"

def create_tool(field_name):
    @mcp.tool(name=f"get_user_{field_name}")
    def field_tool(login: str) -> str:
        """
        Récupère la valeur du champ spécifié (filed_name) pour un utilisateur donné via son login.
        Si tu ne possèdes que le nom et le prénom de la personne, utilise get_login_from_name pour récupérer son login avant.
        """
        try:
            with get_db_connection() as conn:
                # Sécurité : on utilise le nom du champ validé dans la liste FIELDS
                query = f"SELECT {field_name} FROM users WHERE login = ?"
                res = conn.execute(query, (login,)).fetchone()
                
                if res:
                    valeur = res[field_name]
                    return f"La valeur de '{field_name}' pour l'utilisateur {login} est : {valeur}"
                return f"Utilisateur {login} introuvable."
        except Exception as e:
            return f"Erreur lors de la récupération de {field_name} : {str(e)}"
    
    return field_tool

# 3. Génération automatique de tous les outils
for field in FIELDS:
    create_tool(field)

@mcp.tool()
def update_user_data(login: str, field_name: str, new_value: float) -> str:
    """
    Met à jour un champ d'un utilisateur (ex: 'jours_conges_restants', 'credit_swile').
    Le champ field_name est modifie et vaut new_value après l'appel à update_user_date
    """

    try:
        with get_db_connection() as conn:
            # On vérifie d'abord que l'user existe
            user = conn.execute("SELECT login FROM users WHERE login = ?", (login,)).fetchone()
            if not user:
                return f"Utilisateur {login} non trouvé."

            # Mise à jour dynamique
            query = f"UPDATE users SET {field_name} = ? WHERE login = ?"
            conn.execute(query, (new_value, login))
            conn.commit()
            return f"Succès : Le champ {field_name} vaut à présent {new_value} pour {login}."
    except Exception as e:
        return f"Erreur lors de la mise à jour : {str(e)}"

if __name__ == "__main__":
    # Lancement du serveur (par défaut en mode stdio pour Langchain/Claude Desktop)
    mcp.run()