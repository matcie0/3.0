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

        self.sublist_data = {}  # Dictionary to store sublist items

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

        self.list_widget.itemClicked.connect(lambda item: self.open_sublist(item, self.left_bottom_section_splitter, self.sublist_data, 1))

        # Load list items from file
        self.load_items_from_file()
        self.load_sublists_from_file()

    def populate_table(self, table):
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                table.setItem(row, col, QTableWidgetItem(f"Item {row+1},{col+1}"))

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
        sub_add_button.clicked.connect(lambda: self.add_item_to_sublist(sublist, sub_input_line, item.text(), current_data, level))

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
            sublist.itemClicked.connect(lambda sub_item: self.open_sublist(sub_item, sublist_splitter, current_data[item.text()]["sublists"], 2))

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
        items = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
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
