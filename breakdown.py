import nuke
import nukescripts
from PySide2.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QPushButton

class PassList(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        
        #init widgets
        self.list = QListWidget()
        self.addButton = QPushButton('add selected nodes')
        
        #add widgets to layout
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.addButton)
        self.setLayout(self.layout)
        
        #bind buttons
        self.addButton.clicked.connect(self.addItem)


    def addItem(self, item):
        items = [self.list.item(x).text() for x in range(self.list.count())]
        for node in nuke.selectedNodes():
            name = node.name()
            if name not in items:
                self.list.addItem(QListWidgetItem(name))
        
    def makeUI(self):
        return self
        

class BreakdownPanel(nukescripts.PythonPanel):
    def __init__(self):
        nukescripts.PythonPanel.__init__(self, 'breakdown')

        #knobs
        self.renderPath = nuke.File_Knob('render_path', 'file')
        self.textBox = nuke.BBox_Knob('text_box', 'text area')
        self.frame = nuke.Int_Knob('frame', 'frame')
        
        self.passList = nuke.PyCustom_Knob('pass_list', 'pass order', 'PassList()')
        self.renderButton = nuke.PyScript_Knob("render_button", "render")
        

        #adding knobs to panel
        self.addKnob(self.renderPath)
        self.addKnob(self.textBox)
        self.addKnob(self.frame)
        self.addKnob(self.passList)
        self.addKnob(self.renderButton)
        
        #set button commands

    def knobChanged(self, knob):
        #cases for the knobChanged callback
        #the knobChanged callback passes the knob that changed
        
        name = knob.name()

        match name:
            case 'frame':
                print('frame changed')
            case _:
                pass
    
    

def addPanel():
    p = BreakdownPanel()
    return p.addToPane()

paneMenu = nuke.menu('Pane')
paneMenu.addCommand('breakdown', addPanel)
