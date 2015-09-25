import sys

from orangewidget import gui, widget
from orangewidget.widget import OWWidget
from orangewidget.settings import Setting
from PyQt4 import QtGui
from PyQt4.QtGui import QApplication, QPalette, QColor, QFont
from PyQt4.QtCore import QRect

from orangecontrib.shadow.util.shadow_util import ShadowGui, ConfirmDialog

from orangecontrib.optics.objects.optics_objects import LensIdealParameters

class LensIdeal(OWWidget):

    name = "SRW Lens Ideal"
    description = "SRW: Lens Ideal"
    icon = "icons/lens.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "Optical Elements"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Parameters", LensIdealParameters, "setLensIdealParameters"),
              ("Input Wavefront", object, "set_input")]

    outputs = [{"name":"Output Wavefront",
                "type":object,
                "doc":"Output",
                "id":"output"}]

    lens_position = Setting(0.0)
    focal_x       = Setting(0.0)
    focal_y       = Setting(0.0)

    want_main_area=0

    MAX_WIDTH = 500
    MAX_HEIGHT = 100

    error_id = 0
    warning_id = 0
    info_id = 0

    lens_ideal_parameters = None

    def __init__(self):
        super().__init__()

        self.runaction = widget.OWAction("Run Simulation", self)
        self.runaction.triggered.connect(self.run_simulation)
        self.addAction(self.runaction)

        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width()*0.05),
                               round(geom.height()*0.05),
                               round(min(geom.width()*0.5, self.MAX_WIDTH)),
                               round(min(geom.height()*0.5, self.MAX_HEIGHT))))

        label_box = ShadowGui.widgetBox(self.controlArea, "", orientation="horizontal")

        gui.separator(label_box, height=50)
        gui.label(label_box, self, "                                JUST A DEMO WIDGET!!!!!")
        gui.separator(label_box, height=50)

        self.left_box_1 = ShadowGui.widgetBox(self.controlArea, "Electron Beam", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(self.left_box_1, self, "lens_position", "Position on beamline", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_1, self, "focal_x", "Focal length (horizontal) [m]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_1, self, "focal_y", "Focal length (vertical) [m]", labelWidth=300, valueType=float, orientation="horizontal")

        button_box = ShadowGui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Run Simulation", callback=self.run_simulation)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)

        button = gui.button(button_box, self, "Reset Fields", callback=self.callResetSettings)
        font = QFont(button.font())
        font.setItalic(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Red'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)
        button.setFixedWidth(100)

        gui.rubber(self.controlArea)

    def run_simulation(self):
        self.error(self.error_id)
        self.setStatusMessage("")
        self.progressBarInit()

        try:
            self.setStatusMessage("Running SRW")

            from time import sleep
            sleep(1)

            self.setStatusMessage("")

            self.send("Output", None)

        except Exception as exception:
            QtGui.QMessageBox.critical(self, "QMessageBox.critical()",
                                       str(exception),
                QtGui.QMessageBox.Ok)

            self.error_id = self.error_id + 1
            self.error(self.error_id, "Exception occurred: " + str(exception))

        self.progressBarFinished()

    def setLensIdealParameters(self, lens_ideal_parameters):
        if not lens_ideal_parameters is None:
            self.lens_ideal_parameters = lens_ideal_parameters

            beamline = self.lens_ideal_parameters._beamline
            component = self.lens_ideal_parameters._lens_ideal

            self.lens_position = beamline.position_of(component).z()
            self.focal_x       = self.lens_ideal_parameters._lens_ideal._focal_x
            self.focal_y       = self.lens_ideal_parameters._lens_ideal._focal_y

            self.left_box_1.setEnabled(False)
        else:
            self.left_box_1.setEnabled(True)

    def set_input(self, input):
        pass

    def callResetSettings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            try:
                self.resetSettings()
            except:
                pass
