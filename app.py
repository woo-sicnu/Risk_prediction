# app.py
import streamlit as st
import pandas as pd
import io
from datetime import datetime

# 导入模型
from model import predict_risk

st.set_page_config(page_title="风险预测系统", page_icon="⚠️", layout="wide")
st.title("⚠️ 风险预测系统")
st.markdown("请输入参数，系统将自动评估当前风险值。")

# ==================== 侧边栏：历史记录 ====================
st.sidebar.header("📋 历史预测记录")
if 'history' not in st.session_state:
    st.session_state.history = []

if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history)
    st.sidebar.caption(f"共 {len(history_df)} 条记录")
    # 使用 st.table 避免空行
    st.sidebar.table(history_df)

    # ----- 导出 Excel 按钮 -----
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        history_df.to_excel(writer, sheet_name='风险预测记录', index=False)
    output.seek(0)

    st.sidebar.download_button(
        label="📥 导出历史记录 (Excel)",
        data=output,
        file_name=f"风险预测记录_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_history"
    )

    if st.sidebar.button("清空历史记录"):
        st.session_state.history = []
        st.rerun()
else:
    st.sidebar.info("暂无记录，预测后将自动添加。")

# ==================== 主界面：参数输入 ====================
with st.expander("📌 输入参数", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        people = st.number_input("👥 人数", min_value=0, max_value=20000, value=500, step=50, help = "现场实际参与活动的总人数"
 )
        help = "现场实际参与活动的总人数"
        weather = st.selectbox(
            "🌧️ 天气",
            options=["晴", "多云", "小雨", "中雨", "大雨", "暴雨"],
            index=0
        )
        weather_map = {"晴": 0.0, "多云": 0.2, "小雨": 0.4, "中雨": 0.6, "大雨": 0.8, "暴雨": 1.0}
        weather_index = weather_map[weather]

    with col2:
        safety = st.number_input(
            "🛡️ 安全系数",
            min_value=0.0,
            max_value=1.0,
            value=0.8,
            step=0.01，
            format="%.2f"
            help = "安全系数必须在 0~1 之间！,越接近1越安全"
        )
        

# ==================== 参数验证 ====================
def validate_params(people, safety):
    errors = []
    if people < 0:
        errors.append("人数不能为负数！")
    if people > 20000:
        errors.append("人数超过最大承载量！")
    if safety < 0.0 or safety > 1.0:
        errors.append("安全系数必须在 0~1 之间！")
    return errors

def get_risk_level(risk):
    if risk < 30:
        return "低风险"
    elif risk < 60:
        return "中等风险"
    else:
        return "高风险"

# ==================== 显示上次预测结果 ====================
if 'last_result' in st.session_state:
    res = st.session_state.last_result
    st.subheader("预测结果")
    st.metric("⚠️ 风险值 (0-100)", f"{res['risk']:.1f}")

    # 动态进度条
    risk = res['risk']
    if risk < 30:
        bar_color = "#28a745"
        status_text = "✅ 风险较低，可正常运行。"
    elif risk < 60:
        bar_color = "#fd7e14"
        status_text = "⚠️ 中等风险，建议加强防范措施。"
    else:
        bar_color = "#dc3545"
        status_text = "🚨 高风险！建议启动应急预案！"

    st.markdown(f"""
    <div style="margin: 20px 0;">
        <div style="display: flex; align-items: center;">
            <span style="font-weight: bold; width: 50px;">低风险</span>
            <div style="flex: 1; background: #eee; border-radius: 10px; height: 30px; margin: 0 10px;">
                <div style="width: {risk}%; background: {bar_color}; height: 100%; border-radius: 10px; transition: width 0.5s ease;"></div>
            </div>
            <span style="font-weight: bold; width: 50px; text-align: right;">高风险</span>
        </div>
        <p style="font-size: 18px; font-weight: bold; color: {bar_color}; margin-top: 10px;">{status_text}</p>
    </div>
    """, unsafe_allow_html=True)

    # ----- 风险分析摘要卡片 -----
    base_risk = res['people'] * 0.01
    weather_factor = res['weather_index']
    safety_factor = res['safety']
    weather_desc = "不增加额外风险" if weather_factor < 0.3 else "小幅增加风险" if weather_factor < 0.6 else "明显增加风险"
    safety_contribution = int((1 - safety_factor) * 100)

    # 根据风险等级调整卡片颜色
    if risk < 30:
        card_border = "#28a745"
        card_bg = "#f0f8f0"
    elif risk < 60:
        card_border = "#fd7e14"
        card_bg = "#fff4e6"
    else:
        card_border = "#dc3545"
        card_bg = "#ffeaea"

    st.markdown(f"""
    <div style="background-color:{card_bg}; border-left: 5px solid {card_border}; padding: 15px; border-radius: 8px; margin-top: 15px;">
        <h4 style="margin-top: 0;">📋 风险分析摘要</h4>
        <ul style="list-style-type: none; padding-left: 0;">
            <li><b>👥 人数 ({res['people']}人)</b> → 基础风险值 <b>{base_risk:.1f}</b></li>
            <li><b>🌧️ 天气 ({res['weather']})</b> → 影响系数 <b>{weather_factor}</b>，{weather_desc}</li>
            <li><b>🛡️ 安全系数 ({safety_factor:.2f})</b> → 风险降低约 <b>{safety_contribution}%</b></li>
        </ul>
        <p style="margin-bottom: 0; font-weight: bold; color: {card_border};">
            综合风险值 <b>{risk:.1f}</b>（{get_risk_level(risk)}）
        </p>
    </div>
    """, unsafe_allow_html=True)

    del st.session_state.last_result

# ==================== 预测按钮 ====================
st.markdown("---")
predict_clicked = st.button("📊 开始预测风险", type="primary")

if predict_clicked:
    errors = validate_params(people, safety)
    if errors:
        for e in errors:
            st.error(e)
    else:
        try:
            risk = predict_risk(people, weather_index, safety)
        except Exception as e:
            st.error(f"模型计算失败：{e}")
            risk = None

        if risk is not None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            risk_level = get_risk_level(risk)
            risk_display = f"{risk:.2f} ({risk_level})"

            st.session_state.history.append({
                "时间": timestamp,
                "人数": people,
                "天气": weather,
                "安全系数": safety,
                "风险值": risk_display
            })

            st.session_state.last_result = {
                'risk': risk,
                'people': people,
                'weather': weather,
                'safety': safety,
                'weather_index': weather_index
            }

            st.rerun()

st.markdown("---")
st.caption("模型仅供参考，实际决策请结合现场情况。")
