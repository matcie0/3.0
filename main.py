import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, 
    QTableWidgetItem, QListWidget, QPushButton, QLineEdit, QLabel, QSplitter
)
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aplikacja z trzema sekcjami")
        self.setGeometry(100, 100, 1200, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Duża sekcja na górze
        top_section_layout = QVBoxLayout()
        top_section_table = QTableWidget(5, 3)  # 5 wierszy, 3 kolumny
        top_section_table.setHorizontalHeaderLabels(["Kolumna 1", "Kolumna 2", "Kolumna 3"])
        top_section_layout.addWidget(top_section_table)

        # Dodanie dużej sekcji do głównego layoutu
        main_layout.addLayout(top_section_layout)

        # Małe sekcje na dole
        bottom_section_layout = QHBoxLayout()

        # Lewa dolna sekcja - lista z możliwością dodawania napisów
        self.left_bottom_section_splitter = QSplitter(Qt.Horizontal)
        self.left_bottom_section_splitter.setChildrenCollapsible(False)

        left_bottom_section_widget = QWidget()
        self.left_bottom_section_layout = QVBoxLayout(left_bottom_section_widget)
        
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
        right_bottom_section_layout = QVBoxLayout()
        right_bottom_table = QTableWidget(5, 3)  # 5 wierszy, 3 kolumny
        right_bottom_table.setHorizontalHeaderLabels(["Kolumna 1", "Kolumna 2", "Kolumna 3"])
        right_bottom_section_layout.addWidget(right_bottom_table)

        right_bottom_section_widget = QWidget()
        right_bottom_section_widget.setLayout(right_bottom_section_layout)

        # Dodanie małych sekcji do głównego layoutu
        bottom_section_layout.addWidget(self.left_bottom_section_splitter)
        bottom_section_layout.addWidget(right_bottom_section_widget)
        main_layout.addLayout(bottom_section_layout)

        # Przykładowe dane
        self.populate_table(top_section_table)
        self.populate_table(right_bottom_table)

        self.list_widget.itemClicked.connect(lambda item: self.open_sublist(item, self.left_bottom_section_splitter))

    def populate_table(self, table):
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                table.setItem(row, col, QTableWidgetItem(f"Item {row+1},{col+1}"))

    def add_item_to_list(self):
        text = self.input_line.text()
        if text:
            self.list_widget.addItem(text)
            self.input_line.clear()

    def open_sublist(self, item, splitter):
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
        sub_add_button.clicked.connect(lambda: self.add_item_to_sublist(sublist, sub_input_line))

        sublist_layout.addWidget(sub_input_line)
        sublist_layout.addWidget(sub_add_button)

        sublist_splitter.addWidget(sublist_widget)

        splitter.addWidget(sublist_splitter)
        splitter.setSizes([100, 100])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        sublist.itemClicked.connect(lambda sub_item: self.open_sublist(sub_item, sublist_splitter))

    def add_item_to_sublist(self, sublist, sub_input_line):
        text = sub_input_line.text()
        if text:
            sublist.addItem(text)
            sub_input_line.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
