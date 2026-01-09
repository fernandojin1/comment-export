import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- UI Setup ---
st.set_page_config(page_title="ExportComments Pro Automator", layout="wide")
st.title("🚀 Bulk Export Automator")

# --- Sidebar: Credentials ---
st.sidebar.header("1. Login Credentials")
user_email = st.sidebar.text_input("Email")
user_password = st.sidebar.text_input("Password", type="password")

st.sidebar.header("2. Settings")
delay = st.sidebar.slider("Wait time (seconds)", 2, 10, 3)

# --- Main Input ---
links_input = st.text_area("Paste your links here (one per line):", height=300)

def start_automation(email, password, all_links):
    # --- FIXED SETUP FOR STREAMLIT CLOUD ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # These two lines are the "secret sauce" for Streamlit Cloud:
    chrome_options.binary_location = "/usr/bin/chromium" 
    service = Service("/usr/bin/chromedriver")

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20)

        # 1. Login Phase
        st.info("Logging in to ExportComments...")
        driver.get("https://exportcomments.com/login")
        
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_field.send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        time.sleep(5) # Give it time to redirect
        
        # 2. Process Links in Batches of 5
        batches = [all_links[i:i + 5] for i in range(0, len(all_links), 5)]
        
        for b_idx, batch in enumerate(batches):
            st.write(f"--- Processing Batch {b_idx+1} ---")
            
            if b_idx == 0:
                driver.get("https://exportcomments.com/")
            else:
                driver.execute_script("window.open('https://exportcomments.com/', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])

            time.sleep(3)

            # 3. Add slots
            num_to_add = len(batch) - 1
            for _ in range(num_to_add):
                try:
                    # ExportComments uses a specific button for adding URLs
                    add_btn = wait.until(EC.element_to_be_clickable((By.ID, "add-url")))
                    add_btn.click()
                    time.sleep(0.5)
                except:
                    # Fallback if ID is different
                    try:
                        add_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Add another URL')]")
                        add_btn.click()
                    except: pass

            # 4. Fill slots
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[name='url']")
            for i, link in enumerate(batch):
                if i < len(inputs):
                    inputs[i].send_keys(link)
            
            # 5. Submit
            try:
                submit_btn = driver.find_element(By.ID, "submit-url")
                submit_btn.click()
                st.success(f"Batch {b_idx+1} submitted!")
            except:
                st.error("Submit button not found.")
            
            time.sleep(delay)

        st.balloons()
        st.success("All links have been processed!")

    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if st.button("Start Automation"):
    if not user_email or not user_password:
        st.error("Please provide your login details.")
    elif not links_input:
        st.error("Please paste your links.")
    else:
        link_list = [l.strip() for l in links_input.split('\n') if l.strip()]
        start_automation(user_email, user_password, link_list)
