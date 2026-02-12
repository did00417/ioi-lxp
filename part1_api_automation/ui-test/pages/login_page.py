from selenium.webdriver.common.by import By
from .base_page import BasePage
import os
from dotenv import load_dotenv
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


load_dotenv()

class LoginPage(BasePage):
    #카카오로 로그인 버튼
    KAKAO_BTN = (By.CSS_SELECTOR, "button[aria-label='Kakao']")
    
    ID_INPUT = (By.NAME, "loginId")      # 카카오 ID 입력
    PW_INPUT = (By.NAME, "password")     # 카카오 비밀번호 입력
    SUBMIT_BTN = (By.XPATH, "//button[@type='submit']") # 로그인 버튼
    
    def navigate(self):
        """엘리스 로그인 페이지로 이동"""
        self.driver.get("https://accounts.elice.io/accounts/signin/me?continue_to=https%3A%2F%2Fqatrack.elice.io%2F&org=qatrack&lang=ko")

    def login_with_kakao(self):
        user_id = os.getenv("KAKAO_ID")
        user_pw = os.getenv("KAKAO_PW")
        
        main_window = self.driver.current_window_handle
        self.click(self.KAKAO_BTN)
        
        time.sleep(3) 
        
        # 1. 팝업창으로 전환
        for handle in self.driver.window_handles:
            if handle != main_window:
                self.driver.switch_to.window(handle)
                break
        
        # 2. 값 입력 및 로그인 버튼 클릭
        self.wait_for_element(self.ID_INPUT).send_keys(user_id)
        self.wait_for_element(self.PW_INPUT).send_keys(user_pw)
        self.click(self.SUBMIT_BTN)
        
        # 3. 팝업 처리 및 복귀
        time.sleep(5) 
        try:
            if len(self.driver.window_handles) > 1:
                self.driver.close() 
        except:
            pass 
            
        self.driver.switch_to.window(main_window)

        print("🚀 캘린더 페이지로 이동을 시작합니다...")
        self.go_to_schedule_page()
        
    def go_to_schedule_page(self, class_name="3기"):
        """강의실 진입부터 캘린더 로딩까지 확실하게 대기"""
        print(f"🚀 {class_name} 강의실 진입 시도 중...")
        
        # 1. '3기' 강의실 버튼 대기 및 클릭
        class_xpath = f"//span[contains(text(), '{class_name}')]/ancestor::a"
        class_btn = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, class_xpath))
        )
        self.driver.execute_script("arguments[0].click();", class_btn) 
        print(f"✅ {class_name} 강의실 클릭 완료")
        
        # 2. '수업 일정' 메뉴 대기 및 클릭
        schedule_css = "a[aria-label='수업 일정']"
        schedule_btn = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, schedule_css))
        )
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, schedule_css)))
        self.driver.execute_script("arguments[0].click();", schedule_btn)
        print("✅ '수업 일정' 메뉴 클릭 완료")
        
        WebDriverWait(self.driver, 20).until(
            lambda d: "schedules" in d.current_url
        )
        print(f"🏁 캘린더 접속 성공: {self.driver.current_url}")
        
    def toggle_exclude_weekends(self):
        print("🔘 '주말 제외' 필터 적용 시도 중...")
        
        # 1. 체크박스 본체와 라벨을 각각 정의
        checkbox_xpath = "//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')]"
        label_xpath = "//p[contains(text(), '주말 제외')]/ancestor::label"
        
        try:
            checkbox = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, checkbox_xpath))
            )
            
            if not checkbox.is_selected():
                # 2. 라벨을 클릭하여 체크박스 활성화
                label = self.driver.find_element(By.XPATH, label_xpath)
                self.driver.execute_script("arguments[0].click();", label)
                print("✅ '주말 제외' 클릭 완료")
                
                WebDriverWait(self.driver, 5).until(lambda d: checkbox.is_selected())
                print("🏁 UI 상태 검증 성공: 체크박스가 활성화되었습니다.")
            else:
                print("ℹ️ 이미 주말 제외 상태입니다.")

        except Exception as e:
            print(f"❌ 필터 조작 실패: {e}")
            raise e
        
    def switch_to_month_view(self):
        """'매주' 뷰에서 '매월' 뷰로 전환 및 그리드 검증"""
        print("📅 '매월' 뷰 모드로 전환 시도 중...")
        
        try:
            # 1. '매주'라고 써진 셀렉트 박스(콤보박스) 클릭
            combo_selector = "//div[@role='combobox' and contains(@class, 'MuiSelect-select')]"
            combo_box = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, combo_selector))
            )
            combo_box.click()
            print("✅ 뷰 선택 콤보박스 클릭 완료")

            # 2. 드롭다운 목록에서 '매월' 항목 클릭
            month_option_xpath = "//li[@data-value='dayGridMonth']"
            month_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, month_option_xpath))
            )
            month_option.click()
            print("✅ '매월' 옵션 선택 완료")

            time.sleep(2)
            
            # MUI 캘린더의 날짜 칸들을 모두 찾음
            grid_cells = self.driver.find_elements(By.CSS_SELECTOR, "[role='gridcell']")
            cell_count = len(grid_cells)
            
            print(f"📊 월간 뷰 전환 후 감지된 그리드 셀: {cell_count}개")

            # 보통 월간 뷰는 최소 28개 이상의 셀이 존재해야 함
            assert cell_count > 10, f"⚠️ 월간 뷰로 전환되었으나 그리드 셀이 부족합니다 (개수: {cell_count})"
            print("🏁 월간 뷰 그리드 검증 성공!")

        except Exception as e:
            print(f"❌ 뷰 모드 전환 중 에러 발생: {e}")
            raise e
        
    def verify_today_focus(self):
        print("🎯 '오늘' 버튼 포커싱 테스트 시작...")
        
        try:
            # 1. '오늘' 버튼 클릭
            today_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='오늘']"))
            )
            
            # 2. 테스트를 위해 스크롤을 하단으로 미리 내려둠
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # 3. '오늘' 버튼 클릭
            today_btn.click()
            print("✅ '오늘' 버튼 클릭 완료")
            time.sleep(2) # 스크롤 이동 애니메이션 대기

            # 4. fc-day-today 클래스로 오늘 날짜 요소 특정
            today_indicator_selector = ".fc-day-today" 
            today_cell = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, today_indicator_selector))
            )

            # 5. 뷰포트 안에 있는지 검증
            is_in_viewport = self.driver.execute_script("""
                var elem = arguments[0];
                var bounding = elem.getBoundingClientRect();
                return (
                    bounding.top >= 0 &&
                    bounding.bottom <= (window.innerHeight || document.documentElement.clientHeight)
                );
            """, today_cell)

            assert is_in_viewport is True, "❌ '오늘' 버튼 클릭 후 오늘 날짜로 화면이 이동하지 않았습니다."
            print("🏁 포커싱 검증 성공: 오늘 날짜(fc-day-today)가 화면에 노출됩니다.")

        except Exception as e:
            print(f"❌ 포커싱 검증 실패: {e}")
            raise e