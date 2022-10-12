from krita import *
from PyQt5.QtWidgets import *
from PyQt5.Qt import *

DOCKER_TITLE = "BVenom's Grid Splitter"

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
        self.tbox.addItems(['.png', '.jpg', '.jpeg', '.bmp', '.ppm'])
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
        self.window = None

        # InfoObject to pass to save function
        self.saveInfo = InfoObject()
        
        # jpeg properties
        self.saveInfo.setProperty('quality', 100)
        self.saveInfo.setProperty('optimize', True)
        self.saveInfo.setProperty('subsampling', 0)

        Krita.instance().notifier().windowCreated.connect(self.on_windowCreated)
    
    def on_windowCreated(self):
        self.window = Krita.instance().activeWindow()
    
    # function called when splitButton is clicked, splits the current active layer and saves the splits to given folder
    def on_splitButton_clicked(self):
        if self.window == None or len(self.window.views()) == 0:
            self.popup('ERROR: no document is open')
            return
        
        activeNode = self.doc.activeNode()

        dirpath = QFileDialog.getExistingDirectory(None, 'Saves folder', '')
        if dirpath == '':
            self.popup('No seves folder selected, split aborted')
            return
        
        # replace button with progress bar
        self.splitButton = self.mainWidget.layout().takeRow(3).fieldItem.widget()       # reomve button
        progressBar = QProgressBar(self)
        self.mainWidget.layout().addRow(progressBar)                # insert progress bar in its place

        # get base file path to save the splits
        basename = activeNode.uniqueId().toByteArray(1)
        filestem = f'{dirpath}/{basename}'

        # get split width, split height and file extension from docker
        sp_w = self.wbox.value()
        sp_h = self.hbox.value()
        ext = self.tbox.currentText()

        # get number of full splits and dimensions of fractional splits
        num_splits_w = self.width // sp_w
        num_splits_h = self.height // sp_h
        frac_w = self.width % sp_w
        frac_h = self.height % sp_h

        # make a progress bar
        temp1 = num_splits_h
        if frac_h != 0 :
            temp1 += 1
        temp2 = num_splits_w
        if frac_w != 0:
            temp2 += 1
        progressBar.setMaximum(temp1*temp2-1)
        progressBar.setValue(progressBar.value()+1)

        # split the images and save them
        for i in range(0, num_splits_h):
            for j in range(0, num_splits_w):                            # block to get all sp_w x sp_h sized splits
                activeNode.save(f'{filestem}-{i:d}-{j:d}{ext}', 
                                self.xRes, self.yRes, self.saveInfo,
                                QRect(j*sp_w, i*sp_h, sp_w, sp_h))
                progressBar.setValue(progressBar.value()+1)
            
            if frac_w != 0:                                             # block to get all frac_w x sp_h sized splits
                activeNode.save(f'{filestem}-{i:d}-{num_splits_w:d}{ext}', 
                                self.xRes, self.yRes, self.saveInfo,
                                QRect(num_splits_w*sp_w, i*sp_h, frac_w, sp_h))
                progressBar.setValue(progressBar.value()+1)
        
        if frac_h != 0:
            for j in range(0, num_splits_w):                            # block to get all sp_w x frac_h sized splits
                activeNode.save(f'{filestem}-{num_splits_h:d}-{j:d}{ext}', 
                                self.xRes, self.yRes, self.saveInfo,
                                QRect(j*sp_w, num_splits_h*sp_h, sp_w, frac_h))
                progressBar.setValue(progressBar.value()+1)
            
            if frac_w != 0:                                             # block to get the frac_w x frac_h sized split
                activeNode.save(f'{filestem}-{num_splits_h:d}-{num_splits_w:d}{ext}', 
                                self.xRes, self.yRes, self.saveInfo,
                                QRect(num_splits_w*sp_w, num_splits_h*sp_h, frac_w, frac_h))
                progressBar.setValue(progressBar.value()+1)
        
        self.mainWidget.layout().removeRow(3)       # remove the progress bar
        self.mainWidget.layout().addRow(self.splitButton)   # add the button back
        self.popup('Active layer has been split')
    
    # generic popup message function
    def popup(self, string: str):
        QMessageBox.information(QWidget(), 'Grid Splitter', string)

    # function to make a debug message popup
    def debugPopup(self):
        self.popup('debug')

    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        if self.window == None:
            return

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