dt_new = dt + t_new - t
n_m_new = dt / dt_new * n_m + (dt_new - dt) / dt_new * n_new
n_m = n_m_new
dt = dt_new
t = t_new