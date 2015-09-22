import sys

from orangewidget import gui, widget
from orangewidget.widget import OWWidget
from orangewidget.settings import Setting
from PyQt4 import QtGui
from PyQt4.QtGui import QApplication, QPalette, QColor, QFont
from PyQt4.QtCore import QRect

from orangecontrib.shadow.util.shadow_util import ShadowGui, ConfirmDialog

from orangecontrib.optics.objects.optics_objects import LensIdealParameters, BeamlineParameters

import optics.beamline.optical_elements.lens.lens_ideal as li
from optics.beamline.beamline import Beamline
from optics.beamline.beamline_position import BeamlinePosition

class LensIdeal(OWWidget):

    name = "Lens Ideal"
    description = "Optics: Lens Ideal"
    icon = "icons/lens.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "Optical Elements"
    keywords = ["data", "file", "load", "read"]


    inputs = [("Parameters", BeamlineParameters, "set_beamline")]

    outputs = [{"name":"Lens Parameters",
                "type":LensIdealParameters,
                "doc":"LensIdealParameters",
                "id":"parameters"},
               {"name":"Beamline Parameters",
                "type":BeamlineParameters,
                "doc":"BeamlineParameters",
                "id":"beamline_parameters"}]


    lens_name       = Setting("Unnamed")

    lens_position = Setting(0.0)

    focal_x       = Setting(0.0)
    focal_y       = Setting(0.0)

    want_main_area=0

    MAX_WIDTH = 500
    MAX_HEIGHT = 200

    error_id = 0
    warning_id = 0
    info_id = 0

    beamline_parameters = None

    def __init__(self):
        super().__init__()

        self.runaction = widget.OWAction("Send Data to Simulators", self)
        self.runaction.triggered.connect(self.send_data)
        self.addAction(self.runaction)

        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width()*0.05),
                               round(geom.height()*0.05),
                               round(min(geom.width()*0.5, self.MAX_WIDTH)),
                               round(min(geom.height()*0.5, self.MAX_HEIGHT))))


        left_box_1 = ShadowGui.widgetBox(self.controlArea, "Lens Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(left_box_1, self, "lens_name", "Lens Name", labelWidth=200, valueType=str, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "lens_position", "Position on beamline", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "focal_x", "Focal length (horizontal) [m]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "focal_y", "Focal length (vertical) [m]", labelWidth=300, valueType=float, orientation="horizontal")

        button_box = ShadowGui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Send Data to Simulators", callback=self.send_data)
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

    def set_beamline(self, beamline_parameters):
            self.beamline_parameters = beamline_parameters
            self.send_data()

    def send_data(self):
        self.error(self.error_id)
        self.setStatusMessage("")
        self.progressBarInit()

        try:
            self.check_fields()

            lens_ideal_parameters = self.populate_fields()

            self.progressBarSet(50)

            self.setStatusMessage("")

            if not self.beamline_parameters is None:
                self.send("Beamline Parameters", BeamlineParameters(electron_beam=self.beamline_parameters._electron_beam,
                                                                    magnetic_structure=self.beamline_parameters._magnetic_structure,
                                                                    beamline=lens_ideal_parameters._beamline,
                                                                    energy_min=self.beamline_parameters._energy_min,
                                                                    energy_max=self.beamline_parameters._energy_max))
            else:
                self.send("Beamline Parameters", BeamlineParameters(electron_beam=None,
                                                                    magnetic_structure=None,
                                                                    beamline=lens_ideal_parameters._beamline))

            self.send("Lens Parameters", lens_ideal_parameters)

        except Exception as exception:
            QtGui.QMessageBox.critical(self, "QMessageBox.critical()",
                                       str(exception),
                QtGui.QMessageBox.Ok)

            self.error_id = self.error_id + 1
            self.error(self.error_id, "Exception occurred: " + str(exception))

        self.progressBarFinished()

    def check_fields(self):
        self.lens_name = ShadowGui.checkEmptyString(self.lens_name, "Lens Name")
        self.lens_position = ShadowGui.checkPositiveNumber(self.lens_position, "Lens Position")
        self.focal_x = ShadowGui.checkPositiveNumber(self.focal_x, "Focal length (horizontal)")
        self.focal_y = ShadowGui.checkPositiveNumber(self.focal_y, "Focal length (vertical)")


    def populate_fields(self):
        lens_ideal = li.LensIdeal(self.lens_name, self.focal_x, self.focal_y)

        beamline = Beamline()

        if not self.beamline_parameters is None:
            if not self.beamline_parameters._beamline is None:
                for component in self.beamline_parameters._beamline:
                    beamline.attach_component_at(component, self.beamline_parameters._beamline.position_of(component))

        beamline.attach_component_at(lens_ideal, BeamlinePosition(self.lens_position))

        if not self.beamline_parameters is None:
            return LensIdealParameters(beamline=beamline,
                                       energy_min=self.beamline_parameters._energy_min,
                                       energy_max=self.beamline_parameters._energy_max,
                                       lens_ideal=lens_ideal)
        else:
            return LensIdealParameters(beamline=beamline,
                                       lens_ideal=lens_ideal)

    def callResetSettings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            try:
                self.resetSettings()
            except:
                pass
