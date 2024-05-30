from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from moviepy.editor import VideoFileClip, clips_array
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import requests
import random
import time
import os


def add_subs(name: str, lang: str, absolute_path) -> None:

    print(f"[SUBS] Adding Subtitles to {name}")
    # Convert relative path to absolute path for file upload (necessary)

    today = datetime.now(timezone.utc).date()
    ua = UserAgent(platforms='pc') # Create a UserAgent instance
    random_user_agent = ua.random # Get a random user-agent string

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") #Disabel for debug
    #chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"user-agent={random_user_agent}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("log-level=1")

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(options=chrome_options)

    url = "https://www.veed.io/tools/add-subtitles"
    driver.get(url)
    driver.add_cookie({"name": "OptanonAlertBoxClosed", "value": f"{today}T00:00:00.000Z"})

    time.sleep(random.uniform(2.0, 3.5))

    # Click button to generate new session
    selector = 'a[data-testid="@titleSection/CTA"]'
    element = driver.find_element(By.CSS_SELECTOR, selector)
    element.click()
    time.sleep(random.uniform(2.0, 2.5))

    # Accept TOS
    selector = 'button[data-testid="@component/terms-consent-modal/btn"]'
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element(By.CSS_SELECTOR, selector)
    element.click()
    time.sleep(random.uniform(0.5, 1.0))

    # Upload video
    selector = 'div[data-testid="@editor/activation-flow-new-modal"] input[type="file"]'
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
    file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    file_input.send_keys(f"{absolute_path}.mp4")
    WebDriverWait(driver, 360).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".ActivationLoaderstyled__ActivationLoaderProgress-sc-2xypj-0.ldMcbd")))

    # Choose video language
    selector = 'div[data-testid="@editor/subtitles/create-subtitles-language-picker"]'
    element = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
    element.click()
    time.sleep(random.uniform(0.5, 1.0))
    element = driver.find_element(By.CSS_SELECTOR, 'input[id="react-select-5-input"]')

    if lang == "es":
        element.send_keys("Spanish (Spain)")
    elif lang == "en":
        element.send_keys("English (US)")
    elif lang == "de":
        element.send_keys("German")
    elif lang == "fr":
        element.send_keys("French (France)")
    elif lang == "ko":
        element.send_keys("Korean")
    elif lang == "zh" or "zh-tw" or "zh-cn" or "zh-sg" or "zh-hk":
        element.send_keys("Chinese")
    elif lang == "jp":
        element.send_keys("Japanese")
    else:
        print(f"Unsupported language code: {lang}")
        return

    element.send_keys(Keys.ENTER)
    selector = 'button[data-testid="@editor/subtitles/create-subtitles-button"]'
    element = driver.find_element(By.CSS_SELECTOR, selector)
    element.click()
    WebDriverWait(driver, 240).until(EC.url_matches("veed.io/edit/.*/subtitles"))

    # Translate subtitle
    if lang != "en":
        selector = 'button[data-testid="@editor/subtitles/translate"]'
        element = driver.find_element(By.CSS_SELECTOR, selector)
        element.click()
        time.sleep(random.uniform(0.7, 1.2))  
        element = driver.find_element(By.CSS_SELECTOR, 'input[id="react-select-7-input"]')
        element.send_keys("English (US)")
        element.send_keys(Keys.ENTER)
        selector = 'div[data-testid="@editor/subtitles/translate-automatically-button-wrapper"]'
        element = driver.find_element(By.CSS_SELECTOR, selector)
        element.click()
        time.sleep(random.uniform(1.0, 1.5))
    
    # Click on subtitle style folder
    selector = 'button[data-testid="@editor/subtitles/styles"]'
    element = driver.find_element(By.CSS_SELECTOR, selector)
    element.click()
    time.sleep(random.uniform(0.5, 1.25))

    # Choose one font and highlight style
    selector = 'div[data-testid="@editor/subtitles/style-preset-thumbnail-slay"]'
    element = driver.find_element(By.CSS_SELECTOR, selector)
    element.click()

    # "Done"
    selector = 'button[data-testid="@header-controls/publish-button"]'
    element = driver.find_element(By.CSS_SELECTOR, selector)
    element.click()
    time.sleep(random.uniform(0.5, 1.25))

    # Add subtitles to video instead of extra file
    text_element = driver.find_element('xpath', '//span[text()="Burn Subtitles"]')
    parent_element = text_element.find_element('xpath', './..')
    element = parent_element.find_element(By.CSS_SELECTOR, 'div[data-testid="@components/toggle"]')
    element.click()
    time.sleep(random.uniform(0.3, 0.75))

    # Set FPS
    selector = 'button[data-testid="@export/advanced-settings"]'
    element = driver.find_element(By.CSS_SELECTOR, selector)
    element.click()
    time.sleep(random.uniform(0.3, 0.75))

    element = driver.find_element(By.CSS_SELECTOR, 'input[data-testid="@slider-with-input/text-input"]')
    element.click()
    element.send_keys(Keys.DELETE)
    element.send_keys("6")
    # Export
    selector = 'button[data-testid="@export/export-button"]'
    element = driver.find_element(By.CSS_SELECTOR, selector)
    element.click()
    WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Play video"]')))



    ''' Proceed with Downloading the Video '''


    # Get the video URL
    soup = BeautifulSoup(driver.page_source, "html.parser")
    video_source = soup.find("source", {"data-testid": "@video-player/source"})
    if video_source:
        video_url = video_source.get("src")
    else:
        print("Video source element not found.")
        driver.quit()
        return

    # Set the headers
    headers = {
        "Referer": driver.current_url,
    }

    # Send a HEAD request to get the video headers
    head_response = requests.head(video_url, headers=headers)

    # Check if the video is accessible
    if head_response.status_code == 200:
        # Get the video content length
        content_length = int(head_response.headers.get("Content-Length", 0))
        

        # Open a file to save the video content
        with open(f"{absolute_path}_subed.mp4", "wb") as video_file:
            start_range = 0
            end_range = 0

            while end_range < content_length:
                # Update the range headers
                end_range = min(start_range + 1024 * 1024, content_length)
                headers["Range"] = f"bytes={start_range}-{end_range - 1}"

                # Send a GET request to fetch the video content range
                get_response = requests.get(video_url, headers=headers, stream=True)

                if get_response.status_code == 206:  # Partial Content
                    # Write the received content to the file
                    for chunk in get_response.iter_content(chunk_size=1024):
                        if chunk:
                            video_file.write(chunk)

                    # Update the start range for the next request
                    start_range = end_range
                else:
                    print(f"Failed to download the video. Status code: {get_response.status_code}")
                    break

        print(f"Video transcribed successfully: {name}")
    else:
        print(f"The video URL is not accessible. Status code: {head_response.status_code}")

    # Close the browser
    driver.quit()
    


def rmv_wtrmrk(path:str ) -> None:
    print("Removing Watermark")

    try:
        og_vid = VideoFileClip(f"{path}.mp4")
        sub_vid = VideoFileClip(f"{path}_subed.mp4")

        width, height = og_vid.size

        upper_vid = og_vid.crop(x1=0, y1=0, x2=width, y2=height//2)
        lower_vid = sub_vid.crop(x1=0, y1=height//2, x2=width, y2=height)

        # Remove the audio from the lower clip
        lower_vid = lower_vid.without_audio()

        # Combine the upper and lower clips vertically
        final_clips = clips_array([[upper_vid], [lower_vid]])

        # Write the final clip to a new Full HD video file
        final_clips.write_videofile(f"{path}_merged.mp4", preset="slow", verbose=False, logger=None)

        # Close the video clips
        og_vid.close()
        sub_vid.close()
        final_clips.close()

    except Exception as e:
        print(f"Error removing watermark: {e}")