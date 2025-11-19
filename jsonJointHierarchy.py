from __future__ import annotations

from PySide2.QtWidgets import QTreeView, QApplication, QHeaderView
from PySide2 import QtWidgets, QtCore, QtGui

import traceback
import json
import os
import sys

from typing import Any

# region pyside example to interpret a json in a qtree view, taken from internet :
# https://doc.qt.io/qtforpython-6/examples/example_widgets_widgetsgallery.html#example-widgets-widgetsgallery
class TreeItem:
    """A Json item corresponding to a line in QTreeView"""

    def __init__(self, parent: "TreeItem" = None):
        self._parent = parent
        self._key = ""
        self._value = ""
        self._value_type = None
        self._children = []

    def appendChild(self, item: "TreeItem"):
        """Add item as a child"""
        self._children.append(item)

    def child(self, row: int) -> "TreeItem":
        """Return the child of the current item from the given row"""
        return self._children[row]

    def parent(self) -> "TreeItem":
        """Return the parent of the current item"""
        return self._parent

    def childCount(self) -> int:
        """Return the number of children of the current item"""
        return len(self._children)

    def row(self) -> int:
        """Return the row where the current item occupies in the parent"""
        return self._parent._children.index(self) if self._parent else 0

    @property
    def key(self) -> str:
        """Return the key name"""
        return self._key

    @key.setter
    def key(self, key: str):
        """Set key name of the current item"""
        self._key = key

    @property
    def value(self) -> str:
        """Return the value name of the current item"""
        return self._value

    @value.setter
    def value(self, value: str):
        """Set value name of the current item"""
        self._value = value

    @property
    def value_type(self):
        """Return the python type of the item's value."""
        return self._value_type

    @value_type.setter
    def value_type(self, value):
        """Set the python type of the item's value."""
        self._value_type = value

    @classmethod
    def load(
        cls, value: list | dict, parent: "TreeItem" = None, sort=True) -> "TreeItem":
        """Create a 'root' TreeItem from a nested list or a nested dictonary

        Examples:
            with open("file.json") as file:
                data = json.dump(file)
                root = TreeItem.load(data)

        This method is a recursive function that calls itself.

        Returns:
            TreeItem: TreeItem
        """
        rootItem = TreeItem(parent)
        rootItem.key = "root"

        if isinstance(value, dict):
            items = sorted(value.items()) if sort else value.items()

            for key, value in items:
                child = cls.load(value, rootItem)
                child.key = key
                child.value_type = type(value)
                rootItem.appendChild(child)

        elif isinstance(value, list):
            for index, value in enumerate(value):
                child = cls.load(value, rootItem)
                child.key = index
                child.value_type = type(value)
                rootItem.appendChild(child)

        else:
            rootItem.value = value
            rootItem.value_type = type(value)

        return rootItem

# override the Qmodel class of a treeView in order to show datas in a customized way
class JsonModel(QtCore.QAbstractItemModel):
    """ An editable model of Json data """

    def __init__(self, parent: QtCore.QObject = None):
        super().__init__(parent)

        self._rootItem = TreeItem()
        self._headers = ("key", "value")

    def clear(self):
        """ Clear data from the model """
        self.load({})

    def load(self, document: dict):
        """Load model from a nested dictionary returned by json.loads()

        Arguments:
            document (dict): JSON-compatible dictionary
        """

        assert isinstance(
            document, (dict, list, tuple)
        ), "`document` must be of dict, list or tuple, " f"not {type(document)}"

        self.beginResetModel()

        self._rootItem = TreeItem.load(document)
        self._rootItem.value_type = type(document)

        self.endResetModel()

        return True

    def data(self, index: QtCore.QModelIndex, role: QtCore.QItemDataRole) -> Any:
        """Override from QAbstractItemModel

        Return data from a json item according index and role

        """
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return item.key

            if index.column() == 1:
                return item.value

        elif role == QtCore.Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                return item.value

    def setData(self, index: QtCore.QModelIndex, value: Any, role: QtCore.Qt.ItemDataRole):
        """Override from QAbstractItemModel

        Set json item according index and role

        Args:
            index (QModelIndex)
            value (Any)
            role (Qt.ItemDataRole)

        """
        if role == QtCore.Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                item = index.internalPointer()
                item.value = str(value)

                self.dataChanged.emit(index, index, [QtCore.Qt.ItemDataRole.EditRole])

                return True

        return False

    def headerData(
        self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole):
        """Override from QAbstractItemModel

        For the JsonModel, it returns only data for columns (orientation = Horizontal)

        """
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == QtCore.Qt.Orientation.Horizontal:
            return self._headers[section]

    def index(self, row: int, column: int, parent=QtCore.QModelIndex()) -> QtCore.QModelIndex:
        """Override from QAbstractItemModel

        Return index according row, column and parent

        """
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        """Override from QAbstractItemModel

        Return parent index of index

        """

        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self._rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QtCore.QModelIndex()):
        """Override from QAbstractItemModel

        Return row count from parent index
        """
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent=QtCore.QModelIndex()):
        """Override from QAbstractItemModel

        Return column number. For the model, it always return 2 columns
        """
        return 2

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        """Override from QAbstractItemModel

        Return flags of index
        """
        flags = super(JsonModel, self).flags(index)

        if index.column() == 1:
            return QtCore.Qt.ItemFlag.ItemIsEditable | flags
        else:
            return flags

    def to_json(self, item=None): # recursive loop to fetch datas from json file

        if item is None:
            item = self._rootItem

        nchild = item.childCount()

        if item.value_type is dict:
            document = {}
            for i in range(nchild):
                ch = item.child(i)
                document[ch.key] = self.to_json(ch)
            return document

        elif item.value_type == list:
            document = []
            for i in range(nchild):
                ch = item.child(i)
                document.append(self.to_json(ch))
            return document

        else:
            return item.value

    def open_json(self):
        # json_path = QFileInfo(__file__).absoluteDir().filePath("example.json")
        json_path = QtCore.QFileInfo(__file__).absoluteDir().filePath("/exos/json/jsonFile.json")
        with open(json_path) as file:
            document = json.load(file)
            self.load(document)

# endregion


class JsonInteract:
    def create_json_file(file_name):
        try:
            with open(file_name, mode="r") as file:
                print(file_name, " : This file already exists")
                print("Writing datas ...")
                return True


        except FileNotFoundError:
            print(file_name, " : Such file doesn't exist")
            print("Creating it and writing datas ...")
            return False

    def json_write(data, file_name):

        file_exist = JsonInteract.create_json_file(file_name)  # verify if the fie already exist

        if file_exist == True:
            with open(file_name, mode="w", encoding="utf-8") as write_file:
                json.dump(data, write_file, indent=2)  # writes the dict into a json file

            return data

        else:
            write_file = open(file_name, mode="x", encoding="utf-8")
            json.dump(data, write_file, indent=2)  # writes the dict into a json file

    def json_read(file_name):
        with open(file_name, mode="r", encoding="utf-8") as read_file:
            data = json.load(read_file)

        return data


class MayaInteract(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_hierarchy(self):
        hierarchy = {"1_name": 0, "2_pos": 0, "2_rot": 0}

        # get the hierarchy of your scene
        sel = cmds.ls(selection=True)

        if not sel:
          print("Must select a hierarchy")
          return

        else:
          root = sel[0]

        self.datas = MayaInteract.get_children(self, root, hierarchy)

        return self.datas

    def get_children(self, obj, hierarchy):

        pos = cmds.xform(obj, ws=True, q=True, t=True)
        rot = cmds.xform(obj, ws=True, q=True, ro=True)

        hierarchy["1_name"] = obj
        hierarchy["2_pos"] = pos
        hierarchy["2_rot"] = rot

        children = cmds.listRelatives(obj, children=True, shapes=False) or []

        if children:
            hierarchy["3_children"] = {}  # initialise l'item children de cet etage de la hierarchie
            for child in children:
                hierarchy["3_children"][child] = {}
                self.get_children(child, hierarchy["3_children"][child])

        return hierarchy

    def create_hierarchy(self, datas, suffix="", symmetrize = None):
        print("i create this : ")

        if not isinstance(suffix, str):
            raise TypeError(f"Provided suffix is not of stype string: {type(suffix)}> {suffix}")

        self.create_children("", datas, suffix, symmetrize)

    def create_children(self, parent, datas, suffix, symmetrize):
        #create joint with the datas provided in the json file
        cmds.select(clear=1)

        try :
            if datas["1_name"].split('_')[1]: # if the joint already has a suffix
                name = datas["1_name"].split('_')[0] + suffix

        except IndexError : # if it has no suffix at the beginning
            name = datas["1_name"] + suffix

        jnt = cmds.joint(name=name)



        if symmetrize == 0: # if not symetrize
            cmds.xform(jnt, ws=1, t = datas["2_pos"], ro=datas["2_rot"])

        else: # if symmetrize
            pos = datas["2_pos"]
            sym_pos = [-pos[0], pos[1], pos[2]]
            cmds.xform(jnt, ws=1, t = sym_pos, ro=datas["2_rot"])


        if parent :
            cmds.parent(jnt, parent)

        cmds.select(clear=1)

        children = []

        try :
            children = datas["3_children"] or [] #get dict of children
        except KeyError :
            pass

        if children:
            for child in children:
                MayaInteract.create_children(self, name, datas["3_children"][child], suffix, symmetrize)


class Ui(QtWidgets.QWidget):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.space = 10

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        margins = QtCore.QMargins(*[self.space*.5 for x in range(4)])
        self.layout.setContentsMargins(margins)
        self.center()

        # -- UI
        # region -- -- Title
        self.my_title = QtWidgets.QLabel("Get joint hierarchy")
        self.my_title.setAlignment(QtCore.Qt.AlignCenter)
        self.my_title.setFixedWidth(150)
        self.my_title.setFixedHeight(self.space*4)
        self.layout.addWidget(self.my_title)

        self.layout.addWidget(self.separator())

        self.my_text = QtWidgets.QLabel("Get the joints hierarchy and write it in a json file")
        self.layout.addWidget(self.my_text)

        self.layout.addWidget(self.separator())

        self.my_source = QtWidgets.QLabel(f"Json source file is : '{self.json_path}'")
        self.layout.addWidget(self.my_source)

        self.layout.addWidget(self.separator())

        self.symmetrize_box = QtWidgets.QCheckBox("symmetrize hierarchy on opposite -X / +X")
        self.layout.addWidget(self.symmetrize_box)

        self.layout.addWidget(self.separator())

        # endregion

        # region -- -- TreeView
        self.view = QtWidgets.QTreeView()
        self.model = JsonModel()
        self.view.setModel(self.model)
        self.view.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.view.setAlternatingRowColors(True)

        self.layout.addWidget(self.view)

        self.populate_tree_view()

        #endregion

        #region -- -- Box Suffix
        self.line_lay = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.line_lay)

        self.suffix_label = QtWidgets.QLabel()
        self.suffix_label.setText("Choose a new suffix for the created joint hierarchy")
        self.line_lay.addWidget(self.suffix_label)

        self.suffix_line = QtWidgets.QLineEdit("_pasted")
        self.line_lay.addWidget(self.suffix_line)

        #endregion

        # region -- -- Buttons
        self.bt_lay = QtWidgets.QHBoxLayout()  # buttons layout
        self.layout.addLayout(self.bt_lay)

        self.btn_get = QtWidgets.QPushButton()
        self.btn_get.setText("GET")
        self.btn_get.clicked.connect(lambda: self.action_get())
        self.bt_lay.addWidget(self.btn_get)

        self.btn_write = QtWidgets.QPushButton()
        self.btn_write.setText("WRITE")
        self.btn_write.clicked.connect(lambda: self.action_write())
        self.bt_lay.addWidget(self.btn_write)

        self.btn_create = QtWidgets.QPushButton()
        self.btn_create.setText("CREATE")
        self.btn_create.clicked.connect(lambda: self.action_create())
        self.bt_lay.addWidget(self.btn_create)

        self.maya_instance = MayaInteract()

        # endregion

    # region -- Utility functions
    def separator(self):
        separator = QtWidgets.QLabel(" ")
        separator.setFixedHeight(self.space)
        return separator

    def center(self):
        """
        Function to center the application
        """
        qRect = self.frameGeometry() # get size and location of the window, will return PySide.QtCore.QRect object which will hold the height, width, top, and left points of the window
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center() # get center point of the screen
        qRect.moveCenter(centerPoint) # move windoww
        self.move(qRect.topLeft()) # move windoww

    # endregion

    @property # makes the method easier to interact with, removing parenthesis when calling it
    def json_path(self):
        # create a string in a file name format
        # it takes the absolute file name os.path.dirname("current file"=__file__=jsoninteract) but it replaces the end after json by json/jsonFile.json
        # return os.path.join(os.path.dirname(__file__), "json/jsonFile.json")

        return "/users_roaming/echagnon/PycharmProjects/echagnon-internship/python/exos/json/jsonFile.json"

    def populate_tree_view(self):
        datas = JsonInteract.json_read(self.json_path)
        self.model.load(datas)
        print("Tree view populated ...")

    def action_get(self):
        print("get hierarchy")

        self.datas = self.maya_instance.get_hierarchy()

        return self.datas

    def action_write(self):
        print("write hierarchy in a json")

        # print in the json file
        JsonInteract.json_write(self.datas, self.json_path)

        # populate the tree view
        self.populate_tree_view()

    def action_create(self):

        # récupérer le json
        self.jnt_hierarchy = JsonInteract.json_read(self.json_path)

        # symmetrize ?
        symmetrize = self.symmetrize_box.isChecked()

        # populate list
        #widget treeview = json populate tree view

        # create joints
        suffix = self.suffix_line.text()
        self.maya_instance.create_hierarchy(self.jnt_hierarchy, suffix=suffix, symmetrize=symmetrize)

        print("create joint hierarchy")


def run(*args):
    import pprint

    import maya.cmds as cmds

    in_maya = False

    # open the window
    try:
        in_maya = not cmds.about(batch=True) # verify if maya is in interface mode or just execute mode (render farm mode)
    except:
        pass

    print("Are we in maya ?", in_maya)

    try:
        if in_maya:
            from ppMaya.tdTools.general.mayaUILaunch import ui_launcher
            ui = Ui()
            view = QTreeView()
            model = JsonModel()
            view.setModel(model)

            ui_launcher(ui, window_name="MyTestUI")
            ui.show()


        else:

            import sys
            from ppGui.stylesheet.darkss import DarkPalette  # change la palette de couleur
            app = QtWidgets.QApplication(*args)
            dp = DarkPalette()

            app.setStyle("Fusion")
            app.setPalette(dp)

            view = QTreeView()
            model = JsonModel()
            view.setModel(model)

            ui = Ui()
            ui.show()

            sys.exit(app.exec_())

    except:
        print(traceback.format_exc())


if __name__ == '__main__':
    run()
