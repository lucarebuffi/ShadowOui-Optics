__author__ = 'labx'

from optics.magnetic_structures.bending_magnet import BendingMagnet
from optics.beam.electron_beam import ElectronBeam

class BendingMagnetParameters(object):
    def __init__(self,
                 electron_beam=ElectronBeam(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                 bending_magnet=BendingMagnet(0.0, 0.0, 0.0)):
        self.electron_beam=electron_beam
        self.bending_magnet=bending_magnet