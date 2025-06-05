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

if __name__ == '__main__':
    # 加载 dwf.dll （可根据实际路径调整）
    dwf = cdll.dwf

    # 1. 打开设备
    hdwf, _ = open_device()

    # 2. 输出100Hz方波时钟到 DIO24
    pattern_len = 20  # 比特数：每个bit占10ms，一个完整pattern是0.2秒，会循环
    clk_freq = 100    # 100Hz

    # 生成 101010... pattern（低位在前，共20位）
    clock_pattern = 0
    for i in range(pattern_len):
        clock_pattern |= ((i % 2) << i)
    clock_buf = (c_uint * 1)(clock_pattern)
    print(f"Clock pattern: {clock_buf[0]:020b} (length={pattern_len})")

    # 配置 DIO24 (idxChannel=24)
    idxChannel = 24
    dwf.FDwfDigitalOutEnableSet(hdwf, c_int(idxChannel), c_int(1))
    dwf.FDwfDigitalOutTypeSet(hdwf, c_int(idxChannel), c_int(1))  # 2=Custom
    dwf.FDwfDigitalOutDataSet(hdwf, c_int(idxChannel), clock_buf, c_int(pattern_len))

    # 设置输出频率（如果你的DLL版本不支持，可以使用 Divider 方法）
    # try:
    # dwf.FDwfDigitalOutFrequencySet(hdwf, c_double(clk_freq))
    # except AttributeError:
    #     # 兼容老接口，用分频
    #     base_clk = 100_000_000  # Digital Discovery主频率100MHz（实际可查手册）
    #     divider = int(base_clk / clk_freq)
    #     dwf.FDwfDigitalOutDividerSet(hdwf, c_int(idxChannel), c_uint(divider))

    # 无限重复输出（默认就循环）
    # dwf.FDwfDigitalOutRepeatSet(hdwf, c_int(0))  # 可省略

    # 启动输出
    dwf.FDwfDigitalOutConfigure(hdwf, c_int(1))

    print("DIO24输出100Hz方波中...")

    import time
    time.sleep(1)

    # 停止并关闭设备
    dwf.FDwfDeviceClose(hdwf)
    print("Device closed.")
