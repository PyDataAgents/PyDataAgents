from .PIDController import PIDController


class FOCController:
    
    def __init__(self, dt):
        self.i_d_pid = PIDController(5, 500, 0, dt)
        self.i_q_pid = PIDController(5, 500, 0, dt)

    def compute(self, i_d_ref, i_q_ref, i_d, i_q):
        vd = self.i_d_pid.compute(i_d_ref, i_d)
        vq = self.i_q_pid.compute(i_q_ref, i_q)
        return vd, vq