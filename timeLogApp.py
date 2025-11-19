import traceback

from PySide6 import QtWidgets, QtCore, QtGui
# from PySide2 import QtWidgets, QtCore, QtGui
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

class MyList():
    def __init__(self, column_number=3):
        self.column_number = column_number






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


        self._time_group_box = QtWidgets.QGroupBox("Time Logs")
        lay = QtWidgets.QVBoxLayout()
        self._time_group_box.setLayout(lay)

        self.time_combo_box = QtWidgets.QComboBox()
        self.time_combo_box.insertItems(0, list(self.tasks.keys()))
        lay.addWidget(self.time_combo_box)


        self.list = QtWidgets.QListWidget()
        self.list.setSelectionMode(QtWidgets.QListWidget.SelectionMode.ExtendedSelection)
        self.populate_list()
        self.list.itemSelectionChanged.connect(lambda: self.set_edit_task)

        self.time_combo_box.currentIndexChanged.connect(lambda: self.populate_list())
        lay.addWidget(self.list)


        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        lay.addWidget(self.refresh_btn)

    @property
    def time_combo_box_changed(self):
        self._task_time = self.time_combo_box.currentText()
        return self._task_time


    def populate_list(self):
        time = self.time_combo_box_changed

        self.list.clear()
        self.list.addItems(list(self.tasks[time]))

        return


    def remove_list_item(self, index):
        return

    # endregion

    def create_edit_group_box(self):
        # lay.setAlignment(QtCore.Qt.Orientation)
        self._edit_group_box = QtWidgets.QGroupBox("Edit")
        lay = QtWidgets.QGridLayout()
        self._edit_group_box.setLayout(lay)

        self._selected_task_label = QtWidgets.QLabel()
        self.set_edit_task
        lay.addWidget(self._selected_task_label, 0, 0, 1, 2)

        self.plus_btn = QtWidgets.QPushButton("+")
        lay.addWidget(self.plus_btn, 1, 0)

        self.minus_btn = QtWidgets.QPushButton("-")
        lay.addWidget(self.minus_btn, 1, 1)
    # region -- List

    @property
    def set_edit_task(self):
        if self.list.selectedItems():
            self._edit_task = self.list.selectedItems()[0].text()
            self._selected_task_label.setText(self._edit_task)
        else:
            self._selected_task_label.setText(".")
            return

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
            app = QtWidgets.QApplication(*args)
            try:
                from ppGui.stylesheet.darkss import DarkPalette  # change la palette de couleur

                dp = DarkPalette()

                app.setStyle("Fusion")
                app.setPalette(dp)
            except ModuleNotFoundError:
                pass

            ui = MyUi()
            ui.show()

            # sys.exit(app.exec_())
            sys.exit(app.exec())


    except:
        print(traceback.format_exc())

if __name__ == '__main__':
    run(sys.argv)
