import re

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import StringUtils as su


class InfomoneyIbovespaCompanyData(object):
    def __init__(self, server, api_stub):
        self.server = server
        self.primitive_name = 'infomoney-ibovespa-company-data'
        self.api_stub = api_stub

    def consume(self, message):

        # initializes the chrome driver with the requires window size and position
        driver = webdriver.Chrome(executable_path='chromedriver.exe')
        driver.set_window_size(1080, 2500)
        driver.set_window_position(100, 0)

        driver.get('https://www.infomoney.com.br/cotacoes/ibovespa/')

        tbbody_low_xpath = '//*[@id="low"]/tbody'
        tbbody_high_xpath =  '//*[@id="high"]/tbody'

        data_collected = []

        data_collected.extend(_find_companies_data(driver, tbbody_high_xpath))
        data_collected.extend(_find_companies_data(driver, tbbody_low_xpath))

        company_data = []

        stock_title_xpath = '/html/body/div[4]/div/div[1]/div[1]/div/div[1]/h1'
        company_type_xpath = '//*[@id="header-quotes"]/div[2]/h3[2]/strong'
        initials_xpath = '//*[@id="header-quotes"]/div[2]/h3[1]/strong'
        sector_xpath = '//*[@id="header-quotes"]/div[2]/h3[3]/strong'
        description_xpath = '//*[@id="header-quotes"]/div[2]/div'

        for stock_data in data_collected:
            
            driver.get(stock_data['link'])
            
            initials = driver.find_element_by_xpath(initials_xpath).text
            name = re.compile('\\s{2}\\s*').split(driver.find_element_by_xpath(stock_title_xpath).text)[0]
            company_type = driver.find_element_by_xpath(company_type_xpath).text
            sector = driver.find_element_by_xpath(sector_xpath).text
            description = su.remove_html(driver.find_element_by_xpath(description_xpath).text)

            company_data.append({
                'initials': initials,
                'name': name,
                'infomoneyUrl': stock_data['link'],
                'type': company_type,
                'sector': sector,
                'description': description,
            })

        driver.quit()
        api_stub.infomoney_ibovespa_company_data(company_data)
        


    def _find_companies_data(self, driver, tbody_xpath):
        tbody = driver.find_element_by_xpath(tbody_xpath)
        odd = tbody.find_elements_by_class_name('odd')
        even = tbody.find_elements_by_class_name('even')
        data_collected = []
        
        for row in odd + even:
            stock_name_col = row.find_element_by_xpath('.//td[1]/a')
            stock_name = stock_name_col.text
            stock_link = stock_name_col.get_attribute('href')
            if not stock_name:
                stock_name = stock_link.split('/')[-1]

            data_collected.append({
                'name': stock_name,
                'link': stock_link,
            })

        return data_collected
