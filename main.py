import os
import json

from nthu_library import NTHULibrary, timeit
from nthu_library.user import Account

__author__ = 'salas'


function_doc = """
    'personal': get_personal_info,
    'new': get_newest_books,
    'top': get_top_circulations,
    'lost': get_lost,
"""


def get_newest_books(lib, **kwargs):
    """
        :param lang: default is `None` to get both languages,
                     'en' for English; or 'zh' for Chinese
    """
    return lib.get_newest_books(**kwargs)


def get_top_circulations(lib, **kwargs):
    """
        :param year: 4-digit number
        :param type: 'loaned' or 'reserved'
    """
    return lib.get_top_circulated_materials(**kwargs)


def get_personal_info(lib):
    return {
        'personal': lib.get_info(),
        '借閱歷史': lib.get_borrow_history(),
        '借閱中': lib.get_current_borrow(),
        '預約紀錄': lib.get_reserve_history(),
    }


def get_lost(lib):
    """
    :param lib:
    :return: <list()> 失物招領物品列表
    """
    return lib.get_lost()

def get_past_year_questions(lib):
    """
    :param lib:
    :return: <list()> 考古題連結清單
    """
    return lib.get_past_year_questions()

@timeit
def start(instr, lib):
    results = funcs[instr](lib)
    with open('my-library-data.json', 'w', encoding='utf8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, sort_keys=True)


''' functions eval() from doc string '''
funcs = eval('{%s}' % ''.join(function_doc.split()))


if __name__ == '__main__':

    account = os.getenv('NTHU_LIBRARY_ID') or input('ID: ')
    password = os.getenv('NTHU_LIBRARY_PWD') or input('PWD: ')
    library = NTHULibrary(Account(account, password))

    start('personal', library)
    start('top', library)
    start('new', library)
    start('lost', library)
