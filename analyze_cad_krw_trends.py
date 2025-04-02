import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
import os

# 데이터 로드
try:
    # 일별 데이터 로드
    daily_data = pd.read_csv('/home/ubuntu/cad_krw_analysis/historical_cad_krw_rates.csv')
    daily_data['Date'] = pd.to_datetime(daily_data['Date'])
    daily_data = daily_data.sort_values('Date')
    
    # 월별 데이터 로드
    monthly_data = pd.read_csv('/home/ubuntu/cad_krw_analysis/monthly_avg_cad_krw_rates.csv')
    monthly_data['Month'] = pd.to_datetime(monthly_data['Month'] + '-01')
    monthly_data = monthly_data.sort_values('Month')
    
    # 통계 요약 로드
    with open('/home/ubuntu/cad_krw_analysis/cad_krw_stats_summary.json', 'r') as f:
        stats = json.load(f)
    
    # 결과 디렉토리 생성
    os.makedirs('/home/ubuntu/cad_krw_analysis/charts', exist_ok=True)
    
    # 1. 일별 환율 추세 그래프
    plt.figure(figsize=(12, 6))
    plt.plot(daily_data['Date'], daily_data['Rate'], 'b-')
    plt.title('CAD/KRW 일별 환율 추세 (1년)')
    plt.xlabel('날짜')
    plt.ylabel('환율 (KRW)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/cad_krw_analysis/charts/daily_trend.png')
    
    # 2. 월별 평균 환율 추세 그래프
    plt.figure(figsize=(12, 6))
    plt.plot(monthly_data['Month'], monthly_data['Average Rate'], 'r-o')
    plt.title('CAD/KRW 월별 평균 환율 추세')
    plt.xlabel('월')
    plt.ylabel('평균 환율 (KRW)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/cad_krw_analysis/charts/monthly_trend.png')
    
    # 3. 이동평균선 추가한 추세 그래프
    plt.figure(figsize=(12, 6))
    plt.plot(daily_data['Date'], daily_data['Rate'], 'b-', label='일별 환율')
    
    # 20일 이동평균
    daily_data['MA20'] = daily_data['Rate'].rolling(window=20).mean()
    plt.plot(daily_data['Date'], daily_data['MA20'], 'r-', label='20일 이동평균')
    
    # 60일 이동평균
    daily_data['MA60'] = daily_data['Rate'].rolling(window=60).mean()
    plt.plot(daily_data['Date'], daily_data['MA60'], 'g-', label='60일 이동평균')
    
    plt.title('CAD/KRW 환율 추세 및 이동평균선')
    plt.xlabel('날짜')
    plt.ylabel('환율 (KRW)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/cad_krw_analysis/charts/moving_averages.png')
    
    # 4. 최근 3개월 추세 확대 그래프
    three_months_ago = daily_data['Date'].max() - pd.Timedelta(days=90)
    recent_data = daily_data[daily_data['Date'] >= three_months_ago]
    
    plt.figure(figsize=(12, 6))
    plt.plot(recent_data['Date'], recent_data['Rate'], 'b-')
    plt.title('CAD/KRW 최근 3개월 환율 추세')
    plt.xlabel('날짜')
    plt.ylabel('환율 (KRW)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/cad_krw_analysis/charts/recent_3months.png')
    
    # 5. 변동성 분석 (일별 변화율)
    daily_data['Change'] = daily_data['Rate'].pct_change() * 100
    
    plt.figure(figsize=(12, 6))
    plt.bar(daily_data['Date'], daily_data['Change'], color='blue', alpha=0.7)
    plt.title('CAD/KRW 일별 변화율 (%)')
    plt.xlabel('날짜')
    plt.ylabel('변화율 (%)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/cad_krw_analysis/charts/daily_volatility.png')
    
    # 6. 추세 분석 (선형 회귀)
    # 최근 6개월 데이터에 대한 선형 회귀
    six_months_ago = daily_data['Date'].max() - pd.Timedelta(days=180)
    recent_6m_data = daily_data[daily_data['Date'] >= six_months_ago].copy()
    
    # 날짜를 숫자로 변환 (선형 회귀용)
    recent_6m_data['Days'] = (recent_6m_data['Date'] - recent_6m_data['Date'].min()).dt.days
    
    # 선형 회귀 계산
    x = recent_6m_data['Days'].values.reshape(-1, 1)
    y = recent_6m_data['Rate'].values
    
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(x, y)
    
    # 회귀선 예측
    recent_6m_data['Trend'] = model.predict(x)
    
    # 추세 방향 및 기울기
    slope = model.coef_[0]
    trend_direction = "상승" if slope > 0 else "하락"
    monthly_change = slope * 30  # 한 달 동안의 예상 변화
    
    plt.figure(figsize=(12, 6))
    plt.scatter(recent_6m_data['Date'], recent_6m_data['Rate'], color='blue', alpha=0.5, label='실제 환율')
    plt.plot(recent_6m_data['Date'], recent_6m_data['Trend'], 'r-', label='추세선')
    
    # 한 달 후 예측 지점
    last_day = recent_6m_data['Days'].max()
    next_month_day = last_day + 30
    next_month_prediction = model.intercept_ + model.coef_[0] * next_month_day
    
    # 현재 마지막 날짜에서 30일 후의 날짜
    last_date = recent_6m_data['Date'].max()
    next_month_date = last_date + pd.Timedelta(days=30)
    
    plt.scatter([next_month_date], [next_month_prediction], color='green', s=100, label='한 달 후 예측')
    
    plt.title(f'CAD/KRW 6개월 추세 분석 (추세: {trend_direction})')
    plt.xlabel('날짜')
    plt.ylabel('환율 (KRW)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/cad_krw_analysis/charts/trend_prediction.png')
    
    # 분석 결과 저장
    analysis_results = {
        "current_rate": stats["current_rate"],
        "trend_direction_6m": trend_direction,
        "monthly_change_rate": monthly_change,
        "next_month_prediction": next_month_prediction,
        "prediction_date": next_month_date.strftime('%Y-%m-%d'),
        "avg_daily_volatility": daily_data['Change'].abs().mean(),
        "max_daily_volatility": daily_data['Change'].abs().max(),
        "recent_3m_trend": "상승" if recent_data['Rate'].iloc[-1] > recent_data['Rate'].iloc[0] else "하락",
        "recent_3m_change_percent": ((recent_data['Rate'].iloc[-1] - recent_data['Rate'].iloc[0]) / recent_data['Rate'].iloc[0]) * 100,
        "ma20_position": "상승세" if daily_data['Rate'].iloc[-1] > daily_data['MA20'].iloc[-1] else "하락세",
        "ma_crossover": "골든크로스" if (daily_data['MA20'].iloc[-1] > daily_data['MA60'].iloc[-1]) and (daily_data['MA20'].iloc[-20] < daily_data['MA60'].iloc[-20]) else 
                        "데드크로스" if (daily_data['MA20'].iloc[-1] < daily_data['MA60'].iloc[-1]) and (daily_data['MA20'].iloc[-20] > daily_data['MA60'].iloc[-20]) else "없음"
    }
    
    with open('/home/ubuntu/cad_krw_analysis/trend_analysis_results.json', 'w') as f:
        json.dump(analysis_results, f, indent=4)
    
    # 분석 결과 요약 텍스트 파일 생성
    with open('/home/ubuntu/cad_krw_analysis/trend_analysis_summary.txt', 'w') as f:
        f.write("# CAD/KRW 환율 추세 분석 요약\n\n")
        f.write(f"## 현재 환율 정보\n")
        f.write(f"- 현재 환율: {stats['current_rate']} KRW\n")
        f.write(f"- 1년 최저: {stats['min_rate_1y']} KRW\n")
        f.write(f"- 1년 최고: {stats['max_rate_1y']} KRW\n")
        f.write(f"- 1년 평균: {stats['avg_rate_1y']:.2f} KRW\n")
        f.write(f"- 6개월 변화율: {stats['six_month_change_percent']}\n\n")
        
        f.write(f"## 추세 분석\n")
        f.write(f"- 최근 6개월 추세: {trend_direction}\n")
        f.write(f"- 월간 변화율: {monthly_change:.2f} KRW\n")
        f.write(f"- 한 달 후 예상 환율 ({next_month_date.strftime('%Y-%m-%d')}): {next_month_prediction:.2f} KRW\n")
        f.write(f"- 최근 3개월 추세: {analysis_results['recent_3m_trend']}\n")
        f.write(f"- 최근 3개월 변화율: {analysis_results['recent_3m_change_percent']:.2f}%\n\n")
        
        f.write(f"## 기술적 지표\n")
        f.write(f"- 20일 이동평균 대비: {analysis_results['ma20_position']}\n")
        f.write(f"- 이동평균선 교차: {analysis_results['ma_crossover']}\n")
        f.write(f"- 평균 일일 변동성: {analysis_results['avg_daily_volatility']:.2f}%\n")
        f.write(f"- 최대 일일 변동성: {analysis_results['max_daily_volatility']:.2f}%\n\n")
        
        f.write(f"## 결론\n")
        if trend_direction == "상승":
            f.write(f"CAD/KRW 환율은 최근 6개월간 상승 추세를 보이고 있으며, 이 추세가 지속된다면 한 달 후에는 현재보다 약 {monthly_change:.2f} KRW 상승한 {next_month_prediction:.2f} KRW에 도달할 것으로 예상됩니다.\n")
        else:
            f.write(f"CAD/KRW 환율은 최근 6개월간 하락 추세를 보이고 있으며, 이 추세가 지속된다면 한 달 후에는 현재보다 약 {abs(monthly_change):.2f} KRW 하락한 {next_month_prediction:.2f} KRW에 도달할 것으로 예상됩니다.\n")
    
    print("환율 추세 분석 완료")
    print(f"현재 환율: {stats['current_rate']} KRW")
    print(f"추세 방향 (6개월): {trend_direction}")
    print(f"한 달 후 예상 환율: {next_month_prediction:.2f} KRW")
    
except Exception as e:
    print(f"오류 발생: {str(e)}")
