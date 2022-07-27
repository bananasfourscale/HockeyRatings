from ast import Del
from time import sleep
from selenium import webdriver
import time
from bs4 import BeautifulSoup

driver = webdriver.Chrome("C:\\Users\\lindb\\Documents\\chromedriver_win32\\chromedriver.exe")
driver.get("https://www.nhl.com/stats/teams")
time.sleep(5)
pageSource = driver.page_source
soup = BeautifulSoup(pageSource, 'html.parser')
# print(soup.prettify)
driver.close()
fileToWrite = open("test_file.txt", "w", encoding="utf-8")
source_str = soup.prettify()
table_index = source_str.find('''<div class="rt-tbody" role="rowgroup" style="min-width: 1244px;">''')
print(table_index)
source_str_trimmed = source_str[table_index:-1]
# fileToWrite.write(soup.prettify())
# fileToWrite.write(str(soup.find_all('div')))
fileToWrite.write(source_str_trimmed)
del source_str
del soup
del pageSource
del driver
fileToWrite.close()
