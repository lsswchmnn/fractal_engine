from utils import clear_cli, print_thin_separation
#============================================================
def print_debug_info(
        fractal, 
        viewport, 
        coloring_mode, 
        adaptive_iter, 
        original_iter, 
        span, 
        times,
        palette_name,
        settings=None
        ):
    
    clear_cli()
    print_thin_separation(linebreak=False)

    print("FRACTAL")
    print(f"Fractal:                {fractal._name}")
    print(f"Formula:                {fractal._formula}")
    print(f"Startvalue:             {fractal.start_real} + {fractal.start_imag}i")
    print(f"Exponent:               {fractal.exp_real} + {fractal.exp_imag}i")

    print("\nRENDERING")
    if settings:
        print(f"Supersampling:          {f'Enabled (factor: {settings.supersampling_factor})' if settings.supersampling_enabled else 'Disabled'}")
    print(f"Viewport:               x[{viewport.xmin:.2e}, {viewport.xmax:.2e}] y[{viewport.ymin:.2e}, {viewport.ymax:.2e}]")
    print(f"Center:                 {viewport.center_real:.2e} + {viewport.center_imag:.2e}i")
    print(f"Width:                  {viewport.width:.2e}")
    print(f"Adaptive iterations:    {adaptive_iter:.0f} (base: {original_iter}, span: {span:.2e})")
    if viewport.width < 1e-14:
        print("Warning: Numerical instability likely")

    print("\nCOLORING")
    print(f"Coloring mode:          {coloring_mode}")
    if coloring_mode == "orbit trap":
        print(f"Orbit-Trap type:        {fractal.trap_type_name}")
    print(f"Palette:                {palette_name}")
    if settings:
        print(f"Color inversion:        {'Enabled' if settings.inversion_enabled else 'Disabled'}")
        print(f"Gamma correction:       {f'Enabled (factor: {settings.gamma_factor}'})" if settings.post_process_enabled else "Disabled")
        print(f"Contrast adjustment:    {f'Enabled (factor: {settings.contrast_factor}'})" if settings.post_process_enabled else "Disabled")

    print("\nPROCESSING-TIMES")
    print(f"Rendering:              {times.render_time:.2f} sec")
    print(f"Coloring:               {times.coloring_time:.2f} sec")
    print(f"Downsampling:           {times.downsample_time:.2f} sec")
    print(f"Total:                  {times.render_time + times.coloring_time + times.downsample_time:.2f} sec")

    print_thin_separation(linebreak=False)
    print()
