import sqlite3
import os
from datetime import date

DB_NAME = 'database/hr_bot.db'

def setup_test_db():
    # 1. On supprime le fichier s'il est corrompu
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Ancien fichier {DB_NAME} supprimé.")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 2. Création de la table avec la structure complète
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        -- Informations Statiques (Obligatoires *)
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        login TEXT PRIMARY KEY, -- Login unique comme identifiant
        matricule TEXT,
        date_embauche DATE NOT NULL,
        date_sortie DATE,
        login_createur TEXT,
        date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
        login_modification TEXT,
        date_modification DATETIME,

        -- Contacts
        telephone TEXT,
        telephone_portable TEXT,
        email TEXT,
        email_notification TEXT,
        bureau TEXT,

        -- Contrat (Obligatoires *)
        departement TEXT,
        form_label_pays TEXT,
        business_unit TEXT NOT NULL,
        societe TEXT,
        etablissement TEXT NOT NULL,
        fonction_generique_groupe TEXT NOT NULL,
        poste TEXT,
        specialite TEXT,
        description_poste TEXT,
        type_contrat TEXT,
        type_ressource TEXT,

        -- Responsables (Obligatoires *)
        responsable_hierarchique TEXT NOT NULL,
        responsable_valideur TEXT NOT NULL,
        gestionnaire_admin_pers TEXT,
        rrh TEXT,
        gestionnaire_pole TEXT,
        gestionnaire_rh TEXT,

        -- Champs Dynamiques
        jours_conges_restants REAL DEFAULT 0,
        credit_swile REAL DEFAULT 0,
        heures_supp_semaine REAL DEFAULT 0,
        
        -- Champs Pertinents ajoutés
        teletravail_eligible BOOLEAN DEFAULT 1,
        derniere_formation_securite DATE,
        pointure_chaussures_epi INTEGER -- Exemple pour le matériel de sécurité
    )
    ''')

    # 3. Insertion d'un utilisateur de test (John Doe)
    user_test = (
        'Doe', 'John', 'j.doe', 'MAT-001', '2022-01-15', 'admin',
        '0123456789', 'john.doe@tech-corp.com',
        'TECH_PROD', 'FRANCE', 'BU_TECH', 'SE Engineering', 'Paris-Etoile', 'Ingénieur Senior',
        'Alice Manager', 'Bob Valideur', 'Claire RH',
        25.0, 145.50, 3.5
    )

    cursor.execute('''
    INSERT INTO users (
        nom, prenom, login, matricule, date_embauche, login_createur,
        telephone, email, 
        departement, form_label_pays, business_unit, societe, etablissement, fonction_generique_groupe,
        responsable_hierarchique, responsable_valideur, rrh,
        jours_conges_restants, credit_swile, heures_supp_semaine
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', user_test)

    conn.commit()
    conn.close()
    print(f"Base de données {DB_NAME} créée avec succès avec 1 profil de test.")

def check_user(login):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    res = conn.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchone()
    conn.close()
    if res:
        print(f"--- Fiche de {res['prenom']} {res['nom']} ---")
        print(f"BU: {res['business_unit']} | Congés: {res['jours_conges_restants']}j")
        print(f"Manager: {res['responsable_hierarchique']}")
    else:
        print("Utilisateur non trouvé.")
    

if __name__ == "__main__":
    #setup_test_db()
    check_user('j.doe')