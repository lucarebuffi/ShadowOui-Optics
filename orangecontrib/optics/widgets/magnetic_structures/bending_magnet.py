import sys

from orangewidget import gui, widget
from orangewidget.widget import OWWidget
from orangewidget.settings import Setting
from PyQt4 import QtGui
from PyQt4.QtGui import QApplication, QPalette, QColor, QFont
from PyQt4.QtCore import QRect

from orangecontrib.shadow.util.shadow_util import ShadowGui, ConfirmDialog

from orangecontrib.optics.objects.optics_objects import BendingMagnetParameters, BeamlineParameters
import optics.magnetic_structures.bending_magnet as bm
import optics.beam.electron_beam as eb
import optics.beam.electron_beam_pencil as ebp

class BendingMagnet(OWWidget):

    name = "Bending Magnet"
    description = "Optics: Bending Magnet"
    icon = "icons/bending_magnet.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "Magnetic Structures"
    keywords = ["data", "file", "load", "read"]

    outputs = [{"name":"Source Parameters",
                "type":BendingMagnetParameters,
                "doc":"BendingMagnetParameters",
                "id":"paramters"},
               {"name":"Beamline Parameters",
                "type":BeamlineParameters,
                "doc":"BeamlineParameters",
                "id":"beamline_parameters"}]


    energy_in_GeV       = Setting(6.0)

    energy_spread       = Setting(0.89e-03)
    current             = Setting(0.2)
    electrons_per_bunch = Setting(500)

    kind_of_beam = Setting(0)

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


        left_box_1 = ShadowGui.widgetBox(self.controlArea, "Electron Beam", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(left_box_1, self, "energy_in_GeV", "Energy [GeV]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "energy_spread", "Energy spread (relative)", labelWidth=300, valueType=int, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "current", "Current (A)", labelWidth=300, valueType=float, orientation="horizontal")

        gui.comboBox(left_box_1, self, "kind_of_beam", label="Kind of Beam", items=["General", "Pencil"], labelWidth=300, orientation="horizontal", callback=self.set_kind_of_beam)

        self.left_box_2 = ShadowGui.widgetBox(left_box_1, "", addSpace=True, orientation="vertical", height=200)

        ShadowGui.lineEdit(self.left_box_2, self, "electrons_per_bunch", "Number of electrons per bunch", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_2, self, "moment_xx", "Moment (spatial^2, horizontal) [m^2]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_2, self, "moment_xxp", "Moment (spatial-angular, horizontal) [m]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_2, self, "moment_xpxp", "Moment (angular^2, horizontal)", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_2, self, "moment_yy", "Moment (spatial^2, vertical) [m^2]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_2, self, "moment_yyp", "Moment (spatial-angular, vertical) [m]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.left_box_2, self, "moment_ypyp", "Moment (angular^2, vertical)", labelWidth=300, valueType=float, orientation="horizontal")

        self.left_box_2_hidden = ShadowGui.widgetBox(left_box_1, "", addSpace=True, orientation="vertical", height=200)

        self.set_kind_of_beam()

        left_box_3 = ShadowGui.widgetBox(self.controlArea, "Bending Magnet Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(left_box_3, self, "radius", "Magnetic Radius [m]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_3, self, "magnetic_field", "Magnetic Field [T]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_3, self, "length", "Arc length [m]", labelWidth=300, valueType=float, orientation="horizontal")

        left_box_4 = ShadowGui.widgetBox(self.controlArea, "Simulation Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(left_box_4, self, "e_min", "Energy min [eV]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_4, self, "e_max", "Energy max [eV]", labelWidth=300, valueType=float, orientation="horizontal")

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

    def set_kind_of_beam(self):
        self.left_box_2.setVisible(self.kind_of_beam == 0)
        self.left_box_2_hidden.setVisible(self.kind_of_beam == 1)

    def send_data(self):
        self.error(self.error_id)
        self.setStatusMessage("")
        self.progressBarInit()

        try:
            self.check_fields()

            bending_magnet_parameters = self.populate_fields()

            self.progressBarSet(50)

            self.setStatusMessage("Running SHADOW")

            #self.information()
            self.setStatusMessage("")

            self.send("Beamline Parameters", BeamlineParameters(electron_beam=bending_magnet_parameters._electron_beam,
                                                                magnetic_structure=bending_magnet_parameters._bending_magnet,
                                                                beamline=None))
            self.send("Source Parameters", bending_magnet_parameters)

        except Exception as exception:
            QtGui.QMessageBox.critical(self, "QMessageBox.critical()",
                                       str(exception),
                QtGui.QMessageBox.Ok)

            self.error_id = self.error_id + 1
            self.error(self.error_id, "Exception occurred: " + str(exception))

        self.progressBarFinished()

    def check_fields(self):
        self.energy_in_GeV = ShadowGui.checkPositiveNumber(self.energy_in_GeV, "Energy")
        self.energy_spread = ShadowGui.checkPositiveNumber(self.energy_spread, "Energy Spread")
        self.current = ShadowGui.checkPositiveNumber(self.current, "Current")
        self.electrons_per_bunch = ShadowGui.checkPositiveNumber(self.electrons_per_bunch, "Number of electrons per bunch")

        if self.kind_of_beam == 0:
            self.moment_xx   = ShadowGui.checkPositiveNumber(self.moment_xx  , "Moment (spatial^2, horizontal)")
            self.moment_xxp  = ShadowGui.checkPositiveNumber(self.moment_xxp , "Moment (spatial-angular, horizontal)")
            self.moment_xpxp = ShadowGui.checkPositiveNumber(self.moment_xpxp, "Moment (angular^2, horizontal)")
            self.moment_yy   = ShadowGui.checkPositiveNumber(self.moment_yy  , "Moment (spatial^2, vertical)")
            self.moment_yyp  = ShadowGui.checkPositiveNumber(self.moment_yyp , "Moment (spatial-angular, vertical)")
            self.moment_ypyp = ShadowGui.checkPositiveNumber(self.moment_ypyp, "Moment (angular^2, vertical)")

        self.e_min = ShadowGui.checkPositiveNumber(self.e_min, "Minimum energy")
        self.e_max = ShadowGui.checkPositiveNumber(self.e_max, "Maximum energy")

        if self.e_min > self.e_max: raise Exception("Energy min should be <= Energy max")

    def populate_fields(self):
        if self.kind_of_beam == 0:
            electron_beam = eb.ElectronBeam(self.energy_in_GeV,
                                            self.energy_spread,
                                            self.current,
                                            self.electrons_per_bunch,
                                            self.moment_xx,
                                            self.moment_xxp,
                                            self.moment_xpxp,
                                            self.moment_yy,
                                            self.moment_yyp,
                                            self.moment_ypyp)
        else:
            electron_beam = ebp.ElectronBeamPencil(self.energy_in_GeV,
                                                   self.energy_spread,
                                                   self.current)

        bending_magnet = bm.BendingMagnet(self.radius, self.magnetic_field, self.length)

        return BendingMagnetParameters(electron_beam, bending_magnet, self.e_min, self.e_max)

    def callResetSettings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            try:
                self.resetSettings()
            except:
                pass
