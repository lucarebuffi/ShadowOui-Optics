import sys

from orangewidget import gui, widget
from orangewidget.widget import OWWidget
from orangewidget.settings import Setting
from PyQt4 import QtGui
from PyQt4.QtGui import QApplication, QPalette, QColor, QFont
from PyQt4.QtCore import QRect

from orangecontrib.shadow.util.shadow_util import ShadowGui, ConfirmDialog

from orangecontrib.optics.objects.optics_objects import BendingMagnetParameters, BeamlineParameters
from optics.beamline.beamline import Beamline
import optics.magnetic_structures.bending_magnet as bm
import optics.beam.electron_beam as eb
import optics.beam.electron_beam_pencil as ebp

class BendingMagnet(OWWidget):

    name = "Bending Magnet"
    description = "SRW: Bending Magnet"
    icon = "icons/bending_magnet.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "Magnetic Structures"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Parameters", BendingMagnetParameters, "setBendingMagnetParameters")]

    outputs = [{"name":"Output",
                "type":object,
                "doc":"Output",
                "id":"output"}]


    energy_in_GeV       = Setting(6.0)

    energy_spread       = Setting(0.89e-03)
    current             = Setting(0.2)
    electrons_per_bunch = Setting(500)

    kind_of_beam        = Setting(0)

    moment_xx           = Setting((77.9e-06)**2)
    moment_xxp          = Setting(0.0)
    moment_xpxp         = Setting((110.9e-06)**2)
    moment_yy           = Setting((12.9e-06)**2)
    moment_yyp          = Setting(0.0)
    moment_ypyp         = Setting((0.5e-06)**2)

    radius=Setting(23.2655)
    magnetic_field=Setting(0.86)
    length=Setting(0.5)

    e_min = Setting(0.0)
    e_max = Setting(100000.0)

    want_main_area=0

    MAX_WIDTH = 500
    MAX_HEIGHT = 700

    error_id = 0
    warning_id = 0
    info_id = 0

    bending_magnet_parameters = None

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


        self.left_box_1 = ShadowGui.widgetBox(self.controlArea, "Electron Beam", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(self.left_box_1, self, "energy_in_GeV", "Energy [GeV]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_1, self, "energy_spread", "Energy spread (relative)", labelWidth=300, valueType=int, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_1, self, "current", "Current (A)", labelWidth=300, valueType=float, orientation="horizontal")

        gui.comboBox(self.left_box_1, self, "kind_of_beam", label="Kind of Beam", items=["General", "Pencil"], labelWidth=300, orientation="horizontal", callback=self.set_kind_of_beam)

        self.left_box_2 = ShadowGui.widgetBox(self.left_box_1, "", addSpace=True, orientation="vertical", height=200)

        ShadowGui.lineEdit(self.left_box_2, self, "electrons_per_bunch", "Number of electrons per bunch", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_2, self, "moment_xx", "Moment (spatial^2, horizontal) [m^2]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_2, self, "moment_xxp", "Moment (spatial-angular, horizontal) [m]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_2, self, "moment_xpxp", "Moment (angular^2, horizontal)", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_2, self, "moment_yy", "Moment (spatial^2, vertical) [m^2]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_2, self, "moment_yyp", "Moment (spatial-angular, vertical) [m]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_2, self, "moment_ypyp", "Moment (angular^2, vertical)", labelWidth=300, valueType=float, orientation="horizontal")

        self.left_box_2_hidden = ShadowGui.widgetBox(self.left_box_1, "", addSpace=True, orientation="vertical", height=200)

        self.set_kind_of_beam()

        self.left_box_3 = ShadowGui.widgetBox(self.controlArea, "Bending Magnet Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(self.left_box_3, self, "radius", "Magnetic Radius [m]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_3, self, "magnetic_field", "Magnetic Field [T]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_3, self, "length", "Arc length [m]", labelWidth=300, valueType=float, orientation="horizontal")

        self.left_box_4 = ShadowGui.widgetBox(self.controlArea, "Simulation Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(self.left_box_4, self, "e_min", "Energy min [eV]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_4, self, "e_max", "Energy max [eV]", labelWidth=300, valueType=float, orientation="horizontal")

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

    def set_kind_of_beam(self):
        self.left_box_2.setVisible(self.kind_of_beam == 0)
        self.left_box_2_hidden.setVisible(self.kind_of_beam == 1)

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

    def setBendingMagnetParameters(self, bending_magnet_parameters):
        if not bending_magnet_parameters is None:
            self.bending_magnet_parameters = bending_magnet_parameters

            self.energy_in_GeV       = self.bending_magnet_parameters._electron_beam._energy_in_GeV
            self.energy_spread       = self.bending_magnet_parameters._electron_beam._energy_spread
            self.current             = self.bending_magnet_parameters._electron_beam._current
            self.electrons_per_bunch = self.bending_magnet_parameters._electron_beam._electrons_per_bunch
            self.moment_xx           = self.bending_magnet_parameters._electron_beam._moment_xx
            self.moment_xxp          = self.bending_magnet_parameters._electron_beam._moment_xxp
            self.moment_xpxp         = self.bending_magnet_parameters._electron_beam._moment_xpxp
            self.moment_yy           = self.bending_magnet_parameters._electron_beam._moment_yy
            self.moment_yyp          = self.bending_magnet_parameters._electron_beam._moment_yyp
            self.moment_ypyp         = self.bending_magnet_parameters._electron_beam._moment_ypyp


            if isinstance(self.bending_magnet_parameters._electron_beam, ebp.ElectronBeamPencil):
                self.kind_of_beam = 1
            else:
                self.kind_of_beam = 0

            self.set_kind_of_beam()

            self.radius         = self.bending_magnet_parameters._bending_magnet._radius
            self.magnetic_field = self.bending_magnet_parameters._bending_magnet._magnetic_field
            self.length         = self.bending_magnet_parameters._bending_magnet._length

            self.e_min = self.bending_magnet_parameters._energy_min
            self.e_max = self.bending_magnet_parameters._energy_max

            self.left_box_1.setEnabled(False)
            self.left_box_3.setEnabled(False)
            self.left_box_4.setEnabled(False)
        else:
            self.left_box_1.setEnabled(True)
            self.left_box_3.setEnabled(True)
            self.left_box_4.setEnabled(True)

    def callResetSettings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            try:
                self.resetSettings()
            except:
                pass
