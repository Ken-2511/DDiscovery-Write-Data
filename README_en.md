# DDiscovery-Write-Data User Guide

This project is designed to write custom digital data sequences to devices using the Digilent Digital Discovery. All configuration parameters and data bits are managed via the `config.csv` file.

## Requirements

- Python 3.7 or above
- [dwfpy](https://github.com/mariusgreuel/dwfpy)
  
  Installation:
  ```
  pip install dwfpy
  ```

## File Structure

- `main.py`: Main program, responsible for reading configuration and data, and writing to the device
- `config.csv`: Configuration parameters and data bits (to be edited by the user)

## config.csv Format

Example:

```
key,value
frequency,100
num_cycles_to_reset,2
length_of_data,16
repeats,2
clock_channel,24
data_channel,25
resetn_channel,26
splitter,========================
bitA,1
bitB,0
bitC,1
bitD,0
...
```

### Parameter Descriptions

- `frequency`: Clock signal frequency in Hz (e.g., 100 means 100Hz)
- `num_cycles_to_reset`: Number of clock cycles the reset signal stays low before writing data
- `length_of_data`: Number of data bits per write (must match the number of data bits below)
- `repeats`: Number of times to repeat the data sequence (writes the same sequence multiple times)
- `clock_channel`: Output channel number for the clock signal (typically 24~39 on Digital Discovery)
- `data_channel`: Output channel number for the data bits (typically 24~39)
- `resetn_channel`: Output channel number for the reset signal (typically 24~39)
- `splitter`: Separator row, content can be arbitrary, used to separate parameters from data bits

### Data Bits

- Every row after the `splitter` is treated as a data bit. The key can be any name (does not need to start with `data_`), and the value must be 0 or 1.
- The number of data bits must match the `length_of_data` parameter, otherwise the program will report an error.

## Usage

1. **Edit `config.csv`**  
   Fill in the parameters and data bits as described above. Data bit keys can be named arbitrarily, as long as the value is 0 or 1.

2. **Connect the Digital Discovery device**

3. **Run the main program**  
   In the terminal, execute:
   ```
   python main.py
   ```

4. **Follow the prompts**  
   Each time you press Enter, the data will be written to the device.

## Notes

- All parameters must be set in `config.csv`. The `config` dictionary in the code is only a placeholder.
- The number of data bits must match the `length_of_data` parameter.
- To change the write frequency, channels, or other parameters, modify `config.csv` directly.
- Data bit keys can be customized and do not need to start with `data_`.
