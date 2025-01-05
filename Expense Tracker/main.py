from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QDateEdit, QComboBox, QPushButton, QLineEdit, QMessageBox, QInputDialog
from PyQt6.QtSql import QSqlDatabase,QSqlQuery
from PyQt6.QtGui import QIcon
from sys import exit
import os
try:
    class Expenss(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Expense Tracker 3.0")
            self.resize(700,400)
            icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
            self.setWindowIcon(QIcon(icon_path))
            self.setStyleSheet("""
        QPushButton {
                background-color: #4991B6;
                border: none;
                color: white;
                padding: 20px 30px;
                text-align: center;
                border-radius: 20px;
            };
        QTableWidget {
            gridline-color: #dcdcdc;
            font-size: 13px;
        }
""")
            
            self.functions()
            
        def init_ui(self):
            
            self.table = QTableWidget()
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(["ID", "Date", "Catogary", "Amount", "Description"])
            self.table.setSelectionMode(self.table.SelectionMode.ExtendedSelection)
            self.table.horizontalHeader().setSectionResizeMode(self.table.horizontalHeader().ResizeMode.Stretch)
            
            self.date_box = QDateEdit()
            self.date_box.setDate(QDate.currentDate())
            self.add_button = QPushButton("Add Expense")
            self.delete_button = QPushButton("Delete Expense")
            self.category_box = QComboBox()
            self.category_box.addItems(["Food", "Education", "Entertainment", "Shopping", "Rent", "Others"])
            self.amount = QLineEdit()
            self.amount.setPlaceholderText("100")
            self.description = QLineEdit()
            self.description.setPlaceholderText("Went to the cinema")
            self.export_button = QPushButton("Export To CSV")
            
            
            self.add_button.clicked.connect(self.add_expenses)
            self.delete_button.clicked.connect(self.delete_expenses)
            self.export_button.clicked.connect(self.export_to_csv)
            
            self.row1 = QHBoxLayout()
            for i in [QLabel("Date: "),self.date_box, QLabel("Category: "),self.category_box]:
                self.row1.addWidget(i)
                
            self.row2 = QHBoxLayout()
            for i in [QLabel("Amount: "),self.amount, QLabel("Description: "),self.description]:
                self.row2.addWidget(i)
            
            self.row3 = QHBoxLayout()
            for i in [self.add_button, self.delete_button]:
                self.row3.addWidget(i)
            
            
            self.master_layout = QVBoxLayout()
            for i in [self.row1, self.row2, self.row3]:
                self.master_layout.addLayout(i)
            self.master_layout.addWidget(self.table)
            self.master_layout.addWidget(self.export_button)
            self.setLayout(self.master_layout)
            
        def functions(self):
            self.init_ui()
            self.initialize_db()
            self.load_tables()
            self.amount.setFocus()
            self.master_password()
        
        def load_tables(self):
            self.table.setRowCount(0)
            query = QSqlQuery("SELECT * FROM expenses")
            row = 0
            while query.next():
                expense_id = query.value(0)
                date = query.value(1)
                category = query.value(2)
                amount = query.value(3)
                description = query.value(4)
                self.table.insertRow(row)
                
                
                self.table.setItem(row,0,QTableWidgetItem(str(expense_id)))
                self.table.setItem(row,1,QTableWidgetItem(date))
                self.table.setItem(row,2,QTableWidgetItem(category))
                self.table.setItem(row,3,QTableWidgetItem(f"${(str(amount))}"))
                self.table.setItem(row,4,QTableWidgetItem(description))
                row+=1
            
        def add_expenses(self):
            if not self.amount.text().isdigit() or int(self.amount.text()) <= 0:
                QMessageBox.warning(self, "Error", "Amount must be a positive number.")
                self.amount.clear()
                self.amount.setFocus()
                return
            if self.amount.text() and self.amount.text().isdigit() == True:
                date = (self.date_box.date()).toString("MM/dd/yyyy")
                category = self.category_box.currentText()
                amount = self.amount.text()
                description = self.description.text()[:46]
                if len(self.description.text()) >=46:
                    QMessageBox.warning(self, "Error", "Only first 45 letters will be added")
                query = QSqlQuery()
                query.prepare(""" 
                            INSERT INTO expenses 
                            (date, category, amount, description)
                            VALUES(?,?,?,?) 
                            """)
                
                query.addBindValue(date)
                query.addBindValue(category)
                query.addBindValue(amount)
                query.addBindValue(description)
                query.exec()
                
                self.category_box.setCurrentIndex(0)
                self.date_box.setDate(QDate.currentDate())
                for i in [self.amount, self.description]:
                    i.clear()
                    
                self.load_tables()
                
        def delete_expenses(self):
            selected_rows = [i.row() for i in self.table.selectedItems()]
            if not selected_rows:
                QMessageBox.warning(self, "Error", "Select a row or more to delete")
                return
            confirm = QMessageBox.question(self,"Confirm","Delete Selected Expenses?",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                ids = [int(self.table.item(i,0).text()) for i in selected_rows]
                for id in ids:    
                    query = QSqlQuery()
                    query.prepare("""
                                
                                Delete FROM expenses WHERE id = ?
                                
                                """)
                    query.addBindValue(id)
                    query.exec()
                    self.load_tables()
                QMessageBox.information(self, "Success", "Selected Expenses Deleted")
        
        def export_to_csv(self):
            query = QSqlQuery("SELECT * FROM expenses")
            if not query.exec():
                QMessageBox.warning(self, "Error", "Failed to execute query")
                return
            if not query.next():
                QMessageBox.warning(self, "Error", "No expenses to export")
                return
            query.previous()
            file_name, _ = QInputDialog.getText(self, "Enter File Name", "Enter File Name")
            if not file_name:
                return
            file_name = file_name + ".csv" if not file_name.endswith(".csv") else file_name
            with open(file_name, "w") as f:
                f.write("ID,Date,Category,Amount,Description\n")
                while query.next():
                    row = [str(query.value(i)) for i in range(5)]
                    f.write(",".join(row) + "\n")
            QMessageBox.information(self, "Success", "Expenses exported to CSV")
        
        def initialize_db(self):
            data_base = QSqlDatabase.addDatabase("QSQLITE")
            data_base.setDatabaseName("expenses.db")
            if not data_base.open():
                QMessageBox.critical(self,"ERROR","Can't connect to database")
                exit(1)

            query = QSqlQuery()
            sql_command1 = """
                        CREATE TABLE IF NOT EXISTS expenses (
                            id INTEGER PRIMARY KEY AUTOINCREMENT
                            , date TEXT
                            , category TEXT
                            , amount REAL
                            , description TEXT   
                        )
                        """
            sql_command2 = "CREATE TABLE IF NOT EXISTS master_password (password TEXT NOT NULL UNIQUE)"
            query.exec(sql_command1)
            query.exec(sql_command2)
            
        def master_password(self):
            query = QSqlQuery("SELECT * FROM master_password")
            if not query.next():
                password, ok = QInputDialog.getText(self, "Set Master Password", "Enter Master Password")
                if ok and password:
                    query = QSqlQuery()
                    query.prepare("INSERT INTO master_password (password) VALUES(?)")
                    query.addBindValue(password)
                    query.exec()
                    QMessageBox.information(self, "Success", "Master Password Set")
                    return
            else:
                password, ok = QInputDialog.getText(self, "Enter Master Password", "Enter Master Password")
                if ok and password:
                    if password == query.value(0):
                        return
                    else:
                        QMessageBox.critical(self, "Error", "Incorrect Password")
            exit(1)
                        
            
            
    if __name__ == "__main__":
        App = QApplication([])
        main_window = (Expenss())
        main_window.show()
        App.exec()
except Exception as e:
    QMessageBox.information(None, "Error", f"An error occured: {e}")
    exit()