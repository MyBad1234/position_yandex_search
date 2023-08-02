import time
import exceptions
from components import \
    Browser, SearchCompanyYandex, ListOverflowException
from sql_query import SqlQuery


def make_url(url, zoom):
    return url[:-2] + zoom


def zoom_search(url, browser, search):
    browser.driver.get(url)

    # input keywords
    search.input_text()

    # get position
    try:
        result_scroll = search.scroll_results()
        print('position: ' + str(result_scroll))
    except ListOverflowException:
        print('position: not found')

    return browser.driver.execute_script(
        "return document.location.href"
    )


def get_data_db(sql_work_obj: SqlQuery):
    """get data for work with task"""

    # get info from db
    data1 = sql_work_obj.get_queue()
    data2 = sql_work_obj.get_keyword_coordinates(data1.get('resource_id'), data1.get('entity_id'))
    id_result = sql_work_obj.get_row_for_result(data1.get('id'))

    # make data for getting
    data = {}
    data.update(data1)
    data.update(data2)
    data.update({'id_result': id_result})

    return data


if __name__ == '__main__':
    for_while = True

    while for_while:
        try:
            sql_obj = SqlQuery()
            task = get_data_db(sql_obj)
        except exceptions.TaskNotFound:
            time.sleep(60)
        except exceptions.ErrorDataDb:
            for_while = False
            print('error in struct in db')

        # basic logic
        browser_obj = Browser(mode='window')
        search_obj = SearchCompanyYandex(
            browser=browser_obj,
            keyword=task.get('keyword'),
            filial=task.get('yandex_id')
        )

        # get position
        url1 = zoom_search('https://yandex.ru/maps/?ll=37.436598%2C55.679159&z=13', browser_obj, search_obj)
        zoom_search(make_url(url1, '13'), browser_obj, search_obj)
        zoom_search(make_url(url1, '14'), browser_obj, search_obj)

        browser_obj.driver.quit()
