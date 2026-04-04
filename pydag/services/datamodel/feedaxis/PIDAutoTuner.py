import numpy as np
from scipy.optimize import minimize

from .BallscrewSimulation import BallscrewSimulation

class PIDAutoTuner:

    def __init__(self, sim_class : BallscrewSimulation, dt):
        self.sim_class = sim_class
        self.dt = dt

    def performance_cost(self, gains):

        kp, ki, kd = gains

        # Create new simulation instance
        sim = self.sim_class(self.dt)

        # Replace position PID gains
        sim.control.pos_pid.kp = kp
        sim.control.pos_pid.ki = ki
        sim.control.pos_pid.kd = kd

        x_ref = 0.05
        t_final = 0.1
        steps = int(t_final/self.dt)

        error_sum = 0
        overshoot = 0

        for _ in range(steps):
            sim.step(x_ref)
            x = sim.append_data["x"][-1]
            error = x_ref - x
            error_sum += error**2

            if x > x_ref:
                overshoot = max(overshoot, x - x_ref)

        # Settling time estimate
        final_error = abs(sim.append_data["x"][-1] - x_ref)

        cost = error_sum + 500*overshoot + 200*final_error

        return cost

    def tune(self, initial_guess=(100, 0, 10)):

        bounds = [(0,1000),(0,1000),(0,200)]

        result = minimize(
            self.performance_cost,
            initial_guess,
            bounds=bounds,
            method='L-BFGS-B'
        )

        return result.x