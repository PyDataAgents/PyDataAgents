import numpy as np


class LuGreFriction:
    
    def __init__(self, sigma_0, sigma_1, sigma_2, F_c, F_s, v_s):
        self.sigma_0 = sigma_0
        self.sigma_1 = sigma_1
        self.sigma_2 = sigma_2
        self.F_c = F_c
        self.F_s = F_s
        self.v_s = v_s
        self.z = 0

    def g(self, v):
        return self.F_c + (self.F_s - self.F_c) * np.exp(-(v / self.v_s)**2)

    def compute(self, v, dt):
        dz = v - abs(v) / self.g(v) * self.z
        self.z += dz * dt
        F = self.sigma_0 * self.z + self.sigma_1 * dz + self.sigma_2 * v
        return F
