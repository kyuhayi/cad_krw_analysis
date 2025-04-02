import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

# 데이터 로드
try:
    # 추세 분석 결과 로드
    with open('/home/ubuntu/cad_krw_analysis/trend_analysis_results.json', 'r') as f:
        trend_analysis = json.load(f)
    
    # 경제적 요인 분석 결과 로드
    with open('/home/ubuntu/cad_krw_analysis/economic_factors.json', 'r') as f:
        economic_factors = json.load(f)
    
    # 통계 요약 로드
    with open('/home/ubuntu/cad_krw_analysis/cad_krw_stats_summary.json', 'r') as f:
        stats_summary = json.load(f)
    
    # 일별 데이터 로드
    daily_data = pd.read_csv('/home/ubuntu/cad_krw_analysis/historical_cad_krw_rates.csv')
    daily_data['Date'] = pd.to_datetime(daily_data['Date'])
    
    # 결과 디렉토리 확인
    os.makedirs('/home/ubuntu/cad_krw_analysis/charts', exist_ok=True)
    
    # 1. 향후 1개월 예측 시각화
    # 최근 3개월 데이터 추출
    three_months_ago = daily_data['Date'].max() - pd.Timedelta(days=90)
    recent_data = daily_data[daily_data['Date'] >= three_months_ago].copy()
    
    # 날짜를 숫자로 변환 (선형 회귀용)
    recent_data['Days'] = (recent_data['Date'] - recent_data['Date'].min()).dt.days
    
    # 선형 회귀 계산
    from sklearn.linear_model import LinearRegression
    X = recent_data['Days'].values.reshape(-1, 1)
    y = recent_data['Rate'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    # 향후 30일 예측
    future_days = np.arange(recent_data['Days'].max() + 1, recent_data['Days'].max() + 31)
    future_dates = [recent_data['Date'].max() + timedelta(days=i+1) for i in range(30)]
    future_rates = model.predict(future_days.reshape(-1, 1))
    
    # 예측 데이터프레임 생성
    forecast_df = pd.DataFrame({
        'Date': future_dates,
        'Predicted_Rate': future_rates
    })
    
    # 예측 그래프 생성
    plt.figure(figsize=(12, 6))
    plt.plot(recent_data['Date'], recent_data['Rate'], 'b-', label='실제 환율')
    plt.plot(forecast_df['Date'], forecast_df['Predicted_Rate'], 'r--', label='예측 환율')
    
    # 현재 환율과 한 달 후 예측 환율 표시
    current_rate = recent_data['Rate'].iloc[-1]
    one_month_later_rate = forecast_df['Predicted_Rate'].iloc[-1]
    
    plt.scatter([recent_data['Date'].iloc[-1]], [current_rate], color='blue', s=100, zorder=5)
    plt.scatter([forecast_df['Date'].iloc[-1]], [one_month_later_rate], color='red', s=100, zorder=5)
    
    plt.annotate(f'현재: {current_rate:.2f} KRW', 
                 xy=(recent_data['Date'].iloc[-1], current_rate),
                 xytext=(10, -20), textcoords='offset points',
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.2'))
    
    plt.annotate(f'한 달 후 예측: {one_month_later_rate:.2f} KRW', 
                 xy=(forecast_df['Date'].iloc[-1], one_month_later_rate),
                 xytext=(10, 20), textcoords='offset points',
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.2'))
    
    plt.title('CAD/KRW 향후 1개월 환율 예측')
    plt.xlabel('날짜')
    plt.ylabel('환율 (KRW)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/cad_krw_analysis/charts/one_month_forecast.png')
    
    # 2. 시나리오 분석 (낙관적, 중립적, 비관적 시나리오)
    # 변동성 계산
    volatility = daily_data['Rate'].pct_change().std()
    
    # 시나리오 생성
    optimistic_rates = future_rates * (1 + volatility * 2)  # 낙관적 시나리오 (2 표준편차 상승)
    pessimistic_rates = future_rates * (1 - volatility * 2)  # 비관적 시나리오 (2 표준편차 하락)
    
    # 시나리오 그래프 생성
    plt.figure(figsize=(12, 6))
    plt.plot(recent_data['Date'], recent_data['Rate'], 'b-', label='실제 환율')
    plt.plot(forecast_df['Date'], forecast_df['Predicted_Rate'], 'g-', label='기본 예측')
    plt.plot(forecast_df['Date'], optimistic_rates, 'r--', label='낙관적 시나리오')
    plt.plot(forecast_df['Date'], pessimistic_rates, 'y--', label='비관적 시나리오')
    
    plt.title('CAD/KRW 환율 시나리오 분석')
    plt.xlabel('날짜')
    plt.ylabel('환율 (KRW)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/cad_krw_analysis/charts/scenario_analysis.png')
    
    # 3. 매수/매도 결정 지표 시각화
    # 현재 환율과 예측 환율의 차이 계산
    rate_change = one_month_later_rate - current_rate
    rate_change_percent = (rate_change / current_rate) * 100
    
    # 매수/매도 결정 지표 생성
    decision_factors = {
        "현재_환율": current_rate,
        "한달후_예측_환율": one_month_later_rate,
        "변화량": rate_change,
        "변화율": rate_change_percent,
        "추세_방향": trend_analysis["trend_direction_6m"],
        "기술적_지표": trend_analysis["ma20_position"],
        "이동평균선_교차": trend_analysis["ma_crossover"],
        "경제_지표_차이": {
            "GDP_성장률_차이": economic_factors["캐나다"]["GDP_성장률"] - economic_factors["한국"]["GDP_성장률"],
            "물가상승률_차이": economic_factors["캐나다"]["물가상승률"] - economic_factors["한국"]["소비자물가"]
        },
        "시나리오": {
            "낙관적": optimistic_rates[-1],
            "기본": future_rates[-1],
            "비관적": pessimistic_rates[-1]
        },
        "매수_매도_신호": "매수" if rate_change > 0 else "매도" if rate_change < 0 else "관망"
    }
    
    # 결정 지표 저장
    with open('/home/ubuntu/cad_krw_analysis/decision_factors.json', 'w') as f:
        json.dump(decision_factors, f, indent=4, ensure_ascii=False)
    
    # 매수/매도 결정 시각화
    plt.figure(figsize=(10, 6))
    
    # 게이지 차트 생성
    gauge_value = (rate_change_percent + 5) / 10  # -5% ~ +5% 범위를 0~1로 정규화
    gauge_value = max(0, min(1, gauge_value))  # 0~1 범위로 제한
    
    # 게이지 색상 설정
    if decision_factors["매수_매도_신호"] == "매수":
        color = 'green'
    elif decision_factors["매수_매도_신호"] == "매도":
        color = 'red'
    else:
        color = 'gray'
    
    # 반원형 게이지 생성
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 배경 반원 (회색)
    background = np.linspace(0, np.pi, 100)
    ax.plot(np.cos(background), np.sin(background), 'lightgray', linewidth=20)
    
    # 값 표시 반원
    value_arc = np.linspace(0, np.pi * gauge_value, 100)
    ax.plot(np.cos(value_arc), np.sin(value_arc), color, linewidth=20)
    
    # 텍스트 추가
    ax.text(0, -0.2, f"{decision_factors['매수_매도_신호']}", 
            ha='center', va='center', fontsize=24, color=color)
    ax.text(0, -0.4, f"예상 변화율: {rate_change_percent:.2f}%", 
            ha='center', va='center', fontsize=16)
    
    # 축 설정
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-0.6, 1.1)
    ax.axis('off')
    
    plt.title('CAD/KRW 환율 매수/매도 신호')
    plt.tight_layout()
    plt.savefig('/home/ubuntu/cad_krw_analysis/charts/buy_sell_signal.png')
    
    # 4. 환율 전망 요약 텍스트 파일 생성
    with open('/home/ubuntu/cad_krw_analysis/exchange_rate_forecast.txt', 'w') as f:
        f.write("# CAD/KRW 환율 1개월 전망 분석\n\n")
        
        f.write("## 현재 환율 정보\n")
        f.write(f"- 현재 환율: {current_rate:.2f} KRW\n")
        f.write(f"- 1년 최저: {stats_summary['min_rate_1y']} KRW\n")
        f.write(f"- 1년 최고: {stats_summary['max_rate_1y']} KRW\n")
        f.write(f"- 1년 평균: {stats_summary['avg_rate_1y']:.2f} KRW\n\n")
        
        f.write("## 향후 1개월 예측\n")
        f.write(f"- 한 달 후 예상 환율 ({forecast_df['Date'].iloc[-1].strftime('%Y-%m-%d')}): {one_month_later_rate:.2f} KRW\n")
        f.write(f"- 예상 변화량: {rate_change:.2f} KRW\n")
        f.write(f"- 예상 변화율: {rate_change_percent:.2f}%\n\n")
        
        f.write("## 시나리오 분석\n")
        f.write(f"- 낙관적 시나리오: {optimistic_rates[-1]:.2f} KRW (현재 대비 {((optimistic_rates[-1]/current_rate)-1)*100:.2f}%)\n")
        f.write(f"- 기본 시나리오: {future_rates[-1]:.2f} KRW (현재 대비 {((future_rates[-1]/current_rate)-1)*100:.2f}%)\n")
        f.write(f"- 비관적 시나리오: {pessimistic_rates[-1]:.2f} KRW (현재 대비 {((pessimistic_rates[-1]/current_rate)-1)*100:.2f}%)\n\n")
        
        f.write("## 기술적 지표\n")
        f.write(f"- 추세 방향: {trend_analysis['trend_direction_6m']}\n")
        f.write(f"- 20일 이동평균 대비: {trend_analysis['ma20_position']}\n")
        f.write(f"- 이동평균선 교차: {trend_analysis['ma_crossover']}\n\n")
        
        f.write("## 경제적 요인\n")
        f.write(f"- 캐나다 GDP 성장률: {economic_factors['캐나다']['GDP_성장률']}% (한국: {economic_factors['한국']['GDP_성장률']}%)\n")
        f.write(f"- 캐나다 물가상승률: {economic_factors['캐나다']['물가상승률']}% (한국 소비자물가: {economic_factors['한국']['소비자물가']}%)\n")
        f.write(f"- 캐나다 금리: {economic_factors['캐나다']['금리']}%\n\n")
        
        f.write("## 매수/매도 신호\n")
        f.write(f"- 추천: {decision_factors['매수_매도_신호']}\n")
        if decision_factors['매수_매도_신호'] == "매수":
            f.write("- 이유: 향후 1개월 내 CAD/KRW 환율이 상승할 것으로 예상되어 캐나다 달러 매수가 유리할 수 있습니다.\n")
        elif decision_factors['매수_매도_신호'] == "매도":
            f.write("- 이유: 향후 1개월 내 CAD/KRW 환율이 하락할 것으로 예상되어 캐나다 달러 매도가 유리할 수 있습니다.\n")
        else:
            f.write("- 이유: 향후 1개월 내 CAD/KRW 환율의 변동이 미미할 것으로 예상되어 현재 포지션 유지가 권장됩니다.\n")
        
        f.write("\n## 결론\n")
        if rate_change > 0:
            f.write(f"CAD/KRW 환율은 현재 {current_rate:.2f} KRW에서 한 달 후 {one_month_later_rate:.2f} KRW로 상승할 것으로 예상됩니다. ")
            f.write(f"이는 {rate_change_percent:.2f}%의 상승을 의미하며, 캐나다 달러의 강세가 예상됩니다. ")
            f.write("캐나다의 높은 GDP 성장률과 물가상승률, 그리고 상대적으로 높은 금리가 캐나다 달러 강세의 주요 요인으로 작용하고 있습니다. ")
            f.write("따라서 현재 시점에서 캐나다 달러 매수를 고려해볼 수 있습니다.")
        else:
            f.write(f"CAD/KRW 환율은 현재 {current_rate:.2f} KRW에서 한 달 후 {one_month_later_rate:.2f} KRW로 하락할 것으로 예상됩니다. ")
            f.write(f"이는 {abs(rate_change_percent):.2f}%의 하락을 의미하며, 캐나다 달러의 약세가 예상됩니다. ")
            f.write("글로벌 경제 불확실성과 원자재 가격 변동이 캐나다 달러 약세의 주요 요인으로 작용할 수 있습니다. ")
            f.write("따라서 현재 시점에서 캐나다 달러 매도를 고려해볼 수 있습니다.")
    
    print("환율 전망 분석 완료")
    print(f"현재 환율: {current_rate:.2f} KRW")
    print(f"한 달 후 예상 환율: {one_month_later_rate:.2f} KRW")
    print(f"추천: {decision_factors['매수_매도_신호']}")
    
except Exception as e:
    print(f"오류 발생: {str(e)}")
