import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

if len(sys.argv) != 4:
    print("error-usage: add_member_from_listserv.py EMAIL URL PASSWORD", file=sys.stderr)
    sys.exit(1)

email = sys.argv[1]
url = sys.argv[2]
password = sys.argv[3]
if not email or email.strip().lower() in ("null", "none", "") or email.startswith("error"):
    print("error-skipped-empty-or-error-email")
    sys.exit(0)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 20)

try:
    driver.get(url)

    # Login if required
    try:
        pw_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password' and @name='adminpw']")))
        pw_input.send_keys(password)
        pw_input.submit()
    except Exception:
        pass  # If there is no login, proceed

    wait.until(EC.presence_of_element_located((By.TAG_NAME, "li")))
    li = driver.find_element(By.TAG_NAME, "li")
    print(li.text.strip())

except Exception as ex:
    maxlen = 100
    msg = str(ex).replace('\n', '\\n')
    if len(msg) > maxlen:
        msg = msg[:maxlen] + '...'
    print("error-" + msg)
finally:
    driver.quit()
