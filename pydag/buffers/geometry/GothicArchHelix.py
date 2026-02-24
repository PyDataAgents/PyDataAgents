import numpy as np

class GothicArchHelix:
    """
    Generates a 3D mesh of a gothic arch swept along a helix,
    oriented correctly using the Frenet-Serret frame.
    """

    def __init__(
        self,
        pitch_diameter=6.0,
        pitch=0.5,
        ball_diameter=0.3,
        conformity=0.55,
        contact_angle=45,
        turns=3,
        res_arch=200,
        res_turn=300,
        use_bishop_frame=False,   # avoids twist if needed
        
    ):
        self.D_pw = pitch_diameter
        self.P = pitch
        self.D_w = ball_diameter
        self.f_r = conformity
        self.alpha = contact_angle
        self.turns = turns

        self.res_arch = res_arch
        self.res_turn = res_turn

        self.use_bishop = use_bishop_frame

    def ballscrew_gothic_profile(self, u):
        """
        Returns x,y coordinates of a ballscrew-style 2-circle gothic arch.

        Parameters
        ----------
        u : array-like in [0,1]
        ball_diameter : float
        conformity : float (typ 0.55–0.6)
        contact_angle_deg : float (typ 30°–45°)
        """

        # geometry
        Rg = self.f_r * self.D_w          # groove radius
        alpha = np.radians(self.alpha)

        # circle center offsets
        e = Rg * np.cos(alpha)
        h = Rg * np.sin(alpha)

        # param
        u = np.asarray(u)

        # split param into left / right halves
        x = np.zeros_like(u)
        y = np.zeros_like(u)

        left = u <= 0.5
        right = u > 0.5

        # angles for left circle: θ from (π + α) → (2π - α)
        theta_L = np.linspace(np.pi + alpha, 2*np.pi - alpha, left.sum())
        x[left]  = -e + Rg * np.cos(theta_L)
        y[left]  = -h + Rg * np.sin(theta_L)

        # angles for right circle: θ from (π - α) → α
        theta_R = np.linspace(np.pi - alpha, alpha, right.sum())
        x[right] = +e + Rg * np.cos(theta_R)
        y[right] = -h + Rg * np.sin(theta_R)

        return x, y

    # ----------------------------------------------------------------------
    #  Helix centerline
    # ----------------------------------------------------------------------
    def helix_center(self, t):
        D_pw = self.D_pw / 2
        P = self.P
        return np.stack([
            D_pw / 2 * np.cos(t),
            D_pw / 2 * np.sin(t),
            P * t
        ], axis=-1)

    # ----------------------------------------------------------------------
    #  Frenet-Serret frame
    # ----------------------------------------------------------------------
    def tangent(self, t):
        D_pw = self.D_pw / 2
        P = self.P
        Tx = -D_pw / 2 * np.sin(t)
        Ty =  D_pw / 2  * np.cos(t)
        Tz =  P * np.ones_like(t)
        T = np.stack([Tx, Ty, Tz], axis=-1)
        return T / np.linalg.norm(T, axis=-1)[..., None]

    def normal(self, t):
        Nx = -np.cos(t)
        Ny = -np.sin(t)
        Nz = np.zeros_like(t)
        N = np.stack([Nx, Ny, Nz], axis=-1)
        return N / np.linalg.norm(N, axis=-1)[..., None]

    def binormal(self, T, N):
        B = np.cross(T, N)
        return B / np.linalg.norm(B, axis=-1)[..., None]

    # ----------------------------------------------------------------------
    # Optional Bishop frame (minimizes twist)
    # ----------------------------------------------------------------------
    def bishop_frame(self, T):
        """
        Computes a Bishop frame (rotation-minimizing frame)
        from a tangent field T(t).
        """
        # Initial normal
        N0 = np.array([1.0, 0.0, 0.0])
        N = np.zeros_like(T)
        B = np.zeros_like(T)

        N[0] = N0
        B[0] = np.cross(T[0], N0)

        for i in range(1, len(T)):
            v = T[i] - T[i - 1]
            if np.linalg.norm(v) > 1e-9:
                axis = np.cross(T[i - 1], T[i])
                angle = np.arccos(np.clip(np.dot(T[i - 1], T[i]), -1, 1))
                if np.linalg.norm(axis) > 1e-9:
                    axis = axis / np.linalg.norm(axis)
                    N[i] = self.rotate_vector(N[i - 1], axis, angle)
                else:
                    N[i] = N[i - 1]
            else:
                N[i] = N[i - 1]

            B[i] = np.cross(T[i], N[i])

        return N, B

    @staticmethod
    def rotate_vector(v, axis, theta):
        """
        Rodrigues' rotation formula.
        """
        axis = axis / np.linalg.norm(axis)
        return (v * np.cos(theta)
                + np.cross(axis, v) * np.sin(theta)
                + axis * np.dot(axis, v) * (1 - np.cos(theta)))

    # ----------------------------------------------------------------------
    #  Build mesh
    # ----------------------------------------------------------------------
    def build_mesh(self):
        # parameters
        u = np.linspace(0, 1, self.res_arch)
        t = np.linspace(0, 2 * np.pi * self.turns, self.res_turn)

        U, Tparam = np.meshgrid(u, t)

        # arch local coords
        ax, ay = self.ballscrew_gothic_profile(U)

        # helix centerline positions
        center = self.helix_center(Tparam)

        # tangent vectors
        Tvec = self.tangent(Tparam)

        # orthonormal frame
        if self.use_bishop:
            Nvec, Bvec = self.bishop_frame(Tvec.reshape(-1, 3))
            Nvec = Nvec.reshape(center.shape)
            Bvec = Bvec.reshape(center.shape)
        else:
            Nvec = self.normal(Tparam)
            Bvec = self.binormal(Tvec, Nvec)

        # compute mesh coordinates
        X = center[..., 0] + ax * Nvec[..., 0] + ay * Bvec[..., 0]
        Y = center[..., 1] + ax * Nvec[..., 1] + ay * Bvec[..., 1]
        Z = center[..., 2] + ax * Nvec[..., 2] + ay * Bvec[..., 2]

        return X, Y, Z