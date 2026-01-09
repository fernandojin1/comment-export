import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# --- UI Header ---
st.set_page_config(page_title="ExportComments Auto-Loader", layout="wide")
st.title("🤖 Bulk Link Auto-Inserter")
st.markdown("Paste your links below. The app will open tabs and insert 5 links per tab.")

# --- Sidebar ---
st.sidebar.header("Settings")
wait_time = st.sidebar.slider("Seconds to wait between links", 1, 10, 3)

# --- Input Area ---
links_text = st.text_area("Paste links here (one per line):", height=300)

def run_automation(all_links):
    # Setup Chrome Options (Headless for Cloud, Visible for Local)
    chrome_options = Options()
    # If running on Streamlit Cloud, these flags are mandatory
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Batch the links into groups of 5
    batch_size = 5
    batches = [all_links[i:i + batch_size] for i in range(0, len(all_links), batch_size)]
    
    progress_text = st.empty()
    
    for b_idx, batch in enumerate(batches):
        progress_text.text(f"Processing Batch {b_idx + 1} of {len(batches)}...")
        
        # Open a new tab for this batch
        if b_idx == 0:
            driver.get("https://exportcomments.com/")
        else:
            driver.execute_script("window.open('https://exportcomments.com/', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
        
        time.sleep(2) # Wait for page load
        
        for link in batch:
            try:
                # Find the input box (using common selectors for ExportComments)
                # Note: If they change their ID, change 'url' below
                input_box = driver.find_element(By.CSS_SELECTOR, "input[name='url']") 
                input_box.clear()
                input_box.send_keys(link)
                input_box.send_keys(Keys.ENTER)
                
                st.write(f"✅ Inserted: {link[:50]}...")
                time.sleep(wait_time) 
            except Exception as e:
                st.error(f"Could not find input box for link: {link}")
    
    st.success("🎉 All links have been sent to the browser!")
    driver.quit()

if st.button("🚀 Start Automation"):
    if links_text:
        link_list = [l.strip() for l in links_text.split('\n') if l.strip()]
        run_automation(link_list)
    else:
        st.warning("Please paste some links first.")
