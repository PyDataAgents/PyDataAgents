import numpy as np


class BallScrew:
    def __init__(self, lead, eta):
        self.lead = lead
        self.eta = eta

    def torque_to_force(self, T):
        return (2*np.pi*self.eta/self.lead)*T

    def force_to_torque(self, F):
        return (self.lead/(2*np.pi*self.eta))*F