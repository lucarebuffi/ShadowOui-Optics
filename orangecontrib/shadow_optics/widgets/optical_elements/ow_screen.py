import sys

from orangewidget import gui, widget
from orangewidget.settings import Setting
from PyQt4 import QtGui
from PyQt4.QtGui import QPalette, QColor, QFont

from orangecontrib.shadow.widgets.gui import ow_generic_element
from orangecontrib.shadow.util.shadow_objects import EmittingStream, TTYGrabber

from code_drivers.shadow.driver.shadow_driver import ShadowDriver
from code_drivers.shadow.driver.shadow_beam import ShadowBeam
from code_drivers.shadow.optical_elements.shadow_screen_slit import ShadowScreenSlit, ShadowScreenSlitSettings

from orangecontrib.shadow.util.shadow_util import ShadowGui
from orangecontrib.optics.objects.optics_objects import ImagePlaneParameters

class Screen(ow_generic_element.GenericElement):
    name = "Shadow Screen"
    description = "Shadow OE: Screen"
    icon = "icons/screen_2.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 2
    category = "OE"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Parameters", ImagePlaneParameters, "setImagePlaneParameters"),
              ("Input Beam", ShadowBeam, "setBeam")]

    outputs = [{"name": "Beam",
                "type": ShadowBeam,
                "doc": "Shadow Beam",
                "id": "beam"}]

    input_beam = None

    NONE_SPECIFIED = "NONE SPECIFIED"

    CONTROL_AREA_HEIGHT = 440
    CONTROL_AREA_WIDTH = 470

    source_plane_distance = Setting(0.0)
    image_plane_distance = Setting(0)

    focal_x = Setting(0.0)
    focal_y = Setting(0.0)

    want_main_area = 1

    driver = ShadowDriver()

    def __init__(self):
        super().__init__()

        self.runaction = widget.OWAction("Run Shadow/Trace", self)
        self.runaction.triggered.connect(self.traceOpticalElement)
        self.addAction(self.runaction)

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        tabs_setting = gui.tabWidget(self.controlArea)

        tab_bas = ShadowGui.createTabPage(tabs_setting, "Basic Setting")

        lens_box = ShadowGui.widgetBox(tab_bas, "Input Parameters", addSpace=False, orientation="vertical", height=600, width=450)

        self.le_source_plane_distance = ShadowGui.lineEdit(lens_box, self, "source_plane_distance", "Source Plane Distance [cm]", labelWidth=350, valueType=float, orientation="horizontal")
        self.le_image_plane_distance = ShadowGui.lineEdit(lens_box, self, "image_plane_distance", "Image Plane Distance [cm]", labelWidth=350, valueType=float, orientation="horizontal")

        gui.separator(self.controlArea)

        button_box = ShadowGui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Run Shadow/trace", callback=self.traceOpticalElement)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette())  # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette)  # assign new palette
        button.setFixedHeight(45)

        button = gui.button(button_box, self, "Reset Fields", callback=self.callResetSettings)
        font = QFont(button.font())
        font.setItalic(True)
        button.setFont(font)
        palette = QPalette(button.palette())  # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Red'))
        button.setPalette(palette)  # assign new palette
        button.setFixedHeight(45)
        button.setFixedWidth(100)

    def callResetSettings(self):
        super().callResetSettings()

    ############################################################
    #
    # GRAPHIC USER INTERFACE MANAGEMENT
    #
    ############################################################

    def populateFields(self):

        if self.image_plane_parameters is None:
            raise NotImplementedError("Widget to be plugged to Optic Package!")
        else:
            settings = self.image_plane_parameters._image_plane.settings(self.driver)

            settings._source_plane_distance = self.source_plane_distance
            settings._image_plane_distance = self.image_plane_distance

            return ShadowScreenSlit(image_plane=self.image_plane_parameters._image_plane)

    def doSpecificSetting(self, shadow_oe):
        pass

    def checkFields(self):
        ShadowGui.checkPositiveNumber(self.source_plane_distance, "Distance from Source")
        ShadowGui.checkPositiveNumber(self.image_plane_distance, "Image Plane Distance")

    def completeOperations(self, shadow_oe=None):
        self.setStatusMessage("Running SHADOW")

        if self.trace_shadow:
            grabber = TTYGrabber()
            grabber.start()

        self.progressBarSet(50)

        ###########################################
        # TODO: TO BE ADDED JUST IN CASE OF BROKEN
        #       ENVIRONMENT: MUST BE FOUND A PROPER WAY
        #       TO TEST SHADOW
        self.fixWeirdShadowBug()
        ###########################################

        shadow_oe._oe.write("ziotreno.00")

        beam_out = ShadowBeam.traceFromOE(shadow_oe, self.input_beam)

        if self.trace_shadow:
            grabber.stop()

            for row in grabber.ttyData:
                self.writeStdOut(row)

        self.setStatusMessage("Plotting Results")

        self.plot_results(beam_out)

        self.setStatusMessage("")

        self.send("Beam", beam_out)

    def traceOpticalElement(self):
        try:
            self.error(self.error_id)
            self.setStatusMessage("")
            self.progressBarInit()

            if ShadowGui.checkEmptyBeam(self.input_beam):
                if ShadowGui.checkGoodBeam(self.input_beam):
                    sys.stdout = EmittingStream(textWritten=self.writeStdOut)

                    self.checkFields()

                    shadow_oe = self.populateFields()

                    self.doSpecificSetting(shadow_oe)

                    self.progressBarSet(10)

                    self.completeOperations(shadow_oe)
                else:
                    raise Exception("Input Beam with no good rays")
            else:
                raise Exception("Empty Input Beam")

        except Exception as exception:
            QtGui.QMessageBox.critical(self, "QMessageBox.critical()",
                                       str(exception),
                                       QtGui.QMessageBox.Ok)

            self.error_id = self.error_id + 1
            self.error(self.error_id, "Exception occurred: " + str(exception))

        self.progressBarFinished()

    def setBeam(self, beam):
        self.onReceivingInput()

        if ShadowGui.checkEmptyBeam(beam):
            self.input_beam = beam

            if self.is_automatic_run:
                self.traceOpticalElement()

    def setImagePlaneParameters(self, image_plane_parameters):
        if not image_plane_parameters is None:
            self.image_plane_parameters = image_plane_parameters

            if not self.image_plane_parameters._image_plane.has_settings(self.driver):
                self.image_plane_parameters._image_plane.add_settings(ShadowScreenSlitSettings())

            beamline = self.image_plane_parameters._beamline
            component = self.image_plane_parameters._image_plane

            position = beamline.position_of(component).z()

            previous_component = beamline.previous_component(component)
            next_component = beamline.next_component(component)

            if previous_component is None:
                position_previous_component = 0.0
            else:
                position_previous_component = beamline.position_of(previous_component).z()

            if next_component is None:
                position_next_component = 0.0
            else:
                position_next_component = beamline.position_of(next_component).z()

            if position_next_component > position:
                q = 100*(position_next_component - position)
            else:
                q = 0.0

            p = 100*(position - position_previous_component)


            self.source_plane_distance = p
            self.image_plane_distance = q

            self.le_source_plane_distance.setEnabled(False)
            self.le_image_plane_distance.setEnabled(False)
        else:
            if not self.image_plane_parameters is None:
                self.image_plane_parameters._image_plane.remove_settings(self.driver)
                self.image_plane_parameters = None

            self.le_source_plane_distance.setEnabled(True)
            self.le_image_plane_distance.setEnabled(True)
