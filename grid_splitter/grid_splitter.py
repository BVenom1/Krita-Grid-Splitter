from krita import *
from PyQt5.QtWidgets import *
from PyQt5.Qt import *

DOCKER_TITLE = 'Grid Splitter'

class GridSplitter(DockWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE)

        # set up blank docker
        self.mainWidget = QWidget(self)
        self.setWidget(self.mainWidget)

        # set up prompt for split width
        self.wbox = QSpinBox(self)
        self.wbox.setRange(0,0)
        self.wbox.setSuffix('px')
        wlabel = QLabel('split width : ', self)     # label in the widget

        # set up prompt for split height
        self.hbox = QSpinBox(self)
        self.hbox.setRange(0,0)
        self.hbox.setSuffix('px')
        hlabel = QLabel('split height : ', self)     # label in the widget

        # set up button to split the layer and save it
        self.splitButton = QPushButton('split', self)
        self.splitButton.clicked.connect(self.debugPopup)

        # add GUI elements to docker
        self.mainWidget.setLayout(QFormLayout())
        self.mainWidget.layout().addRow(wlabel, self.wbox)
        self.mainWidget.layout().addRow(hlabel, self.hbox)
        self.mainWidget.layout().addRow(self.splitButton)

        # set up some additional fields
        self.width = 0                  # width of open image
        self.height = 0                 # height of open image
        self.doc = None                 # document reference of open image

        # call a second set up function to finish the set up when the main window is fully loaded
        Krita.instance().notifier().windowCreated.connect(self.on_windowCreated)

    # secondary setup function
    def on_windowCreated(self):
        self.window = Krita.instance().activeWindow()
        self.window.activeViewChanged.connect(self.update)
    
    # function to update ranges of width and height
    def update(self):
        if self.window.activeView() == None:
            self.width = 0
            self.height = 0
            self.wbox.setRange(0, 0)
            self.hbox.setRange(0, 0)
            self.doc = None
        
        else:
            self.doc = self.window.activeView().document()
            self.width = self.doc.bounds().width()
            self.height = self.doc.bounds().height()
            self.wbox.setRange(1, self.width)
            self.hbox.setRange(1, self.height)
    
    # generic popup message function
    def popup(self, string: str):
        QMessageBox.information(QWidget(), 'Grid Splitter', string)

    # function to make a debug message popup
    def debugPopup(self):
        self.popup('debug')

    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        pass