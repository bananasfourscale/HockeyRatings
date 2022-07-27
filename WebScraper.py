from selenium import webdriver
import time
from bs4 import BeautifulSoup

driver = webdriver.Chrome("P:\\chromedriver.exe")
driver.get("https://www.nhl.com/stats/teams")
time.sleep(10)
pageSource = driver.page_source
soup = BeautifulSoup(pageSource, 'html.parser')
driver.close()
source_str = soup.prettify()
table_index = source_str.find(
    '''<div class="rt-tbody" role="rowgroup" style="min-width: 1244px;">''')
source_str_trimmed = source_str[table_index:-1]
table_index = source_str_trimmed.find(
    '''<button class="prev-button" disabled="">''')
source_str_trimmed = source_str_trimmed[0:table_index]
source_str_trimmed = source_str_trimmed.split('\n')
index = 0
for row in source_str_trimmed:
    if index < 50:
        print("{} = {}".format(index, row))
        index += 1
del source_str_trimmed
del source_str
del soup
del pageSource
del driver
