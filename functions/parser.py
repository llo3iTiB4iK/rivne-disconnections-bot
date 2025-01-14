import requests
import re
from bs4 import BeautifulSoup


class Parser:

    def __init__(self, url):
        response = requests.get(url, verify=False)
        self.content = response.text

    def read_table(self):
        soup = BeautifulSoup(self.content, 'html.parser')
        table = soup.find("table")
        return [cell.getText() for cell in table.find_all("td")]

    def find_text_by_pattern(self, pattern):
        return re.search(pattern, self.content).group()
