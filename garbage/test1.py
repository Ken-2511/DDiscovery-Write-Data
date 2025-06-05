import pattern
import device

device_data = device.open()

print(device_data.name)

pattern.enable(device_data, channel=24)

pattern.generate(device_data,
				 channel=24,
				 function=pattern.function.custom,
				 frequency=1000,
				 data=[i % 1 for i in range(100)],
				 run_time=0,
				 repeat=10000)

device.close(device_data)