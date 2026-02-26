## Sensor Data Logging and Filtering

**Project name**: `sensor-data-logging-and-filtering`  
**Domain focus**: Mechatronics, embedded sensing, and control systems.

This project simulates a noisy sensor (temperature or distance), logs the data to CSV,
filters the signal using a moving average and an optional first‑order low‑pass filter,
and visualizes the result. It is designed to look and feel like the data‑processing
pipeline you would build for a real microcontroller‑based system.

---

### Why filtering matters in mechatronic sensor systems

Real sensors are never perfect:

- **Electrical noise** from ADCs, switching power supplies, and EMI
- **Mechanical vibration** from motors, fans, and gearboxes
- **Quantization and jitter** from discrete sampling
- **Environmental disturbances** such as drafts (temperature) or echoes (ultrasonic)

In a mechatronic control loop, feeding this raw, noisy data directly into your
controller (PID, state machine, safety logic, etc.) can cause:

- **Chattering actuators** (relays and valves switching rapidly)
- **Unstable control behaviour** and overshoot
- **False alarms** in safety or fault‑detection logic

Digital filters help by separating the **true physical signal** from the **unwanted
noise**, giving the controller a more stable, reliable measurement:

- **Moving average filter**  
  A simple “boxcar” filter that averages a fixed number of recent samples. It is easy
  to implement on small microcontrollers and works well for reducing high‑frequency
  noise (e.g. vibration on accelerometers, jitter on distance sensors).

- **First‑order low‑pass filter (IIR)**  
  A lightweight exponential filter that approximates an analog RC low‑pass circuit.
  It trades off responsiveness vs. smoothness with a single parameter (`alpha`) and
  is very common in embedded code for temperature, pressure, and position sensors.

This project demonstrates these concepts in a way that mirrors what you would do
on real hardware, but entirely in Python.

---

### Project structure

- `main.py` – CLI entry point. Simulates sensor readings, logs raw data, applies filters, saves CSVs, and generates plots.
- `filters.py` – Reusable filter implementations:
  - `moving_average`
  - `low_pass_filter` (first‑order IIR / exponential smoothing)
- `data/` – Auto‑created output directory for CSV files and plots (no need to create it manually).
- `requirements.txt` – Python dependencies.

---

### Installation

1. **Create and activate a virtual environment (recommended)**  

   ```bash
   cd "Application 2"  # adjust if your folder name differs

   python -m venv .venv
   source .venv/bin/activate  # on Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

### How to run the simulation

From the project directory (where `main.py` lives):

```bash
python main.py
```

This runs the default **temperature sensor** simulation with:

- 500 samples
- 0.05 s sampling period
- Moving average window of 10 samples
- Low‑pass filter with `alpha = 0.2`

You can customize the behaviour via command‑line options:

- **Select sensor type**

  ```bash
  # Temperature sensor (default)
  python main.py --sensor temperature

  # Distance sensor (e.g. ultrasonic)
  python main.py --sensor distance
  ```

- **Control sampling**

  ```bash
  # 1000 samples at 10 ms period
  python main.py --samples 1000 --dt 0.01
  ```

- **Tune the moving average window**

  ```bash
  # Stronger smoothing (slower response)
  python main.py --window 25

  # Lighter smoothing (faster response)
  python main.py --window 5
  ```

- **Tune the low‑pass filter**

  ```bash
  # Smoother, slower response
  python main.py --low-pass-alpha 0.1

  # Faster, less smoothing
  python main.py --low-pass-alpha 0.5

  # Disable low-pass filter completely
  python main.py --low-pass-alpha 0
  ```

- **Adjust signal characteristics**

  ```bash
  # Higher‑amplitude motion / ripple and more noise
  python main.py --sensor distance --amplitude 0.2 --noise-std 0.05
  ```

You can combine these options to quickly explore the impact of sampling rate and
filter tuning on your virtual sensor.

---

### Where the CSV files and plots are saved

When you run `main.py`, the script automatically creates a `data/` folder (if it
does not already exist). Each run generates time‑stamped artifacts:

- **Raw data CSV**

  - Path pattern: `data/raw_<sensor>_<timestamp>.csv`
  - Columns:
    - `time_s` – simulation time in seconds
    - `raw` – unfiltered sensor reading

- **Filtered data CSV**

  - Path pattern: `data/filtered_<sensor>_<timestamp>.csv`
  - Columns:
    - `time_s` – simulation time in seconds
    - `raw` – unfiltered sensor reading
    - `moving_average` – output of the moving average filter
    - `low_pass` – output of the low‑pass filter (present only if enabled)

- **Plot image**

  - Path pattern: `data/plot_<sensor>_<timestamp>.png`
  - Shows **raw vs filtered** signals on the same axes so you can visually inspect
    noise reduction, lag, and overall filter performance.

These files are ideal for:

- Plotting and further analysis in tools like MATLAB, Excel, or Jupyter
- Including screenshots and snippets in a **portfolio** or **lab report**
- Comparing different filter configurations by running several simulations

---

### Portfolio and learning highlights

This project is intentionally structured to be **portfolio‑ready**:

- Clear separation between **data generation** (`main.py`) and **filter logic** (`filters.py`)
- Mechatronics‑relevant terminology (sampling period, sensor type, noise, low‑pass filter)
- Easily extensible to real hardware:
  - Replace the simulated sensor with serial / CAN / fieldbus input
  - Reuse the same filtering functions on microcontroller data

Feel free to extend it by adding:

- Higher‑order filters (e.g. Butterworth, digital PID pre‑filtering)
- Frequency‑domain analysis (FFT of raw vs filtered data)
- Logging hooks for real sensor streams instead of simulated data.

