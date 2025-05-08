import sys
import pymysql
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QTableWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDate


class EmployeeApp(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("emp.ui", self)
        self.setWindowIcon(QIcon("computer-worker.png"))

        # Connect to MySQL
        self.conn = pymysql.connect(host="localhost", user="root", password="root", database="employee_db")
        self.cursor = self.conn.cursor()

        # Connect buttons
        self.btnAdd.clicked.connect(self.add_employee)
        self.btnUpdate.clicked.connect(self.update_employee)
        self.btnDelete.clicked.connect(self.delete_employee)
        self.btnSearch.clicked.connect(self.search_employee)
        self.tableWidget.cellClicked.connect(self.table_row_clicked)

        self.selected_id = None
        self.load_table()

    def add_employee(self):
        try:
            data = self.get_form_data()
            if not data:
                return

            query = """INSERT INTO employees (name, email, phone, gender, dob, address)
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(query, data)
            self.conn.commit()

            QMessageBox.information(self, "Success", "Employee added.")
            self.clear_form()
            self.load_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_employee(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Warning", "Please select a row first.")
            return

        try:
            data = self.get_form_data()
            if not data:
                return

            query = """UPDATE employees SET name=%s, email=%s, phone=%s, gender=%s, dob=%s, address=%s
                       WHERE id=%s"""
            self.cursor.execute(query, data + (self.selected_id,))
            self.conn.commit()

            QMessageBox.information(self, "Updated", "Employee updated.")
            self.clear_form()
            self.load_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_employee(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Warning", "Select a row to delete.")
            return

        confirm = QMessageBox.question(self, "Confirm", "Delete this employee?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM employees WHERE id=%s", (self.selected_id,))
            self.conn.commit()
            QMessageBox.information(self, "Deleted", "Employee deleted.")
            self.clear_form()
            self.load_table()

    def search_employee(self):
        name = self.txtName.text()
        self.cursor.execute("SELECT * FROM employees WHERE name LIKE %s", ('%' + name + '%',))
        self.show_table_data(self.cursor.fetchall())

    def load_table(self):
        self.cursor.execute("SELECT * FROM employees")
        self.show_table_data(self.cursor.fetchall())

    def show_table_data(self, rows):
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(rows):
            self.tableWidget.insertRow(i)
            for j, val in enumerate(row[1:]):  # skip ID
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

    def table_row_clicked(self, row, _):
        self.txtName.setText(self.tableWidget.item(row, 0).text())
        self.txtEmail.setText(self.tableWidget.item(row, 1).text())
        self.txtMobileno.setText(self.tableWidget.item(row, 2).text())
        self.txtCombobox.setCurrentText(self.tableWidget.item(row, 3).text())
        self.txtDate.setDate(QDate.fromString(self.tableWidget.item(row, 4).text(), "yyyy-MM-dd"))
        self.txtAddress.setPlainText(self.tableWidget.item(row, 5).text())

        # Get ID
        self.cursor.execute("SELECT id FROM employees WHERE name=%s AND email=%s AND phone=%s LIMIT 1",
                            (self.txtName.text(), self.txtEmail.text(), self.txtMobileno.text()))
        result = self.cursor.fetchone()
        self.selected_id = result[0] if result else None

    def get_form_data(self):
        name = self.txtName.text()
        email = self.txtEmail.text()
        phone = self.txtMobileno.text()
        gender = self.txtCombobox.currentText()
        dob = self.txtDate.date().toString("yyyy-MM-dd")
        address = self.txtAddress.toPlainText()

        if not name or gender == "Select Gender":
            QMessageBox.warning(self, "Input Error", "Please fill all fields correctly.")
            return None
        return name, email, phone, gender, dob, address

    def clear_form(self):
        self.txtName.clear()
        self.txtEmail.clear()
        self.txtMobileno.clear()
        self.txtCombobox.setCurrentIndex(0)
        self.txtDate.setDate(QDate.currentDate())
        self.txtAddress.clear()
        self.selected_id = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = EmployeeApp()
    win.setWindowTitle("Employee Manager")
    win.show()
    sys.exit(app.exec())
