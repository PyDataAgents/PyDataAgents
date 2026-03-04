import numpy as np


class Inverter:
    
    def __init__(self, V_dc):
        self.V_dc = V_dc

    def apply_voltage(self, v_d_ref, v_q_ref):
        v_d = np.clip(v_d_ref, -self.V_dc, self.V_dc)
        v_q = np.clip(v_q_ref, -self.V_dc, self.V_dc)
        return v_d, v_q