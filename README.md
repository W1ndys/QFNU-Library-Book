# QFNU-Library-Book

曲阜师范大学图书馆预约程序

## 快速启动

### 前提条件

- Python 3.12.1（Python 3.10+）
- 运行环境：Windows 10、Ubuntu 20.04、MacOS 12.0+

### 安装依赖

```
pip install -r requirements.txt
```

### 配置程序

打开配置文件 `py/config.json` ，根据注释修改配置项。

1. `USERNAME`：图书馆账号
2. `PASSWORD`：图书馆密码

### 程序介绍

相较于原作者的程序，本项目删除了预约当日的设置，只保留预约明天的设置。

- `py/get_seat_tomorrow_mode_1.py`：预约模式 1，预约明天的座位，仅适用于西校区图书馆的三个自习室，个人优选了有插座的位置。
- `py/get_seat_tomorrow_mode_2.py`：预约模式 2，预约明天的座位，指定模式，请预先根据 json/seat_info 中各个自习室的真实位置('name')获取座位代号('id')，请输入对应自习室的对应 id。
- `py/get_seat_tomorrow_mode_3.py`：预约模式 3，预约明天的座位，默认模式，全随机预约，速度最快，成功的概率最大。
- `py/sign_out.py`：签退程序，签退图书馆。
- `py/checkin.py`：签到程序，签到图书馆。该脚本属于**违规操作**，请务必**谨慎使用**。请务必在**合理的时间段内执行**脚本

## 开源许可协议

本项目是由 [W1ndys](https://github.com/W1ndys) 基于 [上杉九月](https://github.com/sakurasep) 的 开源项目 [qfnuLibraryBook](https://github.com/sakurasep/qfnuLibraryBook) 二次开发，使用 CC BY-NC 4.0 协议进行授权，拷贝、分享或基于此进行创作时请遵守协议内容：

```
Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)

This is a human-readable summary of (and not a substitute for) the license. You are free to:

Share — copy and redistribute the material in any medium or format
Adapt — remix, transform, and build upon the material

The licensor cannot revoke these freedoms as long as you follow the license terms.
Under the following terms:

Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

NonCommercial — You may not use the material for commercial purposes.

No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

Notices:

You do not have to comply with the license for elements of the material in the public domain or where your use is permitted by an applicable exception or limitation.
No warranties are given. The license may not give you all of the permissions necessary for your intended use. For example, other rights such as publicity, privacy, or moral rights may limit how you use the material.
```
