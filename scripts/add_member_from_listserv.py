import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

if len(sys.argv) != 4:
    print("Usage: add_member_from_listserv.py EMAIL URL PASSWORD", file=sys.stderr)
    sys.exit(1)

email = sys.argv[1]
url = sys.argv[2]
password = sys.argv[3]

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 20)

try:
    driver.get(url)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Visit Site')]"))).click()
    pw_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password' and @name='adminpw']")))
    pw_input.send_keys(password)
    pw_input.submit()
    radio = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='send_welcome_msg_to_this_batch' and @type='RADIO' and @value='1']")))
    radio.click()
    textarea = wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@name='subscribees']")))
    textarea.clear()
    textarea.send_keys(email)
    driver.find_element(By.XPATH, "//input[@name='setmemberopts_btn' and @type='SUBMIT']").click()
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "li")))
    lis = driver.find_elements(By.TAG_NAME, "li")
    entry = next((li.text for li in lis if email in li.text), None)
    if entry:
        print(entry.strip())
    else:
        print("error-Response parse failed: " + " | ".join(li.text for li in lis))
except Exception as ex:
    print("error-" + str(ex))
finally:
    driver.quit()
