from pathlib import Path
import logging
import colorlog
from logging.handlers import RotatingFileHandler

# Créer un logger avec le nom du module actuel
logger = logging.getLogger(__name__)

# Définir le niveau de logging à DEBUG
logger.setLevel(logging.DEBUG)

# Créer un formatter pour définir le format des messages de log
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')

# Créer un formatter coloré pour les messages de log sur la console
color_formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    log_colors={
        'DEBUG': 'reset',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red'
    }
)

# Créer un handler pour afficher les messages sur la console avec des couleurs
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)  # Seuls les messages INFO et supérieurs seront affichés sur la console
console_handler.setFormatter(color_formatter)  # Appliquer le formatter coloré au handler

# Créer un handler pour écrire dans un fichier de log avec rotation
file_path = Path(__file__).parent.parent / 'data'/ 'epic_events.log'
# file_path = os.path.abspath(os.path.dirname(__file__))

file_handler = RotatingFileHandler(file_path, maxBytes=1000000, backupCount=3, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)  # Tous les messages de log seront écrits dans le fichier
file_handler.setFormatter(formatter)  # Appliquer le formatter au handler

# Ajouter les handlers au logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
