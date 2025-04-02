import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json
from datetime import datetime, timedelta

# 클라이언트 초기화
client = ApiClient()

# CAD/KRW 환율 데이터 가져오기 (CAD/KRW는 직접적인 심볼이 없으므로 CADKRW=X 사용)
try:
    # 현재 환율 데이터
    cad_krw_data = client.call_api('YahooFinance/get_stock_chart', query={
        'symbol': 'CADKRW=X',
        'interval': '1d',
        'range': '1mo'
    })
    
    # 결과를 파일로 저장
    with open('/home/ubuntu/cad_krw_analysis/current_cad_krw_data.json', 'w') as f:
        json.dump(cad_krw_data, f, indent=4)
    
    # 최신 환율 정보 추출 및 출력
    if cad_krw_data and 'chart' in cad_krw_data and 'result' in cad_krw_data['chart'] and len(cad_krw_data['chart']['result']) > 0:
        result = cad_krw_data['chart']['result'][0]
        
        # 메타 정보
        meta = result['meta']
        current_rate = meta.get('regularMarketPrice', 'N/A')
        currency = meta.get('currency', 'N/A')
        
        # 타임스탬프 및 종가 데이터
        timestamps = result['timestamp']
        close_prices = result['indicators']['quote'][0]['close']
        
        # 최신 데이터 추출
        latest_data = {
            'current_rate': current_rate,
            'currency': currency,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'recent_rates': []
        }
        
        # 최근 5일 데이터 추출
        for i in range(min(5, len(timestamps))):
            if i < len(close_prices) and close_prices[-(i+1)] is not None:
                date = datetime.fromtimestamp(timestamps[-(i+1)]).strftime('%Y-%m-%d')
                latest_data['recent_rates'].append({
                    'date': date,
                    'rate': close_prices[-(i+1)]
                })
        
        # 결과 저장
        with open('/home/ubuntu/cad_krw_analysis/latest_cad_krw_rate.json', 'w') as f:
            json.dump(latest_data, f, indent=4)
        
        print(f"현재 CAD/KRW 환율: {current_rate} {currency}")
        print(f"데이터 수집 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("환율 데이터를 가져오는 데 문제가 발생했습니다.")
except Exception as e:
    print(f"오류 발생: {str(e)}")
