import time

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class ModeException(Exception):
    pass


class ItIsCompanyException(Exception):
    pass


class CompanyNotFound(Exception):
    pass


class ListOverflowException(Exception):
    """if elements of search > 50"""
    pass


class Browser:
    """class for create webdriver"""

    company_found: bool
    in_windows: bool

    def __init__(self, mode: str):
        if mode == 'window':
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument("--disable-gpu")

            self.driver = webdriver.Chrome()
            self.in_windows = True
        elif mode == 'docker':
            # set options for browser in background
            options = FirefoxOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument("--disable-gpu")

            # run background browser
            self.driver = webdriver.Firefox(
                options=options
            )
            self.in_windows = False
        else:
            raise ModeException()


class SearchCompanyYandex:
    """search company by keywords"""

    def __init__(self, browser: Browser, keyword: str, filial: str):
        self.browser = browser
        self.keyword = keyword
        self.filial = filial

    def input_text(self):
        """input keyword and company to search"""

        time.sleep(1)

        # input text
        for i in range(10):
            text_box_input = self.browser.driver.find_element(by=By.CSS_SELECTOR, value="input")

            # clear value of input
            input_text = self.browser.driver.execute_script(
                "return document.querySelector('input').value"
            )
            for j in input_text:
                text_box_input.send_keys("\ue003")

            try:
                text_box_input.send_keys(
                    self.keyword
                    + "\ue007"
                )

                time.sleep(2)
                href = self.browser.driver.execute_script(
                    "return document.location.href"
                )

                if '/maps/org/' in href:
                    raise ItIsCompanyException()

                return

            except exceptions.StaleElementReferenceException:
                time.sleep(3)

        raise exceptions.StaleElementReferenceException()

    def get_position(self):
        """get position of card of company"""


        position_script = ("let condition = true; let result = 0;"
                           "for (let i of document.querySelectorAll"
                           "('.search-snippet-view')) { if (condition) "
                           "{ result += 1; }"
                           "for (let j of document.querySelectorAll('div')) {"
                           "if (i.querySelector"
                           "('.search-snippet-view__body').getAttribute('data-id')"
                           "== '" + self.filial + "')"
                           "{ condition = false; }}} return result")

        result = self.browser.driver.execute_script(position_script)
        return result

    def scroll_results(self):
        """view all results and search"""

        time.sleep(3)

        now_height = 0

        # run scripts

        for_while = True
        while for_while:
            time.sleep(2)
            self.browser.driver.execute_script("document.querySelector('.scroll__container') \
                .scrollTo({top: document \
                .querySelector('.scroll__container') \
                .scrollHeight, behavior: 'smooth'})")

            time.sleep(1)

            scroll_height = self.browser.driver.execute_script(
                "return document.querySelector('.scroll__container').scrollHeight"
            )

            # control scroll
            if scroll_height == now_height:
                for_while = False
            else:
                now_height = scroll_height

            # control elem
            condition_script = ("let company; let condition = false; "
                                "function isFilial(objLi, filial) {"
                                "if (objLi.querySelector('.search-snippet-view__body')"
                                ".getAttribute('data-id') === filial)"
                                "{ return true } else { return false }}"
                                "for (let i of document.querySelectorAll('.search-snippet-view')) {"
                                "for (let j of i.querySelectorAll('div')) { "
                                "if (isFilial(i, '" + str(self.filial) + "')) { "
                                "company = i; condition = true }}}"
                                "if (condition) { company.scrollIntoView({behavior: 'smooth', block: 'center'});"
                                "return 'yes' } else { return 'no' } ")

            condition = self.browser.driver.execute_script(condition_script)

            # work with position
            position = self.get_position()

            if condition == 'yes':
                return position
            else:
                if int(position) > 100:
                    raise ListOverflowException()
                if not for_while:
                    raise ListOverflowException()
