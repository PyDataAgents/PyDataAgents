from .PIDController import PIDController


class CascadedController:
    
    def __init__(self, dt):
        self.pos_pid = PIDController(20, 200, 0, dt)
        self.vel_pid = PIDController(20, 200, 0, dt)

    def compute(self, x_ref, x, v):
        vel_ref = self.pos_pid.compute(x_ref, x)
        iq_ref = self.vel_pid.compute(vel_ref, v)
        return iq_ref