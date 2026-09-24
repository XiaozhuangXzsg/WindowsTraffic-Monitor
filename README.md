# Win11 Traffic Widget

轻量托盘与桌面悬浮窗。依赖 Windows 11 与 Python 3.11+；无需抓包驱动或管理员权限。

## 目录

```text
Win11TrafficWidget/
├── main.py             托盘、定时器、应用入口
├── requirements.txt
├── requirements-windows.txt
├── start.cmd        首次自动安装依赖并启动
├── build-exe.cmd    在 Windows 本机生成 EXE
├── README.md
└── app/
    ├── __init__.py
    ├── autostart.py     当前用户注册表自启
    ├── geometry.py      自由拖动和可找回边界
    ├── layout.py        自适应布局与两位小数格式
    ├── monitor.py       网卡计数采样及周期切换
    ├── settings.py      外观及限额设置
    ├── topmost.py       Windows 任务栏遮挡检测与条件置顶
    ├── storage.py       JSON 原子写入
    ├── widget.py        绘制、自由拖拽及双击切换
    └── windows_usage.py Windows 用量读取
```

## 快速启动（推荐）

1. 在 Windows 11 安装 Python 3.11 或更新的版本（Python 官方 Windows 安装包），安装时勾选 Python Launcher (`py`)。已有可用版本的用户无需重复安装。
2. 先将整个 ZIP 解压到固定目录，例如 `D:\Apps\Win11TrafficWidget`；不要在压缩包预览窗口里直接运行脚本。
3. 双击 `start.cmd`；运行期间会保留命令窗口以显示错误，首次运行会创建 `.venv` 并联网安装依赖，随后在系统托盘显示蓝色向下箭头。再次启动只需双击同一文件。
4. 要生成 EXE，在这台 Windows 电脑上双击 `build-exe.cmd`，完成后在 `dist` 文件夹获取 `Win11TrafficWidget.exe`。

如果窗口没有出现，请点击任务栏右下角的托盘图标菜单“显示悬浮窗”。不要同时运行源码和打包版，否则会有两个进程写入同一份统计数据。

## 手动安装运行（PowerShell）

```powershell
cd Win11TrafficWidget
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-windows.txt
python main.py
```

若 PowerShell 限制虚拟环境激活，可以直接调用 `.\.venv\Scripts\python.exe main.py`。右键托盘图标进入设置；悬浮窗左键自由拖拽；拖动展开窗口右下角的斜线可在 84×28 到 460×300 逻辑像素范围缩放；双击切换圆形和展开形态。默认展开窗口为 190×74 逻辑像素；足够高时三项数字竖排，足够宽时三项数字横排，更小时优先显示你在设置中选择的一项，并尽可能保留本月剩余；本月剩余固定显示两位小数 GB。窗口尺寸和位置都会保存。关闭设置窗口不会退出程序。托盘菜单可退出。

设置中勾选“开机自动启动”后，登录 Windows 时使用 `--quiet` 参数仅启动托盘和流量统计，不自动打开悬浮窗；通过托盘菜单可随时显示悬浮窗。手动启动不带参数时，按上次显示状态打开。拖动结束、双击切换形态、托盘退出和系统正常结束会保存窗口位置与状态；流量数据每 10 秒保存一次。强制断电时最多可能丢失最近 10 秒的本机累计数据。

## 打包 EXE

在 Windows 上的上述环境执行：

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Win11TrafficWidget main.py
```

结果在 `dist\Win11TrafficWidget.exe`。复制 EXE 到最终固定位置后，在设置中开启开机自启；若之后移动 EXE，先关闭再重新打开该选项以更新注册表路径。源码运行时自启使用 `pythonw.exe`。

## 统计口径和限制

每秒读取 psutil 的系统全部网卡累计字节数；下载速度仅计接收字节，当日和当月用量为接收加发送。设置中 1 GB = 1024³ B。数据在 `%LOCALAPPDATA%\Win11TrafficWidget\state.json` 每 10 秒原子保存，退出及正常关机时立即保存。跨日和跨月在下一次采样时归零；跨界那一秒的流量不归入新周期。软件未运行期间、系统计数器重置期间及关机期间的用量不能回填；重启后会以当前系统计数作为新基线，避免重复计数。它不做进程级流量归因，也不会真正限制网络用量。背景图片使用绝对路径，移动或删除原图会失效。背景是自绘圆角面板，无系统 Mica/亚克力 API 依赖。多实例同时运行会影响统计，请只运行一个实例。

## Windows 11 用量来源与性能

设置 → 用量来源可以选择“本机累计（所有网卡）”或“Windows 统计（当前连接）”。Windows 模式通过公开的 `ConnectionProfile.GetNetworkUsageAsync` 读取**当前 Internet 连接配置文件**从本地午夜至当前、从本月 1 日至当前的接收加发送估算用量，每 5 分钟在后台线程更新一次；实时下载速度始终使用系统网卡字节计数。此结果并非保证与“设置 → 网络和 Internet → 数据使用量”逐字节相同：设置页可能显示过去 30 天而非自然月，连接配置文件不同、数据延迟及系统口径也会造成差异。Windows 接口不可用或组件未安装时，悬浮窗标明并临时显示本机累计值，不会将两种来源相加。此模式不修改 Windows 统计或系统流量限额。

安装完整功能请使用 `requirements-windows.txt`，仅用本机统计可安装 `requirements.txt`。打包 Windows 用量功能前请先安装前者。后台每秒采样但每 10 秒才写入 JSON，隐藏悬浮窗时停止逐秒重绘，背景图片按路径与窗口尺寸缓存；PySide6 自身仍有基础内存占用，实际内存占用需要在目标 Windows 11 设备上测量。

如果启动器显示 `No suitable Python runtime found`，请在 Windows 终端运行 `py -0p` 检查已安装版本。新版 `start.cmd` 会尝试任意已安装的 Python 3.11 及以上版本，也能尝试 `python` 命令。

悬浮窗支持移动到任务栏所在的屏幕区域，并阻止异常最大化/全屏。Windows 任务栏自身若显示在悬浮窗上层，覆盖关系仍由 Windows 决定。

升级至布局版本 8 时仅将旧版记录的窗口宽高调整为 190×74；每日、每月统计与外观偏好保持原值。以后手动缩放的尺寸继续保存。背景图片只在路径变化时解码，并缓存缩放结果；值没有显示变化时跳过重绘。84×28 是 Qt 逻辑像素，实际物理尺寸受 Windows 缩放比例影响。

任务栏置顶：当窗口与主/副屏任务栏相交时，每 400 毫秒检查一次原生窗口 Z 顺序；发现任务栏盖过悬浮窗才调用 Windows `SetWindowPos(HWND_TOPMOST, SWP_NOACTIVATE)`，不激活窗口或改变位置/大小。普通位置不执行置顶调用。系统安全桌面和特殊全屏覆盖窗口由 Windows 控制，不在此功能范围内。

位置调整：全局禁用自动贴边。松开鼠标后维持放下的位置，允许窗口部分超出屏幕边缘，但至少保留可拖回的部分。
