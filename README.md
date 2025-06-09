# DDiscovery-Write-Data User Guide

This project writes custom digital data sequences to devices using Digilent Digital Discovery. All configuration parameters and data bits are managed via a single `config.json` file, supporting multiple named profiles.

## Requirements

- Python 3.7 or above
- [dwfpy](https://github.com/mariusgreuel/dwfpy)
  ```powershell
  pip install dwfpy
  ```

## File Structure

- `main.py`: Main program to read the JSON configuration and write to the device
- `config.json`: JSON file defining one or more write profiles
- `README.md`: Chinese user guide
- `README_en.md`: English user guide

## config.json Format

`config.json` is a JSON object where each key is a named profile. Example:

```json
{
  "profile1": {
    "frequency": 100,
    "num_cycles_to_reset": 2,
    "length_of_data": 16,
    "repeats": 2,
    "clock_channel": 24,
    "data_channel": 25,
    "resetn_channel": 26,
    "reset_idle_state": "initial",
    "data": {
      "bit1": 1,
      "bit2": 0,
      ...
      "bit16": 1
    }
  },
  "profile2": {
    // additional profiles
  }
}
```

### Field Descriptions

- `frequency`: Clock signal frequency in Hz
- `num_cycles_to_reset`: Number of clock cycles the reset signal stays low before data write
- `length_of_data`: Number of data bits per write (must match the count of `data` entries)
- `repeats`: Number of times to repeat the data sequence
- `clock_channel`: Channel number for clock output (24–39)
- `data_channel`: Channel number for data output (24–39)
- `resetn_channel`: Channel number for reset output (24–39)
- `reset_idle_state`: Idle state for reset line; one of `"initial"`, `"low"`, `"high"`, `"z"`
- `data`: Object mapping bit names to values (0 or 1)

## Usage

1. Edit `config.json` and define one or more profiles as shown above.
2. Connect the Digilent Digital Discovery device.
3. Run the main script:
   ```powershell
   python main.py
   ```
4. Follow the prompts:
   - Press Enter to write all profiles’ data sequences to the device.
   - Enter `q` and press Enter to exit.

## Notes

- Ensure `config.json` is valid JSON; the program will report field-specific errors if not.
- Channel numbers must be unique and within 24–39.
- Data values in `data` must be either 0 or 1.
