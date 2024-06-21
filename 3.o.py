import sys
import json
from PyQt5.QtCore import Qt
import ast
import os
from dateutil.relativedelta import relativedelta
from datetime import datetime
import calendar
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget,
    QTableWidgetItem, QListWidget, QPushButton, QLineEdit, QLabel, QSplitter, QInputDialog, QMessageBox, QListWidgetItem, 
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QDialog, QLineEdit, QLabel, QPushButton, QDialogButtonBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class my_calendar:
    """
    Klasa obsługująca cały kalendarz: wczytywanie, zapisywanie,
    wyświetlanie oraz wszystkie potrzebne funkcje
    """
    def __init__(self) -> None:
        """
        Utworzenie kalendarza, narazie bez jego wyświetlenia.
        Wczytanie danych z pliku i utworzenie z nich potrzebnych
        zmiennych
        """
        try:
            #Wczytanie danych z pliku jako krotki
            with open('kalendarz.txt', 'r') as file:
                lines = file.readlines()
                tuple_list = [tuple(line.strip().split('\t')) for line in lines]
            self.months = [] 
            months_list = []
            #Stworzenie listy miesięcy, zawierającą listy z danymi
            #zwiazanymi z dniamiw poszczególnych miesięcach
            for x in range(1, 13):
                months_list.append(
                    [tuple for tuple in tuple_list if tuple[1] == str(x)])
            #Posortowanie miesięcy
            months_list = sorted(
                months_list, key=lambda x: (int(x[0][2]), int(x[0][1])))
            #Stworzenie listy zawierającej miesiące zapisane jako klasa my_month,
            # w której znajdują się dni zapisane jako klasa my_day
            for list_of_days_in_month in months_list:
                days_list = []
                for day in list_of_days_in_month:
                    days_list.append(my_day(int(day[0]), int(
                        day[1]), int(day[2]),day[3],day[4], eval(day[5])))
                self.months.append(my_month(int(list_of_days_in_month[0][2]), int(
                    list_of_days_in_month[0][1]), days_list))
        except FileNotFoundError:
            #Jeśli nie ma pliku, to tworzymy podstawowe aktualne dane
            self.reset_calendar(True)


    def set_actual_month_to_now(self) -> None:
        """
        Ustawienie  numeru wyswietlanego miesiąca (w postaci numeru z listy)
        namiesiąc zgodny z aktualną datą
        """
        actual_month=datetime.now().month
        for position_in_list in range(12):
            if self.months[position_in_list].month_number==actual_month:
                self.displayed_month=position_in_list

    def change_displayed_month_by_x(self,x:int) -> None:
        """
        Przesuwa numer wyswietlanego miesiąca o x i go wyświetla
        """
        if self.displayed_month+x in list(range(12)):
            self.displayed_month+=x
            self.display_actual_month()
            
    def reset_calendar(self,is_in_init:bool = False) -> None:
        """
        Zrestartowanie kalendarza, czyli usunięcie wszystkich aktualnych
        danych oraz zastąpienie ich danymi zgodnymi z aktualną datą.
        """
        #Wyczyszczenie listy miesięcy
        self.months = []
        actual_date = datetime.now()
        #Dodanie pięciu miesięcy przed aktualną datą
        for i in range(5, 0, -1):
            previous_date = actual_date - relativedelta(months=i)
            self.months.append(
                my_month(previous_date.year, previous_date.month))
        #Dodanie aktualnego miesiąca
        self.months.append(my_month(actual_date.year, actual_date.month))
        #Dodanie 6 następnych miesięcy
        for i in range(1, 7):
            comming_date = actual_date + relativedelta(months=i)
            self.months.append(
                my_month(comming_date.year, comming_date.month))
        #Ustawienie aktualnie wyswietlanego miesiąca na teraz
        self.set_actual_month_to_now()
        #Jeśli funkcja nie jest wywołana w __Init__ to wyświetla aktualny miesiąc
        if is_in_init==False:
            self.display_actual_month()
        
    def save_calendar(self) -> None:
        """
        Zapisanie wprowadzonych od rozpoczęcia programu danych do pliku
        """
        with open('kalendarz.txt', 'w') as file:
            file.write('')
            for x in self.months:
                for y in x.list_of_days:
                    line = f"{y.day}\t{y.month}\t{y.year}\t{y.text}\t{y.side_note}\t{y.is_university}\n"
                    file.write(line)
                    
    def display_actual_month(self) -> None:
        """
        Umieszczenie w tabeli kalendarza dni miesiąca zgodnego ze
        zmienną odpowiedzialną za aktualnie wyswietlany miesiąc
        """
        #Czyszczenie kalendarza z przycisków
        for column in range(1,8):
            for row in range(6):
                self.main_table.removeCellWidget(row, column)
        month=self.months[self.displayed_month]
        #ustawienie kolumny w zależności jakim dniem tygodnia jest pierwszy dzien miesiaca
        actual_column_to_set=month.list_of_days[0].day_of_week+1
        #Ustawienie miesiąca, czyli wiersza na pierwszy
        actual_week=0
        #Przechodzenie po tabeli kolei po dniach i dodawanie przycisków
        for day in range(len(month.list_of_days)):
            if actual_column_to_set==8:
                actual_column_to_set=1
                actual_week+=1
            month.list_of_days[day].insert_button(actual_week,actual_column_to_set,self.main_table)
            actual_column_to_set+=1
        #Zapisanie aktualnej daty w prawym górnym rogu
        self.display_actual_date()

    def set_everything_on_university(self) -> None:
        """
        Ustawia wszystkie dni aktualnie wyswietlanego miesiąca
        (nie licząc weekendów) na uczelniane
        """
        for day in self.months[self.displayed_month].list_of_days:
            if day.day_of_week in [0,1,2,3,4]:
                day.is_university=True
                day.refresh_button_colour()

    def display_actual_date(self) -> None:
        """
        ustawia w prawym górnym rogu datę
        zgodną z aktualnie wyświetlanym miesiącem
        """
        to_display=str(self.months[self.displayed_month].month_number)+'.'+str(self.months[self.displayed_month].year)
        self.main_table.setItem(0, 9, QTableWidgetItem(to_display))

    def change_parametr_to_setting_days_to_university(self) -> None:
        """
        Zmienia wartość zmiennej odpowiedzialnej za to, czy po kliknięciu
        w dzień uruchomi się okno tekstowe, czy zmieni się wartość 
        zmiennej czy_uczelniany dla danego dnia
        """
        if my_day.button_command_parametr==True:
            my_day.button_command_parametr=False
            self.button_to_change_days_to_univeristy.setStyleSheet("background-color: white;")
        else:
            my_day.button_command_parametr=True
            self.button_to_change_days_to_univeristy.setStyleSheet("background-color: blue;")

    def initialize_calendar(self, parent_window) -> None:
        """
        Wyświetla kalendarz oraz wszystkie potrzebne przyciski
        """
        #Utworzenie layoutu
        self.right_bottom_section_layout = QVBoxLayout()
        #Utworzenie tabeli
        self.main_table=QTableWidget(6, 10)
        #Ustawienie szerokości kolumn
        for kolumna in range(9):
            self.main_table.setColumnWidth(kolumna, 60)
        self.main_table.setColumnWidth(9, 160)
        self.main_table.setColumnWidth(8, 100)
        self.main_table.setColumnWidth(0, 100)
        #Ustawienie wysokości kolumn
        for row in range(6):
            self.main_table.setRowHeight(row, 60)
        #utworzenie i dodatnie przyciskow przesuwających miesiące
        button_previois=QPushButton("Poprzedni")
        button_next=QPushButton("Nastepny")
        self.main_table.setCellWidget(2, 0, button_previois)
        self.main_table.setCellWidget(2, 8, button_next)
        button_previois.clicked.connect(lambda: self.change_displayed_month_by_x(-1))
        button_next.clicked.connect(lambda: self.change_displayed_month_by_x(1))
        #Dodanie przycisku do zmiany dni na uniwersyteckie
        self.button_to_change_days_to_univeristy=QPushButton("Zacznij ustawiać \n dni uczelniane")
        self.main_table.setCellWidget(1, 9, self.button_to_change_days_to_univeristy)
        self.button_to_change_days_to_univeristy.clicked.connect(self.change_parametr_to_setting_days_to_university)
        #Dodanie przycisku do ustawienia wszystkich dni na uczelniane
        button_set_everything_university=QPushButton("Ustaw wszystko\n na uczelniane")
        self.main_table.setCellWidget(2, 9, button_set_everything_university)
        button_set_everything_university.clicked.connect(self.set_everything_on_university)
        #Dodane przycisku do resetu danych kalendarza
        button_reset=QPushButton("Resetuj")
        self.main_table.setCellWidget(4, 9, button_reset)
        button_reset.clicked.connect(self.reset_calendar)
        #Dodanie przycisku do zapisywania danych
        button_save=QPushButton("Zapisz zmiany")
        self.main_table.setCellWidget(3, 9, button_save)
        button_save.clicked.connect(self.save_calendar)
        #Ustawienie i wyświetlenie aktualnego miesiąca
        self.set_actual_month_to_now()
        self.display_actual_date()
        #Dodanie nazw kolumn
        self.main_table.setHorizontalHeaderLabels(["","Pn", "Wt", "Śr","Czw","Pt","So","Nd","",""])
        #Dodanie sekcji do głównego okna
        self.right_bottom_section_layout.addWidget(self.main_table)
        self.right_bottom_section_widget = QWidget()
        self.right_bottom_section_widget.setLayout(self.right_bottom_section_layout)
        parent_window.addWidget(self.right_bottom_section_widget)

class my_month:
    """
    Klasa odpowiadająca za dane związane z konkretnym miesiącem
    """
    def __init__(self, year:int, month_number:int, list_of_days:list=[]) -> None:
        """
        Utworzenie miesiąca z podaną już listą dni, lub tworzenie nowej
        """
        self.month_number = month_number
        self.year = year
        if len(list_of_days) == 0:
            self.list_of_days = list(my_day(x, month_number, year) for x in range(
                1, calendar.monthrange(year, month_number)[1]+1))
        else:
            self.list_of_days = list_of_days

class Okienko_na_tekst(QDialog):
    """
    Klasa odpowiedzialna za wyswietlanie okna, w którym wpisywane
    są notatki do danego dnia
    """
    def __init__(self,main_text:str,side_text:str,day:int,parent=None) -> None:
        """
        Utworzenie i wyswietlenie okna
        """
        super().__init__(parent)
        self.main_text=main_text
        self.side_text=side_text
        #Ustawienie nazwy okna
        self.setWindowTitle(f"Informacje o dniu {day}")
        layout = QVBoxLayout()
        #Ustawienie napisów i pól do wpisania notatek oraz dodanie ich do layoutu"
        self.writing1 = QLabel("Ważne informacje o kolosach, egzaminach itd")
        self.main_text = QLineEdit(self,text=self.main_text)
        self.writing2 = QLabel("Mniej ważna notatka do dnia")
        self.side_text = QLineEdit(self,text=self.side_text)
        layout.addWidget(self.writing1)
        layout.addWidget(self.main_text)
        layout.addWidget(self.writing2)
        layout.addWidget(self.side_text)
        #Dodanie przycisków do zatwierdzenia wpisanych informacji
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.setLayout(layout)
        
    def give_notes(self) -> tuple:
        """
        Metoda, która zwraca wpisane notatki
        """
        return self.main_text.text(), self.side_text.text()

class my_day:
    """
    Klasa odpowiedzialna za przechowywanie danych związanych z danym dniem
    oraz metody potrzebne do obsługi przycisków
    """
    button_command_parametr=False
    def __init__(self, day, month, year, text="",side_note="" ,is_university:bool=False) -> None:
        """
        Utworzenie dnia z podanymi potrzebnymi danymi
        """
        self.day = day
        self.month = month
        self.year = year
        self.day_of_week = calendar.weekday(year, month, day)
        self.is_university = is_university
        self.side_note=side_note
        self.text=text

    def change_the_is_university_attribute(self) -> None:
        """
        Zmieniamy wartośc zmiennej odpowiedzialnej za przechowywanie
        informacji o tym, czy w dany dzień jest uczelnia
        """
        if self.is_university == True:
            self.is_university = False
        else:
            self.is_university = True

    def button_command(self) -> None:
        """
        Metoda odpowiedzialna za to, co się dzieje po kliknięciu przycisku dnia
        """
        if my_day.button_command_parametr==True:
            self.change_the_is_university_attribute()
        else:
            self.open_the_window_with_notes()
        self.refresh_button_colour()
        
    def open_the_window_with_notes(self) -> None:
        """
        Metoda odpowiedzialna za otwarcie okna z notatkami
        """
        window_for_text = Okienko_na_tekst(self.text,self.side_note,self.day,main_window)
        if window_for_text.exec_() == QDialog.Accepted:
            self.text, self.side_note = window_for_text.give_notes()
            
    def insert_button(self,row:int,column:int,table) -> None:
        """
        Metoda odpowiedzialna za utworzenie przycisku w podanym miejscu w tabeli
        """
        self.button = QPushButton(f"{self.day}")
        table.setCellWidget(row, column, self.button)
        self.button.clicked.connect(self.button_command)
        self.refresh_button_colour()
        
    def refresh_button_colour(self) -> None:
        """
        metoda odpowiedzialna za odświeżenie koloru przycisku dnia,
        w zależności od związanych z nim danych
        """
        #Jeśli jest główna notatka, ustawiamy na niebieski
        if self.text!="":
            self.button.setStyleSheet("background-color: blue")
        #Jeśli nie ma głównej notatki, ale jest notatka poboczna ustawiamy na zielony"
        elif self.side_note!="":
            self.button.setStyleSheet("background-color: limegreen")
        #Jeśli nie ma notatek, ale w dany dzien jest uczelnia, to ustawiamy na jasny niebieski
        elif self.is_university==True:
            self.button.setStyleSheet("background-color: lightblue")
        #Jesli nic z powyższych, to ustawiamy na biały
        else:
            self.button.setStyleSheet("background-color: white")


class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = FigureCanvas(Figure())
        self.axis = self.canvas.figure.add_subplot(111)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

#tu sie zmienia wykres
    def plot(self, data):
        lista=[]
        procenty=[]
        with open('sumowane_punkty.txt', 'r') as file:
            data = json.load(file)
            print(data)
        for items, values in data.items():
            print(values)
            for items1, values2 in values.items():
                procenty.append(values2)
                print(procenty)
                lista.append(items1)
                print(lista)
        self.axis.clear()
        self.axis.bar(lista,procenty)
        self.axis.set_xticks(lista,lista)
        self.canvas.draw()


class ListItemWidget(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.initUI()
    
    def initUI(self):
        layout = QHBoxLayout()
        
        self.label = QLabel(self.name)
        self.textBox = QLineEdit()
        self.saveButton = QPushButton("Zapisz")
        self.saveButton.clicked.connect(self.saveText)
        
        layout.addWidget(self.label)
        layout.addWidget(self.textBox)
        layout.addWidget(self.saveButton)
        
        self.setLayout(layout)
    
    def saveText(self):
        text = self.textBox.text()
        try:
            with open("progi.txt", 'a') as file:
                file.write(f"{self.name}: {text}\n")
        except Exception as e:
            print(f"Error saving text to file: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # odwołujemy się do rodzica - QMainWindow

        top_section_layout = QVBoxLayout()
         # Dodanie wykresu do sekcji górnej
        self.plot_widget = PlotWidget()
        top_section_layout.addWidget(self.plot_widget)
        self.plot_widget.plot([0, 1, 0, 3, 7,2,6])

        self.setWindowTitle("Aplikacja 3.0")
        # ustawienie rozmiaru wyświetlanego okna aplikacji
        self.setGeometry(100, 100, 1200, 600)
        self.sublist_data = {}
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)



# Dodanie dużej sekcji do głównego layoutu
        main_layout.addLayout(top_section_layout)
# Sekcja lewa dolna - zadanie Marty i Mateusza - zliczanie punktów i przedmioty
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
        #przycisk do dodawania przedmiotów
        self.input_line = QLineEdit()
        self.add_button = QPushButton("Dodaj przedmiot")
        self.add_button.clicked.connect(self.add_item_to_list)
        self.delete_button = QPushButton("Usuń zaznaczony przedmiot")
        self.delete_button.clicked.connect(self.usuwanie_rzeczy_z_list)

        #przycisk do dodawania progów punktowych dla przedmiotów
        self.input_line = QLineEdit()
        self.dodaj_progi_button = QPushButton("Dodaj progi")
        self.dodaj_progi_button.clicked.connect(self.dodaj_progi_punktowe)
        

        self.left_bottom_section_layout.addWidget(self.input_line)
        self.left_bottom_section_layout.addWidget(self.add_button)
        self.left_bottom_section_layout.addWidget(self.dodaj_progi_button)
        self.left_bottom_section_layout.addWidget(self.delete_button)

        self.left_bottom_section_splitter.addWidget(left_bottom_section_widget)

# Prawa dolna sekcja
        right_bottom_section_widget = QWidget()

# Dodanie małych sekcji do głównego layoutu
        bottom_section_layout.addWidget(self.left_bottom_section_splitter)
        calendar1=my_calendar()
        calendar1.initialize_calendar(bottom_section_layout)
        calendar1.display_actual_month()
        bottom_section_layout.addWidget(right_bottom_section_widget)
        main_layout.addLayout(bottom_section_layout)

# dodanie danych
        self.list_widget.itemClicked.connect(lambda item: self.open_sublist(
            item, self.left_bottom_section_splitter, self.sublist_data, 1))

# Ładujemy liste itemsów z plików
        self.load_items_from_file()
        self.load_sublists_from_file()

    def add_item_to_list(self):
        text = self.input_line.text()
        if text:
            self.list_widget.addItem(text)
            self.input_line.clear()
            self.save_items_to_file()
    def usuwanie_rzeczy_z_list(self):
        wybierz_rzecz = self.list_widget.currentItem()
        #wybieram rzecz, przedmiot/ punkty
        if wybierz_rzecz:
            #pobieram teraz ta nazwe 
            tekst = wybierz_rzecz.text()
            self.list_widget.takeItem(self.list_widget.row(wybierz_rzecz))
            #teraz row dale mi indeks numer wiersza w naszym widgetcie rzeczy 
            #którą chcemy usunąć, a takeItem(ideks) usuwa tą rzecz z widegtu,
            #ale nie z pamięci, więc
            if tekst in self.sublist_data:
                del self.sublist_data[tekst]
            #usuwamy cały element o kluczu tekst ze słownika
            self.save_sublist_to_file()
            self.save_items_to_file()
            self.usun_zapis_sumy(tekst)

    def usun_zapis_sumy(self, tekst):
            with open("sumowane_punkty.txt", "w", encoding='utf-8') as file:
                file.write('{}')
            #otwieram plik 
            with open("sumowane_punkty.txt", "r") as file:
                linijki = file.readlines()
            #otwieram plik, by ponownie zapisac i usunac to czego nie chce
            with open("sumowane_punkty.txt", "w") as file:
                for x in linijki:
                # sprawdzam, czy linia zawiera tekst do usuniecia i usuwam linie
                        if tekst not in x:
                            file.write(str(x))

    
    
    
    
    def dodaj_progi_punktowe(self):
        self.okno_do_progów = self.Okno_do_progów('items.txt')
        self.okno_do_progów.show()
    
    
    

    class Okno_do_progów(QWidget):
        def __init__(self,filename):
            super().__init__()
            self.filename = filename
            self.initUI()
            
        def initUI(self):
            self.setWindowTitle("Wpisz progi punktowe")
            self.setGeometry(100, 100, 450, 400)
            
            layout = QVBoxLayout()
            self.listWidget = QListWidget(self)
            
            self.loadNames()
            
            layout.addWidget(self.listWidget)
            self.setLayout(layout)

        def loadNames(self):
            try:
                with open(self.filename, 'r') as file:
                    names = file.readlines()
                    for name in names:
                        name = name.strip()
                        if name:
                            item = QListWidgetItem(self.listWidget)
                            item_widget = ListItemWidget(name)
                            item.setSizeHint(item_widget.sizeHint())
                            self.listWidget.addItem(item)
                            self.listWidget.setItemWidget(item, item_widget)
            except Exception as e:
                print(f"Error loading names from file: {e}")

    

    
    
        
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

# Ładujemy elementy dla podlisty
        if item.text() in current_data:
            for sub_item_text in current_data[item.text()]["items"]:
                sublist.addItem(sub_item_text)
# Tworzymy przycisk do sumowania
        if level == 2:
            suma_przycisk = QPushButton("Sumuj swoje punkty!")
            suma_przycisk.clicked.connect(
                lambda: self.suma(item.text()))
            sublist_layout.addWidget(suma_przycisk)

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

        serialized_data = serialize_sublists(self.sublist_data)
        with open("sublists.txt", "w") as file:
            file.write(str(serialized_data))

    def load_sublists_from_file(self):
        def deserialize_sublists(data):
            return {key: {"items": value["items"], "sublists": deserialize_sublists(value["sublists"])} for key, value in data.items()}

        try:
            if os.path.getsize("sublists.txt") > 0:
                with open("sublists.txt", "r") as file:
                    serialized_data = file.read()
                    self.sublist_data = deserialize_sublists(
                        ast.literal_eval(serialized_data))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error loading sublists: {e}")
# Kod by zliczało sumę punktów

    def suma(self, parent_item_text):
        try:
            punkty_otrzymane = {}  # słownik przechowujący sume pkt.

            # Przechodzimy po pliku
            for przedmioty, wartości in self.sublist_data.items():
                # Przypisujemy 0, do którego będziem dodawać rzeczy
                punkty_otrzymane[przedmioty] = 0

                # Sprawdzam czy nasz przedmiot ma podlisty: kolosy etc.
                if "sublists" in wartości:
                    # Iterujemy po podlistach i sumujemy punkty
                    for przedmiot, punkty in wartości["sublists"].items():
                        for punkt in punkty["items"]:
                            punkty_otrzymane[przedmioty] += float(punkt)
             # Tworze okienko, które bedzie sie wyświetlało
            QMessageBox.information(
                self, "Sumuj swoje punkty!", f"Twoje punkty: {punkty_otrzymane}")
            self.zapis_sumy(parent_item_text, punkty_otrzymane)
        except ValueError:
            QMessageBox.warning(
                self, "Błąd", "Zostały wprowadzone niepoprawne dane, upwenij się, że są to liczby")
# robię teraz aby suma się zapisywała w pliku txt

    def zapis_sumy(self, parent_item_text, punkty_otrzymane):
        try:
            #tworze plik i pusty słowniczek
            with open("sumowane_punkty.txt", "w", encoding='utf-8') as file:
                file.write('{}')
            # otwieram plik i czytam linijka po linijce 
            with open("sumowane_punkty.txt", "r", encoding='utf-8') as file:
                linijka = file.read()

            #przerabiam na slownik za pmoca json (ułatwienie dla Olgi i Bartka)
            if linijka.strip():
                słownik = json.loads(linijka)

            #dodaje wpisy do słownika
            słownik[parent_item_text] = punkty_otrzymane

            #zapisuje słownik do pliku w formacie json - z jego wymaganiami (dwa cudzyslowy ")
            with open("sumowane_punkty.txt", "w", encoding='utf-8') as file:
                json.dump(słownik, file, ensure_ascii=False)
        except Exception as e:
            print(f"Błąd przy zapisywaniu sumy, niepoprawne wartości: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
