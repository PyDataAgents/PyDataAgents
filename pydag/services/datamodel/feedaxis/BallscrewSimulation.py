import numpy as np

from .PMSMotor import PMSMotor
from .Inverter import Inverter
from .FOCController import FOCController
from .CascadedController import CascadedController
from .LuGreFriction import LuGreFriction
from .BallScrew import BallScrew
from .LoadMass import LoadMass
from .MotorThermal import MotorThermal


class BallScrewSimulation:

    def __init__(self, dt):
        self.dt = dt
        # Components
        self.motor = PMSMotor(R = 0.5, Ld = 0.001, Lq = 0.001, psi_f = 0.05, pole_pairs = 4)
        self.inverter = Inverter(300)
        self.friction = LuGreFriction(1e5, 10, 50, 100, 150, 0.01)
        self.screw = BallScrew(lead = 0.01, eta = 0.9)
        self.load = LoadMass(5)
        self.control = CascadedController(dt)
        self.foc = FOCController(dt)
        self.thermal = MotorThermal(C = 50, h = 5, T_amb = 25)
        # States
        self.i_d = 0
        self.i_q = 0
        self.omega = 0
        self.x = 0
        self.v = 0
        self.T_motor = 0
        # data logging
        self.data = {}

    def step(self, x_ref):
        # Position → velocity → iq_ref
        iq_ref = self.control.compute(x_ref, self.x, self.v)
        id_ref = 0

        # FOC
        vd_ref, vq_ref = self.foc.compute(id_ref, iq_ref, self.i_d, self.i_q)
        v_d, v_q = self.inverter.apply_voltage(vd_ref, vq_ref)

        # Electrical update
        di_d, di_q = self.motor.dynamics(self.i_d, self.i_q, v_d, v_q, self.omega)
        self.i_d += di_d * self.dt
        self.i_q += di_q * self.dt

        # Torque
        T_m = self.motor.torque(self.i_d, self.i_q)

        # Screw conversion
        F = self.screw.torque_to_force(T_m)

        # Friction
        F_f = self.friction.compute(self.v, self.dt)

        # Mechanics
        a = self.load.acceleration(F - F_f)
        self.v += a * self.dt
        self.x += self.v * self.dt

        # Motor speed (rigid coupling assumption)
        self.omega = (2 * np.pi / self.screw.lead) * self.v

        # Thermal
        self.T_motor = self.thermal.update(np.sqrt(self.i_d**2 + self.i_q**2), self.motor.R, self.dt)

        self.append_data("x", self.x)
        self.append_data("v", self.v)
        self.append_data("i_q", self.i_q)
        self.append_data("T_motor", self.T_motor)

    def append_data(self, key, value):
        if key not in self.data:
            self.data[key] = []
        self.data[key].append(value)