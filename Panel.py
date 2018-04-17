from PySide.QtCore import *
from PySide.QtGui import *

import ramayana
QString = str



class Hanuman(QThread):
    def __init__(self):
        super(Hanuman, self).__init__()
        self.ac = ramayana.Multivac()
        pass


    def run(self):
        self.ac.setup()

class LoginScreen(QWidget):


    def __init__(self):
        super(LoginScreen, self).__init__()

        self.master_layout = QVBoxLayout()
        self.setLayout( self.master_layout )

        self.info = QLabel('Polaris')
        self.amount_tables = QLabel('No Tables')

        self.progress = QProgressBar()


        self.password = QLineEdit()
        self.master_layout.addWidget( self.info )
        self.master_layout.addWidget( self.amount_tables )
        self.master_layout.addWidget( self.progress )

class LoadingWindow(QWidget):
    def __init__(self):
        super(LoadingWindow, self).__init__()

        self.progress = QProgressBar()
        self.label = QLabel("Loading:")





class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        #self.ac = ramayana.Multivac()
        self.hanuman = Hanuman()
        self.count = 0

        self.setMinimumWidth( 500 )
        self.setMinimumHeight( 400 )

        self.switch = QStackedWidget()
        # declare central layout
        self.master_layout = QHBoxLayout()
        self.setLayout(self.master_layout)

        self.login = LoginScreen()
        #self.login.password.returnPressed

        self.projects_view = QTableView()
        self.projects_view.verticalHeader().hide()
        self.projects_view.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.switch.addWidget( self.projects_view )
        self.switch.addWidget( self.login )
        self.switch.setCurrentWidget( self.login)


        self.master_layout.addWidget( self.switch )
        #self.master_layout.addWidget( self.nodz )



        self.hanuman.ac.this_project.connect(self.update_info)
        self.hanuman.ac.project_table_count.connect(self.update_progress)
        self.hanuman.ac.table_increment.connect( self.increment_progress )
        self.hanuman.ac.setup_complete.connect( self.go_to_main )
        self.hanuman.start()


    def update_info(self, info):
        self.login.info.setText( info )

    def update_progress(self, count):
        #self.count = count
        self.login.progress.setMaximum(count*2)
        self.login.amount_tables.setText( "%d tables in this project" %count )

    def increment_progress(self, increment):
        self.login.progress.setValue(increment)


    def setup_project_view(self):
        rowCount = 4
        columnCount = 6

        projects = self.hanuman.ac.config['BASE'].get_all()
        headers = projects[0]['fields'].keys()
        tableData0 = [[p['fields'][i] for i in headers] for p in projects]
        print tableData0

        model = TableModel(tableData0, headers)
        #model.insertColumns(0, 5)

        self.projects_view.setModel(model)

    def go_to_main(self):
        self.setup_project_view()
        self.switch.setCurrentWidget( self.projects_view )



class TableModel(QAbstractTableModel):

    def __init__(self, colors=[[]], headers=[], parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.__colors = colors
        self.__headers = headers

    def rowCount(self, parent):
        return len(self.__colors)

    def columnCount(self, parent):
        return len(self.__colors[0])

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):

        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            return self.__colors[row][column].name()

        if role == Qt.ToolTipRole:
            row = index.row()
            column = index.column()
            return "Hex code: " + self.__colors[row][column]

        if role == Qt.DecorationRole:
            pass
            row = index.row()
            column = index.column()
            value = self.__colors[row][column]

            pixmap = QPixmap(26, 26)
            pixmap.fill(value)

            icon = QIcon(pixmap)
            if self.__headers[column] == 'project_code':
                return icon
            else:
                pass

        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self.__colors[row][column]

            return value

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:

            row = index.row()
            column = index.column()

            color = QColor(value)

            if color.isValid():
                self.__colors[row][column] = color
                self.dataChanged.emit(index, index)
                return True
        return False

    def headerData(self, section, orientation, role):

        if role == Qt.DisplayRole:

            if orientation == Qt.Horizontal:

                if section < len(self.__headers):
                    return self.__headers[section]
                else:
                    return "not implemented"
            else:
                return "Color %s" %section

    # =====================================================#
    # INSERTING & REMOVING
    # =====================================================#
    def insertRows(self, position, rows, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)

        for i in range(rows):
            defaultValues = [QColor("#000000") for i in range(self.columnCount(None))]
            self.__colors.insert(position, defaultValues)

        self.endInsertRows()

        return True

    def insertColumns(self, position, columns, parent=QModelIndex()):
        self.beginInsertColumns(parent, position, position + columns - 1)

        rowCount = len(self.__colors)

        for i in range(columns):
            for j in range(rowCount):
                self.__colors[j].insert(position, QColor("#000000"))

        self.endInsertColumns()

        return True

