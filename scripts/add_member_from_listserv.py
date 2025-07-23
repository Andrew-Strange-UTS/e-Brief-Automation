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
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        if body.get_attribute("id") == "ngrok":
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Visit Site')]"))).click()
    except Exception:
        pass

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

    result_line = ""
    for li in lis:
        txt = li.text.strip().lower()
        if email.lower() in txt:
            if "already" in txt and "member" in txt:
                result_line = f"🤖 Mailman result: {email} -- already a member"
                break
            elif "successfully subscribed" in txt or "subscribed" in txt:
                result_line = f"🤖 Mailman result: {email} -- subscribed"
                break
            elif "error" in txt or "failed" in txt:
                result_line = f"🤖 Mailman result: {email} -- error: {li.text.strip()}"
                break
    if not result_line:
        # Try to find any li indicating 'already a member', even if email is not echoed
        for li in lis:
            txt = li.text.strip().lower()
            if "already" in txt and "member" in txt:
                result_line = f"🤖 Mailman result: {email} -- already a member"
                break
            elif "successfully subscribed" in txt or "subscribed" in txt:
                result_line = f"🤖 Mailman result: {email} -- subscribed"
                break
    if not result_line and lis:
        # fallback: just join the first li, but mark as unknown result
        result_line = f"🤖 Mailman result: {email} -- unknown result: {lis[0].text.strip()}"
    if result_line:
        print(result_line)
    else:
        print(f"error-No result li found for {email}")
except Exception as ex:
    maxlen = 100
    msg = str(ex).replace('\n', '\\n')
    if len(msg) > maxlen:
        msg = msg[:maxlen] + '...'
    print("error-" + msg)
finally:
    driver.quit()
