# Settings
supply_voltage = 2.5  # V
config_file_name = "config.json"  # JSON 配置文件名

import dwfpy as dwf

def read_configs_from_json(file_path):
	"""从JSON文件读取配置参数和数据"""
	import json
	with open(file_path, 'r') as file:
		configs = json.load(file)
	return configs

def configs_sanity_check(configs):
	"""对读取的 configs 做全面的校验，确保所有字段存在且符合预期类型及约束"""
	if not isinstance(configs, dict):
		raise TypeError(f"configs 应该是 dict 类型，收到 {type(configs).__name__}")
	used_channels = set()
	for name, cfg in configs.items():
		# 名称校验
		if not isinstance(name, str):
			raise TypeError(f"配置项的 key 应该是字符串，收到 {type(name).__name__}：{name}")
		if not isinstance(cfg, dict):
			raise TypeError(f"配置 '{name}' 应该是 dict 类型，收到 {type(cfg).__name__}")

		# 必须字段
		required = (
			"clock_channel", "data_channel", "resetn_channel",
			"frequency", "num_cycles_to_reset", "reset_idle_state",
			"repeats", "length_of_data", "data"
		)
		for field in required:
			if field not in cfg:
				raise KeyError(f"配置 '{name}' 缺少必填字段 '{field}'")

		# 通道号校验，必须互不重复且为整数
		for ch_field in ("clock_channel", "data_channel", "resetn_channel"):
			ch = cfg[ch_field]
			if not isinstance(ch, int):
				raise TypeError(f"'{name}.{ch_field}' 必须是 int，收到 {type(ch).__name__}")
			if ch < 0 or ch > 63:
				raise ValueError(f"'{name}.{ch_field}'={ch} 超出 0–63 可用范围")
			if ch in used_channels:
				raise ValueError(f"通道号 {ch} 在多个配置中重复使用")
			used_channels.add(ch)

		# 频率
		freq = cfg["frequency"]
		if not (isinstance(freq, int) or isinstance(freq, float)):
			raise TypeError(f"'{name}.frequency' 必须是数值类型，收到 {type(freq).__name__}")
		if freq <= 0:
			raise ValueError(f"'{name}.frequency' 必须大于 0，收到 {freq}")

		# 循环重置周期
		num_reset = cfg["num_cycles_to_reset"]
		if not isinstance(num_reset, int) or num_reset < 0:
			raise ValueError(f"'{name}.num_cycles_to_reset' 必须是非负整数，收到 {num_reset}")

		# 空闲状态
		idle = cfg["reset_idle_state"]
		valid_idle_strs = ("initial", "low", "high", "z")
		if not (isinstance(idle, str) and idle.lower() in valid_idle_strs):
			raise ValueError(
			f"'{name}.reset_idle_state' 必须是 'initial'、'low'、'high'、'z' 之一，收到 {idle!r}"
			)

		# 重复次数
		repeats = cfg["repeats"]
		if not isinstance(repeats, int) or repeats <= 0:
			raise ValueError(f"'{name}.repeats' 必须是正整数，收到 {repeats}")

		# 数据长度与实际 data 对象校验
		length = cfg["length_of_data"]
		if not isinstance(length, int) or length < 0:
			raise ValueError(f"'{name}.length_of_data' 必须是非负整数，收到 {length}")
		data = cfg["data"]
		if not isinstance(data, dict):
			raise TypeError(f"'{name}.data' 必须是 dict，收到 {type(data).__name__}")
		if len(data) != length:
			raise ValueError(f"'{name}.data' 长度 {len(data)} 与 length_of_data {length} 不匹配")
		# data 中的值校验
		for val in data.values():
			if val not in (0, 1):
				raise ValueError(f"'{name}.data' 中的值只能是 0 或 1，收到 {val}")

def write_to_device(device):
	# configurations
	configs = read_configs_from_json(config_file_name)
	try:
		configs_sanity_check(configs)
	except (TypeError, KeyError, ValueError) as e:
		print(f"\033[91mJson 文件出错啦！ {e}\033[0m")
		return
	"""将配置写入设备"""
	# setup digital output
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
		reset_data = [0] * config['num_cycles_to_reset'] + [1] * config['length_of_data'] * config['repeats']
		pattern[resetn_channel].setup_custom(config['frequency'], reset_data, repetition=1, idle_state=config['reset_idle_state'])
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
