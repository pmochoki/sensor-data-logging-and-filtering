from typing import Iterable, List


def moving_average(samples: Iterable[float], window_size: int) -> List[float]:
    """
    Simple moving average (boxcar) filter.

    For mechatronics applications, this is often the first filter used to reduce
    high-frequency sensor noise (e.g. vibration on an accelerometer or ultrasonic
    distance sensor jitter).

    The implementation keeps the output length equal to the input length by
    reusing the first valid average for the initial samples until the window is
    "full".
    """
    if window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    buf: List[float] = []
    output: List[float] = []
    running_sum = 0.0

    for x in samples:
        buf.append(x)
        running_sum += x

        if len(buf) > window_size:
            running_sum -= buf[-window_size - 1]

        current_window = min(len(buf), window_size)
        avg = running_sum / current_window
        output.append(avg)

    return output


def low_pass_filter(samples: Iterable[float], alpha: float) -> List[float]:
    """
    First-order IIR low-pass filter (exponential smoothing).

    y[k] = alpha * x[k] + (1 - alpha) * y[k-1]

    where:
    - alpha close to 1.0  -> fast response, less smoothing
    - alpha close to 0.0  -> slow response, more smoothing

    This is a common pattern in embedded systems because it is cheap to
    compute and easy to tune empirically on real hardware.
    """
    if not 0.0 < alpha <= 1.0:
        raise ValueError("alpha must be in the range (0, 1]")

    iterator = iter(samples)
    try:
        first = next(iterator)
    except StopIteration:
        return []

    output: List[float] = [float(first)]
    y_prev = float(first)

    for x in iterator:
        y = alpha * float(x) + (1.0 - alpha) * y_prev
        output.append(y)
        y_prev = y

    return output

