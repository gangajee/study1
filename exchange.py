import time
import pandas as pd
from selenium import webdriver as wb          # 브라우저 자동화 라이브러리
from selenium.webdriver.common.by import By   # 요소 탐색 방식 지정 (CSS, TAG 등)
from selenium.webdriver.chrome.service import Service          # ChromeDriver 실행 관리
from webdriver_manager.chrome import ChromeDriverManager       # ChromeDriver 자동 설치

# 헤드리스 모드 설정: 브라우저 창을 띄우지 않고 백그라운드에서 실행
options = wb.ChromeOptions()
options.add_argument("--headless")

# ChromeDriver를 자동으로 설치하고 헤드리스 옵션 적용하여 브라우저 실행
driver = wb.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 네이버 금융 메인 페이지 접속
driver.get("https://finance.naver.com/")
time.sleep(1)

# 페이지 맨 아래로 스크롤 (환율 섹션이 lazy loading될 경우를 대비)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
time.sleep(1)

# tr.down 클래스를 가진 모든 행(하락 표시 환율 행)을 한번에 가져옴
rows = driver.find_elements(By.CSS_SELECTOR, "#content > div.article2 > div.section1 > div.group1 > table > tbody > tr.down")

data = []
for row in rows:
  # th: 통화명 (예: 미국 USD), td: 환율 수치 데이터
  currency = row.find_element(By.TAG_NAME, "th").text
  cols = row.find_elements(By.TAG_NAME, "td")
  data.append([currency] + [col.text for col in cols])

# 수집한 데이터로 DataFrame 생성
df = pd.DataFrame(data, columns=["통화", "환율", "전일대비"])
print(df)

# CSV 파일로 저장 (index=False: 행 번호 제외, utf-8-sig: 엑셀 한글 깨짐 방지)
df.to_csv("exchange.csv", index=False, encoding="utf-8-sig")
print("exchange.csv 저장 완료")
