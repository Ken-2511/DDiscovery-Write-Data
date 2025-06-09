# Settings
supply_voltage = 2.5  # V
config_file_name = "config.json"  # JSON config file name

import dwfpy as dwf

def read_configs_from_json(file_path):
	"""Read configuration parameters and data from a JSON file"""
	import json
	with open(file_path, 'r') as file:
		configs = json.load(file)
	return configs

def configs_sanity_check(configs):
	"""Perform comprehensive validation on configs to ensure all fields exist and meet expected types and constraints"""
	if not isinstance(configs, dict):
		raise TypeError(f"configs should be of type dict, got {type(configs).__name__}")
	used_channels = set()
	for name, cfg in configs.items():
		# Name validation
		if not isinstance(name, str):
			raise TypeError(f"The key of a config item should be a string, got {type(name).__name__}: {name}")
		if not isinstance(cfg, dict):
			raise TypeError(f"Config '{name}' should be of type dict, got {type(cfg).__name__}")

		# Required fields
		required = (
			"clock_channel", "data_channel", "resetn_channel",
			"frequency", "num_cycles_to_reset", "reset_mode",
			"repeats", "length_of_data", "data"
		)
		for field in required:
			if field not in cfg:
				raise KeyError(f"Config '{name}' is missing required field '{field}'")

		# Channel number validation: must be unique and integer
		for ch_field in ("clock_channel", "data_channel", "resetn_channel"):
			ch = cfg[ch_field]
			if not isinstance(ch, int):
				raise TypeError(f"'{name}.{ch_field}' must be int, got {type(ch).__name__}")
			if ch < 0 or ch > 63:
				raise ValueError(f"'{name}.{ch_field}'={ch} is out of the valid range 0–63")
			if ch in used_channels:
				raise ValueError(f"Channel number {ch} is used in multiple configs")
			used_channels.add(ch)

		# Frequency
		freq = cfg["frequency"]
		if not (isinstance(freq, int) or isinstance(freq, float)):
			raise TypeError(f"'{name}.frequency' must be a numeric type, got {type(freq).__name__}")
		if freq <= 0:
			raise ValueError(f"'{name}.frequency' must be greater than 0, got {freq}")

		# Number of reset cycles
		num_reset = cfg["num_cycles_to_reset"]
		if not isinstance(num_reset, int) or num_reset < 0:
			raise ValueError(f"'{name}.num_cycles_to_reset' must be a non-negative integer, got {num_reset}")

		# Reset mode
		idle = cfg["reset_mode"]
		valid_idle_strs = ("low", "high")
		if not (isinstance(idle, str) and idle.lower() in valid_idle_strs):
			raise ValueError(
			f"'{name}.reset_mode' must be one of 'low', 'high', got {idle!r}"
			)

		# Repeats
		repeats = cfg["repeats"]
		if not isinstance(repeats, int) or repeats <= 0:
			raise ValueError(f"'{name}.repeats' must be a positive integer, got {repeats}")

		# Data length and actual data object validation
		length = cfg["length_of_data"]
		if not isinstance(length, int) or length < 0:
			raise ValueError(f"'{name}.length_of_data' must be a non-negative integer, got {length}")
		data = cfg["data"]
		if not isinstance(data, dict):
			raise TypeError(f"'{name}.data' must be dict, got {type(data).__name__}")
		if len(data) != length:
			raise ValueError(f"'{name}.data' length {len(data)} does not match length_of_data {length}")
		# Validate values in data
		for val in data.values():
			if val not in (0, 1):
				raise ValueError(f"Values in '{name}.data' can only be 0 or 1, got {val}")

def write_to_device(device):
	# configurations
	configs = read_configs_from_json(config_file_name)
	try:
		configs_sanity_check(configs)
	except (TypeError, KeyError, ValueError) as e:
		print(f"\033[91mJson file error! {e}\033[0m")
		return
	"""Write configuration to device"""
	# Set up digital output
	pattern = device.digital_output
	device.supplies.digital.voltage = supply_voltage
	for key, config in configs.items():
		print(f"Writing to device with configuration: {key}")
		if len(config['data']) != config['length_of_data']:
			raise ValueError(f"Data length mismatch: expected {config['length_of_data']}, got {len(config['data'])}")
		# clock
		clock_channel = config['clock_channel'] - 24
		clock_repetition = config['num_cycles_to_reset'] * 2 + config['length_of_data'] * config['repeats'] * 2
		pattern[clock_channel].setup_clock(frequency=config['frequency'], repetition=clock_repetition)
		# data
		data_channel = config['data_channel'] - 24
		data = list(config['data'].values())
		data = [0] * config['num_cycles_to_reset'] + data * config['repeats']
		pattern[data_channel].setup_custom(config['frequency'], data, repetition=1)
		# resetn
		resetn_channel = config['resetn_channel'] - 24
		active_bit = 1 if config['reset_mode'].lower() == 'high' else 0  # active bit is 1 for high reset mode, 0 for low reset mode
		idle_bit = 0 if active_bit == 1 else 1
		idle_state = "low" if active_bit == 1 else "high"
		reset_data = [active_bit] * config['num_cycles_to_reset'] + [idle_bit] * config['length_of_data'] * config['repeats']
		pattern[resetn_channel].setup_custom(config['frequency'], reset_data, repetition=1, idle_state=idle_state)
		# print
		print(f"writing the following data  to pin {config['data_channel']}: {data}")
		print(f"writing the following reset to pin {config['resetn_channel']}: {reset_data}")
	# run
	pattern.configure(start=True)

if __name__ == '__main__':
	with dwf.DigitalDiscovery() as device:
		while True:
			temp = input("Press Enter to write data to device, [q] to quit: ")
			if temp.lower() == 'q':
				print("Exiting...")
				break
			write_to_device(device)
