class PIDController:
    
    def __init__(self, k_p, k_i, k_d, dt):
        self.k_p = k_p
        self.k_i = k_i
        self.k_d = k_d
        self.dt = dt
        self.integral = 0
        self.prev_error = 0

    def compute(self, ref, feedback):
        error = ref - feedback
        self.integral += error*self.dt
        derivative = (error - self.prev_error)/self.dt
        self.prev_error = error
        return self.k_p*error + self.k_i*self.integral + self.k_d*derivative