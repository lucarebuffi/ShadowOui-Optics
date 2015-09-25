import sys

from orangewidget import gui, widget
from orangewidget.widget import OWWidget
from orangewidget.settings import Setting
from PyQt4 import QtGui
from PyQt4.QtGui import QApplication, QPalette, QColor, QFont
from PyQt4.QtCore import QRect

from orangecontrib.shadow.util.shadow_util import ShadowGui, ConfirmDialog

from orangecontrib.optics.objects.optics_objects import ImagePlaneParameters, BeamlineParameters

import optics.beamline.optical_elements.image_plane as ip
from optics.beamline.beamline import Beamline
from optics.beamline.beamline_position import BeamlinePosition

class ImagePlane(OWWidget):

    name = "Image Plane"
    description = "Optics: Image Plane"
    icon = "icons/image_plane.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 2
    category = "Optical Elements"
    keywords = ["data", "file", "load", "read"]


    inputs = [("Parameters", BeamlineParameters, "set_beamline")]

    outputs = [{"name":"Image Plane Parameters",
                "type":ImagePlaneParameters,
                "doc":"ImagePlaneParameters",
                "id":"parameters"},
               {"name":"Beamline Parameters",
                "type":BeamlineParameters,
                "doc":"BeamlineParameters",
                "id":"beamline_parameters"}]

    image_plane_name = Setting("Unnamed")
    image_plane_position = Setting(0.0)

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


        left_box_1 = ShadowGui.widgetBox(self.controlArea, "Image Plane Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(left_box_1, self, "image_plane_name", "Image Plane Name", labelWidth=200, valueType=str, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "image_plane_position", "Position on beamline", labelWidth=300, valueType=float, orientation="horizontal")

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

            image_plane_parameters = self.populate_fields()

            self.progressBarSet(50)

            self.setStatusMessage("")

            if not self.beamline_parameters is None:
                self.send("Beamline Parameters", BeamlineParameters(electron_beam=self.beamline_parameters._electron_beam,
                                                                    magnetic_structure=self.beamline_parameters._magnetic_structure,
                                                                    beamline=image_plane_parameters._beamline,
                                                                    energy_min=self.beamline_parameters._energy_min,
                                                                    energy_max=self.beamline_parameters._energy_max))
            else:
                self.send("Beamline Parameters", BeamlineParameters(electron_beam=None,
                                                                    magnetic_structure=None,
                                                                    beamline=image_plane_parameters._beamline))

            self.send("Image Plane Parameters", image_plane_parameters)

        except Exception as exception:
            QtGui.QMessageBox.critical(self, "QMessageBox.critical()",
                                       str(exception),
                QtGui.QMessageBox.Ok)

            self.error_id = self.error_id + 1
            self.error(self.error_id, "Exception occurred: " + str(exception))

        self.progressBarFinished()

    def check_fields(self):
        self.image_plane_name = ShadowGui.checkEmptyString(self.image_plane_name, "Image Plane Name")
        self.image_plane_position = ShadowGui.checkPositiveNumber(self.image_plane_position, "Image Plane Position")


    def populate_fields(self):
        image_plane = ip.ImagePlane(self.image_plane_name)

        beamline = Beamline()

        if not self.beamline_parameters is None:
            if not self.beamline_parameters._beamline is None:
                for component in self.beamline_parameters._beamline:
                    beamline.attach_component_at(component, self.beamline_parameters._beamline.position_of(component))

        beamline.attach_component_at(image_plane, BeamlinePosition(self.image_plane_position))

        if not self.beamline_parameters is None:
            return ImagePlaneParameters(beamline=beamline,
                                        image_plane=image_plane,
                                        energy_min=self.beamline_parameters._energy_min,
                                        energy_max=self.beamline_parameters._energy_max)
        else:
            return ImagePlaneParameters(beamline=beamline,
                                        image_plane=image_plane)

    def callResetSettings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            try:
                self.resetSettings()
            except:
                pass
