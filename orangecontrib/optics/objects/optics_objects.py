__author__ = 'labx'

from optics.magnetic_structures.bending_magnet import BendingMagnet
from optics.beam.electron_beam import ElectronBeam
from optics.beamline.optical_elements.lens.lens_ideal import LensIdeal
from optics.beamline.optical_elements.image_plane import ImagePlane
from optics.beamline.beamline import Beamline

class BeamlineParameters(object):
    def __init__(self,
                 electron_beam=None,
                 magnetic_structure=None,
                 beamline=Beamline(),
                 energy_min=0.0,
                 energy_max=100000.0):
        self._electron_beam=electron_beam
        self._magnetic_structure=magnetic_structure
        self._beamline=beamline
        self._energy_min=energy_min
        self._energy_max=energy_max

class BendingMagnetParameters(object):
    def __init__(self,
                 electron_beam=ElectronBeam(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                 bending_magnet=BendingMagnet(0.0, 0.0, 0.0),
                 energy_min=0.0,
                 energy_max=100000.0):
        self._electron_beam=electron_beam
        self._bending_magnet=bending_magnet
        self._energy_min=energy_min
        self._energy_max=energy_max

class OpticElementParameters(object):
    def __init__(self, beamline=Beamline(),
                 energy_min=0.0,
                 energy_max=100000.0):
        self._beamline=beamline
        self._energy_min=energy_min
        self._energy_max=energy_max

class ImagePlaneParameters(OpticElementParameters):
    def __init__(self, beamline=Beamline(),
                 energy_min=0.0,
                 energy_max=100000.0,
                 image_plane=ImagePlane("image plane")):
        super().__init__(beamline=beamline, energy_min=energy_min, energy_max=energy_max)
        self._image_plane = image_plane

class LensIdealParameters(OpticElementParameters):
    def __init__(self, beamline=Beamline(),
                 energy_min=0.0,
                 energy_max=100000.0,
                 lens_ideal=LensIdeal("lens", 0.0, 0.0)):
        super().__init__(beamline=beamline, energy_min=energy_min, energy_max=energy_max)
        self._lens_ideal = lens_ideal
