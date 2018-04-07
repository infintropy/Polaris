from PySide.QtCore import *
from PySide.QtGui import *
import ramayana
QString = str
#ac = ramayana.Multivac()
ac = None

class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.ac = ac

        # declare central layout
        self.master_layout = QHBoxLayout()
        self.setLayout(self.master_layout)

        self.projects_view = QTableView()
        self.master_layout.addWidget( self.projects_view )

        rowCount = 4
        columnCount = 6

        headers = ["Pallete0", "Colors", "Brushes", "Omg", "Technical", "Artist"]
        tableData0 = [[QColor("#FFFF00") for i in range(columnCount)] for j in range(rowCount)]

        model = TableModel(tableData0, headers)
        model.insertColumns(0, 5)

        self.projects_view.setModel(model)


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
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):

        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            return self.__colors[row][column].name()

        if role == Qt.ToolTipRole:
            row = index.row()
            column = index.column()
            return "Hex code: " + self.__colors[row][column].name()

        if role == Qt.DecorationRole:
            row = index.row()
            column = index.column()
            value = self.__colors[row][column]

            pixmap = QPixmap(26, 26)
            pixmap.fill(value)

            icon = QIcon(pixmap)

            return icon

        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self.__colors[row][column]

            return value.name()

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

