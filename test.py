from ctypes import *


def open_device():
    ## Input: none
    ## Output: hdwf (device handle), version (DWF version)
    version = create_string_buffer(16)
    dwf.FDwfGetVersion(version)
    print(f"DWF Version: {version.value.decode('utf-8')}")

    print("Opening the first device")
    hdwf = c_int()
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

    if hdwf.value == 0:
        print("failed to open device")
        sz_err = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(sz_err)
        raise RuntimeError("Failed to open device: " + sz_err.value.decode('utf-8'))

    return hdwf, version


def open_device():
    ## Input: none
    ## Output: hdwf (device handle), version (DWF version)
    version = create_string_buffer(16)
    dwf.FDwfGetVersion(version)
    print(f"DWF Version: {version.value.decode('utf-8')}")

    print("Opening the first device")
    hdwf = c_int()
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

    if hdwf.value == 0:
        print("failed to open device")
        sz_err = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(sz_err)
        raise RuntimeError("Failed to open device: " + sz_err.value.decode('utf-8'))

    return hdwf, version


def close_device(hdwf):
    print("Closing device")
    dwf.FDwfDeviceClose(hdwf)


if __name__ == '__main__':
    dwf = cdll.dwf
    # 用户参数配置
    pattern_len = 20          # Pattern长度，bit数
    clk_freq = 100            # Clock频率，Hz
    # 示例自定义 data pattern（20位，只要bit pattern即可，低位在前）
    data_pattern = 0b10011000101101100110

    # 1. 打开设备
    hdwf, _ = open_device()

    # 2. 配置 DigitalOut（Pattern Generator）三个通道

    # ---- Channel 0: Clock ----
    # 生成交替0/1的时钟pattern, 例如 101010...，长度为pattern_len
    clock_pattern = 0
    for i in range(pattern_len):
        clock_pattern |= ((i % 2) << i)   # 低位优先

    # DIO24: data
    dwf.FDwfDigitalOutEnableSet(hdwf, c_int(24), c_int(1))
    dwf.FDwfDigitalOutTypeSet(hdwf, c_int(24), c_int(0))
    data_buf = (c_uint * 1)(data_pattern)
    dwf.FDwfDigitalOutDataSet(hdwf, c_int(24), data_buf, c_int(pattern_len))

    # DIO25: clock
    dwf.FDwfDigitalOutEnableSet(hdwf, c_int(25), c_int(1))
    dwf.FDwfDigitalOutTypeSet(hdwf, c_int(25), c_int(0))
    clock_buf = (c_uint * 1)(clock_pattern)
    dwf.FDwfDigitalOutDataSet(hdwf, c_int(25), clock_buf, c_int(pattern_len))

    # DIO26: resetn
    dwf.FDwfDigitalOutEnableSet(hdwf, c_int(26), c_int(1))
    dwf.FDwfDigitalOutTypeSet(hdwf, c_int(26), c_int(0))
    resetn_pattern = 0b11111111111111111111  # 20位全1
    resetn_buf = (c_uint * 1)(resetn_pattern)
    dwf.FDwfDigitalOutDataSet(hdwf, c_int(26), resetn_buf, c_int(pattern_len))

    # 3. 设置总的输出频率（所有pattern以同样时钟输出）
    # dwf.FDwfDigitalOutFrequencySet(hdwf, c_double(clk_freq))

    # 可选：pattern重复次数设置
    # dwf.FDwfDigitalOutRepeatSet(hdwf, c_int(0))  # 只发一次，默认会无限循环

    print("Start!")

    # 4. 启动Pattern输出
    dwf.FDwfDigitalOutConfigure(hdwf, c_int(1))

    print("Pattern generation started.")
    print("Press Enter to stop.")
    input()

    # 5. 关闭
    dwf.FDwfDeviceClose(hdwf)
    print("Device closed.")

