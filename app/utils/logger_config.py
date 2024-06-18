import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import colorlog


class LoggerConfig:
    """Configuration de logger pour l'application"""

    def __init__(self, name=__name__, log_file="epic_events.log", max_bytes=1000000, backup_count=3):
        """
        Initialise la configuration du logger.

        :param name: Nom du logger (par défaut, le nom du module actuel).
        :param log_file: Nom du fichier de log (par défaut, 'epic_events.log').
        :param max_bytes: Taille maximale du fichier de log avant rotation (par défaut, 1000000).
        :param backup_count: Nombre de fichiers de sauvegarde à conserver (par défaut, 3).
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Créer un formatter pour définir le format des messages de log
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%d-%m-%Y %H:%M:%S"
        )

        # Créer un formatter coloré pour les messages de log sur la console
        color_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%d-%m-%Y %H:%M:%S",
            log_colors={
                "DEBUG": "reset",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )

        # Créer un handler pour afficher les messages sur la console avec des couleurs
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(color_formatter)  # Appliquer le formatter coloré au handler

        # Créer un handler pour écrire dans un fichier de log avec rotation
        file_path = Path(__file__).parent.parent / "data" / log_file
        file_handler = RotatingFileHandler(file_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Tous les messages de log seront écrits dans le fichier
        file_handler.setFormatter(formatter)  # Appliquer le formatter au handler

        # Ajouter les handlers au logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

        # Ajouter un gestionnaire d'exceptions global
        sys.excepthook = self.handle_exception

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Gestionnaire d'exceptions global qui enregistre toutes les exceptions non gérées."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    def get_logger(self):
        """Retourne le logger configuré"""
        return self.logger


# Utilisation de la classe LoggerConfig
if __name__ == "__main__":
    logger_config = LoggerConfig()
    logger = logger_config.get_logger()

    logger.debug("Ceci est un message de debug")
    logger.info("Ceci est un message d'information")
    logger.warning("Ceci est un message d'avertissement")
    logger.error("Ceci est un message d'erreur")
    logger.critical("Ceci est un message critique")

    # crée une exception
    print(1 / 0)
