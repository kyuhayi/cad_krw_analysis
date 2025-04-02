import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json
from datetime import datetime, timedelta

# 클라이언트 초기화
client = ApiClient()

# CAD/KRW 환율 역사적 데이터 가져오기 (1년 데이터)
try:
    # 역사적 환율 데이터
    historical_data = client.call_api('YahooFinance/get_stock_chart', query={
        'symbol': 'CADKRW=X',
        'interval': '1d',
        'range': '1y'  # 1년 데이터
    })
    
    # 결과를 파일로 저장
    with open('/home/ubuntu/cad_krw_analysis/historical_cad_krw_data.json', 'w') as f:
        json.dump(historical_data, f, indent=4)
    
    # 데이터 처리 및 분석용 CSV 파일 생성
    if historical_data and 'chart' in historical_data and 'result' in historical_data['chart'] and len(historical_data['chart']['result']) > 0:
        result = historical_data['chart']['result'][0]
        
        # 타임스탬프 및 종가 데이터
        timestamps = result['timestamp']
        close_prices = result['indicators']['quote'][0]['close']
        
        # CSV 파일 생성
        with open('/home/ubuntu/cad_krw_analysis/historical_cad_krw_rates.csv', 'w') as f:
            f.write("Date,Rate\n")
            for i in range(len(timestamps)):
                if i < len(close_prices) and close_prices[i] is not None:
                    date = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d')
                    f.write(f"{date},{close_prices[i]}\n")
        
        # 월별 평균 계산
        monthly_data = {}
        for i in range(len(timestamps)):
            if i < len(close_prices) and close_prices[i] is not None:
                date = datetime.fromtimestamp(timestamps[i])
                month_key = date.strftime('%Y-%m')
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {'sum': 0, 'count': 0}
                
                monthly_data[month_key]['sum'] += close_prices[i]
                monthly_data[month_key]['count'] += 1
        
        # 월별 평균 CSV 파일 생성
        with open('/home/ubuntu/cad_krw_analysis/monthly_avg_cad_krw_rates.csv', 'w') as f:
            f.write("Month,Average Rate\n")
            for month, data in sorted(monthly_data.items()):
                avg_rate = data['sum'] / data['count']
                f.write(f"{month},{avg_rate:.2f}\n")
        
        # 통계 요약 생성
        if len(close_prices) > 0:
            valid_prices = [p for p in close_prices if p is not None]
            if valid_prices:
                current_rate = valid_prices[-1]
                min_rate = min(valid_prices)
                max_rate = max(valid_prices)
                avg_rate = sum(valid_prices) / len(valid_prices)
                
                # 6개월 전 대비 변화율
                six_months_ago_index = max(0, len(valid_prices) - 180)  # 약 6개월 전 (180일)
                if six_months_ago_index < len(valid_prices):
                    six_months_ago_rate = valid_prices[six_months_ago_index]
                    change_rate = ((current_rate - six_months_ago_rate) / six_months_ago_rate) * 100
                else:
                    change_rate = "N/A"
                
                # 통계 요약 저장
                stats = {
                    "current_rate": current_rate,
                    "min_rate_1y": min_rate,
                    "max_rate_1y": max_rate,
                    "avg_rate_1y": avg_rate,
                    "six_month_change_percent": change_rate if isinstance(change_rate, str) else f"{change_rate:.2f}%",
                    "data_period": f"{datetime.fromtimestamp(timestamps[0]).strftime('%Y-%m-%d')} to {datetime.fromtimestamp(timestamps[-1]).strftime('%Y-%m-%d')}",
                    "data_points": len(valid_prices)
                }
                
                with open('/home/ubuntu/cad_krw_analysis/cad_krw_stats_summary.json', 'w') as f:
                    json.dump(stats, f, indent=4)
        
        print(f"역사적 CAD/KRW 환율 데이터 수집 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"데이터 기간: {datetime.fromtimestamp(timestamps[0]).strftime('%Y-%m-%d')} ~ {datetime.fromtimestamp(timestamps[-1]).strftime('%Y-%m-%d')}")
        print(f"데이터 포인트 수: {len(timestamps)}")
    else:
        print("역사적 환율 데이터를 가져오는 데 문제가 발생했습니다.")
except Exception as e:
    print(f"오류 발생: {str(e)}")
