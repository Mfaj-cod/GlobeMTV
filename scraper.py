import requests
from bs4 import BeautifulSoup
import re

movie_img_link = []
movies_title = []

url = "https://m.imdb.com/search/title/?title_type=feature,tv_series&count=25"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36"
}



try:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        print()

        for item in soup.select("li.ipc-metadata-list-summary-item")[:25]:
            # Title
            title_tag = item.select_one("h3")
            if title_tag:
                title = title_tag.get_text(strip=True)

                clean_title = re.sub(r'^[\.\d\s]+', '', title)
                movies_title.append(clean_title)

            # Image
            img_tag = item.select_one("img")
            if img_tag and img_tag.get("src"):
                movie_img_link.append(img_tag["src"])

        print("✅ Fetched successfully")
    else:
        print("❌ Failed:", response.status_code)
except Exception as e:
    print("❌ An error occurred in scraper:", e)
    

# print("Titles:", movies_title)
# print("Images:", movie_img_link)
