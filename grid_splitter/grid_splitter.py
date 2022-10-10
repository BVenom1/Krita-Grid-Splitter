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

        # set up dropdown menu for file type
        self.tbox = QComboBox(self)
        self.tbox.addItems(['.png', '.jpg', '.bmp', '.ppm'])
        tlabel = QLabel('save file extension : ', self)

        # set up button to split the layer and save it
        self.splitButton = QPushButton('split', self)
        self.splitButton.clicked.connect(self.on_splitButton_clicked)

        # add GUI elements to docker
        self.mainWidget.setLayout(QFormLayout())
        self.mainWidget.layout().addRow(wlabel, self.wbox)
        self.mainWidget.layout().addRow(hlabel, self.hbox)
        self.mainWidget.layout().addRow(tlabel, self.tbox)
        self.mainWidget.layout().addRow(self.splitButton)

        # set up some additional fields
        self.width = 0                  # width of open image
        self.height = 0                 # height of open image
        self.doc = None                 # document reference of open image
        self.xRes = 72                  # x-resolution of image (pixels per inch)
        self.yRes = 72                  # y-resolution of image (pixels per inch)

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
            self.xRes = 72
            self.yRes = 72
        
        else:
            self.doc = self.window.activeView().document()
            self.width = self.doc.width()
            self.height = self.doc.height()
            self.wbox.setRange(1, self.width)
            self.hbox.setRange(1, self.height)
            self.xRes = self.doc.xRes()
            self.yRes = self.doc.yRes()
    
    # function called when splitButton is clicked, splits the current active layer and saves the splits to given folder
    def on_splitButton_clicked(self):
        if len(self.window.views()) == 0:
            self.popup('ERROR: no document is open')
            return
        
        activeNode = self.doc.activeNode()

        dirpath = QFileDialog.getExistingDirectory(None, 'Saves folder', '')
        if dirpath == '':
            self.popup('No seves folder selected, split aborted')
            return
        
        basename = activeNode.uniqueId().toByteArray(1)

        filestem = f'{dirpath}/{basename}'

        sp_w = self.wbox.value()
        sp_h = self.hbox.value()
        ext = self.tbox.currentText()

        num_splits_w = self.width // sp_w
        num_splits_h = self.height // sp_h
        frac_w = self.width % sp_w
        frac_h = self.height % sp_h

        for i in range(0, num_splits_h):
            for j in range(0, num_splits_w):
                activeNode.save(f'{filestem}-{i:d}-{j:d}{ext}', 
                                self.xRes, self.yRes, 
                                InfoObject(), 
                                QRect(j*sp_w, i*sp_h, sp_w, sp_h))
            
            if frac_w != 0:
                activeNode.save(f'{filestem}-{i:d}-{num_splits_w:d}{ext}', 
                                self.xRes, self.yRes, 
                                InfoObject(), 
                                QRect(num_splits_w*sp_w, i*sp_h, frac_w, sp_h))
        
        if frac_h != 0:
            for j in range(0, num_splits_w):
                activeNode.save(f'{filestem}-{num_splits_h:d}-{j:d}{ext}', 
                                self.xRes, self.yRes, 
                                InfoObject(), 
                                QRect(j*sp_w, num_splits_h*sp_h, sp_w, frac_h))
            
            if frac_w != 0:
                activeNode.save(f'{filestem}-{num_splits_h:d}-{num_splits_w:d}{ext}', 
                                self.xRes, self.yRes, 
                                InfoObject(), 
                                QRect(num_splits_w*sp_w, num_splits_h*sp_h, frac_w, frac_h))

        self.popup('go check')
    
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