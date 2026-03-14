import time
import pymysql
from datetime import datetime
from selenium import webdriver as wb
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 수집 대상 통화 (네이버 증권 표기명 기준)
TARGET_CURRENCIES = {"미국 USD", "일본 JPY(100엔)", "유럽연합 EUR", "중국 CNY"}

# ── 크롤링 ──────────────────────────────────────────────
options = wb.ChromeOptions()
options.add_argument("--headless")

driver = wb.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://finance.naver.com/marketindex/")
time.sleep(2)

# href의 marketindexCd로 통화 식별 (span.blind는 CSS로 숨겨져 .text가 빈 문자열)
CURRENCY_MAP = {
    "FX_USDKRW": "미국 USD",
    "FX_JPYKRW": "일본 JPY(100엔)",
    "FX_EURKRW": "유럽연합 EUR",
    "FX_CNYKRW": "중국 CNY",
}

rows = driver.find_elements(By.CSS_SELECTOR, "#exchangeList > li")

data = []
for row in rows:
    try:
        href = row.find_element(By.CSS_SELECTOR, "a.head").get_attribute("href")
        cd   = href.split("marketindexCd=")[-1]          # FX_USDKRW 등
        name = CURRENCY_MAP.get(cd)
        if not name:
            continue
        rate       = row.find_element(By.CSS_SELECTOR, ".value").text.strip().replace(",", "")
        change_el  = row.find_element(By.CSS_SELECTOR, ".change")
        change_txt = change_el.get_attribute("textContent").strip().replace(",", "")
        info_class = row.find_element(By.CSS_SELECTOR, ".head_info").get_attribute("class")
        sign       = "+" if "point_up" in info_class else "-"
        data.append({
            "currency": name,
            "rate":     float(rate),
            "change":   float(sign + change_txt) if change_txt else 0.0,
            "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
    except Exception as e:
        print("파싱 오류:", e)
        continue

driver.quit()

for d in data:
    print(d)

# ── MySQL 저장 ───────────────────────────────────────────
conn = pymysql.connect(
    host="localhost",
    user="root",          # 본인 계정으로 변경
    password="0724",          # 본인 비밀번호로 변경
    database="finance",   # 미리 생성된 DB 이름으로 변경
    charset="utf8mb4",
)

with conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS exchange_rate (
                id           INT AUTO_INCREMENT PRIMARY KEY,
                currency     VARCHAR(30)    NOT NULL,
                rate         DECIMAL(12, 4) NOT NULL,
                change_amt   DECIMAL(10, 4) NOT NULL,
                collected_at DATETIME       NOT NULL
            )
        """)
        cur.executemany(
            """
            INSERT INTO exchange_rate (currency, rate, change_amt, collected_at)
            VALUES (%(currency)s, %(rate)s, %(change)s, %(collected_at)s)
            """,
            data,
        )
    conn.commit()

print(f"{len(data)}건 MySQL 저장 완료")
