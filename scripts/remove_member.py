import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

EMAIL = os.environ["EMAIL_ADDRESS"]
PASSWORD = os.environ["TESTPASSWORD"]

URL = "https://b7943cf2de68.ngrok-free.app/mailman/admin/testlist/members/remove"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 20)

try:
    # 1. Go to the remove page
    driver.get(URL)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Visit Site')]")))

    # 2. Click "Visit Site"
    visit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Visit Site')]")
    visit_btn.click()

    # 3. Wait for password input and enter password
    pw_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password' and @name='adminpw']")))
    pw_input.send_keys(PASSWORD)

    # 4. Submit password (hit Enter)
    pw_input.submit()

    # 5. Wait for the "send_unsub_ack_to_this_batch" radio and tick it
    radio = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='send_unsub_ack_to_this_batch' and @type='RADIO' and @value='1']")))
    radio.click()

    # 6. Put the email address in the textarea
    textarea = wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@name='unsubscribees']")))
    textarea.clear()
    textarea.send_keys(EMAIL)

    # 7. Click submit button
    submit = driver.find_element(By.XPATH, "//input[@name='setmemberopts_btn' and @type='SUBMIT']")
    submit.click()

    # 8. Wait for one of the result messages to appear
    #   Either success: <h5>Successfully Unsubscribed:</h5>
    #   Or failure: <font color="#ff0000" size="+2">Cannot unsubscribe non-members:</font>
    result = None
    try:
        # wait for either element to appear (first one found)
        wait.until(
            lambda d: d.find_elements(By.XPATH, "//h5[contains(text(), 'Successfully Unsubscribed:')]") or
                      d.find_elements(By.XPATH, "//font[contains(text(), 'Cannot unsubscribe non-members:')]")
        )

        if driver.find_elements(By.XPATH, "//h5[contains(text(), 'Successfully Unsubscribed:')]"):
            print(f"Result: {EMAIL} Successfully Unsubscribed")
        elif driver.find_elements(By.XPATH, "//font[contains(text(), 'Cannot unsubscribe non-members:')]"):
            print(f"Result: {EMAIL} Cannot unsubscribe non-members")
        else:
            print(f"Could not find clear result for {EMAIL}.")
    except Exception as e:
        print("Timed out waiting for unsubscription result.")
finally:
    driver.quit()
