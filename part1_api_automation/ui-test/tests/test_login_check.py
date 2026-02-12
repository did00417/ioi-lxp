import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.login_page import LoginPage


def test_calendar_entry_flow(driver):
    
    login_page = LoginPage(driver)
    login_page.navigate()
    
    # 로그인 수행
    login_page.login_with_kakao()
    
    WebDriverWait(driver, 10).until(lambda d: "schedules" in d.current_url)
    assert "schedules" in driver.current_url
    print(f"🏁 최종 테스트 통과 확인: {driver.current_url}")
 
#주말 제외 ui테스트   
def test_calendar_entry_flow(driver):
    login_page = LoginPage(driver)
    login_page.navigate()
    login_page.login_with_kakao() #로그인 수행

    # 2. 주말 제외 필터 클릭
    login_page.toggle_exclude_weekends()
    print("🏁 주말 제외 필터 UI/UX 동기화 검증 완료!")
    
    # 3. 월간 표시 검증
    login_page.switch_to_month_view()
    print("🏁 월간 바뀜 동기화 검증 완료!")
    
    # 4. 오늘 버튼 클릭 검증
    login_page.verify_today_focus()

    print("\n🎉 모든 UI/UX 시나리오 테스트 통과 (PASSED)!")
    
