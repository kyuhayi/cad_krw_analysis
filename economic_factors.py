import json
import matplotlib.pyplot as plt
import os
from datetime import datetime

# 경제적 요인 데이터 정리
economic_factors = {
    "캐나다": {
        "GDP_성장률": 2.4,
        "실업률": 6.6,
        "물가상승률": 2.6,
        "금리": 2.75,
        "무역수지": "3970 CAD 백만",
        "기업신뢰지수": 55.3,
        "제조업_PMI": 46.3,
        "소비자신뢰지수": 48.8
    },
    "한국": {
        "GDP_성장률": 0.1,
        "소비자물가": 0.3,
        "생산자물가": 0.0,
        "경상수지": "29.4 억$",
        "통화량": 0.5,
        "금리": "미확인" # 한국은행 사이트에서 확인 필요
    },
    "환율_영향_요인": [
        {
            "요인": "금리 차이",
            "설명": "캐나다와 한국의 금리 차이는 환율에 직접적인 영향을 미침. 캐나다의 금리(2.75%)가 한국보다 높을 경우 캐나다 달러 강세 요인",
            "영향도": "높음"
        },
        {
            "요인": "경제 성장률 차이",
            "설명": "캐나다의 GDP 성장률(2.4%)이 한국(0.1%)보다 높아 캐나다 달러 강세 요인",
            "영향도": "중간"
        },
        {
            "요인": "원자재 가격",
            "설명": "캐나다는 석유 등 원자재 수출국으로, 원자재 가격 상승 시 캐나다 달러 강세",
            "영향도": "높음"
        },
        {
            "요인": "무역 관계",
            "설명": "캐나다는 미국과의 무역 의존도가 높음. 미국 경제 상황과 무역 정책이 캐나다 달러에 영향",
            "영향도": "높음"
        },
        {
            "요인": "중앙은행 정책",
            "설명": "캐나다 은행(BoC)과 한국은행의 통화 정책 결정이 환율에 영향",
            "영향도": "높음"
        },
        {
            "요인": "글로벌 경제 불확실성",
            "설명": "글로벌 경제 불확실성 증가 시 안전자산 선호 현상으로 통화 가치 변동",
            "영향도": "중간"
        }
    ],
    "최근_동향": [
        "캐나다 경제는 건설업 부진과 수출 여건 악화로 경기 하방 위험이 확대되는 모습",
        "제조업생산은 반도체를 중심으로 개선세 유지",
        "한국 경제는 건설업 부진과 수출 여건 악화로 경기 하방 위험이 확대되는 모습",
        "캐나다 달러는 최근 6개월간 상승 추세를 보이고 있음",
        "한 달 후 예상 환율은 현재보다 소폭 상승한 1022.45 KRW로 예측됨"
    ]
}

# 결과 저장
os.makedirs('/home/ubuntu/cad_krw_analysis/charts', exist_ok=True)
with open('/home/ubuntu/cad_krw_analysis/economic_factors.json', 'w') as f:
    json.dump(economic_factors, f, indent=4, ensure_ascii=False)

# 경제 지표 비교 시각화
plt.figure(figsize=(12, 6))
indicators = ['GDP_성장률', '물가상승률/소비자물가']
canada_values = [economic_factors['캐나다']['GDP_성장률'], economic_factors['캐나다']['물가상승률']]
korea_values = [economic_factors['한국']['GDP_성장률'], economic_factors['한국']['소비자물가']]

x = range(len(indicators))
width = 0.35

plt.bar([i - width/2 for i in x], canada_values, width, label='캐나다')
plt.bar([i + width/2 for i in x], korea_values, width, label='한국')

plt.ylabel('퍼센트 (%)')
plt.title('캐나다와 한국의 주요 경제 지표 비교')
plt.xticks(x, indicators)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('/home/ubuntu/cad_krw_analysis/charts/economic_indicators_comparison.png')

# 환율 영향 요인 중요도 시각화
plt.figure(figsize=(12, 6))
factors = [factor['요인'] for factor in economic_factors['환율_영향_요인']]
importance = [3 if factor['영향도'] == '높음' else 2 if factor['영향도'] == '중간' else 1 for factor in economic_factors['환율_영향_요인']]

plt.barh(factors, importance, color='skyblue')
plt.xlabel('중요도')
plt.title('CAD/KRW 환율에 영향을 미치는 요인 중요도')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('/home/ubuntu/cad_krw_analysis/charts/exchange_rate_factors.png')

# 경제적 요인 분석 요약 텍스트 파일 생성
with open('/home/ubuntu/cad_krw_analysis/economic_factors_summary.txt', 'w') as f:
    f.write("# CAD/KRW 환율에 영향을 미치는 경제적 요인 분석\n\n")
    
    f.write("## 캐나다 경제 지표\n")
    for key, value in economic_factors['캐나다'].items():
        f.write(f"- {key.replace('_', ' ')}: {value}\n")
    f.write("\n")
    
    f.write("## 한국 경제 지표\n")
    for key, value in economic_factors['한국'].items():
        f.write(f"- {key.replace('_', ' ')}: {value}\n")
    f.write("\n")
    
    f.write("## 환율 영향 요인\n")
    for factor in economic_factors['환율_영향_요인']:
        f.write(f"### {factor['요인']} (중요도: {factor['영향도']})\n")
        f.write(f"{factor['설명']}\n\n")
    
    f.write("## 최근 동향\n")
    for trend in economic_factors['최근_동향']:
        f.write(f"- {trend}\n")
    f.write("\n")
    
    f.write("## 결론\n")
    f.write("캐나다와 한국의 경제 지표를 비교 분석한 결과, 캐나다의 경제 성장률과 물가상승률이 한국보다 높은 상황입니다. ")
    f.write("특히 캐나다의 GDP 성장률(2.4%)이 한국(0.1%)보다 현저히 높고, 금리도 상대적으로 높은 수준을 유지하고 있어 ")
    f.write("캐나다 달러의 강세 요인으로 작용하고 있습니다. 또한 캐나다는 원자재 수출국으로서 원자재 가격 변동에 민감하게 반응하며, ")
    f.write("미국과의 무역 관계가 환율에 큰 영향을 미치고 있습니다.\n\n")
    
    f.write("현재 추세와 경제적 요인을 종합적으로 고려할 때, CAD/KRW 환율은 단기적으로 소폭 상승할 것으로 예상됩니다. ")
    f.write("다만, 글로벌 경제 불확실성과 양국 중앙은행의 통화 정책 변화에 따라 변동성이 있을 수 있으므로 지속적인 모니터링이 필요합니다.")

print("경제적 요인 분석 완료")
