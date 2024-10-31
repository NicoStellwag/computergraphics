from dataclasses import dataclass
import numpy as np
from typing import List

from matutils import frustumMatrix, translationMatrix, rotationMatrixX, rotationMatrixY


WINDOW_SIZE = (800, 600)
P = frustumMatrix(l=-1.0, r=1.0, t=-1.0, b=1.0, n=1.5, f=20.0)


@dataclass
class Camera:
    center: np.ndarray = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    psi: float = 0.0
    phi: float = 0.0
    distance: float = 5.0

    def V(self):
        D = translationMatrix(-np.array(self.center))
        R = rotationMatrixX(self.psi) @ rotationMatrixY(self.phi)
        T = translationMatrix([0.0, 0.0, -self.distance])
        V = T @ R @ D
        return V
