from nthu_library.user import User as LibraryUser
from nthu_library.crawler import crawl_rss, \
    get_circulation_links, \
    crawl_top_circulations, crawl_lost_objects, \
    crawl_past_year_questions, crawl_available_space


class NTHULibrary(object):

    def __init__(self, user=None):
        self.user = LibraryUser(self, user) if user else None
        self._circulation_links = get_circulation_links()

    def __repr__(self):
        return '%s@library object' % self.user.account

    @staticmethod
    def get_lost(place='ALL', date_start='2015-02-10',
                 date_end='2015-08-10', catalog='ALL',
                 keyword=''):
        data = {
            'place': place, 'date_start': date_start,
            'date_end': date_end, 'catalog': catalog,
            'keyword': keyword
        }
        return crawl_lost_objects(data)

    @staticmethod
    def get_newest_books(lang=None):
        """
        fetch recent newest books from official RSS
        :param lang: default is `None` to get both languages,
                     'en' for English; or 'zh' for Chinese
        :return: `RSS dict()`
        """
        param = {'en': '?C=LCC', 'zh': '?C=CCL'}
        return crawl_rss(param.get(lang, ''))

    def get_top_circulated_materials(
            self, year=None, type='loaned'):
        """
        fetch the top circulated materials(借閱排行) in library
        :param year: 4-digit number
        :param type: 'loaned' or 'reserved'
        :return: `dict()` type data
        """
        q_type = 'b_' if type == 'loaned' else 'o_'
        query = [
            href
            for a, href in self._circulation_links
            if not year or str(year) in a.get('text')
            if a.get('href').startswith(q_type)
        ]
        return crawl_top_circulations(type, query)

    def get_info(self):
        return self.user.get_info()

    def get_current_borrow(self):
        return self.user.get_current_borrow()

    def get_borrow_history(self):
        return self.user.get_borrow_history()

    def get_current_reserve(self):
        pass

    def get_hold_reserve(self):
        pass

    def get_reserve_history(self):
        return self.user.get_reserve_history()

    @staticmethod
    def get_past_year_questions():
        return crawl_past_year_questions()

    @staticmethod
    def get_available_space():
        return crawl_available_space()
