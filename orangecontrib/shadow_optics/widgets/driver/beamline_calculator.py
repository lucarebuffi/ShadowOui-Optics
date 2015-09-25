__author__ = 'labx'


import sys

from orangewidget import gui, widget
from PyQt4 import QtGui
from PyQt4.QtGui import QPalette, QColor, QFont

from orangecontrib.shadow.widgets.gui import ow_generic_element
from orangecontrib.shadow.util.shadow_objects import EmittingStream

from code_drivers.shadow.driver.shadow_driver import ShadowDriver
from code_drivers.shadow.driver.shadow_beam import ShadowBeam

from orangecontrib.shadow.util.shadow_util import ShadowGui

from orangecontrib.optics.objects.optics_objects import BeamlineParameters


class BeamlineCalculator(ow_generic_element.GenericElement):
    name = "Shadow Beamline Calculator"
    description = "Shadow Driver: Beamline Calculator"
    icon = "icons/calculator.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "Driver"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Parameters", BeamlineParameters, "setBeamlineParameters")]

    outputs = [{"name": "Beam",
                "type": ShadowBeam,
                "doc": "Shadow Beam",
                "id": "beam"}]

    beamline_parameters = None

    NONE_SPECIFIED = "NONE SPECIFIED"

    CONTROL_AREA_HEIGHT = 440
    CONTROL_AREA_WIDTH = 470

    want_main_area = 1

    driver = ShadowDriver()

    def __init__(self):
        super().__init__()

        self.runaction = widget.OWAction("Run Shadow Beamline Simulation", self)
        self.runaction.triggered.connect(self.runSimulation)
        self.addAction(self.runaction)

        gui.separator(self.controlArea, height=600)

        button_box = ShadowGui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Run Simulation", callback=self.runSimulation)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette())  # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette)  # assign new palette
        button.setFixedHeight(45)


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
                driver = ShadowDriver()

                sys.stdout = EmittingStream(textWritten=self.writeStdOut)


                self.setStatusMessage("Running SHADOW simulation")

                self.progressBarSet(50)

                ###########################################
                # TODO: TO BE ADDED JUST IN CASE OF BROKEN
                #       ENVIRONMENT: MUST BE FOUND A PROPER WAY
                #       TO TEST SHADOW
                self.fixWeirdShadowBug()
                ###########################################

                ShadowGui.checkStrictlyPositiveNumber(self.beamline_parameters._energy_min, "Energy Min")
                ShadowGui.checkStrictlyPositiveNumber(self.beamline_parameters._energy_max, "Energy Max")

                shadow_beam = driver.calculate_radiation(self.beamline_parameters._electron_beam,
                                                         self.beamline_parameters._magnetic_structure,
                                                         self.beamline_parameters._beamline,
                                                         self.beamline_parameters._energy_min,
                                                         self.beamline_parameters._energy_max)


                self.setStatusMessage("Plotting Results")

                self.plot_results(shadow_beam)

                self.setStatusMessage("")

                self.send("Beam", shadow_beam)

        except Exception as exception:
            QtGui.QMessageBox.critical(self, "QMessageBox.critical()",
                                       str(exception),
                                       QtGui.QMessageBox.Ok)

            self.error_id = self.error_id + 1
            self.error(self.error_id, "Exception occurred: " + str(exception))

            raise exception

        self.progressBarFinished()




