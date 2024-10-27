import sys
import mysql.connector
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel,
                             QMessageBox)
from PyQt5.QtCore import Qt  # For at definere read-only flags
from forside_vurdering import create_main_window  # Importer vurderingsvinduet
from indhent_data.info import host1, user1, password1, database1  # Forbindelsesinfo til SQL-databasen


class CaseSelection(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Vælg eller Opret Sag')
        self.setGeometry(100, 100, 1700, 1000)

        # Layout for hovedvindue
        layout = QVBoxLayout()

        # Titel
        layout.addWidget(QLabel('Vælg en eksisterende sag eller opret en ny'))

        # Tabel over eksisterende sager
        self.case_table = QTableWidget()
        self.case_table.setColumnCount(4)  # Vi har 4 kolonner: Sag ID, Startdato, Adresse, Postnummer
        self.case_table.setHorizontalHeaderLabels(["Sag ID", "Startdato", "Adresse", "Postnummer"])

        # Juster bredden af kolonner
        self.case_table.setColumnWidth(0, 80)  # Sag ID kolonne
        self.case_table.setColumnWidth(1, 120)  # Startdato kolonne
        self.case_table.setColumnWidth(2, 300)  # Adresse kolonne
        self.case_table.setColumnWidth(3, 80)  # Postnummer kolonne

        self.case_table.setSelectionBehavior(QTableWidget.SelectRows)  # Gør så kun hele rækker markeres
        self.case_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Gør tabellen read-only
        self.case_table.verticalHeader().setVisible(False)  # Skjul rækkeindeksene
        self.case_table.cellDoubleClicked.connect(self.open_case_on_double_click)  # Tilføj dobbeltklik-funktion
        self.load_cases_from_db()  # Hent sager fra SQL-database og tilføj dem til tabellen
        layout.addWidget(self.case_table)

        # Knap til at åbne en eksisterende sag
        open_case_button = QPushButton('Tilgå Valgte Sag')
        open_case_button.clicked.connect(self.open_existing_case)
        layout.addWidget(open_case_button)

        # Knap til at oprette en ny sag
        new_case_button = QPushButton('Opret Ny Sag')
        new_case_button.clicked.connect(self.create_new_case)
        layout.addWidget(new_case_button)

        self.setLayout(layout)

    def load_cases_from_db(self):
        """Henter eksisterende sager fra SQL-databasen og tilføjer dem til tabel."""
        try:
            connection = mysql.connector.connect(
                host=host1,
                user=user1,
                password=password1,
                database=database1
            )
            cursor = connection.cursor()

            # SQL-forespørgsel for at hente id, startdato, adresse og postnummer fra databasen
            cursor.execute("SELECT id, startdato, adresse, postnummer FROM sager")
            cases = cursor.fetchall()

            # Indstil antallet af rækker i tabellen
            self.case_table.setRowCount(len(cases))

            # Tilføj sager til tabellen
            for row, case in enumerate(cases):
                case_id, startdato, adresse, postnummer = case

                # Opret tabelceller som read-only
                case_id_item = QTableWidgetItem(str(case_id))
                case_id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Gør cellen ikke-redigerbar
                self.case_table.setItem(row, 0, case_id_item)

                startdato_item = QTableWidgetItem(str(startdato))
                startdato_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.case_table.setItem(row, 1, startdato_item)

                adresse_item = QTableWidgetItem(adresse)
                adresse_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.case_table.setItem(row, 2, adresse_item)

                postnummer_item = QTableWidgetItem(str(postnummer))
                postnummer_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.case_table.setItem(row, 3, postnummer_item)

            cursor.close()
            connection.close()

        except mysql.connector.Error as err:
            print(f"Fejl ved forbindelse til databasen: {err}")
            QMessageBox.warning(self, "Database Fejl", f"Kunne ikke hente sager: {err}")

    def create_new_case(self):
        """Opretter en ny sag i databasen og åbner vurderingsvinduet for den nye sag."""
        try:
            connection = mysql.connector.connect(
                host=host1,
                user=user1,
                password=password1,
                database=database1
            )
            cursor = connection.cursor()

            # Tilføj en ny sag med dags dato som startdato
            cursor.execute("INSERT INTO sager (startdato) VALUES (CURDATE())")
            connection.commit()

            # Hent ID for den nyoprettede sag
            new_case_id = cursor.lastrowid

            cursor.close()
            connection.close()

            # Åbn vurderingsvinduet for den nye sag
            self.open_vurdering(new_case_id)

        except mysql.connector.Error as err:
            print(f"Fejl ved oprettelse af ny sag: {err}")
            QMessageBox.warning(self, "Database Fejl", f"Kunne ikke oprette ny sag: {err}")

    def open_existing_case(self):
        """Åbner vurderingsvinduet for den valgte sag."""
        selected_row = self.case_table.currentRow()
        if selected_row != -1:
            # Hent sag ID fra den valgte række
            case_id = int(self.case_table.item(selected_row, 0).text())
            self.open_vurdering(case_id)
        else:
            QMessageBox.warning(self, "Fejl", "Ingen sag valgt.")

    def open_case_on_double_click(self, row):
        """Åbner den valgte sag, når der dobbeltklikkes på en række."""
        case_id = self.case_table.item(row, 0).text()  # Hent Sag ID fra første kolonne
        self.open_vurdering(int(case_id))  # Åbn vurderingsvinduet for det valgte Sag ID

    def open_vurdering(self, sags_id):
        """Åbner vurderingsvinduet og skjuler det nuværende vindue."""
        self.vurdering_window = create_main_window(sags_id, self.show)  # Send self.show som callback
        self.vurdering_window.show()  # Sørg for at det nye vindue vises
        self.hide()  # Skjul dette vindue


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CaseSelection()
    window.show()
    sys.exit(app.exec_())
