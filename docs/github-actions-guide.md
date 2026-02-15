# GitHub Actions로 반복 작업 자동화하기

네, 가능합니다. 특히 **매일 오전 10시(KST)에 전일 요약 HTML 생성** 같은 반복 작업은 GitHub Actions가 잘 맞습니다.

## 추천 아키텍처
1. `src/main.py`를 단일 실행 진입점으로 둡니다.
2. 워크플로우에서 Python/의존성(`FinanceDataReader`, `pandas`, `jinja2`)을 설치합니다.
3. `python src/main.py --output-dir output`으로 HTML을 생성합니다.
4. 변경된 `output/*.html`이 있으면 자동 커밋/푸시합니다.

## 스케줄 설정
- GitHub Actions `cron`은 **UTC 기준**입니다.
- 한국시간 오전 10시는 UTC 01:00이므로 아래처럼 설정합니다.

```yaml
schedule:
  - cron: "0 1 * * 1-5"
```

> 참고: `1-5`는 월~금 실행이며, 공휴일 구분은 별도 로직이 필요합니다.

## 운영 시 고려 사항
- 데이터 소스 장애가 있어도 전체 파이프라인이 중단되지 않도록, 항목별 예외 처리를 분리합니다.
- 생성 기준일(`base_date`)과 직전 거래일(`prev_date`)을 명시적으로 계산합니다.
- 실패 시 Slack/Email/Webhook 알림을 추가하면 운영성이 높아집니다.

## 포함된 예시 파일
- 워크플로우: `.github/workflows/daily-market-briefing.yml`
- 실행 진입점: `src/main.py`

현재 `src/main.py`는 플레이스홀더이며, 이전에 논의한 FinanceDataReader 수집/렌더링 로직으로 교체하면 바로 운영 가능한 구조입니다.
