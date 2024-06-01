from dateutil.relativedelta import relativedelta
from datetime import datetime
import calendar
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget,
    QTableWidgetItem, QListWidget, QPushButton, QLineEdit, QLabel, QSplitter, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QDialog, QLineEdit, QLabel, QPushButton, QDialogButtonBox


class kalendarz:
    """
    Klasa obsługująca cały kalendarz: wczytywanie, zapisywanie,
    wyświetlanie oraz wszystkie potrzebne funkcje
    """

    def __init__(self):
        """
        Utworzenie kalendarza, narazie bez jego wyświetlenia.
        Wczytanie danych z pliku i utworzenie z nich potrzebnych
        zmiennych
        """
        with open('kalendarz.txt', 'r') as file:
            lines = file.readlines()
            lista_krotek = [tuple(line.strip().split('\t')) for line in lines]
        self.miesiace = []
        self.czy_ustawiamy_dni_uczelniane = False

        lista_miesięcy = []
        for x in range(1, 13):
            lista_miesięcy.append(
                [krotka for krotka in lista_krotek if krotka[1] == str(x)])
        lista_miesięcy = sorted(
            lista_miesięcy, key=lambda x: (int(x[0][2]), int(x[0][1])))
        for lista_dni_miesiąca in lista_miesięcy:
            lista_dni = []
            for dzień in lista_dni_miesiąca:
                lista_dni.append(dzien(int(dzień[0]), int(
                    dzień[1]), int(dzień[2]), dzień[3], dzień[4], eval(dzień[5])))
            self.miesiace.append(miesiac(int(lista_dni_miesiąca[0][2]), int(
                lista_dni_miesiąca[0][1]), lista_dni))
        self.ustaw_wyswietlany_miesiąc_na_teraz()

    def ustaw_wyswietlany_miesiąc_na_teraz(self):
        """
        Ustawienie wyswietlanego miesiąca na
        miesiąc zgodny z aktualną datą
        """
        aktualny_miesiac = datetime.now().month
        for pozycja_na_liscie in range(12):
            if self.miesiace[pozycja_na_liscie].numer_miesiaca == aktualny_miesiac:
                self.aktualnie_wyswietlany_miesiac = pozycja_na_liscie

    def przesuń_wyswietlany_miesiac_o_x(self, x):
        if self.aktualnie_wyswietlany_miesiac+x in list(range(12)):
            self.aktualnie_wyswietlany_miesiac += x
            self.wyswietl_aktualny_miesiac()

    def zaktualizuj_kalendarz(self):
        """
        Zrestartowanie kalendarza, czyli usunięcie wszystkich aktualnych
        danych oraz zastąpienie ich danymi zgodnymi z aktualną datą.
        """
        self.miesiace = []
        aktualna_data = datetime.now()

        for i in range(5, 0, -1):
            poprzednia_data = aktualna_data - relativedelta(months=i)
            self.miesiace.append(
                miesiac(poprzednia_data.year, poprzednia_data.month))

        self.miesiace.append(miesiac(aktualna_data.year, aktualna_data.month))

        for i in range(1, 7):
            przyszła_data = aktualna_data + relativedelta(months=i)
            self.miesiace.append(
                miesiac(przyszła_data.year, przyszła_data.month))
        self.ustaw_wyswietlany_miesiąc_na_teraz()
        self.wyswietl_aktualny_miesiac()

    def zapisz_kalendarz(self):
        """
        Zapisanie wprowadzonych od rozpoczęcia programu danych do pliku
        """
        with open('kalendarz.txt', 'w') as file:
            file.write('')
            for x in self.miesiace:
                for y in x.lista_dni:
                    line = f"{y.dzien}\t{y.miesiac}\t{y.rok}\t{y.text}\t{y.notatka_poboczna}\t{y.czy_uczelniany}\n"
                    file.write(line)


    def wyswietl_aktualny_miesiac(self):
        """
        Umieszczenie w tabeli kalendarza dni miesiąca zgodnego ze
        zmienną odpowiedzialną za aktualnie wyswietlany miesiąc
        """
        for kolumna in range(1,8):
            for wiersz in range(5):
                self.tabela_główna.removeCellWidget(wiersz, kolumna)
        miesiac=self.miesiace[self.aktualnie_wyswietlany_miesiac]
        aktualna_kolumna_do_wstawienia=miesiac.lista_dni[0].dzien_tygodnia+1

        aktualny_tydzien=0
        for dzien in range(len(miesiac.lista_dni)):
            if aktualna_kolumna_do_wstawienia==8:
                aktualna_kolumna_do_wstawienia=1
                aktualny_tydzien+=1

            miesiac.lista_dni[dzien].wstaw_przycisk(aktualny_tydzien,aktualna_kolumna_do_wstawienia,self.tabela_główna)
            aktualna_kolumna_do_wstawienia+=1
        self.ustaw_aktualna_date_w_kalendarzu()

    def ustaw_aktualna_date_w_kalendarzu(self):
        """
        ustawia w prawym górnym rogu datę
        zgodną z aktualnie wyświetlanym miesiącem
        """
        do_wyswietlenia=str(self.miesiace[self.aktualnie_wyswietlany_miesiac].numer_miesiaca)+'.'+str(self.miesiace[self.aktualnie_wyswietlany_miesiac].rok)
        self.tabela_główna.setItem(0, 9, QTableWidgetItem(do_wyswietlenia))


    def inicjalizuj_kalendarz(self,Okno_nadrzedne):
        """
        Wyświetla kalendarz oraz wszystkie potrzebne przyciski
        """
        self.right_bottom_section_layout = QVBoxLayout()
        self.tabela_główna=QTableWidget(5, 10)

        for kolumna in range(9):
            self.tabela_główna.setColumnWidth(kolumna, 60)
        self.tabela_główna.setColumnWidth(9, 160)

        for row in range(5):
            self.tabela_główna.setRowHeight(row, 80)

        przycisk_poprzedni=QPushButton("Poprzedni")
        przycisk_nastepny=QPushButton("Nastepny")
       
        self.tabela_główna.setCellWidget(2, 0, przycisk_poprzedni)
        self.tabela_główna.setCellWidget(2, 8, przycisk_nastepny)
        przycisk_poprzedni.clicked.connect(lambda: self.przesuń_wyswietlany_miesiac_o_x(-1))
        przycisk_nastepny.clicked.connect(lambda: self.przesuń_wyswietlany_miesiac_o_x(1))

        przycisk_resetowania=QPushButton("Resetuj")
        self.tabela_główna.setCellWidget(4, 9, przycisk_resetowania)
        przycisk_resetowania.clicked.connect(self.zaktualizuj_kalendarz)

        przycisk_zapisywania=QPushButton("Zapisz zmiany")
        self.tabela_główna.setCellWidget(3, 9, przycisk_zapisywania)
        przycisk_zapisywania.clicked.connect(self.zapisz_kalendarz)

        self.ustaw_aktualna_date_w_kalendarzu()

        self.tabela_główna.setHorizontalHeaderLabels(["","Pn", "Wt", "Śr","Czw","Pt","So","Nd","",""])
        self.right_bottom_section_layout.addWidget(self.tabela_główna)

        self.right_bottom_section_widget = QWidget()
        self.right_bottom_section_widget.setLayout(self.right_bottom_section_layout)

        Okno_nadrzedne.addWidget(self.right_bottom_section_widget)

class miesiac:
    """
    Klasa odpowiadająca za dane związane z konkretnym miesiącem
    """
    def __init__(self, rok, numer_miesiaca, lista_dni=[]):
        """
        Utworzenie miesiąca z podaną już listą dni, lub tworzenie nowej
        """
        self.numer_miesiaca = numer_miesiaca
        self.rok = rok
        if len(lista_dni) == 0:
            self.lista_dni = list(dzien(x, numer_miesiaca, rok) for x in range(
                1, calendar.monthrange(rok, numer_miesiaca)[1]+1))
        else:
            self.lista_dni = lista_dni


class dzien:
    def __init__(self, dzien, miesiac, rok, text="",notatka_poboczna="" ,czy_uczelniany=False):
        self.dzien = dzien
        self.miesiac = miesiac
        self.rok = rok
        self.dzien_tygodnia = calendar.weekday(rok, miesiac, dzien)
        self.czy_uczelniany = czy_uczelniany
        self.text = text
        self.notatka_poboczna=notatka_poboczna

    def wstaw_przycisk(self,wiersz,kolumna,tabela):
        self.przycisk = QPushButton(f"{self.dzien}")
        tabela.setCellWidget(wiersz, kolumna, self.przycisk)
        
        
kalendarzyk = kalendarz()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aplikacja z trzema sekcjami")
        self.setGeometry(100, 100, 1200, 600)

        self.sublist_data = {}  # Dictionary to store sublist items

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Duża sekcja na górze
        top_section_layout = QVBoxLayout()
        top_section_table = QTableWidget(5, 3)  # 5 wierszy, 3 kolumny
        top_section_table.setHorizontalHeaderLabels(
            ["Kolumna 1", "Kolumna 2", "Kolumna 3"])
        top_section_layout.addWidget(top_section_table)

        # Dodanie dużej sekcji do głównego layoutu
        main_layout.addLayout(top_section_layout)

        # Małe sekcje na dole
        bottom_section_layout = QHBoxLayout()

        # Lewa dolna sekcja - lista z możliwością dodawania napisów
        self.left_bottom_section_splitter = QSplitter(Qt.Horizontal)
        self.left_bottom_section_splitter.setChildrenCollapsible(False)

        left_bottom_section_widget = QWidget()
        self.left_bottom_section_layout = QVBoxLayout(
            left_bottom_section_widget)

        self.list_widget = QListWidget()
        self.left_bottom_section_layout.addWidget(QLabel("Twoje przedmioty:"))
        self.left_bottom_section_layout.addWidget(self.list_widget)

        self.input_line = QLineEdit()
        self.add_button = QPushButton("Dodaj napis")
        self.add_button.clicked.connect(self.add_item_to_list)

        self.left_bottom_section_layout.addWidget(self.input_line)
        self.left_bottom_section_layout.addWidget(self.add_button)

        self.left_bottom_section_splitter.addWidget(left_bottom_section_widget)

        # Prawa dolna sekcja

        right_bottom_section_widget = QWidget()

        # Dodanie małych sekcji do głównego layoutu
        bottom_section_layout.addWidget(self.left_bottom_section_splitter)
        kalendarzyk.inicjalizuj_kalendarz(bottom_section_layout)
        kalendarzyk.wyswietl_aktualny_miesiac()
        bottom_section_layout.addWidget(right_bottom_section_widget)
        main_layout.addLayout(bottom_section_layout)

        # Przykładowe dane
        self.populate_table(top_section_table)

        self.list_widget.itemClicked.connect(lambda item: self.open_sublist(
            item, self.left_bottom_section_splitter, self.sublist_data, 1))

        # Load list items from file
        self.load_items_from_file()
        self.load_sublists_from_file()

    def populate_table(self, table):
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                table.setItem(row, col, QTableWidgetItem(
                    f"Item {row+1},{col+1}"))

    def add_item_to_list(self):
        text = self.input_line.text()
        if text:
            self.list_widget.addItem(text)
            self.input_line.clear()
            self.save_items_to_file()

    def open_sublist(self, item, splitter, current_data, level):
        if splitter.count() > 1:
            splitter.widget(1).deleteLater()

        sublist_splitter = QSplitter(Qt.Horizontal)
        sublist_splitter.setChildrenCollapsible(False)

        sublist_widget = QWidget()
        sublist_layout = QVBoxLayout(sublist_widget)

        sublist = QListWidget()
        sublist_layout.addWidget(QLabel(f"Podlista dla: {item.text()}"))
        sublist_layout.addWidget(sublist)

        sub_input_line = QLineEdit()
        sub_add_button = QPushButton("Dodaj napis do podlisty")
        sub_add_button.clicked.connect(lambda: self.add_item_to_sublist(
            sublist, sub_input_line, item.text(), current_data, level))

        sublist_layout.addWidget(sub_input_line)
        sublist_layout.addWidget(sub_add_button)

        # Load existing items for the selected sublist
        if item.text() in current_data:
            for sub_item_text in current_data[item.text()]["items"]:
                sublist.addItem(sub_item_text)

        sublist_splitter.addWidget(sublist_widget)

        splitter.addWidget(sublist_splitter)
        splitter.setSizes([100, 100])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        if level == 1:
            sublist.itemClicked.connect(lambda sub_item: self.open_sublist(
                sub_item, sublist_splitter, current_data[item.text()]["sublists"], 2))

    def add_item_to_sublist(self, sublist, sub_input_line, parent_item_text, current_data, level):
        text = sub_input_line.text()
        if text:
            sublist.addItem(text)
            sub_input_line.clear()

            if parent_item_text not in current_data:
                current_data[parent_item_text] = {"items": [], "sublists": {}}
            current_data[parent_item_text]["items"].append(text)
            self.save_sublist_to_file()

    def save_items_to_file(self):
        items = [self.list_widget.item(i).text()
                 for i in range(self.list_widget.count())]
        with open("items.txt", "w") as file:
            file.write("\n".join(items))

    def load_items_from_file(self):
        try:
            with open("items.txt", "r") as file:
                items = file.readlines()
                for item in items:
                    self.list_widget.addItem(item.strip())
        except FileNotFoundError:
            pass

    def save_sublist_to_file(self):
        def serialize_sublists(data):
            return {key: {"items": value["items"], "sublists": serialize_sublists(value["sublists"])} for key, value in data.items()}

        with open("sublists.txt", "w") as file:
            file.write(str(serialize_sublists(self.sublist_data)))

    def load_sublists_from_file(self):
        def deserialize_sublists(data):
            return {key: {"items": value["items"], "sublists": deserialize_sublists(value["sublists"])} for key, value in data.items()}

        try:
            with open("sublists.txt", "r") as file:
                content = file.read()
                if content:
                    self.sublist_data = deserialize_sublists(eval(content))
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
