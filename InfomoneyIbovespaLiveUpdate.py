import datetime
import re

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import StringUtils as su


class InfomoneyIbovespaLiveUpdate(object):
    def __init__(self, server, api_stub):
        self.server = server
        self.primitive_name = 'infomoney-ibovespa-live-update'
        self.api_stub = api_stub

    def consume(self, message):
        print(message)
        if 'initials' in message:
            initials_arr = message['initials']
            
            # initializes the chrome driver with the requires window size and position
            driver = webdriver.Chrome(executable_path='chromedriver.exe')
            driver.set_window_size(1080, 2500)
            driver.set_window_position(100, 0)

            live_updates = []

            close_xpath = '//*[@id="header-quotes"]/div[1]/table[1]/tbody/tr[1]/td[2]'
            open_xpath = '//*[@id="header-quotes"]/div[1]/table[1]/tbody/tr[2]/td[2]'
            business_xpath = '//*[@id="header-quotes"]/div[1]/table[1]/tbody/tr[3]/td[2]'
            quantity_xpath = '//*[@id="header-quotes"]/div[1]/table[1]/tbody/tr[4]/td[2]'
            volume_xpath = '//*[@id="header-quotes"]/div[1]/table[1]/tbody/tr[5]/td[2]'
            min_xpath = '/html/body/div[4]/div/div[1]/div[1]/div/div[3]/div[3]/p'
            max_xpath = '/html/body/div[4]/div/div[1]/div[1]/div/div[3]/div[4]/p'
            variation_day_xpath = '//*[@id="header-quotes"]/div[1]/table[2]/tbody/tr[2]/td[2]'
            variation_month_xpath = '//*[@id="header-quotes"]/div[1]/table[2]/tbody/tr[3]/td[2]'
            variation_year_xpath = '//*[@id="header-quotes"]/div[1]/table[2]/tbody/tr[4]/td[2]'
            variation_52_weeks_xpath = '//*[@id="header-quotes"]/div[1]/table[2]/tbody/tr[5]/td[2]'

            for initials in initials_arr:
                try:
                    driver.get(f'https://www.infomoney.com.br/{initials}')

                    live_updates.append({
                        'name': initials,
                        'fetchTime': datetime.datetime.now().__str__(),
                        'close': driver.find_element_by_xpath(close_xpath).text,
                        'open': driver.find_element_by_xpath(open_xpath).text,
                        'business': driver.find_element_by_xpath(business_xpath).text,
                        'quantity': driver.find_element_by_xpath(quantity_xpath).text,
                        'volume': driver.find_element_by_xpath(volume_xpath).text,
                        'min': driver.find_element_by_xpath(min_xpath).text,
                        'max': driver.find_element_by_xpath(max_xpath).text,
                        'variationDay': driver.find_element_by_xpath(variation_day_xpath).text,
                        'variationMonth': driver.find_element_by_xpath(variation_month_xpath).text,
                        'variationYear': driver.find_element_by_xpath(variation_year_xpath).text,
                        'variation52weeks': driver.find_element_by_xpath(variation_52_weeks_xpath).text,
                    })
                except Exception as e:
                    print(f'Error fetching live update for {initials}. {e}')


            driver.quit()
            self.api_stub.infomoney_ibovespa_live_update({ 'liveUpdateStockData': live_updates })
