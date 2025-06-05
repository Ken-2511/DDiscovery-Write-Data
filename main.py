import csv
import dwfpy as dwf

def read_config_from_csv(file_path, data: list, config: dict):
	"""从CSV文件读取配置参数和数据"""
	with open(file_path, 'r') as file:
		reader = csv.reader(file)

		# Pattern：
		# 第一行是标题
		# 第二行到splitter之前是配置参数
		# 接下来是splitter行
		# 接下来都是数据位
		rows = list(reader)
		# 找到 splitter 行的索引（data 从该行下一行开始）
		split_index = None
		for idx, row in enumerate(rows):
			if row and row[0].strip().lower() == 'splitter':
				split_index = idx
				break
		if split_index is None:
			raise ValueError(f"Splitter row not found in {file_path}")
		# 解析标题行之后、splitter 之前的配置参数
		for row in rows[1:split_index]:
			assert len(row) == 2, f"CSV format error: expected 2 columns, got {len(row)} in row {row}"
			key, val = row[0].strip(), row[1].strip()
			config[key] = int(val)
		# 解析数据位
		for row in rows[split_index+1:]:
			assert len(row) == 2, f"CSV file format error: expected 2 columns, got {len(row)} in row {row}"
			assert row[1].strip() in ('0', '1'), f"Invalid bit '{row[1]}' for {row[0]} in file {file_path}"
			data.append(int(row[1].strip()))
		assert len(data) == config['length_of_data'], f"Data length mismatch: expected {config['length_of_data']}, got {len(data)}"

def write_to_device(device):
	# configurations
	config = {
		# 注意：在这里修改参数是没用的，这些只是placeholder。该参数要到csv里面改
		'frequency': 100,
		'num_cycles_to_reset': 2,
		'length_of_data': 16,
		'repeats': 2,
		'clock_channel': 24,
		'data_channel': 25,
		'resetn_channel': 26
	}
	data = []
	read_config_from_csv('config.csv', data, config)
	# setup digital output
	pattern = device.digital_output
	# clock
	clock_channel = config['clock_channel'] - 24
	clock_repetition = config['num_cycles_to_reset'] * 2 + config['length_of_data'] * 2 * config['repeats']
	pattern[clock_channel].setup_clock(frequency=config['frequency'], repetition=clock_repetition)
	# data
	data_channel = config['data_channel'] - 24
	data = [0] * config['num_cycles_to_reset'] + data * config['repeats']
	pattern[data_channel].setup_custom(config['frequency'], data, repetition=1)
	# resetn
	resetn_channel = config['resetn_channel'] - 24
	reset_data = [0] * config['num_cycles_to_reset']
	pattern[resetn_channel].setup_custom(config['frequency'], reset_data, repetition=1, idle_state="high")
	# run
	pattern.configure(start=True)
	print(f"data:  {data}")
	print(f"reset: {reset_data}")

if __name__ == '__main__':
	with dwf.DigitalDiscovery() as device:
		while True:
			input("Press Enter to write data to device...")
			write_to_device(device)