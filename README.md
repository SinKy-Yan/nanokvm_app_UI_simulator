# 帧缓冲 UI 模拟器

本目录提供一个基于 Pygame 的模拟器，用于在桌面环境调试原本需要直接写 `/dev/fb0` 的 Python 脚本。通过猴子补丁替换脚本中的 `RGB565Display`，在窗口中动态渲染设备 UI，便于开发与验证。

## 功能特性

- **Display 替换**：自动继承并替换硬件版 `RGB565Display`，复用现有绘制逻辑。
- **可选超时**：支持 `--timeout` 参数，便于自动化测试时按需退出。
- **方向匹配**：默认旋转输出，模拟与设备一致的屏幕朝向。

## 使用方法

1. **激活虚拟环境**

   ```bash
   cd simulator_app
   source nv/bin/activate
   ```

2. **运行模拟器**

   ```bash
   # 基本语法
   python simulator.py <目标脚本路径> [--timeout 秒数]

   # 示例：在父目录运行 clash 监视器，保持窗口常驻
   python simulator_app/simulator.py clash/main.py

   # 示例：调试 coin.py，并在 10 秒后自动退出
   python simulator_app/simulator.py coin.py --timeout 10
   ```

3. **退出虚拟环境**

   ```bash
   deactivate
   ```

如需调整旋转方向或缩放比例，可在 `simulator.py` 内直接修改相关常量。
