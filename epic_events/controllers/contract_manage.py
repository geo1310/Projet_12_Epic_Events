from rich.console import Console
from rich.table import Table
from sqlalchemy.exc import IntegrityError

from ..models.contract import Contract
from ..models.customer import Customer
from ..models.database import Session
from ..models.employee import Employee
from ..models.role import Role
from ..permissions.permissions import Permissions
from ..views.views import View


class ContractManage:
    """
    Gère les opérations liées aux contrats, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self, user_connected_id):
        self.session = Session()
        self.view = View()
        self.console = Console()
        self.permissions = Permissions()
        self.user_connected_id = user_connected_id
        self.employee = self.session.query(Employee).filter_by(Id=user_connected_id).one()
        self.role = self.session.query(Role).filter_by(Id=self.employee.RoleId).one()

    def _get_data(self):
        """
        Récupère et initialise les données nécessaires.
        incluant les contrats et les clients selon les autorisations de l'utilisateur connecté.

        Attributs:
            self.contracts (list): Liste des contrats accessibles par l'utilisateur connecté.
            self.customers_list (list): Liste des clients accessibles par l'utilisateur connecté.

        """

        # liste des contrats selon autorisation
        if self.permissions.can_access_all_contract(self.role):
            self.contracts = self.session.query(Contract).all()
        else:
            self.contracts = (
                self.session.query(Contract)
                .join(Customer, Contract.CustomerId == Customer.Id)
                .filter(Customer.CommercialId == self.user_connected_id)
                .all()
            )

        # liste des clients selon autorisation
        if self.permissions.can_access_all_customer(self.role):
            self.customers_list = self.session.query(Customer).all()
        else:
            self.customers_list = Customer.get_customers_list(self.session, self.user_connected_id)

    def list(self):
        """
        Affiche la liste des contrats.

        Cette méthode récupère la liste des contrats à afficher en fonction des autorisations de l'utilisateur connecté.
        Si l'utilisateur a la permission d'accéder à tous les contrats, tous les contrats sont récupérés.
        Sinon, seuls les contrats associés aux clients de l'utilisateur connecté sont récupérés.

        """

        self._get_data()

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

        for contract in self.contracts:

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
        """
        Crée un nouveau contrat.

        Cette méthode permet de créer un nouveau contrat en saisissant les détails nécessaires
        via des invites à l'utilisateur. Elle gère également la validation des données
        saisies et assure que le contrat est correctement lié à un client existant.

        Workflow:
            1. Récupère les données nécessaires (contrats et clients) via la méthode `_get_data`.
            2. Affiche le titre de la section de création.
            3. Demande à l'utilisateur de saisir le titre du contrat.
            4. Valide et sélectionne le client associé au contrat.
            5. Demande à l'utilisateur de saisir les montants et vérifie leur validité.
            6. Demande à l'utilisateur de saisir l'état de signature du contrat.
            7. Crée une instance du contrat avec les données saisies.
            8. Ajoute le contrat à la session et tente de le valider en base de données.
            9. Affiche et confirme la création du contrat.
            10. Gère les exceptions potentielles et affiche les messages d'erreur appropriés.

        Exceptions:
            IntegrityError: Si une contrainte d'intégrité de la base de données est violée.
            ValueError: Si la validation des montants échoue.
            Exception: Pour toutes autres erreurs inattendues.

        Returns:
            None
        """

        self._get_data()

        self.view.display_title_panel_color_fit("Création d'un contrat", "green")

        title = self.view.return_choice("Entrez le Titre du contrat ( vide pour annuler )", False)
        if not title:
            return

        # validation du client lié au contrat
        customer_id = self.valid_customer()
        if not customer_id:
            return

        # validation des détails du contrat
        amount = self.validation_amount("Montant du contrat", "amount")
        amount_outstanding = self.validation_amount(
            "Montant restant du", "amount_outstanding", f"{amount if amount else None}"
        )
        contract_signed = self.str_to_bool(self.view.return_choice("Contrat signé", False, "non", ("oui", "non")))

        # Instance du nouveau contrat
        self.contract = Contract(
            CustomerId=customer_id,
            Title=title,
            Amount=amount,
            AmountOutstanding=amount_outstanding,
            ContractSigned=contract_signed,
        )

        # Ajouter à la session et commit
        try:
            self.session.add(self.contract)
            self.session.flush()

            # Affichage et confirmation de la création
            if not self.confirm_table_recap("Création", "green"):
                self.session.expunge(self.contract)
                self.session.rollback()
                return
            self.session.commit()
            self.view.display_green_message("\nContrat créé avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e.args[0].split("DETAIL:")[1] if e.args else "Erreur inconnue"
            self.view.display_red_message(f"Erreur : {error_detail}")
        except ValueError as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur de validation : {e}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la création du contrat : {e}")

        self.view.prompt_wait_enter()

    def update(self):
        """
        Met à jour les détails d'un contrat existant.

        Cette méthode permet de modifier les informations d'un contrat sélectionné par son identifiant.
        L'utilisateur est guidé à travers un processus de saisie pour mettre à jour les champs du contrat.
        La méthode assure également que seules les personnes autorisées peuvent modifier un contrat donné.

        Workflow:
            1. Affiche le titre de la section de modification.
            2. Demande l'identifiant du contrat à modifier.
            3. Vérifie que l'utilisateur est autorisé à modifier le contrat.
            4. Affiche et confirme les modifications.
            5. Met à jour les champs du contrat avec les nouvelles valeurs.
            6. Valide le client lié au contrat.
            7. Enregistre les modifications dans la base de données.

        Exceptions:
            ValueError: Si la validation des montants échoue.
            IntegrityError: Si une contrainte d'intégrité de la base de données est violée.
            Exception: Pour toutes autres erreurs inattendues.

        Returns:
            None
        """

        self._get_data()

        self.view.display_title_panel_color_fit("Modification d'un contrat", "yellow")

        # Validation du contrat à modifier par son Id
        while True:
            contract_id = self.view.return_choice(
                "Entrez l'identifiant du client à modifier ( vide pour annuler )", False
            )

            if not contract_id:
                return

            try:
                self.contract = self.session.query(Contract).filter_by(Id=int(contract_id)).one()

                # vérifie que le contrat est dans la liste autorisée.
                if self.contract in self.contracts:
                    break
                self.view.display_red_message("Vous n'etes pas autorisé à modifier ce contrat !")

            except Exception:
                self.view.display_red_message("Identifiant non valide !")

        # affichage et confirmation de modification
        if not self.confirm_table_recap("Modification", "yellow"):
            return

        self.view.display_title_panel_color_fit("Modification d'un contrat", "yellow", True)

        self.contract.Title = self.view.return_choice("Titre", False, f"{self.contract.Title}")
        self.contract.Amount = self.validation_amount("Montant du contrat", "amount", self.contract.Amount)
        self.contract.AmountOutstanding = self.validation_amount(
            "Montant restant du", "amount_outstanding", self.contract.AmountOutstanding
        )
        self.contract.ContractSigned = self.str_to_bool(
            self.view.return_choice(
                "Contrat signé", False, f"{'oui' if self.contract.ContractSigned else 'non'}", ("oui", "non")
            )
        )
        # validation du client lié au contrat
        self.contract.CustomerId = self.valid_customer(self.contract.CustomerId)
        if not self.contract.CustomerId:
            return

        # Ajouter à la session et commit
        try:
            self.session.commit()

            # Affichage et confirmation de la modification
            if not self.confirm_table_recap("Modification", "yellow"):
                self.session.expunge(self.contract)
                self.session.rollback()
                return

            self.view.display_green_message("\nContrat modifié avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e.args[0].split("DETAIL:")[1] if e.args else "Erreur inconnue"
            self.view.display_red_message(f"Erreur : {error_detail}")
        except ValueError as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur de validation : {e}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la modification : {e}")

        self.view.prompt_wait_enter()

    def delete(self):
        """
        Supprime un contrat existant.

        Cette méthode permet de supprimer un contrat de la base de données.
        L'utilisateur est invité à entrer l'identifiant du contrat à supprimer,
        et la méthode vérifie si l'utilisateur est autorisé à supprimer ce contrat.
        Si l'identifiant est valide et que l'utilisateur est autorisé, le contrat est supprimé
        après une confirmation.

        Raises:
            ValueError: Si l'identifiant du contrat n'est pas valide.
            Exception: Pour toute autre erreur lors de la suppression du contrat.
        """

        self._get_data()

        self.view.display_title_panel_color_fit("Suppression d'un contrat", "red")

        # Validation du contrat à supprimer par son Id
        while True:
            contract_id = self.view.return_choice(
                "Entrez l'identifiant du contrat à supprimer ( vide pour annuler )", False
            )

            if not contract_id:
                return
            try:
                self.contract = self.session.query(Contract).filter_by(Id=int(contract_id)).one()

                # vérifie que le contrat est dans la liste autorisée
                if self.contract in self.contracts:
                    break
                self.view.display_red_message("Vous n'etes pas autorisé à supprimer ce contrat !")
            except Exception:
                self.view.display_red_message("Identifiant non valide !")

        # confirmation de suppression
        if not self.confirm_table_recap("Suppression", "red"):
            return

        try:
            self.session.delete(self.contract)
            self.session.commit()
            self.view.display_green_message("Contrat supprimé avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e.args[0].split("DETAIL:")[1] if e.args else "Erreur inconnue"
            self.view.display_red_message(f"Erreur : {error_detail}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la suppression : {e}")

        self.view.prompt_wait_enter()

    def format_date(self, date: str):
        """
        Formate une date en chaîne de caractères au format "JJ/MM/AAAA HH:MN".
        Si la date est None, la méthode retourne None.

        Args:
            date: La date à formater.

        Returns:
            str: La date formatée en chaîne de caractères si la date est fournie, None sinon.
        """
        if date:
            return date.strftime("%d/%m/%Y %H:%M")
        return None

    def str_to_bool(self, str_value):
        """
        Convertit une chaîne de caractères en une valeur booléenne.

        Args:
            str_value (str): La chaîne de caractères à convertir.

        Returns:
            bool: Retourne True si la chaîne de caractères représente une valeur vraie, sinon False.
        """

        if str_value.lower() in ("true", "1", "oui"):
            return True
        return False

    def validation_amount(self, message: str, key: str, default: str = "0"):
        """
        Valide et convertit un montant saisi par l'utilisateur.

        Cette méthode affiche un message à l'utilisateur, lui demande de saisir un montant,
        et valide ensuite que le montant est bien un nombre flottant. Si la validation échoue,
        un message d'erreur est affiché et l'utilisateur est invité à saisir à nouveau le montant.

        Args:
            message (str): Le message à afficher pour demander le montant à l'utilisateur.
            key (str): Le nom du champ montant (utilisé dans la validation).
            default (str): La valeur par défaut à utiliser si l'utilisateur ne saisit rien (par défaut "0").

        Returns:
            float: Le montant validé saisi par l'utilisateur.
        """

        while True:
            amount = self.view.return_choice(f"{message}", False, f"{default}")

            try:
                Contract.validate_amount(self, f"{key}", amount)
            except ValueError as e:
                self.view.display_red_message(f"Erreur de validation : {e}")
            else:
                return amount

    def valid_customer(self, default=None):
        """
        Valide et récupère l'identifiant d'un client sélectionné pour un contrat.

        Cette méthode affiche une liste des clients disponibles pour la création d'un contrat.
        Elle demande à l'utilisateur de saisir l'identifiant du client choisi.
        Si l'identifiant est valide et correspond à un client dans la liste, celui-ci est sélectionné.
        Sinon, l'utilisateur est invité à saisir à nouveau un identifiant valide.

        Returns:
            int or None: L'identifiant du client sélectionné, ou None si aucun client n'est sélectionné.
        """

        # Tableau de choix pour les clients
        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("Prénom", style="magenta")
        table.add_column("Nom", style="magenta")
        table.add_column("Email", style="magenta")
        table.add_row("0", "Annuler")

        for customer in self.customers_list:
            table.add_row(str(customer.Id), customer.FirstName, customer.LastName, customer.Email)

        self.view.display_table(table, "Liste des clients")

        while True:

            customer_id = self.view.return_choice(
                "Entrez l'identifiant du client pour le contrat", False, f"{default}"
            )

            try:
                selected_customer = next(
                    (customer for customer in self.customers_list if customer.Id == int(customer_id)), None
                )
                if selected_customer:
                    self.view.display_green_message(f"Client sélectionné : {selected_customer.Email}")
                    return int(customer_id)
                else:
                    return None
            except ValueError:
                self.view.display_red_message("Choix invalide !")
            except Exception:
                self.view.display_red_message("Choix invalide !")

    def confirm_table_recap(self, oper: str, color: str = "white"):
        """
        Affiche un tableau récapitulatif des informations du contrat et demande une confirmation à l'utilisateur.

        Cette méthode affiche les détails du contrat dans un tableau et demande à l'utilisateur de confirmer
        l'opération en cours (création, modification, suppression, etc.). Si l'utilisateur ne confirme pas,
        l'opération est annulée.

        Args:
            oper (str): Le nom de l'opération en cours (par exemple, "Création", "Modification", "Suppression").
            color (str, optional): La couleur du titre de la section pour l'affichage (par défaut "white").

        Returns:
            bool: True si l'utilisateur confirme l'opération, False sinon.

        Workflow:
            1. Affiche le titre de la section avec le nom de l'opération et la couleur spécifiée.
            2. Crée un tableau récapitulatif des détails du contrat.
            3. Affiche le tableau avec les informations du contrat.
            4. Demande à l'utilisateur de confirmer l'opération.
            5. Si l'utilisateur ne confirme pas, affiche un message d'annulation et renvoie False.
            6. Si l'utilisateur confirme, renvoie True.
        """

        self.view.display_title_panel_color_fit(f"{oper} d'un contrat", f"{color}", True)

        # Tableau récapitulatif
        summary_table = Table()
        summary_table.add_column("Champ", style="cyan")
        summary_table.add_column("Valeur", style="magenta")
        summary_table.add_row("Client", self.contract.CustomerRel.Email)
        summary_table.add_row("Title", self.contract.Title)
        summary_table.add_row("Montant", str(self.contract.Amount))
        summary_table.add_row("Restant du", str(self.contract.AmountOutstanding))
        summary_table.add_row("Contrat signé", str(self.contract.ContractSigned))

        self.view.display_table(summary_table, "Résumé du contrat")

        # Demander une confirmation avant validation
        confirm = self.view.return_choice(f"Confirmation {oper} ? (oui/non)", False)
        if confirm:
            confirm = confirm.lower()
        if confirm != "oui":
            self.view.display_red_message("Opération annulée.")
            self.view.prompt_wait_enter()
            return False
        return True
