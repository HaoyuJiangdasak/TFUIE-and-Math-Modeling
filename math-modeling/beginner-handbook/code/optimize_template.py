import numpy as np  # 导入数组和范数计算工具
from scipy.optimize import minimize, least_squares  # 导入约束优化和残差向量拟合求解器

def objective(z):  # 定义无量纲目标函数，z 是两个决策变量组成的数组
    return (z[0] - 2.0)**2 + (z[1] - 1.0)**2  # 计算到理想点二一的平方距离，越小越好

def gradient(z):  # 定义目标函数的一阶偏导数组
    return np.array([2.0 * (z[0] - 2.0), 2.0 * (z[1] - 1.0)])  # 返回分别对两个变量求偏导的结果

constraint = {"type": "ineq", "fun": lambda z: 2.0 - z[0] - z[1], "jac": lambda z: np.array([-1.0, -1.0])}  # SciPy 的不等式函数必须大于等于零，表示两变量之和不超过二
starts = [np.array([0.2, 0.2]), np.array([1.8, 0.1]), np.array([0.1, 1.8])]  # 给出三个不同的可行初值供交叉验证
results = []  # 创建列表保存每次优化的完整结果
for start in starts:  # 从每个初值独立求解同一问题
    result = minimize(objective, start, jac=gradient, method="SLSQP", bounds=[(0.0, 2.0), (0.0, 2.0)], constraints=[constraint], options={"ftol": 1e-12, "maxiter": 200})  # 指定目标、梯度、边界、不等式和迭代精度
    assert result.success, result.message  # 如果优化器未正常终止就显示失败原因
    assert constraint["fun"](result.x) >= -1e-8, "不满足总量约束"  # 独立检查最终点是否可行
    assert np.all(result.x >= -1e-8), "不满足非负边界"  # 独立检查非负性
    results.append(result)  # 保存此次计算结果供比较
best = min(results, key=lambda result: result.fun)  # 从所有可行成功结果中选取目标值最小者
assert np.linalg.norm(best.x - np.array([1.5, 0.5])) < 1e-6, "未接近解析最优解"  # 用严格凸例题的解析解检验算法实现
print("约束最优变量:", best.x, "目标值:", best.fun)  # 输出最佳决策变量和目标值

times = np.linspace(0.0, 30.0, 31)  # 生成三十一个观测时间，单位为秒
data = 20.0 + 70.0 * np.exp(-0.08 * times)  # 生成无噪声教学数据，实际比赛应替换为真实温度测量值
sigma = 0.5  # 设置温度误差的参考标准差，单位为摄氏度

def residual(z):  # 定义残差向量函数，z 的两个分量都已经无量纲化
    cooling_rate = 0.1 * z[0]  # 把第一个无量纲参数换回每秒的冷却系数
    ambient_temperature = 20.0 * z[1]  # 把第二个无量纲参数换回摄氏度的环境温度
    prediction = ambient_temperature + (90.0 - ambient_temperature) * np.exp(-cooling_rate * times)  # 计算给定参数下的模型温度
    return (prediction - data) / sigma  # 返回按误差尺度归一化的无量纲残差数组

fit = least_squares(residual, [0.5, 0.5], bounds=([0.01, 0.0], [5.0, 3.0]), method="trf", xtol=1e-12, ftol=1e-12, gtol=1e-12)  # 在物理允许的参数范围内拟合残差向量
assert fit.success, fit.message  # 检查非线性最小二乘是否成功终止
estimated = np.array([0.1 * fit.x[0], 20.0 * fit.x[1]])  # 恢复有物理单位的冷却系数和环境温度
assert np.allclose(estimated, [0.08, 20.0], rtol=1e-6, atol=1e-6), "无噪声参数恢复失败"  # 用已知生成参数检查参数识别流程
print("拟合冷却系数（每秒）和环境温度（摄氏度）:", estimated)  # 输出拟合结果和对应单位
