# DDiscovery-Write-Data 使用说明

[English README](./README_en.md)

本项目用于通过 Digilent Digital Discovery 向数字设备写入自定义数据序列。所有配置参数和数据位均通过 `config.json` 管理，支持多个命名配置项。

## 依赖环境

- Python 3.7 及以上
- [dwfpy](https://github.com/mariusgreuel/dwfpy)
  ```powershell
  pip install dwfpy
  ```

## 文件结构

- `main.py`：主程序，负责读取配置文件并写入设备
- `config.json`：配置文件，使用 JSON 格式定义一个或多个写入配置
- `README.md`：中文使用说明
- `README_en.md`：英文使用说明

## config.json 格式说明

config.json 为一个 JSON 对象，每个键对应一个写入配置。示例：

```json
{
  "config1": {
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
  "config2": {
    ... // 可定义更多配置
  }
}
```

### 字段说明

- `frequency`：时钟信号频率，单位 Hz
- `num_cycles_to_reset`：复位信号保持低电平的时钟周期数
- `length_of_data`：单次写入的数据位长度，需与 `data` 对象的键值对数量一致
- `repeats`：数据序列重复写入次数
- `clock_channel`：时钟输出通道号（24~39）
- `data_channel`：数据输出通道号（24~39）
- `resetn_channel`：复位输出通道号（24~39）
- `reset_idle_state`：复位线空闲状态，可选 `"initial"`、`"low"`、`"high"`、`"z"`
- `data`：一个对象，键为数据位名称，值为 0 或 1

## 使用方法

1. 编辑 `config.json`，根据示例添加一个或多个配置项
2. 连接 Digilent Digital Discovery 设备
3. 运行主程序：
   ```powershell
   python main.py
   ```
4. 按提示操作：  
   - 按回车写入所有配置项中的数据序列  
   - 输入 `q` 并回车退出程序

## 注意事项

- 确保 JSON 文件格式正确，否则程序会报错并提示具体字段问题
- 通道号不得重复且需在 24~39 范围内
- `data` 内的值仅能为 0 或 1
