import numpy as np  # 导入数组和指数函数工具，后文用 np 作为简称
from scipy.integrate import solve_ivp  # 导入自动选择时间步长的常微分方程求解器

ambient = 20.0  # 设置恒定环境温度，单位为摄氏度
initial = 90.0  # 设置物体初始温度，单位为摄氏度
rate = 0.08  # 设置冷却系数，单位为每秒
threshold = 40.0  # 设置停止计算的目标温度，单位为摄氏度

def rhs(t, y):  # 定义变化率函数，t 是秒，y 是保存各状态的数组
    return [-rate * (y[0] - ambient)]  # 返回温度变化率列表，单位为摄氏度每秒

def hit_threshold(t, y):  # 定义事件函数，求解器寻找这个函数等于零的时刻
    return y[0] - threshold  # 温度减去阈值，单位为摄氏度

hit_threshold.terminal = True  # 第一次满足事件条件时终止积分
hit_threshold.direction = -1  # 只检测温度从阈值上方向下穿过的事件
times = np.linspace(0.0, 60.0, 301)  # 生成希望输出的时间点，这不等于求解器内部步长
sol = solve_ivp(rhs, (0.0, 60.0), [initial], method="RK45", t_eval=times, events=hit_threshold, rtol=1e-8, atol=1e-10, max_step=0.5)  # 积分并限制内部最大步长为零点五秒
assert sol.success, sol.message  # 如果积分失败，立即显示求解器的错误说明
assert len(sol.t_events[0]) == 1, "未检测到目标温度事件"  # 验证恰好找到一个停止事件
exact = ambient + (initial - ambient) * np.exp(-rate * sol.t)  # 计算同一批输出时刻的解析温度
max_error = np.max(np.abs(sol.y[0] - exact))  # 求数值温度与解析温度的最大绝对误差，单位为摄氏度
event_exact = np.log((initial - ambient) / (threshold - ambient)) / rate  # 计算理论到达阈值时间，单位为秒
event_numeric = sol.t_events[0][0]  # 从事件结果读取数值到达时间，不能用最后一个输出采样点代替
assert max_error < 1e-5, "温度误差超出允许范围"  # 用独立解析解检查数值计算的正确性
assert abs(event_numeric - event_exact) < 1e-5, "事件时间误差超出允许范围"  # 检查事件定位精度
print("最大温度误差（摄氏度）:", max_error)  # 显示温度误差供论文验证使用
print("到达目标温度的时间（秒）:", event_numeric)  # 显示题目常要求的首次达到时刻
