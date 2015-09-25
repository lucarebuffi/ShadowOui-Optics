from orangewidget import gui, widget
from orangewidget.widget import OWWidget
from orangewidget.settings import Setting
from PyQt4 import QtGui
from PyQt4.QtGui import QApplication, QPalette, QColor, QFont
from PyQt4.QtCore import QRect

from orangecontrib.shadow.util.shadow_util import ShadowGui, ConfirmDialog

from orangecontrib.optics.objects.optics_objects import ImagePlaneParameters

class ImagePlane(OWWidget):

    name = "SRW Image Plane"
    description = "SRW: Image Plane"
    icon = "icons/image_plane.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 2
    category = "Optical Elements"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Parameters", ImagePlaneParameters, "setImagePlaneParameters"),
              ("Input Wavefront", object, "set_input")]

    outputs = [{"name":"Output Wavefront",
                "type":object,
                "doc":"Output",
                "id":"output"}]

    image_plane_position = Setting(0.0)

    want_main_area=0

    MAX_WIDTH = 500
    MAX_HEIGHT = 200

    error_id = 0
    warning_id = 0
    info_id = 0

    image_plane_parameters = None

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

        ShadowGui.lineEdit(self.left_box_1, self, "image_plane_position", "Position on beamline", labelWidth=300, valueType=float, orientation="horizontal")

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

    def setImagePlaneParameters(self, image_plane_parameters):
        if not image_plane_parameters is None:
            self.image_plane_parameters = image_plane_parameters

            beamline = self.image_plane_parameters._beamline
            component = self.image_plane_parameters._image_plane

            self.image_plane_position = beamline.position_of(component).z()

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
