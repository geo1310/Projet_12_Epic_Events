from rich.console import Console
from rich.table import Table

from ..models.contract import Contract
from ..models.database import Session
from ..views.views import View


class ContractManage:
    """
    Gère les opérations liées aux contrats, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self):
        self.session = Session()
        self.view = View()
        self.console = Console()

    def list(self):

        contracts = self.session.query(Contract).all()

        # création du tableau
        table = Table(show_header=True, header_style="bold green")

        # Ajouter des colonnes
        table.add_column("ID", style="dim", width=5)
        table.add_column("Titre")
        table.add_column("Nom du Client")
        table.add_column("Email du Client")
        table.add_column("Montant")
        table.add_column("Montant restant du")
        table.add_column("Contrat signé")
        table.add_column("Date de création")

        for contract in contracts:

            table.add_row(
                str(contract.Id),
                contract.Title,
                contract.CustomerRel.FirstName,
                contract.CustomerRel.Email,
                str(contract.Amount),
                str(contract.AmountOutstanding),
                str(contract.ContractSigned),
                self.format_date(contract.DateCreated),
            )

        # Affiche le tableau
        self.view.display_table(table, "\nListe des Contrats")
        self.view.prompt_wait_enter()

    def create(self):
        # TODO
        pass

    def update(self):
        # TODO
        pass

    def delete(self):
        # TODO
        pass

    def format_date(self, date:str):
        """
        Formate une date en chaîne de caractères au format "JJ/MM/AAAA HH:MN".

        Cette méthode prend un objet date et le formate en une chaîne de caractères
        selon le format "jour/mois/année". Si la date est None, la méthode retourne None.

        Args:
            date: La date à formater.

        Returns:
            str: La date formatée en chaîne de caractères si la date est fournie, None sinon.
        """
        if date:
            return date.strftime("%d/%m/%Y %H:%M")
        return None
