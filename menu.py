'''
This file registers the custom node with Nuke, which
lets us use the node in the application
'''
import nuke
from breakdown import addPanel

paneMenu = nuke.menu('Pane')
paneMenu.addCommand('breakdown', addPanel)


