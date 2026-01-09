import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

st.set_page_config(page_title="ExportComments Pro Automator", layout="wide")
st.title("🚀 Bulk Export Automator (Fixed Version)")

# --- Sidebar: Credentials ---
st.sidebar.header("1. Login Credentials")
user_email = st.sidebar.text_input("Email")
user_password = st.sidebar.text_input("Password", type="password")
delay = st.sidebar.slider("Delay between batches (sec)", 2, 10, 5)

# --- Main Input ---
links_input = st.text_area("Paste links (one per line):", height=300)

def js_click(driver, element):
    """Force click using JavaScript (bypasses 'not interactable' errors)"""
    driver.execute_script("arguments[0].click();", element)

def js_fill(driver, element, value):
    """Force fill using JavaScript"""
    driver.execute_script(f"arguments[0].value = '{value}';", element)

def start_automation(email, password, all_links):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080") # Force Desktop View
    
    service = Service("/usr/bin/chromedriver")
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 15)

        # 1. Login Phase
        st.info("Logging in...")
        driver.get("https://exportcomments.com/login")
        
        # Fill email
        email_field = wait.until(EC.visibility_of_element_located((By.NAME, "email")))
        email_field.send_keys(email)
        
        # Fill password
        pass_field = driver.find_element(By.NAME, "password")
        pass_field.send_keys(password)
        
        # Click Login
        login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        js_click(driver, login_btn)
        
        time.sleep(5) # Wait for redirect
        
        # 2. Process Batches
        batches = [all_links[i:i + 5] for i in range(0, len(all_links), 5)]
        
        for b_idx, batch in enumerate(batches):
            st.write(f"--- Processing Batch {b_idx+1} ({len(batch)} links) ---")
            
            if b_idx == 0:
                driver.get("https://exportcomments.com/")
            else:
                driver.execute_script("window.open('https://exportcomments.com/', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])

            time.sleep(3)

            # Close any "Accept Cookies" or popups if they exist
            try:
                cookie_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Accept') or contains(text(), 'Agree')]")
                js_click(driver, cookie_btn)
            except: pass

            # 3. Add slots (Max 5 per tab)
            # We need to click "Add another URL" (len(batch) - 1) times
            for _ in range(len(batch) - 1):
                try:
                    # Find "+" button by ID or text
                    add_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='add-url'] | //*[contains(text(), 'Add another URL')]")))
                    js_click(driver, add_btn)
                    time.sleep(0.5)
                except Exception as e:
                    st.warning("Could not find '+' button. Attempting to fill single slot.")
                    break

            # 4. Fill slots
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[name='url']")
            for i, link in enumerate(batch):
                if i < len(inputs):
                    inputs[i].clear()
                    inputs[i].send_keys(link)
                    st.write(f"✅ Slot {i+1} filled")

            # 5. Start Export
            try:
                start_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='submit-url'] | //button[contains(., 'Start')]")))
                js_click(driver, start_btn)
                st.success(f"Batch {b_idx+1} processing!")
            except:
                st.error("Failed to click 'Start' button.")

            time.sleep(delay)

        st.balloons()
        st.success("All batches sent successfully!")

    except Exception as e:
        st.error(f"Critical Automation Error: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if st.button("🚀 Start Automation"):
    if not user_email or not user_password:
        st.error("Please provide your login credentials.")
    elif not links_input:
        st.error("No links detected.")
    else:
        link_list = [l.strip() for l in links_input.split('\n') if l.strip()]
        start_automation(user_email, user_password, link_list)
