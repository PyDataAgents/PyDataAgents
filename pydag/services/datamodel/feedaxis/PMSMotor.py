class PMSMotor:
    def __init__(self, R, Ld, Lq, psi_f, pole_pairs):
        self.R = R
        self.Ld = Ld
        self.Lq = Lq
        self.psi_f = psi_f
        self.p = pole_pairs

    def dynamics(self, i_d, i_q, vd, vq, omega):
        did = (vd - self.R*i_d + omega*self.Lq*i_q) / self.Ld
        diq = (vq - self.R*i_q - omega*(self.Ld*i_d + self.psi_f)) / self.Lq
        return did, diq

    def torque(self, i_d, i_q):
        return 1.5 * self.p * (self.psi_f*i_q + (self.Ld-self.Lq)*i_d*i_q)