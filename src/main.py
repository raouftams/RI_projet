from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget
from PyQt5.QtCore import QAbstractTableModel, Qt, pyqtSlot
from index import *
import sys

class HomePage(QMainWindow):
    def __init__(self):
        super(HomePage, self).__init__()
        loadUi("src/ui/homepage.ui", self)
        self.boolean_model_action.clicked.connect(lambda: self.switch_to_boolean_model())
        self.vectorial_model_action.clicked.connect(lambda: self.switch_to_vectorial_model())
        self.search_by_term_btn.clicked.connect(lambda: self.search_by_term())
        self.search_by_doc_btn.clicked.connect(lambda: self.search_by_doc())

    def switch_to_boolean_model(self):
        widget.setCurrentIndex(1)
    
    def switch_to_vectorial_model(self):
        widget.setCurrentIndex(2)

    def search_by_term(self):
        term = self.term_field.text()
        data = get_term_freq("out/inversefilebyfreq.pkl", str(term))
        self.set_info_text("")
        if data != None:
            header = ["Document", "Fréquence"]
            docs_freq = []
            for item in data:
                docs_freq.append([item[0], item[1]])

            self.result_table.setModel(TableModel(docs_freq, header))
        else:
            self.set_info_text("Le terme '" + term + "' n'existe pas.")


    def search_by_doc(self):
        doc = self.doc_number_edit.text()
        data = get_doc_freq("out/inversefile.pkl", int(doc))
        self.set_info_text("")
        if data != None:
            header = ["Terme", "Fréquence"]
            term_freq = []
            for item in data.items():
                term_freq.append([item[0], item[1]])

            self.result_table.setModel(TableModel(term_freq, header))
        else:
            self.set_info_text("Le document n°" + doc + " n'existe pas.")

    def set_info_text(self, text):
        self.info_label.setText(text)
        self.info_label.adjustSize()

class BooleanModel(QWidget):
    def __init__(self):
        super(BooleanModel, self).__init__()
        loadUi("src/ui/booleanModel.ui", self)
        self.methodBox.setEnabled(False)
        self.base_functions_action.clicked.connect(lambda: self.switch_to_base_functions())
        self.vectorial_model_action.clicked.connect(lambda: self.switch_to_vectorial_model())
        self.sendRequestBtn.clicked.connect(lambda: self.send_request())
        
    def switch_to_base_functions(self):
        widget.setCurrentIndex(0)
    
    def switch_to_vectorial_model(self):
        widget.setCurrentIndex(2)

    def send_request(self):
        request = self.requestField.toPlainText()
        self.set_info_text("")
        if(request == ""):
            self.set_info_text("Le champ requête est obligatoire.")
        else:
            pertinent_docs = create_boolean_model("out/inversefile.pkl", request)
            if len(pertinent_docs) != 0:
                header = ["Document", "Nombre de termes"]
                self.resultTable.setModel(TableModel(pertinent_docs, header))
            else:
                self.set_info_text("Aucun résultat trouvé.")
    
    def set_info_text(self, text):
        self.info_label.setText(text)
        self.info_label.adjustSize()

class VectorialModel(QWidget):
    def __init__(self):
        super(VectorialModel, self).__init__()
        loadUi("src/ui/booleanModel.ui", self)
        self.methodBox.setEnabled(True)
        self.methodBox.addItem("produit interne")
        self.methodBox.addItem("coefficient de dice")
        self.methodBox.addItem("cosinus")
        self.methodBox.addItem("jaccard")
        self.base_functions_action.clicked.connect(lambda: self.switch_to_base_functions())
        self.boolean_model_action.clicked.connect(lambda: self.switch_to_boolean_model())
        self.sendRequestBtn.clicked.connect(lambda: self.send_request())
        
    def switch_to_base_functions(self):
        widget.setCurrentIndex(0)
    
    def switch_to_boolean_model(self):
        widget.setCurrentIndex(1)

    def send_request(self):
        request = self.requestField.toPlainText()
        method = 1
        if str(self.methodBox.currentText()) == "coefficient de dice":
            method = 2
        if str(self.methodBox.currentText()) == "cosinus":
            method = 3
        if str(self.methodBox.currentText()) == "jaccard":
            method = 4

        self.set_info_text("")
        if(request == ""):
            self.set_info_text("le champ requête est obligatoire")
        else:
            pertinent_docs = create_vectorial_model("out/inversefilebyweight.pkl", "out/inversefile.pkl", request, method)
            data = []
            if len(pertinent_docs) != 0:
                for item in pertinent_docs.items():
                    data.append([item[0], item[1]])
                header = ["Document", "Poids"]
                self.resultTable.setModel(TableModel(data, header))
            else:
                self.set_info_text("Aucun résultat trouvé.")

    def set_info_text(self, text):
        self.info_label.setText(text)
        self.info_label.adjustSize()

class TableModel(QAbstractTableModel):
    def __init__(self, data, header):
        super(TableModel, self).__init__()
        self._data = data
        self._header = header

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            
            return self._data[index.row()][index.column()]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._header[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])



app = QApplication(sys.argv)
main_window = HomePage()
boolean_model_window = BooleanModel()
vectorial_model_window = VectorialModel()
widget = QStackedWidget()
widget.addWidget(main_window)
widget.addWidget(boolean_model_window)
widget.addWidget(vectorial_model_window)
widget.setFixedHeight(600)
widget.setFixedWidth(800)
widget.show()
sys.exit(app.exec_())
