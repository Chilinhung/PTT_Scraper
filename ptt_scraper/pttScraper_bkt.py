import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import time 
import os
import random
import datetime
from datetime import date


keywords = '唐氏症|唐寶寶|政黨'
board = "Gossiping"
begin_date = "" # please follow the format: "yy/mm/dd"
end_date = ""	  # Note that begin_data should not be later than the end_date

def Main():	
	url = f"https://www.ptt.cc/bbs/{board}/index.html" 
	getmsg(url, board, keywords)

def getHtml(url):
	try: #get into ppt gossip
		headers = {'cookie': 'over18=1'}
		resp = requests.get(url, headers = headers)
		resp.encoding = 'utf-8'
		resp.raise_for_status()
		return resp.text
	except:
		print('Html訊息獲取失敗')


def getLastPage(board, timeout=3):
	content = requests.get(
		url= 'https://www.ptt.cc/bbs/' + board + '/index.html',
		cookies={'over18': '1'}, timeout=timeout
	).content.decode('utf-8')
	first_page = re.search(r'href="/bbs/' + board + '/index(\d+).html">&lsaquo;', content)
	if first_page is None:
		return -1
	return int(first_page.group(1)) + 1

def nextpage(url):
	soup = BeautifulSoup(getHtml(url), 'lxml')
	link = soup.find_all('a', class_='btn wide')[1]['href']
	link = 'https://www.ptt.cc' + link
	return link

def getArticleHref(title):
	html = title.find('a')
	address = html['href']
	article_url = 'https://www.ptt.cc' + address
	return article_url, html

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
def checkTime(time_for_check, begin_date, end_date):
	if begin_date == "":
		begin_date = "2004/01/01"
	if end_date == "":
		today = date.today()
		end_date = today.strftime("%Y/%m/%d")
	tfc = time.mktime(datetime.datetime.strptime(time_for_check,"%Y/%m/%d").timetuple())
	begin = time.mktime(datetime.datetime.strptime(begin_date,"%Y/%m/%d").timetuple())
	end = time.mktime(datetime.datetime.strptime(end_date,"%Y/%m/%d").timetuple())
	if tfc >= begin and tfc <= end:
		return True
	if tfc < begin:
		return -1
	return False


def getArticleContent(article_url):
	try:
		article_soup = BeautifulSoup(getHtml(article_url), 'lxml')
	except:
		print("None type has no len()")
		return
	# header
	header = article_soup.select('span.article-meta-value')
	# time check
	time_ = header[3].text
	time_list = time_.split(" ")
	m = months.index(time_list[1]) + 1
	time_for_check = f"{time_list[-1]}/{m}/{time_list[2]}"
	print(f"-----\nDate: {time_for_check}")
	ckt = checkTime(time_for_check, begin_date, end_date)
	if ckt == False:
		return None, [[]]
	elif ckt == -1:
		return -1, [[]]

	title_ = header[2].text
	board_ = header[1].text
	author_ = header[0].text
	# content
	article_container = article_soup.find(id = 'main-content')
	text = article_container.text
	pre_text = text.split('--\n')[0]
	pre_text1 = pre_text.split('\n')
	content_ = pre_text1[2:]
	# aggregate header & content
	file1 = [title_, author_, time_, board_, article_url, content_]
	
	# push
	push_ = text.split('--\n')[-1]
	push0 = push_.split('\n')
	push1 = push0[2:] 
	if push1:
		pushes = []
		pushes2 = []
		for string in push1:
			tmp = string.split(" ")
			filtered_list = [item for item in tmp if item]
			pushes.append(filtered_list)
		# modify the order in each list for easier chunking
		for ph in pushes:
			last2 = ph[-2:]
			ph = ph[:-2]
			for i, item in enumerate(last2, start = 2):
				ph.insert(i, item)
			pushes2.append(ph)
		#concat texts in one push: [tag, userID, time, content & pushIP]
		pushes = []
		for push in pushes2:
			text = push[4:]
			concat_str = ' '.join(text)
			tmp = push[:4]
			tmp.append(concat_str)
			pushes.append(tmp)
		file2 = pushes
	else:
		file2 = []
	
	return file1, file2

def contentToCsv(keywords, board, page, file1: list):
	columns = ['標題','作者', '時間', '看板', '超連結','內文']
	f1df = pd.DataFrame(file1, columns = columns)
	filename = f"ppt{board}_{keywords}{page}.csv"
	f1df.to_csv(filename, encoding = 'utf-8', index = False)
	print(f"[{filename}] has been saved in {os.getcwd()}")


def pushToCsv(title, url, keywords, board, page, file2 = list):
	columns = ['tag','userID', 'date','time', 'content & pushIP']
	f2df = pd.DataFrame(file2, columns = columns)
	f2df.loc[len(f2df.index)] = [title, url, "", "",""]
	content_id = re.search(r'/([^/]+)\.html$', url) # regex cut url to make an unique id 
	#print(f"content_id: {content_id.group(1)}")
	filename = f"ppt{board}Push_{content_id.group(1)}.csv"
	f2df.to_csv(filename, encoding = 'utf-8', index = False)
	print("[{}] has been saved in {}\n=====".format(filename, os.getcwd()))

def getmsg(url, board, keywords:str):
	content_list = [] #file1
	tt_pages = getLastPage(board)
	print("total pages: ", tt_pages)
	time_flag = 0 # early stop: check if the data is earlier than the begin_date
	pg = 0
	start_page = 37695
	for page in range(tt_pages, 0, -1):
		time.sleep(random.randint(4, 10))
		# print regularly in case the code broke in the middle
		if page % 800 == 0:
			print(page)
			if len(content_list) > 0:
				contentToCsv(keywords, board, page, content_list)
		print(page)

		#get header, content and push
		soup = BeautifulSoup(getHtml(url), 'lxml')
		titles = soup.find_all('div', class_ = 'title')
		for title in titles:
			if re.search(keywords, str(title)):
				article_url, ttl = getArticleHref(title)
				try:
					if article_url:
						f1, f2 = getArticleContent(article_url)
						if f1 == -1: # time being eariler than the defined end_data
							time_flag = -1
							break
						if f1:
							content_list.append(f1)					
						if len(f2[0]) >= 1: 
							print("title: ",title.text)
							pushToCsv(title.text, article_url, keywords, board, page, f2)
				except:
					print(".", end = "")

		if time_flag == -1: # time being eariler than the defined end_data
			break
		#if you want to start scraping from any particular page 
		if page == start_page: # remember to modify the number of the start page variable in line 148 and line 149
			url_ = f"{url[:-5]}{page}.html"
			print(url_)
			url = nextpage(url_)
		else:  
			url = nextpage(url)
		pg = page
	contentToCsv(keywords, board, pg, content_list)

				

if __name__ == "__main__":
	Main()

