from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

'''
TODO: IP-Rotator, Language Filter, Make it a module with params
'''

# Params
url = "https://www.twitch.tv/directory/category/league-of-legends/clips?range=24hr"
num_clips = 5 #int(input("Enter the number of clips to download: "))

# Get Proxys
with open("valid_proxies.txt", "r") as f:
    proxies = f.read().split("\n")

# Configurate UserAgent
ua = UserAgent(platforms='pc') # Create a UserAgent instance
random_user_agent = ua.random # Get a random user-agent string

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(f"user-agent={random_user_agent}")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("window-size=960,1080")
chrome_options.add_argument('--proxy-server=%s' % random.choice(proxies))

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(options=chrome_options)

# Setting up the scrape
driver.get(url) # Navigate to the URL
time.sleep(random.uniform(4.0, 6.5)) # Wait for the page to load (adjust the delay as needed)
html_content = driver.page_source # Get the page source after JavaScript rendering
soup = BeautifulSoup(html_content, "html.parser") # Parse the HTML content using BeautifulSoup

# Scraping the desired number of clips, saving in a list of dictionarys
clips = soup.select("div[data-a-target^='clips-card-']") # Find all the clip elements
clip_data = []
for clip in clips[:num_clips]:
    # Find the title tag and extract the title attribute
    title_tag = clip.select_one("a.ScCoreLink-sc-16kq0mq-0.fPPzLm.ScCoreLink-sc-bhsr9c-0.htMMdJ > h3")
    if title_tag:
        alt_text = title_tag.get("title")
    else:
        alt_text = ""

    # Find the link tag and extract the href attribute
    link_tag = clip.select_one("a.ScCoreLink-sc-16kq0mq-0.eFqEFL.tw-link[data-a-target='preview-card-image-link']")
    if link_tag:
        link_href = "https://www.twitch.tv" + link_tag.get("href")
    else:
        link_href = ""

    # Store the clip information in a dictionary
    clip_info = {
        "alt_text": alt_text,
        "link_href": link_href
    }

    # Add the clip information to the list
    clip_data.append(clip_info)

    # Introduce a random delay to simulate human browsing behavior
    time.sleep(random.uniform(1.5, 3.5))

# Exit browser
driver.quit()

# Print the clip information
for clip in clip_data:
    print(f"Alt Text: {clip['alt_text']}")
    print(f"Link: {clip['link_href']}")
    print("---")