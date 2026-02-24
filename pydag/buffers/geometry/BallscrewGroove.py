from typing import Tuple
import numpy as np


from .Helix import Helix
from .D3Geometry import D3Geometry


class BallscrewGroove(D3Geometry):
    
    def __init__(self,
                 D_pw : float = 40.0,
                 P : float = 10.0,
                 D_w : float = 6.0,
                 alpha : float = 45,
                 f_r : float = 0.55,
                 s : float = 1.0,
                 i : float = 1.0,
                 right_or_left : bool = True,
                 nut_or_spindle : bool = True
                 ):
        self.D_pw = D_pw
        self.P = P
        self.D_w = D_w
        self.alpha = alpha
        self.f_r = f_r
        self.s = s
        self.i = i
        self.right_or_left = right_or_left
        self.nut_or_spindle = nut_or_spindle
        
    def create(self, resolution_1 : int = 100, resolution_2 : int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        u = np.linspace(0, 1, resolution_1)
        t = np.linspace(0, 2 * np.pi * self.i, resolution_2)
                
        # local profile coordinates
        px, py = self._ballscrew_profile(resolution_1)
                
        # helix coordinates
        h = Helix(d = self.D_pw, P = self.P, i = self.i)
        hx, hy, hz = h.create(resolution_2)
        H = np.stack([hx, hy, hz], axis=-1)
                
        N, B, _ = self._bishop_frame(t)
        
        X = H[:, 0, None] + px[None, :]*N[:, 0, None] + py[None, :]*B[:, 0, None]
        Y = H[:, 1, None] + px[None, :]*N[:, 1, None] + py[None, :]*B[:, 1, None]
        Z = H[:, 2, None] + px[None, :]*N[:, 2, None] + py[None, :]*B[:, 2, None]
        
        return X, Y, Z        
        
    def _ballscrew_profile(self, resolution):
        r = self.D_w * self.f_r
        a_m_x = (r - self.D_w / 2) * np.cos(np.radians(self.alpha))
        a_m_y = (r - self.D_w /2) * np.sin(np.radians(self.alpha))
        theta_1 = np.arcsin((self.s / 2 + a_m_y) / r)
        theta_2 = np.arccos(a_m_x / r)
        theta = np.linspace(theta_1, theta_2, resolution)
        x = -a_m_x + r * np.cos(theta)
        y = -a_m_y + r * np.sin(theta)
        if self.right_or_left is False:
            x = -x
        if self.nut_or_spindle is False:
            y = -y
        return x, y
            
    def _helix_tangent(self, t):
        #Tx = -self.D_pw / 2 * np.sin(t)
        #Ty = -self.D_pw / 2 * np.cos(t)
        #Tz = self.P * np.ones_like(t)
        #T = np.stack([Tx, Ty, Tz], axis=-1)
        #return T / np.linalg.norm(T, axis=-1)[..., None]
        dtheta = 2*np.pi*self.i

        Tx = -self.D_pw/2*np.sin(t)*dtheta
        Ty =  self.D_pw/2*np.cos(t)*dtheta
        Tz =  np.full_like(Tx, self.P*self.i)

        T = np.stack([Tx, Ty, Tz], axis=-1)
        T /= np.linalg.norm(T, axis=-1, keepdims=True)
        return T
    
    def _bishop_frame(self, t):
        T = self._helix_tangent(t)
        n = T.shape[0]

        # reference vector not parallel to T
        ref = np.array([0.0, 0.0, 1.0])
        dot = T @ ref
        alt = np.tile(ref, (n, 1))
        alt[np.abs(dot) > 0.8] = np.array([1.0, 0.0, 0.0])

        N = alt - np.sum(alt*T, axis=1, keepdims=True)*T
        N /= np.linalg.norm(N, axis=-1, keepdims=True)

        B = np.cross(T, N)
        return N, B, T