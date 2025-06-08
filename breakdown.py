import nuke
import nukescripts
from PySide2.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QPushButton

class PassList(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        
        #init widgets
        self.list = QListWidget()
        self.list.setDragDropMode(self.list.InternalMove)

        self.addButton = QPushButton('add selected nodes')
        self.removeButton = QPushButton('remove selected pass')
        
        #add widgets to layout
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.addButton)
        self.layout.addWidget(self.removeButton)
        self.setLayout(self.layout)
        
        #bind buttons
        self.addButton.clicked.connect(self.addItem)
        self.removeButton.clicked.connect(self.removePass)

    def addItem(self, item):
        #check if string is in the list already, add if not
        items = [self.list.item(x).text() for x in range(self.list.count())]

        for node in nuke.selectedNodes():
            name = node.name()
            if name not in items:
                self.list.addItem(QListWidgetItem(name))
        
    def makeUI(self):
        return self

    def removePass(self):
        #remove selected if there is a selected item
        selected = self.list.currentItem()
        if selected:
            row = self.list.row(selected)
            self.list.takeItem(row)
        

class BreakdownPanel(nukescripts.PythonPanel):
    def __init__(self):
        nukescripts.PythonPanel.__init__(self, 'breakdown')

        #knobs
        self.renderPath = nuke.File_Knob('render_path', 'file')
        self.textBox = nuke.BBox_Knob('text_box', 'text area')
        self.textBox.setVisible(False)
        self.frame = nuke.Int_Knob('frame', 'frame')
        
        self.passList = nuke.PyCustom_Knob('pass_list', 'pass order', 'PassList()')
        self.renderButton = nuke.PyScript_Knob("render_button", "render", "createTransition('Merge13', 'Merge20', (1,20))")
        

        #adding knobs to panel
        self.addKnob(self.renderPath)
        self.addKnob(self.textBox)
        self.addKnob(self.frame)
        
        self.addKnob(self.renderButton)
        self.addKnob(self.passList)
        
     

    def knobChanged(self, knob):
        #cases for the knobChanged callback
        #the knobChanged callback passes the knob that changed
        
        name = knob.name()

        match name:
            case 'frame':
                if self.frame.value() < 0:
                    raise ValueError("Frame must be non-negative")

            case _:
                pass
    
def createTransition(fromPass, toPass, range):
    
    #check if passes exist
    a = nuke.toNode(fromPass)
    if not a: 
        nuke.message(f"Error: Could not find {fromPass}")
        return

    b = nuke.toNode(toPass)
    if not b: 
        nuke.message(f"Error: Could not find {toPass}")
        return
    
    #init nodes for wipe transition
    text = nuke.nodes.Text()
    merge = nuke.nodes.Merge()
    rect = nuke.nodes.CopyRectangle()
    frameRange = nuke.nodes.FrameRange()
    appendClip = nuke.nodes.AppendClip()
    
    #set values of the nodes
    format = a.format()
    width, height = format.width(), format.height()

    text['message'].setValue(b.name())
    text['box'].setValue([0,0, width, height])

    merge['operation'].setValue('over')

    rect['area'].setValue([0, 0, 0, width])

    frameRange['first_frame'].setValue(range[0])    
    frameRange['last_frame'].setValue(range[1])

    appendClip['firstFrame'].setValue(range[0])
    appendClip['lastFrame'].setValue(range[1])

    #connecteding nodes

    print('success')

def addPanel():
    p = BreakdownPanel()
    return p.addToPane()

paneMenu = nuke.menu('Pane')
paneMenu.addCommand('breakdown', addPanel)
