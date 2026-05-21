# model.py —— 模拟的风险预测模型
 predict_risk(people_count, weather_index, safety_factor, is_holiday=False):
    """
    参数:
        people_count: int, 人数
        weather_index: float, 天气恶劣指数 (0~1, 越大越恶劣)
        safety_factor: float, 设施安全系数 (0~1, 越大越安全)
    返回:
        risk_score: float, 风险值 (0~100)
    """
    base_risk = people_count * 0.01
    weather_impact = 1 + weather_index * 2
    safety_impact = 1 - safety_factor * 0.8
    risk_score = base_risk * weather_impact * safety_impact
    return min(risk_score, 100)
