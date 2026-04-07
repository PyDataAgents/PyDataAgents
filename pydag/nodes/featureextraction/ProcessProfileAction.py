from dataclasses import dataclass, field
import numpy as np


from ..NodeException import NodeException
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class ProcessProfileAction(BufferNode, Action):
    """ This `BufferNode` analyzes a time series of a process variable for standstill, constant and acceleration phase
    and computes the ratio of those phases within the timeseries.

    This class provides methods to evaluate a non-equidistant time series of
    timestamps and corresponding process variable. It computes key metrics such as:

    - Time-weighted mean process variable
    - Percentage of time at (approximately) constant process
    - Percentage of time spent accelerating
    - Percentage of time at standstill
    - max process value
    - min process value
    - max acceleration
    - min acceleration    

    The analysis accounts for irregular sampling intervals by weighting all
    calculations with the actual time differences between consecutive samples.

    Constant process is defined based on a relative deviation threshold
    (default: 2%) of process change between consecutive samples. Standstill is
    determined using a small process threshold to account for measurement noise.

    Parameters
    ----------
    tol : float, optional
        Relative tolerance for detecting constant process (default: 0.02, i.e. 2%).
    standstill_thresh : float, optional
        Threshold below which the process variable is considered zero (default: 1e-3).

    Args:
        BufferNode (_type_): parent class
        Action (_type_): interface class
    """
    
    standstill_threshold: float = field(default=1e-3, metadata={"description": "Relative tolerance for detecting constant process (default: 0.02, i.e. 2%)"})
    constant_tolerance : float = field(default=0.02, metadata={"description": "Threshold below which the process variable is considered zero (default: 1e-3)"})
    
    def _on_execute(self):
        data = self.get_parent_data()
        # ignore empty data
        if len(data) == 0:
            return
        # raise exc on wrong number of keys
        if len(data) != 2:
            raise NodeException(f"{self.__class__.__name__} always requires exactly 2 input keys (timestamp and process variable, in this order)")   
        it = iter(data)
        timestamps = next(it)
        process = next(it)
        new_data = self._analyze_profile(timestamps, process)
        self.add_data(new_data)
    
    def _analyze_profile(self, timestamps, process_variable) -> dict[str, float]:
        t = np.asarray(timestamps)
        p = np.asarray(process_variable)

        # time differences (segment durations)
        dt = np.diff(t)

        # use mid-segment process values for weighting
        p_mid = (p[:-1] + p[1:]) / 2

        total_time = np.sum(dt)

        # --- Mean process value (time-weighted!) ---
        mean_process = np.sum(p_mid * dt) / total_time

        # --- Acceleration (finite difference) ---
        dp = np.diff(p)
        acc = dp / dt
        
        p_max = np.max(p)
        p_min = np.min(p)
        acc_max = np.max(acc)
        acc_min = np.min(acc)

        
        # --- Masks ---
        # standstill
        is_standstill = np.abs(p_mid) < self.standstill_threshold

        # constant process: small acceleration relative to process values
        # avoid division by zero
        rel_change = np.zeros_like(acc)
        mask_nonzero = np.abs(p_mid) > self.standstill_threshold
        rel_change[mask_nonzero] = np.abs(acc[mask_nonzero] / p_mid[mask_nonzero])

        is_constant = (rel_change < self.constant_tolerance) & (~is_standstill)

        # accelerating (everything else except standstill)
        is_accelerating = ~(is_constant | is_standstill)

        # --- Time percentages ---
        p_constant = np.sum(dt[is_constant]) / total_time * 100
        p_accelerating = np.sum(dt[is_accelerating]) / total_time * 100
        p_standstill = np.sum(dt[is_standstill]) / total_time * 100

        return {
            "mean": float(mean_process),
            "max": float(p_max),
            "min": float(p_min),
            "acc_max": float(acc_max),
            "acc_min": float(acc_min),
            "p_constant": float(p_constant),
            "p_acceleration": float(p_accelerating),
            "p_standstill": float(p_standstill),
            "total_time": float(total_time),
        }