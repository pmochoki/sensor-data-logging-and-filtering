import argparse
import csv
import math
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt

from filters import low_pass_filter, moving_average


DATA_DIR = Path("data")


@dataclass
class SimulationConfig:
    sensor_type: str
    samples: int
    dt: float
    moving_average_window: int
    low_pass_alpha: Optional[float]
    amplitude: float
    noise_std: float
    seed: Optional[int]


def ensure_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def simulate_temperature_signal(config: SimulationConfig) -> Tuple[List[float], List[float]]:
    """Simulate a noisy temperature sensor signal."""
    times: List[float] = []
    values: List[float] = []

    baseline = 25.0  # °C
    drift_per_second = 0.02  # slow ramp (e.g. heater warming up)
    ripple_amplitude = config.amplitude  # small oscillation

    for k in range(config.samples):
        t = k * config.dt
        drift = drift_per_second * t
        ripple = ripple_amplitude * math.sin(2 * math.pi * 0.05 * t)
        ideal = baseline + drift + ripple
        noise = random.gauss(0.0, config.noise_std)
        measurement = ideal + noise

        times.append(t)
        values.append(measurement)

    return times, values


def simulate_distance_signal(config: SimulationConfig) -> Tuple[List[float], List[float]]:
    """Simulate a noisy distance sensor signal (e.g. ultrasonic)."""
    times: List[float] = []
    values: List[float] = []

    # Object oscillates around 0.5 m
    offset = 0.5
    motion_amplitude = config.amplitude

    for k in range(config.samples):
        t = k * config.dt
        # Simple periodic motion
        ideal = offset + motion_amplitude * math.sin(2 * math.pi * 0.25 * t)
        noise = random.gauss(0.0, config.noise_std)
        measurement = max(0.0, ideal + noise)

        times.append(t)
        values.append(measurement)

    return times, values


def write_raw_csv(path: Path, times: List[float], values: List[float]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time_s", "raw"])
        for t, v in zip(times, values):
            writer.writerow([f"{t:.4f}", f"{v:.6f}"])


def write_filtered_csv(
    path: Path,
    times: List[float],
    raw_values: List[float],
    ma_values: List[float],
    lp_values: Optional[List[float]],
) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        headers = ["time_s", "raw", "moving_average"]
        if lp_values is not None:
            headers.append("low_pass")
        writer.writerow(headers)

        for idx, t in enumerate(times):
            row: List[str] = [
                f"{t:.4f}",
                f"{raw_values[idx]:.6f}",
                f"{ma_values[idx]:.6f}",
            ]
            if lp_values is not None:
                row.append(f"{lp_values[idx]:.6f}")
            writer.writerow(row)


def plot_signals(
    output_path: Path,
    times: List[float],
    raw_values: List[float],
    ma_values: List[float],
    lp_values: Optional[List[float]],
    sensor_type: str,
) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(times, raw_values, label="Raw", color="#999999", linewidth=1, alpha=0.7)
    plt.plot(times, ma_values, label="Moving average", color="#0077b6", linewidth=2)

    if lp_values is not None:
        plt.plot(times, lp_values, label="Low-pass (IIR)", color="#e85d04", linewidth=2)

    plt.xlabel("Time [s]")
    unit = "°C" if sensor_type == "temperature" else "m"
    ylabel = f"Measurement [{unit}]"
    plt.ylabel(ylabel)
    plt.title(f"{sensor_type.capitalize()} sensor: raw vs filtered")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def parse_args() -> SimulationConfig:
    parser = argparse.ArgumentParser(
        description="Simulate noisy sensor data, log to CSV, and apply digital filters.",
    )
    parser.add_argument(
        "--sensor",
        choices=["temperature", "distance"],
        default="temperature",
        help="Type of sensor to simulate.",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=500,
        help="Number of samples to generate.",
    )
    parser.add_argument(
        "--dt",
        type=float,
        default=0.05,
        help="Sampling period in seconds.",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=10,
        help="Moving average window size (number of samples).",
    )
    parser.add_argument(
        "--low-pass-alpha",
        type=float,
        default=0.2,
        help=(
            "Low-pass filter smoothing factor (0–1). "
            "Set to 0 to disable the low-pass filter."
        ),
    )
    parser.add_argument(
        "--amplitude",
        type=float,
        default=1.0,
        help="Signal amplitude (e.g. ripple for temperature, motion for distance).",
    )
    parser.add_argument(
        "--noise-std",
        type=float,
        default=0.5,
        help="Standard deviation of Gaussian noise added to the signal.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible runs. Set to a negative value to use a random seed.",
    )

    args = parser.parse_args()

    low_pass_alpha: Optional[float]
    if args.low_pass_alpha <= 0.0:
        low_pass_alpha = None
    else:
        low_pass_alpha = min(max(args.low_pass_alpha, 0.0), 1.0)

    seed: Optional[int]
    if args.seed is not None and args.seed < 0:
        seed = None
    else:
        seed = args.seed

    return SimulationConfig(
        sensor_type=args.sensor,
        samples=args.samples,
        dt=args.dt,
        moving_average_window=args.window,
        low_pass_alpha=low_pass_alpha,
        amplitude=args.amplitude,
        noise_std=args.noise_std,
        seed=seed,
    )


def main() -> None:
    config = parse_args()
    ensure_data_dir()

    if config.seed is not None:
        random.seed(config.seed)

    if config.sensor_type == "temperature":
        times, raw_values = simulate_temperature_signal(config)
    else:
        times, raw_values = simulate_distance_signal(config)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    raw_csv_path = DATA_DIR / f"raw_{config.sensor_type}_{timestamp}.csv"
    filtered_csv_path = DATA_DIR / f"filtered_{config.sensor_type}_{timestamp}.csv"
    plot_path = DATA_DIR / f"plot_{config.sensor_type}_{timestamp}.png"

    write_raw_csv(raw_csv_path, times, raw_values)

    ma_values = moving_average(raw_values, window_size=config.moving_average_window)
    lp_values: Optional[List[float]] = None
    if config.low_pass_alpha is not None:
        lp_values = low_pass_filter(raw_values, alpha=config.low_pass_alpha)

    write_filtered_csv(filtered_csv_path, times, raw_values, ma_values, lp_values)
    plot_signals(plot_path, times, raw_values, ma_values, lp_values, config.sensor_type)

    print("Simulation complete.")
    print(f"Raw data:      {raw_csv_path}")
    print(f"Filtered data: {filtered_csv_path}")
    print(f"Plot image:    {plot_path}")


if __name__ == "__main__":
    main()

