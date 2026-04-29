from utils import clear_cli, print_thin_separation
#============================================================
def print_debug_info(
        fractal, 
        viewport, 
        Colorizer, 
        coloring_mode, 
        adaptive_iter, 
        original_iter, 
        span, 
        render_time, 
        palette_name,
        settings=None):
    
    clear_cli()
    #total_iter, total_pixels = self._estimate_workload(viewport, adaptive_iter, settings, render_settings=RenderSettings())

    print_thin_separation(linebreak=False)
    print("FRACTAL")
    print(f"Fractal:                {fractal._name}")
    print(f"Formula:                {fractal._formula}")
    print(f"Startvalue:             {fractal.start_real} + {fractal.start_imag}i")
    print(f"Exponent:               {fractal.exp_real} + {fractal.exp_imag}i")
    print("\nCOLORING")
    print(f"Coloring mode:          {coloring_mode}")
    if coloring_mode == "orbit trap":
        print(f"Orbit-Trap type:        {fractal.trap_type_name}")
    print(f"Palette:                {palette_name}")
    print("\nRENDERING")
    if settings:
        print(f"Supersampling:          {f'Enabled (factor: {settings.supersampling_factor})' if settings.supersampling_enabled else 'Disabled'}")
    print(f"Viewport:               x[{viewport.xmin:.2e}, {viewport.xmax:.2e}] y[{viewport.ymin:.2e}, {viewport.ymax:.2e}]")
    print(f"Adaptive iterations:    {adaptive_iter:.0f} (base: {original_iter}, span: {span:.2e})")
    print(f"Rendering-Time:         {render_time} sec")
    #print(f"Estimated workload:     {total_iter:.2e} iterations ({total_pixels:.2e} pixels)")
    print_thin_separation(linebreak=False)
    print()