import traceback

from PySide2 import QtWidgets, QtCore, QtGui
import traceback
import sys

datas = {
    "Today": {
        "Task11": "001-025",
        "Task81": "001-030",
        "Task31": "001-035",
        "Task41": "001-048"
    },
    "Yesterday": {
        "Task87": "001-050",
        "Task27": "001-05",
        "Task37": "001-051"
    },
    "Past Week": {
        "Task15": "000-050",
        "Task25": "000-05",
        "Task35": "000-051",
        "Task45": "000-022",
        "Task55": "000-012"

    }
}

class MyUi(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try :
            self.tasks = sg.request # shot SG request
            # convert Sg tasks in a dict
            # ...
        except :
            print("No tasks have been found, entering exercize mode \nUsing the 'datas' dict to fake tasks")
            self.tasks = datas


        # region -- Main Layout

        main_layout = QtWidgets.QGridLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(5, 5, 5, 5)

        self.my_title = QtWidgets.QLabel("Time Log App")
        main_layout.addWidget(self.my_title, 0, 0)
        main_layout.addWidget(self.my_title, 0, 0)

        # main_layout.addWidget(self.separator, 1, 0) # separator

        self.create_time_group_box() # Time group box
        main_layout.addWidget(self._time_group_box, 2, 0, 2, 1)

        self.create_edit_group_box() # Edit group box
        main_layout.addWidget(self._edit_group_box, 2, 2, 1, 1)


        # endregion

        # self.center()

        return

    def create_time_group_box(self):

        lay = QtWidgets.QVBoxLayout()
        self._time_group_box = QtWidgets.QGroupBox("Time Logs")
        self._time_group_box.setLayout(lay)

        time_combo_box = QtWidgets.QComboBox()
        time_combo_box.insertItems(0, list(self.tasks.keys()))
        lay.addWidget(time_combo_box)


        self.list_widget = QtWidgets.QListView()
        self.list_widget.setSelectionMode(QtWidgets.QListWidget.SelectionMode.ExtendedSelection)
        lay.addWidget(self.list_widget)


        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        lay.addWidget(self.refresh_btn)

    def create_edit_group_box(self):
        lay = QtWidgets.QHBoxLayout()
        # lay.setAlignment(QtCore.Qt.Orientation)
        self._edit_group_box = QtWidgets.QGroupBox("Edit")
        self._edit_group_box.setLayout(lay)

        self.plus_btn = QtWidgets.QPushButton("+")
        lay.addWidget(self.plus_btn)


        self.minus_btn = QtWidgets.QPushButton("-")
        lay.addWidget(self.minus_btn)


    def center(self):
        """
        Function to center the application
        """
        qRect = self.frameGeometry() # get size and location of the window, will return PySide.QtCore.QRect object which will hold the height, width, top, and left points of the window
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center() # get center point of the screen
        qRect.moveCenter(centerPoint) # move windoww
        self.move(qRect.topLeft()) # move windoww

    @property
    def separator(self):
        separator = QtWidgets.QLabel(".")
        separator.setFixedHeight(10)
        return separator

def run(*args):
    in_maya = False

    # window opening, different if we are in maya or not
    try:
        import maya.cmds as cmds
        in_maya = not cmds.about(batch=True) # verify if maya is in interface mode or just execute mode (render farm mode)
    except:
        pass

    print("Are we in maya ?", in_maya)

    try:
        if in_maya:

            from ppMaya.tdTools.general.mayaUILaunch import ui_launcher
            ui = MyUi()
            ui_launcher(ui, window_name="MyTestUI")
            ui.show()

        else:

            import sys
            from ppGui.stylesheet.darkss import DarkPalette  # change la palette de couleur
            app = QtWidgets.QApplication(*args)
            dp = DarkPalette()

            app.setStyle("Fusion")
            app.setPalette(dp)

            ui = MyUi()
            ui.show()

            sys.exit(app.exec_())
    except:
        print(traceback.format_exc())

if __name__ == '__main__':
    run(sys.argv)
