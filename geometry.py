from dataclasses import dataclass
import numpy as np

from matutils import frustumMatrix, translationMatrix, rotationMatrixX, rotationMatrixY


WINDOW_SIZE = (800, 600)
P = frustumMatrix(l=-2.0, r=2.0, t=-1.5, b=1.5, n=1.5, f=20.0)


@dataclass
class Camera:
    center: np.ndarray = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    psi: float = 0.0
    phi: float = 0.0
    distance: float = 5.0

    def V(self):
        D = translationMatrix(-self.center)
        R = np.matmul(rotationMatrixX(self.psi), rotationMatrixY(self.phi))
        T = translationMatrix([0.0, 0.0, -self.distance])
        V = np.matmul(np.matmul(T, R), D)
        return V
