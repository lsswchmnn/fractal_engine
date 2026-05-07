from dataclasses import dataclass
#============================================================
@dataclass
class RenderResult:
    iterations: int
    escaped: bool
    trap: object
    z_real: float
    z_imag: float
    max_iter: int

@dataclass
class ProcessingTimes:
    render_time: float
    coloring_time: float
    downsample_time: float