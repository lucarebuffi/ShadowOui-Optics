__author__ = 'labx'


from orangewidget import gui, widget

from PyQt4 import QtGui
from PyQt4.QtGui import QPalette, QColor, QFont

from code_drivers.SRW.SRW_driver import SRWDriver

from orangecontrib.shadow.util.shadow_util import ShadowGui

from orangecontrib.optics.objects.optics_objects import BeamlineParameters

import matplotlib.pyplot as plt
import time


class BeamlineCalculator(widget.OWWidget):
    name = "SRW Beamline Calculator"
    description = "SRW Driver: Beamline Calculator"
    icon = "icons/calculator.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "Driver"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Parameters", BeamlineParameters, "setBeamlineParameters")]

    beamline_parameters = None

    NONE_SPECIFIED = "NONE SPECIFIED"

    want_main_area = 0

    error_id = 0
    warning_id = 0
    info_id = 0

    driver = SRWDriver()

    def __init__(self):
        super().__init__()

        self.runaction = widget.OWAction("Run SRW Beamline Simulation", self)
        self.runaction.triggered.connect(self.runSimulation)
        self.addAction(self.runaction)

        self.controlArea.setFixedWidth(100)

        gui.separator(self.controlArea, height=50)

        button_box = ShadowGui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Run Simulation", callback=self.runSimulation)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette())  # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette)  # assign new palette
        button.setFixedHeight(45)

        gui.rubber(self.controlArea)

    def setBeamlineParameters(self, beamline_parameters):
        self.beamline_parameters = beamline_parameters

        if not self.beamline_parameters is None:
            self.runSimulation()


    def runSimulation(self):
        try:
            self.error(self.error_id)
            self.setStatusMessage("")
            self.progressBarInit()

            if not self.beamline_parameters is None:
                driver = SRWDriver()

                self.setStatusMessage("Running SRW simulation")

                self.progressBarSet(50)

                ShadowGui.checkStrictlyPositiveNumber(self.beamline_parameters._energy_min, "Energy Min")
                ShadowGui.checkStrictlyPositiveNumber(self.beamline_parameters._energy_max, "Energy Max")

                srw_wavefront = driver.calculate_radiation(self.beamline_parameters._electron_beam,
                                                           self.beamline_parameters._magnetic_structure,
                                                           self.beamline_parameters._beamline,
                                                           self.beamline_parameters._energy_min,
                                                           self.beamline_parameters._energy_max)

                intensity, dim_x, dim_y = driver.calculate_intensity(srw_wavefront)

                self.setStatusMessage("Calling plots with array shape: ',intensity.shape,'...")

                t0_main = time.time()
                plt.pcolormesh(dim_x,dim_y,intensity.transpose())
                plt.title("Real space for infrared example")
                plt.colorbar()

                self.setStatusMessage("done in " + str(round(time.time() - t0_main)) + " s")

                plt.show()

                self.setStatusMessage("")

        except Exception as exception:
            QtGui.QMessageBox.critical(self, "QMessageBox.critical()",
                                       str(exception),
                                       QtGui.QMessageBox.Ok)

            self.error_id = self.error_id + 1
            self.error(self.error_id, "Exception occurred: " + str(exception))

            #raise exception

        self.progressBarFinished()




