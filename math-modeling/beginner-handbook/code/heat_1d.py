import numpy as np  # 导入数组、三角函数和指数函数
from scipy.linalg import solve_banded  # 导入带状矩阵求解器，避免对三对角矩阵求逆

length = 1.0  # 设置杆长，单位为米
alpha = 0.01  # 设置热扩散率，单位为平方米每秒
amplitude = 10.0  # 设置初始温度波形的最大幅值，单位为摄氏度
end_time = 0.5  # 设置最终计算时间，单位为秒

def run(intervals, method):  # 定义一次热传导计算，intervals 是空间区间数，method 是方法名称
    dx = length / intervals  # 用总长除以区间数得到空间步长，单位为米
    target_dt = 0.4 * dx**2 / alpha  # 选择满足显式稳定条件的目标时间步长，单位为秒
    steps = int(np.ceil(end_time / target_dt))  # 向上取整时间步数以保证实际步长不超过目标值
    dt = end_time / steps  # 调整实际步长使最后一步恰好到达终点
    ratio = alpha * dt / dx**2  # 计算无量纲扩散比，也叫网格傅里叶数
    assert ratio <= 0.5, "显式稳定性条件不满足"  # 检查本模板使用的统一时间网格满足显式条件
    x = np.linspace(0.0, length, intervals + 1)  # 生成含左右端点的空间坐标
    u = amplitude * np.sin(np.pi * x / length)  # 设置两端为零的正弦初温，单位为摄氏度
    u[[0, -1]] = 0.0  # 把浮点三角函数产生的端点舍入误差清零
    theta = {"explicit": 0.0, "implicit": 1.0, "cn": 0.5}[method]  # 统一表达显式、后向欧拉和克兰克尼科尔森方法
    count = intervals - 1  # 计算内部未知温度点的个数
    band = np.zeros((3, count))  # 创建三行带状矩阵存储格式，分别存上对角、主对角和下对角
    band[0, 1:] = -theta * ratio  # 填写上对角系数，第一个存储位置不使用
    band[1, :] = 1.0 + 2.0 * theta * ratio  # 填写主对角系数
    band[2, :-1] = -theta * ratio  # 填写下对角系数，最后一个存储位置不使用
    for step in range(steps):  # 按时间顺序重复更新温度场
        rhs = u[1:-1] + (1.0 - theta) * ratio * (u[:-2] - 2.0 * u[1:-1] + u[2:])  # 计算旧时刻温度形成的右端项
        u[1:-1] = solve_banded((1, 1), band, rhs)  # 解三对角方程并写入内部新温度，两端保持零
    exact = amplitude * np.sin(np.pi * x / length) * np.exp(-alpha * (np.pi / length)**2 * end_time)  # 计算精确的正弦衰减解
    error = np.max(np.abs(u - exact))  # 计算所有空间点的最大温度误差
    assert np.min(u) >= -1e-10, "出现不合理的负温度"  # 对本非负初边值例题检查非负性
    assert np.max(u) <= amplitude + 1e-10, "出现不合理的温度增长"  # 对本无热源例题检查最大值不会增加
    assert np.max(np.abs(u[[0, -1]])) < 1e-12, "边界条件未保持"  # 检查两端恒温条件
    return error  # 返回该网格的误差，单位为摄氏度

for method in ("explicit", "implicit", "cn"):  # 依次比较三个时间离散方法
    coarse_error = run(40, method)  # 用四十个空间区间计算较粗网格误差
    fine_error = run(80, method)  # 空间步长减半且时间步长约缩小到四分之一
    observed_order = np.log(coarse_error / fine_error) / np.log(2.0)  # 根据误差比例估计联合加密时的空间收敛阶
    assert fine_error < coarse_error / 3.0, "网格加密没有获得预期误差下降"  # 验证与二阶联合收敛相容的误差降低
    print(method, "粗网格误差=", coarse_error, "细网格误差=", fine_error, "联合收敛阶=", observed_order)  # 打印验证结果
