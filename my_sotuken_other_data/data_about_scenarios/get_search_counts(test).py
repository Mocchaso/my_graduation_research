import requests
from bs4 import BeautifulSoup

words = ["機械学習"]
for word in words:
    res = requests.get("https://google.com/search?q=" + word)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "lxml")
    result_nums = soup.find_all("div", class_="sd", id="resultStats")[0].text
    result_nums = result_nums.split()
    result_nums = int("".join(result_nums[1].split(",")))
    print(result_nums)