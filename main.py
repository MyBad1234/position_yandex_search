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
    result_scroll = None
    try:
        result_scroll = search.scroll_results()
        print('position: ' + str(result_scroll))
    except ListOverflowException:
        print('position: not found')

    return result_scroll


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
        after_error = False
        sql_obj = SqlQuery()

        try:
            task = get_data_db(sql_obj)
        except exceptions.TaskNotFound:
            after_error = True
            time.sleep(60)
        except exceptions.ErrorDataDb:
            after_error = True
            for_while = False
            print('error in struct in db')

        if after_error is False:
            # basic logic
            browser_obj = Browser(mode='window')
            search_obj = SearchCompanyYandex(
                browser=browser_obj,
                keyword=task.get('keyword'),
                filial=task.get('yandex_id')
            )

            # get position
            result1 = zoom_search('https://yandex.ru/maps/?ll=37.436598%2C55.679159&z=13', browser_obj, search_obj)
            result2 = zoom_search('https://yandex.ru/maps/?ll=37.436598%2C55.679159&z=14', browser_obj, search_obj)
            result3 = zoom_search('https://yandex.ru/maps/?ll=37.436598%2C55.679159&z=15', browser_obj, search_obj)

            # update data in db
            sql_obj.update_status_task(task.get('id'), 3)
            sql_obj.update_status_task_other(task.get('id'), 2)
            sql_obj.set_position(result1, result2, result3, task.get('id'))

            browser_obj.driver.quit()

            time.sleep(60)
