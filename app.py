import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# --- UI Setup ---
st.set_page_config(page_title="ExportComments Pro Automator", layout="wide")
st.title("🚀 Bulk Export Automator")
st.markdown("Login once, paste your links, and let the bot handle the multi-slot insertion.")

# --- Sidebar: Credentials ---
st.sidebar.header("1. Login Credentials")
user_email = st.sidebar.text_input("Email")
user_password = st.sidebar.text_input("Password", type="password")

st.sidebar.header("2. Settings")
delay = st.sidebar.slider("Wait time (seconds)", 2, 10, 3)

# --- Main Input ---
links_input = st.text_area("Paste your links here (one per line):", height=300)

def start_automation(email, password, all_links):
    # Setup Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Change to False if running locally to see it work
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        # 1. Login Phase
        st.info("Logging in to ExportComments...")
        driver.get("https://exportcomments.com/login")
        
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_field.send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        time.sleep(3) # Wait for login to process
        
        # 2. Process Links in Batches of 5
        batches = [all_links[i:i + 5] for i in range(0, len(all_links), 5)]
        
        for b_idx, batch in enumerate(batches):
            st.write(f"--- Processing Batch {b_idx+1} ({len(batch)} links) ---")
            
            # Open new tab or use first
            if b_idx == 0:
                driver.get("https://exportcomments.com/")
            else:
                driver.execute_script("window.open('https://exportcomments.com/', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])

            # 3. Click "Add another URL" 4 times to get 5 slots total
            # We click only if we have more than 1 link in the batch
            num_to_add = len(batch) - 1
            for _ in range(num_to_add):
                try:
                    add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Add another URL')]")))
                    add_btn.click()
                    time.sleep(0.5) 
                except:
                    st.warning("Could not find 'Add another URL' button. Site layout might have changed.")

            # 4. Fill the slots
            # Find all URL input boxes
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[name='url']")
            if not inputs: # Fallback if name is different
                 inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='URL']")

            for i, link in enumerate(batch):
                if i < len(inputs):
                    inputs[i].send_keys(link)
                    st.write(f"Slot {i+1}: {link[:50]}...")
            
            # 5. Click Start
            try:
                start_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Start export process')]")
                start_btn.click()
                st.success(f"Batch {b_idx+1} started!")
            except:
                st.error("Could not find 'Start export' button.")
            
            time.sleep(delay) # Pause between batches

        st.balloons()
        st.success("All links have been processed!")

    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        driver.quit()

if st.button("Start Automation"):
    if not user_email or not user_password:
        st.error("Please provide your login details.")
    elif not links_input:
        st.error("Please paste your links.")
    else:
        link_list = [line.strip() for line in links_input.split('\n') if line.strip()]
        start_automation(user_email, user_password, link_list)
