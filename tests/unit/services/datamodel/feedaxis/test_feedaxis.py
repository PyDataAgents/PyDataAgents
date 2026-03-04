from pydag.services.datamodel.feedaxis.BallscrewSimulation import BallScrewSimulation
import matplotlib.pyplot as plt
import numpy as np


def test_000():
    dt = 1e-5
    sim = BallScrewSimulation(dt)

    t_final = 0.2
    steps = int(t_final / dt)
    x_ref = 0.15

    for _ in range(steps):
        sim.step(x_ref)

    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(sim.data["x"])
    plt.title("Position")

    plt.subplot(2, 1, 2)
    plt.plot(sim.data["i_q"])
    plt.title("q-axis Current")
    plt.tight_layout()
    plt.show()