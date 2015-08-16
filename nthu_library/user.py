from nthu_library.crawler import login_action, \
    crawl_user_reserve_history, \
    crawl_current_borrow, crawl_borrow_history, \
    crawl_personal_page, get_personal_details_table

__author__ = 'salas'


class NotLoginException(Exception):
    pass


class Account:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.home_url = ''
        self.session_url = ''
        self.is_login = False

    def login(self):
        resp = login_action(self)
        self.is_login = '您已登入' in resp.text
        self.session_url = resp.url
        return self.is_login

    def to_dict(self):
        return {
            'bor_id': self.username,
            'bor_verification': self.password,
            'func': 'login',
            'ssl_flag': 'Y',
        }


class User:

    def __init__(self, parent, account):
        self.parent = parent
        self.account = account
        self.is_login = self.init_account()
        self.resource_link = None

    def init_account(self):
        return self.account.login()

    def get_info(self):
        if not self.is_login:
            raise NotLoginException
        self.resource_link, result = crawl_personal_page(self.account.session_url)
        return result

    def get_reserve_history(self):
        if not self.is_login:
            raise NotLoginException
        try:
            rows = get_personal_details_table(self.resource_link['預約歷史清單'])
            return crawl_user_reserve_history(rows)
        except AttributeError:
            return []

    def get_current_borrow(self):
        if not self.is_login:
            raise NotLoginException
        try:
            rows = get_personal_details_table(self.resource_link['目前借閱中清單'])
            return crawl_current_borrow(rows)
        except AttributeError:
            return []

    def get_borrow_history(self):
        if not self.is_login:
            raise NotLoginException
        try:
            rows = get_personal_details_table(self.resource_link['借閱歷史清單'])
            return crawl_borrow_history(rows)
        except AttributeError:
            return []

