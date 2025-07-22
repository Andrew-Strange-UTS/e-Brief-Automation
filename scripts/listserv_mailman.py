import argparse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ACTION_CONFIG = {
    "add": {
        "password_field": "adminpw",
        "radio_field": "send_welcome_msg_to_this_batch",
        "textarea": "subscribees",
        "submit": "setmemberopts_btn",
        "output_xpath": "//li[contains(., '{email}')]"
    },
    "remove": {
        "password_field": "adminpw",
        "radio_field": "send_unsub_ack_to_this_batch",
        "textarea": "unsubscribees",
        "submit": "setmemberopts_btn",
        "output_xpath": None  # No output needed for remove
    },
}

def process_mailman(action, url, password, email):
    config = ACTION_CONFIG[action]
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,800")
    driver = webdriver.Chrome(options=opts)
    result = ""
    try:
        driver.get(url)
        pw = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, config["password_field"])))
        pw.clear()
        pw.send_keys(password)
        pw.submit()
        textarea = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, config["textarea"])))
        try:
            radio = driver.find_element(By.NAME, config["radio_field"])
            radio.click()
        except Exception:
            pass
        textarea.clear()
        textarea.send_keys(email)
        btn = driver.find_element(By.NAME, config["submit"])
        btn.click()
        time.sleep(2)
        if action == "add":
            output_xpath = config["output_xpath"].format(email=email)
            try:
                li = driver.find_element(By.XPATH, output_xpath)
                result = li.text.strip()
            except Exception:
                result = f"{email} -- No response found"
        else:
            result = f"{email} - removed for ebrief"
        print(result)
    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["add", "remove"], required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--email", required=True)
    args = parser.parse_args()
    process_mailman(args.action, args.url, args.password, args.email)
