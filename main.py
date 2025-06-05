import csv
import dwfpy as dwf

def read_data_from_file(file_path):
	data = []
	with open(file_path, 'r') as file:
		content = file.read()
		for line in content.splitlines():
			bit = line.partition('#')[0].strip()  # 去除注释和空格
			assert bit in ('0', '1'), f"Invalid bit '{bit}' in file {file_path}"
			data.append(int(bit))
	print(data)
	return data

def read_config_from_csv(file_path, data: list, config: dict):
    """从CSV文件读取配置参数和数据"""
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过标题行 (key, value)
        
        for row in reader:
            if len(row) >= 2:
                key = row[0].strip()
                value = row[1].strip()
                
                # 处理配置参数
                if key in ['frequency', 'num_cycles_to_reset', 'length_of_data']:
                    config[key] = int(value)
                
                # 处理数据位
                elif key.startswith('data_'):
                    assert value in ('0', '1'), f"Invalid bit '{value}' for {key} in file {file_path}"
                    data.append(int(value))
    
    print(f"Config: {config}")
    print(f"Data: {data}")
    return data

def write_to_device(device):
	# configurations
	config = {
		"frequency": None,
		"num_cycles_to_reset": None,
		"length_of_data": None
	}
	data = []
	read_config_from_csv('config.csv', data, config)
	# setup digital output
	pattern = device.digital_output
	# clock
	pattern[0].setup_clock(frequency=config['frequency'], repetition=(config['num_cycles_to_reset'] + config['length_of_data']) * 2)
	# data
	data = [0] * config['num_cycles_to_reset'] + read_data_from_file('data.txt')
	pattern[1].setup_custom(config['frequency'], data, repetition=1)
	# resetn
	reset_data = [0] * config['num_cycles_to_reset'] + [1] * config['length_of_data']
	pattern[2].setup_custom(config['frequency'], reset_data, repetition=1)
	# run
	pattern.configure(start=True)
	print(data)
	print(reset_data)

if __name__ == '__main__':
	with dwf.DigitalDiscovery() as device:
		while True:
			input("Press Enter to write data to device...")
			write_to_device(device)