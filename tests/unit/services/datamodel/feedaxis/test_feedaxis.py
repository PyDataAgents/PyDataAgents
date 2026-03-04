from pydag.services.datamodel.feedaxis.BallscrewSimulation import BallscrewSimulation
import matplotlib.pyplot as plt
import numpy as np


def test_000():
    dt = 1e-5
    sim = BallscrewSimulation(dt)

    t_final = 2.0
    steps = int(t_final / dt)
    x_ref = 0.15

    for _ in range(steps):
        sim.step(x_ref)

    plt.figure(figsize=(12, 6))
    plt.subplot(2, 2, 1)
    plt.plot(sim.data["t"], sim.data["x"])
    plt.title("Position")
    plt.xlabel("Time [s]")
    plt.ylabel("Position [m]")
    plt.grid(True)

    plt.subplot(2, 2, 2)
    plt.plot(sim.data["t"], sim.data["x_err"])
    plt.title("Position Error")
    plt.xlabel("Time [s]")
    plt.ylabel("Position Error [m]")
    plt.grid(True)

    plt.subplot(2, 2, 3)
    plt.plot(sim.data["t"], sim.data["i_q"])
    plt.title("q-axis Current")
    plt.xlabel("Time [s]")
    plt.ylabel("Current [A]")
    plt.grid(True)
    plt.tight_layout()
    plt.show()