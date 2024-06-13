import subprocess

"""
Ce script exécute le script `init_db.py` pour initialiser la base de données.
"""

if __name__ == "__main__":
    try:
        subprocess.run(["python", "dev/init_db.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Une erreur s'est produite lors de l'exécution du script init_db.py : {e}")
