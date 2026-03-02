import subprocess
import sys

def check_dependencies():
    try:
        with open('requirements.txt') as f:
            dependencies = f.read().splitlines()

        installed_packages = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode('utf-8').splitlines()
        installed_packages = [pkg.split('==')[0] for pkg in installed_packages]

        missing_packages = [pkg for pkg in dependencies if pkg not in installed_packages]

        if missing_packages:
            print("Les packages suivants sont manquants :")
            for pkg in missing_packages:
                print(f"- {pkg}")
            print("\nVeuillez installer les packages manquants en exécutant :")
            print("pip install -r requirements.txt")
        else:
            print("Toutes les dépendances sont installées.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

if __name__ == "__main__":
    check_dependencies()