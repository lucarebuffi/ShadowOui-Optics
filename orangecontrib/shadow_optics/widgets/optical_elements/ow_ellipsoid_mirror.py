import sys
from orangewidget import gui
from PyQt4.QtGui import QApplication

import Shadow

from orangecontrib.shadow_optics.widgets.gui import ow_ellipsoid_element, ow_optical_element
from code_drivers.shadow.optical_elements.shadow_optical_element import ShadowOpticalElement

class EllipsoidMirror(ow_ellipsoid_element.EllipsoidElement):

    name = "Shadow Ellipsoid Mirror"
    description = "Shadow OE: Ellipsoid Mirror"
    icon = "icons/ellipsoid_mirror.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 3
    category = "Optical Elements"
    keywords = ["data", "file", "load", "read"]

    def __init__(self):
        graphical_Options=ow_optical_element.GraphicalOptions(is_mirror=True)

        super().__init__(graphical_Options)

        gui.rubber(self.controlArea)

        gui.rubber(self.mainArea)

    ################################################################
    #
    #  SHADOW MANAGEMENT
    #
    ################################################################

    def instantiateShadowOE(self):
        shadow_oe = ShadowOpticalElement(oe=Shadow.OE())

        shadow_oe._oe.FMIRR=2
        shadow_oe._oe.F_CRYSTAL = 0
        shadow_oe._oe.F_REFRACT = 0

        return shadow_oe

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = EllipsoidMirror()
    ow.show()
    a.exec_()
    ow.saveSettings()