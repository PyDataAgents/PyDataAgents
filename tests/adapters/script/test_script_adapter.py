def test_000():
    script_file = "tests\\services\\script\\script1.py"
    with open(script_file) as f:
        code = f.read()
        
        # simulation values
        t_i = [0.5, 1.0, 1.5, 2.0, 2.5]
        n_i = [1.0, 1.5, 1.25, 1.0, 5.0]
                
        # initial values
        dt = 0
        t = 0
        n_m = 0
        n_new = 0
        t_new = 0
        
        # Define the variables you want to bind
        context = {
            "dt": dt,
            "t_new": t_new,
            "t": t,
            "n_m": n_m,
            "n_new": n_new            
        }
        
        for i in range(0, len(t_i)):
            t_new = t_i[i]        
            n_new = n_i[i]
            context["t_new"] = t_new
            context["n_new"] = n_new            
            exec(code, context)           
            print(context)
        