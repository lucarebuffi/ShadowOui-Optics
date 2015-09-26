import sys

import Shadow

from orangewidget import gui
from PyQt4.QtGui import QApplication

from orangecontrib.shadow_optics.widgets.gui import ow_plane_element, ow_optical_element
from code_drivers.shadow.optical_elements.shadow_optical_element import ShadowOpticalElement


class PlaneCrystal(ow_plane_element.PlaneElement):

    name = "Shadow Plane Crystal"
    description = "Shadow OE: Plane Crystal"
    icon = "icons/plane_crystal.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 5
    category = "Optical Elements"
    keywords = ["data", "file", "load", "read"]

    def __init__(self):
        graphical_Options=ow_optical_element.GraphicalOptions(is_crystal=True)

        super().__init__(graphical_Options)

        gui.rubber(self.controlArea)

        gui.rubber(self.mainArea)

    def instantiateShadowOE(self):
        shadow_oe = ShadowOpticalElement(oe=Shadow.OE())

        shadow_oe._oe.FMIRR=5
        shadow_oe._oe.F_CRYSTAL = 1
        shadow_oe._oe.FILE_REFL = bytes("", 'utf-8')
        shadow_oe._oe.F_REFLECT = 0
        shadow_oe._oe.F_BRAGG_A = 0
        shadow_oe._oe.A_BRAGG = 0.0

        shadow_oe._oe.F_REFRACT = 0

        return shadow_oe

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = PlaneCrystal()
    ow.show()
    a.exec_()
    ow.saveSettings()