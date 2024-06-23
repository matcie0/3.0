import os
import ast
import sys
import json
import unittest
import calendar
from PyQt5.QtCore import Qt
from datetime import datetime
from matplotlib.figure import Figure
import matplotlib.patheffects as path_effects
from dateutil.relativedelta import relativedelta
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget,
    QTableWidgetItem, QListWidget, QPushButton, QLineEdit, QLabel, QSplitter,
    QMessageBox, QListWidgetItem, QDialog, QDialogButtonBox
)

class MyCalendar:
    """
    Klasa obsługująca cały kalendarz: wczytywanie, zapisywanie,
    wyświetlanie oraz wszystkie potrzebne funkcje.
    """

    def __init__(self) -> None:
        """
        Utworzenie kalendarza, na razie bez jego wyświetlenia.
        Wczytanie danych z pliku i utworzenie z nich potrzebnych zmiennych.
        """
        try:
            # Wczytanie danych z pliku jako krotki
            with open('kalendarz.txt', 'r') as file:
                lines = file.readlines()
                tuple_list = [tuple(line.strip().split('\t')) for line in lines]

            self.months = [] 
            months_list = []

            # Stworzenie listy miesięcy, zawierającą listy z danymi
            # zwiazanymi z dniamiw poszczególnych miesięcach
            for x in range(1, 13):
                months_list.append(
                    [tuple for tuple in tuple_list if tuple[1] == str(x)]
                )

            # Posortowanie miesięcy
            months_list = sorted(
                months_list, key=lambda x: (int(x[0][2]), int(x[0][1]))
            )

            # Stworzenie listy zawierającej miesiące zapisane jako klasa my_month,
            # w której znajdują się dni zapisane jako klasa my_day
            for list_of_days_in_month in months_list:
                days_list = []
                for day in list_of_days_in_month:
                    days_list.append(MyDay(int(day[0]), int(day[1]), int(day[2]),
                                           day[3], day[4], eval(day[5])))
                self.months.append(
                    MyMonth(int(list_of_days_in_month[0][2]),
                            int(list_of_days_in_month[0][1]), days_list)
                )
        except FileNotFoundError:
            self.reset_calendar(True)

    def set_actual_month_to_now(self) -> None:
        """
        Ustawienie numeru wyświetlanego miesiąca (w postaci numeru z listy)
        na miesiąc zgodny z aktualną datą.
        """
        actual_month = datetime.now().month
        for position_in_list in range(12):
            if self.months[position_in_list].month_number == actual_month:
                self.displayed_month = position_in_list

    def change_displayed_month_by_x(self, x: int) -> None:
        """
        Przesuwa numer wyświetlanego miesiąca o x i go wyświetla.
        """
        if self.displayed_month + x in list(range(12)):
            self.displayed_month += x
            self.display_actual_month()
            
    def reset_calendar(self, is_in_init: bool = False) -> None:
        """
        Zrestartowanie kalendarza, czyli usunięcie wszystkich aktualnych
        danych oraz zastąpienie ich danymi zgodnymi z aktualną datą.
        """
        # Wyczyszczenie listy miesięcy
        self.months = []
        actual_date = datetime.now()

        # Dodanie pięciu miesięcy przed aktualną datą
        for i in range(5, 0, -1):
            previous_date = actual_date - relativedelta(months=i)
            self.months.append(
                MyMonth(previous_date.year, previous_date.month)
            )

        # Dodanie aktualnego miesiąca
        self.months.append(
            MyMonth(actual_date.year, actual_date.month)
        )

        # Dodanie 6 następnych miesięcy
        for i in range(1, 7):
            comming_date = actual_date + relativedelta(months=i)
            self.months.append(
                MyMonth(comming_date.year, comming_date.month)
            )

        # Ustawienie aktualnie wyświetlanego miesiąca na teraz
        self.set_actual_month_to_now()
        # Jeśli funkcja nie jest wywołana w __Init__ to wyświetla aktualny miesiąc
        if is_in_init == False:
            self.display_actual_month()
        
    def save_calendar(self) -> None:
        """
        Zapisanie wprowadzonych od rozpoczęcia programu danych do pliku.
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
        zmienną odpowiedzialną za aktualnie wyświetlany miesiąc.
        """
        # Czyszczenie kalendarza z przycisków
        for column in range(1,8):
            for row in range(6):
                self.main_table.removeCellWidget(row, column)

        month = self.months[self.displayed_month]

        # Ustawienie kolumny w zależności jakim dniem tygodnia jest pierwszy dzień miesiąca 
        actual_column_to_set = month.list_of_days[0].day_of_week + 1

        # Ustawienie miesiąca, czyli wiersza na pierwszy
        actual_week = 0

        # Przechodzenie po tabeli kolei po dniach i dodawanie przycisków
        for day in range(len(month.list_of_days)):
            if actual_column_to_set == 8:
                actual_column_to_set = 1
                actual_week += 1
            month.list_of_days[day].insert_button(actual_week,actual_column_to_set,self.main_table)
            actual_column_to_set += 1

        # Zapisanie aktualnej daty w prawym górnym rogu
        self.display_actual_date()

    def set_everything_on_university(self) -> None:
        """
        Ustawia wszystkie dni aktualnie wyświetlanego miesiąca
        (nie licząc weekendów) na uczelniane.
        """
        for day in self.months[self.displayed_month].list_of_days:
            if day.day_of_week in [0,1,2,3,4]:
                day.is_university = True
                day.refresh_button_colour()

    def display_actual_date(self) -> None:
        """
        Ustawia w prawym górnym rogu datę
        zgodną z aktualnie wyświetlanym miesiącem.
        """
        to_display = str(self.months[self.displayed_month].month_number)+'.'+str(self.months[self.displayed_month].year)
        self.main_table.setItem(0, 9, QTableWidgetItem(to_display))

    def change_parametr_to_setting_days_to_university(self) -> None:
        """
        Zmienia wartość zmiennej odpowiedzialnej za to, czy po kliknięciu
        w dzień uruchomi się okno tekstowe, czy zmieni się wartość 
        zmiennej czy_uczelniany dla danego dnia.
        """
        if MyDay.button_command_parametr == True:
            MyDay.button_command_parametr = False
            self.button_to_change_days_to_univeristy.setStyleSheet("background-color: white;")
        else:
            MyDay.button_command_parametr = True
            self.button_to_change_days_to_univeristy.setStyleSheet("background-color: blue;")

    def initialize_calendar(self, parent_window) -> None:
        """
        Wyświetla kalendarz oraz wszystkie potrzebne przyciski.
        """
        # Utworzenie layoutu
        self.right_bottom_section_layout = QVBoxLayout()

        # Utworzenie tabeli
        self.main_table = QTableWidget(6, 10)

        # Ustawienie szerokości kolumn
        for column in range(9):
            self.main_table.setColumnWidth(column, 60)
        self.main_table.setColumnWidth(9, 160)
        self.main_table.setColumnWidth(8, 100)
        self.main_table.setColumnWidth(0, 100)

        # Ustawienie wysokości kolumn
        for row in range(6):
            self.main_table.setRowHeight(row, 60)

        # Utworzenie i dodatnie przycisków przesuwających miesiące
        button_previois = QPushButton("Poprzedni")
        button_next = QPushButton("Nastepny")
        self.main_table.setCellWidget(2, 0, button_previois)
        self.main_table.setCellWidget(2, 8, button_next)
        button_previois.clicked.connect(lambda: self.change_displayed_month_by_x(-1))
        button_next.clicked.connect(lambda: self.change_displayed_month_by_x(1))

        # Dodanie przycisku do zmiany dni na uniwersyteckie
        self.button_to_change_days_to_univeristy = QPushButton("Zacznij ustawiać \n dni uczelniane")
        self.main_table.setCellWidget(1, 9, self.button_to_change_days_to_univeristy)
        self.button_to_change_days_to_univeristy.clicked.connect(self.change_parametr_to_setting_days_to_university)

        # Dodanie przycisku do ustawienia wszystkich dni na uczelniane
        button_set_everything_university = QPushButton("Ustaw wszystko\n na uczelniane")
        self.main_table.setCellWidget(2, 9, button_set_everything_university)
        button_set_everything_university.clicked.connect(self.set_everything_on_university)

        # Dodane przycisku do resetu danych kalendarza
        button_reset = QPushButton("Resetuj")
        self.main_table.setCellWidget(4, 9, button_reset)
        button_reset.clicked.connect(self.reset_calendar)

        # Dodanie przycisku do zapisywania danych
        button_save = QPushButton("Zapisz zmiany")
        self.main_table.setCellWidget(3, 9, button_save)
        button_save.clicked.connect(self.save_calendar)

        # Ustawienie i wyświetlenie aktualnego miesiąca
        self.set_actual_month_to_now()
        self.display_actual_date()

        # Dodanie nazw kolumn
        self.main_table.setHorizontalHeaderLabels(["","Pn", "Wt", "Śr", "Czw", "Pt", "So", "Nd","",""])

        # Dodanie sekcji do głównego okna
        self.right_bottom_section_layout.addWidget(self.main_table)
        self.right_bottom_section_widget = QWidget()
        self.right_bottom_section_widget.setLayout(self.right_bottom_section_layout)
        parent_window.addWidget(self.right_bottom_section_widget)


class MyMonth:
    """
    Klasa odpowiadająca za dane związane z konkretnym miesiącem.
    """
    def __init__(self, year:int, month_number:int, list_of_days:list=[]) -> None:
        """
        Utworzenie miesiąca z podaną już listą dni, lub tworzenie nowej.
        """
        self.month_number = month_number
        self.year = year
        if len(list_of_days) == 0:
            self.list_of_days = list(MyDay(x, month_number, year) for x in range(
                1, calendar.monthrange(year, month_number)[1]+1))
        else:
            self.list_of_days = list_of_days


class TextWindow(QDialog):
    """
    Klasa odpowiedzialna za wyświetlanie okna, w którym wpisywane
    są notatki do danego dnia.
    """
    def __init__(self,main_text:str,side_text:str,day:int,parent=None) -> None:
        """
        Utworzenie i wyświetlenie okna.
        """
        super().__init__(parent)
        self.main_text = main_text
        self.side_text = side_text

        # Ustawienie nazwy okna
        self.setWindowTitle(f"Informacje o dniu {day}")
        layout = QVBoxLayout()

        # Ustawienie napisów i pól do wpisania notatek oraz dodanie ich do layoutu
        self.writing1 = QLabel("Ważne informacje o kolosach, egzaminach itd")
        self.main_text = QLineEdit(self,text=self.main_text)
        self.writing2 = QLabel("Mniej ważna notatka do dnia")
        self.side_text = QLineEdit(self,text=self.side_text)
        layout.addWidget(self.writing1)
        layout.addWidget(self.main_text)
        layout.addWidget(self.writing2)
        layout.addWidget(self.side_text)

        # Dodanie przycisków do zatwierdzenia wpisanych informacji
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.setLayout(layout)
        
    def give_notes(self) -> tuple:
        """
        Metoda, która zwraca wpisane notatki.
        """
        return self.main_text.text(), self.side_text.text()


class MyDay:
    """
    Klasa odpowiedzialna za przechowywanie danych związanych z danym dniem
    oraz metody potrzebne do obsługi przycisków.
    """
    button_command_parametr = False

    def __init__(self, day, month, year, text="", side_note="" , is_university: bool = False) -> None:
        """
        Utworzenie dnia z podanymi potrzebnymi danymi.
        """
        self.day = day
        self.month = month
        self.year = year
        self.day_of_week = calendar.weekday(year, month, day)
        self.is_university = is_university
        self.side_note = side_note
        self.text = text

    def change_the_is_university_attribute(self) -> None:
        """
        Zmieniamy wartość zmiennej odpowiedzialnej za przechowywanie
        informacji o tym, czy w dany dzień jest uczelnia.
        """
        if self.is_university == True:
            self.is_university = False
        else:
            self.is_university = True

    def button_command(self) -> None:
        """
        Metoda odpowiedzialna za to, co się dzieje po kliknięciu przycisku dnia.
        """
        if MyDay.button_command_parametr == True:
            self.change_the_is_university_attribute()
        else:
            self.open_the_window_with_notes()
        self.refresh_button_colour()
        
    def open_the_window_with_notes(self) -> None:
        """
        Metoda odpowiedzialna za otwarcie okna z notatkami.
        """
        window_for_text = TextWindow(self.text,self.side_note,self.day,main_window)
        if window_for_text.exec_() == QDialog.Accepted:
            self.text, self.side_note = window_for_text.give_notes()
            
    def insert_button(self,row:int,column:int,table) -> None:
        """
        Metoda odpowiedzialna za utworzenie przycisku w podanym miejscu w tabeli.
        """
        self.button = QPushButton(f"{self.day}")
        table.setCellWidget(row, column, self.button)
        self.button.clicked.connect(self.button_command)
        self.refresh_button_colour()
        
    def refresh_button_colour(self) -> None:
        """
        Metoda odpowiedzialna za odświeżenie koloru przycisku dnia,
        w zależności od związanych z nim danych.
        """
        # Jeśli jest główna notatka, ustawiamy na niebieski
        if self.text!="":
            self.button.setStyleSheet("background-color: blue")
        # Jeśli nie ma głównej notatki, ale jest notatka poboczna ustawiamy na zielony"
        elif self.side_note!="":
            self.button.setStyleSheet("background-color: limegreen")
        # Jeśli nie ma notatek, ale w dany dzień jest uczelnia, to ustawiamy na jasny niebieski
        elif self.is_university==True:
            self.button.setStyleSheet("background-color: lightblue")
        # Jeśli nic z powyższych, to ustawiamy na biały
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

    # Tu zmienia się wykres
    def plot(self, data):
        if os.stat("sumowane_punkty.txt").st_size == 0:
            with open("sumowane_punkty.txt", "w", encoding='utf-8') as file:
                file.write('{}')
        list = []
        percent = []
        if os.stat("procenty.txt").st_size == 0:
            with open("procenty.txt", "w", encoding='utf-8') as file:
                file.write('{}')
        with open('procenty.txt', 'r') as file:
            data = json.load(file)
        
            for items1, values2 in data.items():
                percent.append(values2)
                list.append(items1)
        self.axis.clear()
        bars = self.axis.bar(list,percent, color='mediumslateblue')
        self.axis.set_xticks(list,list)
        self.axis.set_ylim(0,100)
        
        for bar in bars:
            text = self.axis.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                round(bar.get_height(), 1),
                fontsize=15,
                horizontalalignment='center',
                color='lime',
                )

            text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='gray'),
                path_effects.Normal()])    
            
        self.canvas.draw()


# Zapisywanie progów do pliku
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
        self.saveButton.clicked.connect(self.save_text)
        
        layout.addWidget(self.label)
        layout.addWidget(self.textBox)
        layout.addWidget(self.saveButton)
        
        self.setLayout(layout)
    
    def save_text(self):
        text = self.textBox.text()
        try:
            # Próbuj wczytać istniejące dane z pliku
            try:
                with open("progi.txt", 'r') as file:
                    data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                # Jeśli plik nie istnieje lub jest pusty, rozpocznij od pustego słownika
                data = {}

            # Dodaj nowy wpis do słownika
            data[self.name] = float(text)

            # Zapisz zaktualizowany słownik z powrotem do pliku
            with open("progi.txt", 'w') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            
        except Exception as e:
            print(f"Error saving text to file: {e}")
 
 
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Odwołujemy się do rodzica - QMainWindow
        top_section_layout = QVBoxLayout()

        # Dodanie wykresu do sekcji górnej
        self.plot_widget = PlotWidget()
        top_section_layout.addWidget(self.plot_widget)
        self.plot_widget.plot([0, 1, 0, 3, 7, 2, 6])

        self.setWindowTitle("Aplikacja 3.0")

        # Ustawienie rozmiaru wyświetlanego okna aplikacji
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
        self.left_bottom_section_layout = QVBoxLayout(left_bottom_section_widget)

        self.list_widget = QListWidget()
        self.left_bottom_section_layout.addWidget(QLabel("Twoje przedmioty:"))
        self.left_bottom_section_layout.addWidget(self.list_widget)

        # Przycisk do dodawania przedmiotów
        self.input_line = QLineEdit()
        self.add_button = QPushButton("Dodaj przedmiot")
        self.add_button.clicked.connect(self.add_item_to_list)
        self.delete_button = QPushButton("Usuń zaznaczony przedmiot")
        self.delete_button.clicked.connect(self.remove_item_from_list)

        # Przycisk do dodawania progów punktowych dla przedmiotów
        self.input_line = QLineEdit()
        self.dodaj_progi_button = QPushButton("Dodaj progi")
        self.dodaj_progi_button.clicked.connect(self.add_score_thresholds)
        
        self.left_bottom_section_layout.addWidget(self.input_line)
        self.left_bottom_section_layout.addWidget(self.add_button)
        self.left_bottom_section_layout.addWidget(self.dodaj_progi_button)
        self.left_bottom_section_layout.addWidget(self.delete_button)

        self.left_bottom_section_splitter.addWidget(left_bottom_section_widget)

        # Prawa dolna sekcja
        right_bottom_section_widget = QWidget()

        # Dodanie małych sekcji do głównego layoutu
        bottom_section_layout.addWidget(self.left_bottom_section_splitter)
        calendar1 = MyCalendar()
        calendar1.initialize_calendar(bottom_section_layout)
        calendar1.display_actual_month()
        bottom_section_layout.addWidget(right_bottom_section_widget)
        main_layout.addLayout(bottom_section_layout)

        # Dodanie danych
        self.list_widget.itemClicked.connect(lambda item: self.open_sublist(
            item, self.left_bottom_section_splitter, self.sublist_data, 1))

        # Ładujemy listę itemsów z plików
        self.load_items_from_file()
        self.load_sublists_from_file()

    def add_item_to_list(self):
        text = self.input_line.text()
        if text:
            self.list_widget.addItem(text)
            self.input_line.clear()
            self.save_items_to_file()

    def remove_item_from_list(self):
        select_item = self.list_widget.currentItem()
        # Wybieram rzecz, przedmiot/ punkty
        if select_item:
            # Pobieram teraz tą nazwę 
            text = select_item.text()
            self.list_widget.takeItem(self.list_widget.row(select_item))
            # Teraz row daje mi indeks numer wiersza w naszym widgetcie rzeczy 
            # którą chcemy usunąć, a takeItem(ideks) usuwa tą rzecz z widegtu,
            # ale nie z pamięci, więc
            if text in self.sublist_data:
                del self.sublist_data[text]
            # Usuwamy cały element o kluczu tekst ze słownika
            self.save_sublist_to_file()
            self.save_items_to_file()
            self.remove_sum_record(text)

    def remove_sum_record(self, text):
            with open("sumowane_punkty.txt", "w", encoding='utf-8') as file:
                file.write('{}')
            # Otwieram plik 
            with open("sumowane_punkty.txt", "r") as file:
                lines = file.readlines()
            # Otwieram plik, by ponownie zapisać i usunąć to czego nie chce
            with open("sumowane_punkty.txt", "w") as file:
                for x in lines:
                # Sprawdzam, czy linia zawiera tekst do usunięcia i usuwam linię
                        if text not in x:
                            file.write(str(x))
          
    # Funkcje do okna od wpisywania progów
    def add_score_thresholds(self):
        self.threshold_window = self.ThresholdWindow('items.txt')
        self.threshold_window.show()

    class ThresholdWindow(QWidget):
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

    def load_items_from_file(self):
        try:
            with open("items.txt", "r", encoding='utf-8') as file:
                items = file.readlines()
                for item in items:
                    self.list_widget.addItem(item.strip())
        except FileNotFoundError:
            pass

    def load_sublists_from_file(self):
        try:
            with open("sublists.txt", "r", encoding='utf-8') as file:
                self.sublist_data = json.load(file)
        except FileNotFoundError:
            pass

    def save_items_to_file(self):
        items = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        with open("items.txt", "w", encoding='utf-8') as file:
            for item in items:
                file.write(f"{item}\n")

    def save_sublist_to_file(self):
        with open("sublists.txt", "w", encoding='utf-8') as file:
            json.dump(self.sublist_data, file, ensure_ascii=False, indent=4)
    


    
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
            sum_button = QPushButton("Sumuj swoje punkty!")
            sum_button.clicked.connect(
                lambda: self.sum(item.text()))
            sublist_layout.addWidget(sum_button)

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

    # Kod by zliczało sumę punktów i liczyło procenty
    def sum(self, parent_item_text):
        try:
            points_received = {}  # Słownik przechowujący sume pkt.

            # Przechodzimy po pliku
            for items, values in self.sublist_data.items():
                # Przypisujemy 0, do którego będziemy dodawać rzeczy
                points_received[items] = 0

                # Sprawdzam czy nasz przedmiot ma podlisty: kolosy etc.
                if "sublists" in values:
                    # Iterujemy po podlistach i sumujemy punkty
                    for item, points in values["sublists"].items():
                        for punkt in points["items"]:
                            points_received[items] += float(punkt)

            # Tworzę okienko, które będzie się wyświetlało
            QMessageBox.information(
                self, "Sumuj swoje punkty!", f"Twoje punkty: {points_received}")
            self.record_sum(parent_item_text, points_received)
        except ValueError:
            QMessageBox.warning(
                self, "Błąd", "Zostały wprowadzone niepoprawne dane, upewnij się, że są to liczby")
        # Robię teraz aby suma się zapisywała w pliku txt
        # Wyliczanie procentów dla każdego przedmiotu
        try:
            # Wczytaj dane z pliku progi.txt
            with open("progi.txt", 'r') as file:
                progi = json.load(file)
            
            # Wczytaj dane z pliku sumowane_punkty.txt
            with open("sumowane_punkty.txt", 'r') as file:
                sum_points = json.load(file)

            # Utwórz nowy słownik na przechowywanie wyników
            percent = {}

            # Oblicz
            for key in sum_points:
                if key in progi:
                    try:
                        percent[key] = (sum_points[key] / progi[key]) * 100
                    except ZeroDivisionError:
                        percent[key] = None  # lub inna wartość oznaczająca błąd podziału przez zero
                else:
                    percent[key] = None  # lub inna wartość oznaczająca brakujące dane w progu

            # Zapisz wyniki do pliku procenty.txt
            with open("procenty.txt", 'w') as file:
                json.dump(percent, file, ensure_ascii=False, indent=4)

            print(f"Successfully wrote to file: {percent}")

        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except Exception as e:
            print(f"Error: {e}")

        self.plot_widget.plot([0, 1, 0, 3, 7, 2, 6])
        self.plot_widget.repaint()
        self.plot_widget.update()
              
    def record_sum(self, parent_item_text, punkty_otrzymane):
        try:
            # Tworzę plik i pusty słownik
            with open("sumowane_punkty.txt", "w", encoding='utf-8') as file:
                file.write('{}')

            # Otwieram plik i czytam linijka po linijce 
            with open("sumowane_punkty.txt", "r", encoding='utf-8') as file:
                line = file.read()

            # Przerabiam na słownik za pomocą json (ułatwienie dla Olgi i Bartka)
            if line.strip():
                dictionary = json.loads(line)

            # Zapisuje słownik do pliku w formacie json - z jego wymaganiami (dwa cudzysłowy ")
            with open("sumowane_punkty.txt", "w", encoding='utf-8') as file:
                json.dump(punkty_otrzymane, file, ensure_ascii=False)
        except Exception as e:
            print(f"Błąd przy zapisywaniu sumy, niepoprawne wartości: {e}")


class Tests(unittest.TestCase):

    def test_1(self):
        """
        Test sprawdza, czy bez podanej liczby dni, jedynie z rokiem i miesiącem, dane zostaną 
        poprawnie ustawione.
        """
        year = 2024
        month_number = 6
        month1 = MyMonth(year, month_number)

        self.assertEqual(month1.year, year)
        self.assertEqual(month1.month_number, month_number)
        self.assertEqual(len(month1.list_of_days), calendar.monthrange(year, month_number)[1])
        self.assertTrue(all(isinstance(day, MyDay) for day in month1.list_of_days))

    def test_2(self):
        """
        Test sprawdza, czy klasa zadziała dobrze dla szczególnego przypadku podania konkretnych dni.
        """
        year = 2024
        month_number = 6
        days = [MyDay(1, month_number, year), MyDay(2, month_number, year)]
        month_ex = MyMonth(year, month_number, days)

        self.assertEqual(month_ex.year, year)
        self.assertEqual(month_ex.month_number, month_number)
        self.assertEqual(len(month_ex.list_of_days), 2)
        self.assertEqual(month_ex.list_of_days, days)

    def test_3(self):
        """
        Test sprawdza, czy klasa poprawnie ustawi datę bez podania dni.
        """
        year = 2024
        month_number = 12
        month1 = MyMonth(year, month_number)
        self.assertEqual(month1.year, year)
        self.assertEqual(month1.month_number, month_number)

    def test_4(self):
        """
        Test sprawdza, czy klasa MyDay odpowiednio ustawia dzień tygodnia.
        """
        # Wybieramy dzień, miesiąc oraz rok, dla którego będziemy testować ustawienie
        day1_test = 1
        month1_test = 6
        year1_test = 2024
        day1 = MyDay(day1_test, month1_test, year1_test)
        day2 = calendar.weekday(year1_test, month1_test, day1_test)
        self.assertEqual(day1.day_of_week, day2)

    def test_5(self):
        """
        Test sprawdza, czy klasa odrzuci niepoprawne dane
        """
        # Sprawdzimy czy dla błędnych danych klasa zwróci błąd
        year = "ABC"
        month_number = 10
        month1 = MyMonth(year, month_number)
        self.assertEqual(month1.year, year)
        self.assertEqual(month1.month_number, month_number)

# Testy testuje się osobno od uruchamiania aplikacji
# unittest.main()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
