import sys
from numpy import array, zeros

from orangewidget import widget, gui
from PyQt4.QtGui import QApplication

import Shadow
from orangecontrib.shadow_optics.widgets.gui.ow_optical_element import OpticalElement, GraphicalOptions
from code_drivers.shadow.optical_elements.shadow_optical_element import ShadowOpticalElement


class ScreenSlits(OpticalElement):

    name = "Shadow Screen-Slits"
    description = "Shadow OE: Screen/Slits"
    icon = "icons/screen_slits.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 7
    category = "Optical Elements"
    keywords = ["data", "file", "load", "read"]

    def __init__(self):
        graphical_Options=GraphicalOptions(is_screen_slit=True)

        super().__init__(graphical_Options)

        gui.rubber(self.controlArea)

        gui.rubber(self.mainArea)

    def instantiateShadowOE(self):
        shadow_oe = ShadowOpticalElement(oe=Shadow.OE())

        shadow_oe._oe.FMIRR=5
        shadow_oe._oe.F_CRYSTAL = 0
        shadow_oe._oe.F_REFRAC=2
        shadow_oe._oe.F_SCREEN=1
        shadow_oe._oe.N_SCREEN=1

        return shadow_oe



    def doSpecificSetting(self, shadow_oe):

        n_screen = 1
        i_screen = array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])  # after
        i_abs = zeros(10)
        i_slit = zeros(10)
        i_stop = zeros(10)
        k_slit = zeros(10)
        thick = zeros(10)
        file_abs = array(['', '', '', '', '', '', '', '', '', ''])
        rx_slit = zeros(10)
        rz_slit = zeros(10)
        sl_dis = zeros(10)
        file_src_ext = array(['', '', '', '', '', '', '', '', '', ''])
        cx_slit = zeros(10)
        cz_slit = zeros(10)

        i_abs[0] = self.absorption
        i_slit[0] = self.aperturing

        if self.aperturing == 1:
            i_stop[0] = self.open_slit_solid_stop
            k_slit[0] = self.aperture_shape

            if self.aperture_shape == 2:
                file_src_ext[0] = bytes(self.external_file_with_coordinate, 'utf-8')
            else:
                rx_slit[0] = self.slit_width_xaxis
                rz_slit[0] = self.slit_height_zaxis
                cx_slit[0] = self.slit_center_xaxis
                cz_slit[0] = self.slit_center_zaxis

        if self.absorption == 1:
            thick[0] = self.thickness
            file_abs[0] = bytes(self.opt_const_file_name, 'utf-8')

        shadow_oe._oe.set_screens(n_screen,
                                i_screen,
                                i_abs,
                                sl_dis,
                                i_slit,
                                i_stop,
                                k_slit,
                                thick,
                                file_abs,
                                rx_slit,
                                rz_slit,
                                cx_slit,
                                cz_slit,
                                file_src_ext)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = ScreenSlits()
    ow.show()
    a.exec_()
    ow.saveSettings()