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

def read_data_from_csv(file_path):
	import csv
	data = []
	with open(file_path, 'r') as file:
		reader = csv.reader(file)
		for row in reader:
			for bit in row:
				bit = bit.strip()  # 去除空格
				assert bit in ('0', '1'), f"Invalid bit '{bit}' in file {file_path}"
				data.append(int(bit))
	print(data)
	return data

def write_to_device(device):
	pattern = device.digital_output
	# clock
	pattern[0].setup_clock(frequency=1e2, repetition=36)
	# data
	data = [0, 0] + read_data_from_file('data.txt')
	pattern[1].setup_custom(1e2, data, repetition=1)
	# resetn
	data = [0, 0] + [1] * 16
	pattern[2].setup_custom(1e2, data, repetition=1)
	# run
	pattern.configure(start=True)

if __name__ == '__main__':
	with dwf.DigitalDiscovery() as device:
		while True:
			input("Press Enter to write data to device...")
			write_to_device(device)