from components import \
    Browser, SearchCompanyYandex, ListOverflowException


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


if __name__ == '__main__':
    # get data from user's import
    company = input()
    keywords = input()
    filial = input()

    # set browser for search
    browser_obj = Browser(mode='window')
    search_obj = SearchCompanyYandex(
        browser=browser_obj,
        keyword=keywords,
        company=company,
        filial=filial
    )

    url1 = zoom_search('https://yandex.ru/maps/', browser_obj, search_obj)
    zoom_search(make_url(url1, '13'), browser_obj, search_obj)
    zoom_search(make_url(url1, '14'), browser_obj, search_obj)

    browser_obj.driver.quit()

"""https://yandex.ru/showcaptcha?cc=1&mt=69E3AA0BD0BDEF0CF170C29EDBFCCE7C752940E645BB051508343B7B81E5BEA7E3E5D3CC6DCFBFC3D545346CC7CAFC2B8976B5652E44C6AD16CA1C1C1A4C05A79C7018752E0EB0A661799864AD553210BA0C152A86708224DA4D&retpath=aHR0cHM6Ly95YW5kZXgucnUvbWFwcz8%2C_8f0465a045eb9ab8408d5ac887a8c260&t=2/1688030506/090bb1126094203b4a9797a93dbe82f1&u=715bac54-70470859-f3ab283d-4b92909c&s=6deedd3c79fe48aad956f3f7cae321e4"""
