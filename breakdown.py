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
        #required for pyside widgets
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
        self.frame = nuke.Int_Knob('frame', 'start frame')
        
        self.passList = nuke.PyCustom_Knob('pass_list', 'pass order', 'PassList()')
        self.renderButton = nuke.PyScript_Knob("render_button", "render")
        
        #adding knobs to panel
        self.addKnob(self.renderPath)
        self.addKnob(self.frame)
        
        self.addKnob(self.renderButton)
        self.addKnob(self.passList)
    #createTransition('Merge13', 'Merge20', (1,20))
    def connectPasses(self):
        passListWidget = self.passList.getObject()
        passes = [passListWidget.list.item(x).text() for x in range(passListWidget.list.count())]
        
        pass_count = 0
        last_clip = None

        for i in range(len(passes) - 1):
            start_frame = self.frame.value() + (21 * pass_count)
            end_frame = start_frame + 20

            if last_clip:
                new_clip = createTransition(passes[i], passes[i+1], (start_frame, end_frame))
                new_clip.setInput(1, last_clip)
                last_clip = new_clip
            else:
                last_clip = createTransition(passes[i], passes[i+1], (start_frame, end_frame))

            pass_count += 1
           

    def knobChanged(self, knob):
        #cases for the knobChanged callback
        #the knobChanged callback passes the knob that changed
        
        name = knob.name()

        match name:
            case 'frame':
                if self.frame.value() < 0:
                    raise ValueError("Frame must be non-negative")
            case 'render_button':
                self.connectPasses()
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
    merge = nuke.nodes.Merge()
    rect = nuke.nodes.CopyRectangle()
    area = rect['area']
    frameRange = nuke.nodes.FrameRange()
    appendClip = nuke.nodes.AppendClip()
    
    #set values of the nodes
    format = a.format()
    width, height = format.width(), format.height()


    merge['operation'].setValue('over')

    rect['area'].setValue([0, 0, 0, height])

    frameRange['first_frame'].setValue(range[0])    
    frameRange['last_frame'].setValue(range[1])

    appendClip['firstFrame'].setValue(range[0])
    appendClip['lastFrame'].setValue(range[1])

    #connecteding nodes
    merge.setInput(0, a)
    rect.setInput(0, merge)
    rect.setInput(1, b)
    frameRange.setInput(0, rect)
    appendClip.setInput(0, frameRange)

    #animating transition
    area.setAnimated()
    #set key frame for width = 0 at first frame
    area.setValueAt(0, range[0], 2)
    area.setValueAt(height, range[0], 3)
    #set key frame for width = full width at last frame
    area.setValueAt(width, range[1], 2)
    area.setValueAt(height, range[1], 3)
    
    return appendClip

def addPanel():
    p = BreakdownPanel()
    return p.addToPane()

paneMenu = nuke.menu('Pane')
paneMenu.addCommand('breakdown', addPanel)
