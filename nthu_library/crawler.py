import re
import feedparser
from urllib.parse import urljoin

import nthu_library.static_urls as nthu_library_url
from nthu_library.tools import get_page, get_pages, build_soup, post_page


get_cols = lambda row: [e for e in row.children if str(e).strip()]


def get_circulation_links():
    return [
        ({'text': a.text, 'href': a.get('href')},
         urljoin(nthu_library_url.top_circulations, a.get('href')))
        for resp in get_pages([
            nthu_library_url.top_circulations,
            nthu_library_url.top_circulations_bc2007])
        for a in build_soup(resp).find(id='cwrp').find_all('a')
    ]


def crawl_top_circulations(query):
    results = dict()
    for content in get_pages(query):
        table = build_soup(content).find('table', 'listview')
        books = list()
        for row in table.find_all('tr')[1:]:
            try:
                rk, title, ref, cnt = row.findChildren()
            except ValueError:
                # for year 2003, there's no <a> tag
                rk, title, cnt = row.findChildren()
            books.append({
                'rank': rk.text,
                'book_name': title.text.strip(' /'),
                'link': ref.get('href') if ref else None,
                'circulations': cnt.text
            })
        results[table.get('summary')] = books
    return results


def crawl_lost_objects(data):
    soup = post_page(nthu_library_url.lost_found_url, data=data)
    lost_items = list()
    for item in build_soup(soup).select('table > tr')[1:]:
        lost_items.append({
            'id': item.select('td:nth-of-type(1)')[0].text,
            'time': item.select('td:nth-of-type(2)')[0].text,
            'place': item.select('td:nth-of-type(3)')[0].text,
            'description': item.select('td:nth-of-type(4)')[0].text,
        })
    return lost_items


def login_action(account):
    """
    :param account
    :return: page source response
    """
    soup = get_page(urljoin(nthu_library_url.info_system, '?func=file&file_name=login1'))
    login_url = soup.find('form').attrs.get('action')
    resp = post_page(login_url, data=account.to_dict())
    return resp


def crawl_personal_page(session_url):
    soup = get_page(urljoin(session_url, '?func=BOR-INFO'))
    tables = soup.find_all('table', attrs={'cellspacing': '2'})

    # 流通狀態連結
    resource_links = dict()

    # 圖書館流通狀態
    status = {}
    for row in tables[0].find_all('tr'):
        cols = get_cols(row)
        key = cols[0].text.strip()
        a_tag = cols[1].find('a')
        val = a_tag.text.strip()
        link = re.findall("'(.*?)'", a_tag.get('href'))[0]
        status[key] = val
        resource_links[key] = link

    # 聯絡資料
    person = {}
    for row in tables[1].find_all('tr'):
        cols = get_cols(row)
        key = cols[0].text.strip() or '地址'
        val = cols[1].text.strip()
        person[key] = person[key] + val if key in person else val

    # 管理資訊
    manage = {}
    for row in tables[2].find_all('tr'):
        cols = get_cols(row)
        key = cols[0].text.strip()
        val = cols[1].text.strip()
        if key == '讀者權限資料':
            val = re.findall("borstatus='(.*)'", val)[0]
        manage[key] = val

    result = dict()
    result['user'] = person
    result['status'] = status
    result['user']['manage'] = manage
    return resource_links, result


def get_personal_details_table(url):
    soup = get_page(url)
    rows = soup.find('table', attrs={'cellspacing': '2', 'border': '0'}).find_all('tr')[1:]
    return rows


def crawl_user_reserve_history(rows):
    books = []
    for row in rows:
        cols = get_cols(row)
        books.append({
            'link': cols[0].find('a').attrs.get('href'),
            'author': cols[1].text,
            'title': cols[2].text.strip(' /'),
            'publish_year': cols[3].text,
            'history_date': cols[4].text,
            'booking_date': cols[5].text,
            'booking_valid': cols[6].text,
            'book_return': cols[7].text,
            'branch': cols[8].text,
            'call_number': cols[9].text,
            'branch_take': cols[10].text,
            'book_status': cols[11].text
        })
    return books


def crawl_current_borrow(rows):
    books = []
    for row in rows:
        cols = get_cols(row)
        meta_deadline = re.findall('(.*?)(\d+)', cols[5].text)[0]
        try:
            status, date = meta_deadline
        except ValueError:
            date = meta_deadline
        finally:
            books.append({
                'link': cols[0].find('a').attrs.get('href'),
                'author': cols[2].text,
                'title': cols[3].text.strip(' /'),
                'publish_year': cols[4].text,
                'deadline_status': status,
                'deadline': date,
                'publish_cost': cols[7].text,
                'branch': cols[8].text,
                'call_number': cols[9].text
            })
    return books


def crawl_borrow_history(rows):
    books = []
    for row in rows:
        cols = get_cols(row)
        meta_deadline = re.findall('(.*?)(\d+)', cols[4].text)[0]
        try:
            status, date = meta_deadline
        except ValueError:
            date = meta_deadline
        finally:
            books.append({
                'link': cols[0].find('a').attrs.get('href'),
                'author': cols[1].text,
                'title': cols[2].text.strip(' /'),
                'publish_year': cols[3].text,
                'deadline_status': status,
                'deadline': date,
                'borrow_time': cols[6].text + ' ' + re.findall('>(.*?)<', str(cols[7]))[0],
                'branch': cols[8].text
            })
    return books


def crawl_rss(param):
    feed = feedparser.parse(nthu_library_url.rss_recent_books + param)
    return feed.get('entries')


def crawl_past_year_questions():
    soup = get_page(nthu_library_url.past_year_questions_url)
    table = soup.find_all('div', 'clearfix')
    blocks = table[0].find_all('div', '')
    for block in blocks[1:]:
        links = block.find_all('a')
        for link in links:
            link = link.get('href', '')
            url = nthu_library_url.past_year_questions + link
            _crawl_detail(url)
    transferLinks = soup.find('ul', 'list02 clearfix').find_all('a')
    for transferLink in transferLinks:
        link = transferLink.get('href', '')
        url = nthu_library_url.past_year_questions + link
        _crawl_transfer(url)


def _crawl_detail(url):
    soup = get_page(url)
    links = soup.find('table', 'listview').find_all('a')
    for link in links:
        link = link.get('href', '')
        target = urljoin(url, link)


def _crawl_transfer(url):
    soup = get_page(url)
    links = soup.find('div', 'clearfix').find_all('a')
    for link in links[1:]:
        link = link.get('href', '')
        target = urljoin(url, link)


def crawl_available_space():
    soup = get_page(nthu_library_url.available_space)
    info = soup.find('section', 'status').find_all('td')
    for data in info:
        data = data.text
