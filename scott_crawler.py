import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def getPage(url):
    page = requests.get(url)
    page.encoding = 'utf-8'
    return page

def parseDetail(page, url):
	soup = BeautifulSoup(page.text, 'lxml')
	links = soup.find('table', 'listview').find_all('a')
	for link in links:
		link = link.get('href', '')
		ta = urljoin(url, link)
		#print(ta)

def parseTransfer(page, url):
	soup = BeautifulSoup(page.text, 'lxml')
	links = soup.find('div', 'clearfix').find_all('a')
	for link in links[1:]:
		link = link.get('href', '')
		ta = urljoin(url, link)
		print(ta)

def parse(page):
	soup = BeautifulSoup(page.text, 'lxml')
	table = soup.find_all('div', 'clearfix')
	blocks = table[0].find_all('div', '')
	for block in blocks[1:]:
		links = block.find_all('a')
		for link in links:
			link = link.get('href', '')
			url = 'http://www.lib.nthu.edu.tw/library/department/ref/exam/' + link
			#print(url)
			detailPage = getPage(url)
			parseDetail(detailPage, url)
	transferLinks = soup.find('ul', 'list02 clearfix').find_all('a')
	for transferLink in transferLinks:
		link = transferLink.get('href', '')
		url = 'http://www.lib.nthu.edu.tw/library/department/ref/exam/' + link
		transferPage = getPage(url)
		parseTransfer(transferPage, url)

if __name__ == '__main__':
	url = 'http://www.lib.nthu.edu.tw/library/department/ref/exam/index.htm'
	departmentPage = getPage(url)
	parse(departmentPage)