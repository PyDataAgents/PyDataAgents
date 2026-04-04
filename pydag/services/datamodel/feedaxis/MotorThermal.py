class MotorThermal:
    
    def __init__(self, C, h, T_amb):
        self.C = C
        self.h = h
        self.T = T_amb
        self.T_amb = T_amb

    def update(self, I, R, dt):
        dT = (I**2 * R - self.h*(self.T - self.T_amb)) / self.C
        self.T += dT * dt
        return self.T