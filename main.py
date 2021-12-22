from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QLabel,  QPlainTextEdit
from PySide6.QtGui import QCloseEvent, QPixmap
import mysql.connector

class LoginWindow(QWidget):
    #initializing window
    def __init__(self):
        self.counter=0
        self.nameOfRecord=""
        super().__init__()
        self.setup()

    #opening connection to database
    #change user, password, host and database to those existing on your computer
    def openConnection(self):
        connection = mysql.connector.connect(user='bartek', password='DB_projects2021', host='127.0.0.1', database='pbd_project',
                                     auth_plugin='mysql_native_password')
        connection.autocommit=True
        return connection

    #definition of all buttons, displays and actions to events
    def setup(self):
        # Picture
        pic_label = QLabel(self)
        pixmap = QPixmap("/home/bartek/Codes/pbd_proj/logo")
        pic_label.setPixmap(pixmap)
        pic_label.move(99, 25)

        # Item database
        self.Item_line = QPlainTextEdit("", self)
        self.Item_line.setFixedSize(410, 460)
        self.Item_line.move(350, 20)
        self.Item_line.setReadOnly(True)

        # Elements' names
        self.add_line_edit = QPlainTextEdit("", self)
        self.add_line_edit.setFixedSize(200, 35)
        self.add_line_edit.move(100, 320)
        self.add_line_edit.textChanged.connect(self.SearchForPossible)

        # Button adding new element to database
        add_btn = QPushButton("Insert", self)
        add_btn.move(110, 360)
        add_btn.clicked.connect(self.InsertData)

        # Button for showing elements contained in database
        show_btn = QPushButton("Show all", self)
        show_btn.move(210, 360)
        show_btn.clicked.connect(self.ShowElements)

        # Button for adding new elements to database
        add_btn = QPushButton("Update", self)
        add_btn.move(110, 390)
        add_btn.clicked.connect(self.UpdateData)

        # Button for deleting records from database
        add_btn = QPushButton("Delete", self)
        add_btn.move(210, 390)
        add_btn.clicked.connect(self.DeleteRecord)

        # Button for closing the application
        quit_btn = QPushButton("Quit", self)
        quit_btn.move(10, 470)
        quit_btn.clicked.connect(QApplication.instance().quit)

        self.resize(800, 500)
        self.setWindowTitle("PBD project")
        self.show()

    #an event to confirm exit
    def closeEvent(self, event: QCloseEvent):
        should_close = QMessageBox.question(self, "Close App", "Do you want to close", QMessageBox.Yes | QMessageBox.No,
                                            QMessageBox.No)

        if should_close == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def SearchForPossible(self):
        if self.counter==0:
            #get text
            item = self.add_line_edit.toPlainText()
            #put query together
            query = "SELECT * FROM electronics WHERE name LIKE %s;"
            itemString = "'%"
            itemString += ''.join(item)
            itemString += "%'"
            #open connection and execute query
            if (itemString != "'%%'"):
                conn = self.openConnection()
                cursor = conn.cursor()
                cursor.execute(query %itemString)
                records = cursor.fetchall()
                cursor.close()
                conn.close()
                if records:
                    self.ShowColumns()
                    for row in records:
                        self.Item_line.insertPlainText(''.join(str(row), ))
                        self.Item_line.insertPlainText("\n")
                else:
                    self.Item_line.clear()
                    self.Item_line.insertPlainText(''.join("There is no such record"))
            else:
                self.Item_line.clear()

    def InsertData(self):
        self.counter=0
        #get data to insert and divide it based on ', '
        item = self.add_line_edit.toPlainText()
        self.add_line_edit.clear()
        parameters = item.split(', ')
        columns = self.GetColumns()
        if len(parameters)<(len(columns)-1):
            item = "'"+"','".join(parameters)+"'"
            for x in range(len(columns)-2):
                item += ", null"
        else:
            item = "'"+"','".join(parameters)+"'"
        #call query to insert data to table
        query = "INSERT INTO electronics(name,parameter) VALUES(%s);" %item
        conn = self.openConnection()
        cursor = conn.cursor()
        cursor.execute(query)
        cursor.close()
        conn.close()
        item += ' added'
        self.Item_line.clear()
        self.Item_line.insertPlainText(''.join(item))

    def UpdateData(self):
        #different actions depending on click counter
        if self.counter==0:
            #if we click for the 1st time
            #check whether record exists, and if so ask user to type needed parameters
            self.nameOfRecord=self.SearchForRecord()
            if self.nameOfRecord!="":
                self.counter+=1
                self.Item_line.insertPlainText("\nType parameters to update as id, name, parameter")
            else:
                self.Item_line.insertPlainText("\nThere is no such record to update")
        else:
            #if we click once again
            if self.nameOfRecord!="":
                #divide given text to different parameters
                item = self.add_line_edit.toPlainText()
                self.add_line_edit.clear()
                parameters = item.split(', ')
                columns = self.GetColumns()
                #if user didn't type enough parameters, fill rest with null
                if len(parameters)<(len(columns)):
                    for x in range(len(columns)-2):
                        parameters.append("null")
                #put query together
                query = "UPDATE electronics SET "
                for i in range(1,len(parameters)):
                    if parameters[i]!="null":
                        query=query+''.join(columns[i])+"='"+''.join(parameters[i])+"'"
                    else:
                        query=query+''.join(columns[i])+"="+''.join(parameters[i])

                    if i!=len(parameters)-1:
                        query+=", "
                    else:
                        query+=" WHERE name='"+self.nameOfRecord+"' AND id="+parameters[0]+";"
                #execute query
                conn=self.openConnection()
                cursor = conn.cursor()
                cursor.execute(query)
                if cursor.rowcount!=0:
                    self.Item_line.insertPlainText("\nRecord updated successfully")
                else:
                    self.Item_line.insertPlainText("\nAn error occured, try again")
                cursor.close()
                conn.close()
                self.counter=0
                self.nameOfRecord=""

    def SearchForRecord(self):
        #find a record in database
        item = self.add_line_edit.toPlainText()
        query = "SELECT name FROM electronics WHERE name=('%s');" %(''.join(item))
        conn = self.openConnection()
        cursor = conn.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        #return it's name or empty String if no such thing exists
        if records:
            return ''.join(item)
        else:
            return ""

    #display all elements located in table
    def ShowElements(self):
        self.counter=0
        self.ShowColumns()
        query = 'SELECT * FROM electronics;'
        conn = self.openConnection()
        cursor = conn.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        for record in records:
            self.Item_line.insertPlainText(''.join(str(record), ))
            self.Item_line.insertPlainText("\n")

    #display names of columns
    def ShowColumns(self):
        self.Item_line.clear()
        query = "SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='pbd_project' AND `TABLE_NAME`='electronics';"
        conn = self.openConnection()
        cursor = conn.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        for record in records:
            for it in record:
                self.Item_line.insertPlainText(''.join(str(it)))
                self.Item_line.insertPlainText("  ")
        self.Item_line.insertPlainText("\n\n")

    #get names of columns from table electronics and return them as a list
    def GetColumns(self):
        query = "SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='pbd_project' AND `TABLE_NAME`='electronics';"
        conn = self.openConnection()
        cursor = conn.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return records

    def DeleteRecord(self):
        self.counter=0
        item = self.add_line_edit.toPlainText()
        self.add_line_edit.clear()
        #find if item to delete actually exist
        query = "SELECT * FROM electronics WHERE name=('%s');" %(''.join(item))
        conn = self.openConnection()
        cursor = conn.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        if records:
            #if it exists, put together another query and execute it
            query = "DELETE FROM electronics WHERE name=('%s');" %(''.join(item))
            conn = self.openConnection()
            cursor = conn.cursor()
            cursor.execute(query)
            cursor.close()
            conn.close()
            item += ' deleted'
            self.Item_line.clear()
            self.Item_line.insertPlainText(''.join(item))
            #reset id parameter
            self.ResetIncrement()
        else:
            self.Item_line.clear()
            self.Item_line.insertPlainText(''.join("There is no such record to delete"))

    #calling query to reset id in electronics
    def ResetIncrement(self):
        query = "SET  @num := 0; UPDATE electronics SET id = @num := (@num+1); ALTER TABLE electronics AUTO_INCREMENT =1;"
        conn = self.openConnection()
        cursor = conn.cursor()
        cursor.execute(query)
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app = QApplication([])

    login_window = LoginWindow()

    app.exec()