import sympy as sp

def test_sympy():
    
    xi_w, K, p, D_F = sp.symbols("xi_w K p D_F")

    
    eq1 = sp.Eq(sp.sympify("p"), sp.sympify("2 * M_t * S_r / (pi * D_F^2 * l_F * µ_ru)"))
    eq2 = sp.Eq(sp.sympify("xi_w"), sp.sympify("K * p / E_A"))
    eq3 = sp.Eq(sp.sympify("xi_w"), sp.sympify("U_w / D_F"))
    eq4 = sp.Eq(sp.sympify("K"), sp.sympify("E_A / E_I * ((1 + Q_I^2) / (1 - Q_I^2) - nu_I) + (1 + Q_A^2) / (1 - Q_A^2) + nu_A"))
    
    solution = sp.solve([eq1, eq2, eq3, eq4], [xi_w, K, p, D_F])
    print(solution)
    