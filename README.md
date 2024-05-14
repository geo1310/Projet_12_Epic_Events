![image](./docs/images/Banner_epic_events.png)
# Epic Events

![Python](https://img.shields.io/badge/python-3.11.x-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.30-green.svg)
![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-blue)


[![pytest](https://img.shields.io/badge/pytest-passing-success)](https://pytest.org)
[![Coverage](https://img.shields.io/badge/coverage-%25-green)](https://coverage.readthedocs.io/en/latest/)
[![Locust](https://img.shields.io/badge/locust-ready-brightgreen)](https://locust.io/)

[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Flake8](https://img.shields.io/badge/flake8-checked-blueviolet)](https://flake8.pycqa.org/en/latest/)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

![Repo Size](https://img.shields.io/github/repo-size/geo1310/Projet_12_Epic_Events)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/geo1310/Projet_12_Epic_Events)

Création d'une solution de CRM (Customer Relationship Management).

Objectif principal est de mettre en place une base de données qui permette de stocker et de manipuler de manière sécurisée les informations de nos clients, ainsi que les contrats et les événements que nous organisons.

## Documents du Projet


1. __[Cahier des charges](docs/Backend+sécurisé_Cahier+des+charges+[2.0].pdf)__
    * Contexte du projet.
    * Exigences du projet.

1. __[Diagramme d'association ERD ( Entity Relationship Diagram) ](docs/Epic_Events_ERD.pdf)__
    * Structure de la base de données.

## Installation et activation de l'environnement Virtuel et des dépendances
Création de l'environnement virtuel : 
```bash
python -m venv env
```
Activation de l'environnement virtuel se placer dans le dossier **env/scripts** et taper : 
```bash
./activate
```
Installation des dependances necessaires au projet avec poetry : 
```bash
pip install poetry
poetry install

```
## Usage

Exécuter la commande suivante dans le dossier racine pour lancer l'application :

```bash
python main.py
```

## Contribuer

Si vous souhaitez contribuer à ce projet, veuillez suivre ces étapes :

    Ouvrez un problème pour discuter de ce que vous souhaitez changer.
    Fork ce dépôt et créez une branche pour votre contribution.
    Soumettez une demande d'extraction avec vos modifications.
