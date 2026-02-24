import numpy as np


class BallscrewGothicHelix:
    """
    Correct Variant A Gothic Arch Sweep (FULL PROFILE)
    """

    def __init__(self,
                 groove_pitch_diameter,
                 pitch,
                 contact_angle_deg,
                 ball_diameter,
                 conformity,
                 turns,
                 ):

        self.Rh = groove_pitch_diameter / 2
        self.pitch = pitch
        self.turns = turns

        self.alpha = np.radians(contact_angle_deg)

        self.Rb = ball_diameter / 2
        self.Rg = conformity * self.Rb  # groove-arc radius

    # -------------------------------
    # Helix geometry
    # -------------------------------
    def helix(self, t):
        theta = 2*np.pi*self.turns*t
        x = self.Rh*np.cos(theta)
        y = self.Rh*np.sin(theta)
        z = self.pitch*self.turns*t
        return np.stack([x, y, z], axis=-1)

    def tangent(self, t):
        theta = 2*np.pi*self.turns*t
        dtheta = 2*np.pi*self.turns

        Tx = -self.Rh*np.sin(theta)*dtheta
        Ty =  self.Rh*np.cos(theta)*dtheta
        Tz =  np.full_like(Tx, self.pitch*self.turns)

        T = np.stack([Tx, Ty, Tz], axis=-1)
        T /= np.linalg.norm(T, axis=-1, keepdims=True)
        return T

    def bishop_frame(self, t):
        T = self.tangent(t)
        n = T.shape[0]

        # reference vector not parallel to T
        ref = np.array([0.0, 0.0, 1.0])
        dot = T @ ref
        alt = np.tile(ref, (n, 1))
        alt[np.abs(dot) > 0.8] = np.array([1.0, 0.0, 0.0])

        N = alt - np.sum(alt*T, axis=1, keepdims=True)*T
        N /= np.linalg.norm(N, axis=-1, keepdims=True)

        B = np.cross(T, N)
        return N, B, T

    # -------------------------------
    # Correct Gothic Variant A profile
    # -------------------------------
    def gothic_profile(self, n=200):
        R = self.Rg
        α = self.alpha

        # correct geometry:
        # centers are left/right IN PROFILE PLANE
        cx = R*np.sin(α)
        cy = R*np.cos(α)

        th = np.linspace(α, np.pi - α, n)

        # Left arc
        xL = -cx + R*np.cos(th)
        yL = -cy + R*np.sin(th)

        # Right arc
        xR =  cx - R*np.cos(th)
        yR = -cy + R*np.sin(th)

        x = np.concatenate([xL, xR])
        y = np.concatenate([yL, yR])

        return x, y

    # -------------------------------
    # Sweep into full 3D groove
    # -------------------------------
    def mesh(self, n_t=200, n_p=200):

        t = np.linspace(0, 1, n_t)
        C = self.helix(t)
        N, B, _ = self.bishop_frame(t)

        xp, yp = self.gothic_profile(n_p)

        X = C[:, 0, None] + xp[None, :]*N[:, 0, None] + yp[None, :]*B[:, 0, None]
        Y = C[:, 1, None] + xp[None, :]*N[:, 1, None] + yp[None, :]*B[:, 1, None]
        Z = C[:, 2, None] + xp[None, :]*N[:, 2, None] + yp[None, :]*B[:, 2, None]

        return X, Y, Z
