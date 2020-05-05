import os
import time
import uuid
import csv
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class FetchInfomoneyIbovespaHistoricDataHandler(object):
    def __init__(self, server, api_stub):
        self.server = server
        self.primitive_name = 'fetch-infomoney-ibovespa-historic-data'
        self.api_stub = api_stub

    def consume(self, message):
        request_id = uuid.uuid4().__str__()
        download_dir = os.path.join(os.path.dirname(__file__), request_id)
        os.mkdir(download_dir)
        
        driver = webdriver.Chrome(executable_path='chromedriver.exe')
        driver.set_window_size(1080, 2500)
        driver.set_window_position(100, 0)
        
        collected_data = self.fetch_company_data_from_ibovespa_page(driver)
        self.configure_download_folder(driver, download_dir)
        for stock_data in collected_data:
            try:
                self.download_historic_data(driver, stock_data)
                time.sleep(5)
                self.send_downloaded_data_to_api(download_dir, stock_data)
                self.delete_downloaded_data(download_dir)
            except Exception as e:
                print(e)
                print(f'Error fetching data of {stock_data}')
        
        driver.quit()
        os.rmdir(download_dir)

    def fetch_company_data_from_ibovespa_page(self, driver):
        driver.get('https://www.infomoney.com.br/cotacoes/ibovespa/')

        tbbody_low_xpath = '//*[@id="low"]/tbody'
        tbbody_high_xpath =  '//*[@id="high"]/tbody'

        data_collected = []

        data_collected.extend(self._find_companies_data(driver, tbbody_high_xpath))
        data_collected.extend(self._find_companies_data(driver, tbbody_low_xpath))

        return data_collected

    def configure_download_folder(self, driver, download_dir):
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd':'Page.setDownloadBehavior', 'params': { 'behavior': 'allow', 'downloadPath': download_dir }}
        driver.execute("send_command", params)

    def download_historic_data(self, driver, stock_data):
        driver.get(stock_data.link)
        
        # all of the xpaths used in this method
        download_file_xpath = '//*[@id="quotes_history_wrapper"]/div/button'
        dt_min_stock_csv_xpath = '//*[@id="dateMin"]'
        dt_max_stock_csv_xpath = '//*[@id="dateMax"]'
        historic_a_xpath = '/html/body/div[4]/div/div[2]/a[2]'
        loading_gif_xpath = '//*[@id="img_load_more_quotes_history"]'
        see_all_stock_csv_xpath = '//*[@id="see_all_quotes_history"]'
        tbody_xpath = '//*[@id="quotes_history"]/tbody'
        
        # finds and clicks on the historic button
        historic_a_element = driver.find_element_by_xpath(historic_a_xpath)
        driver.implicitly_wait(10)
        historic_a_element.click()

        # finds all the elements in the historic data page
        download_file_element = driver.find_element_by_xpath(download_file_xpath)
        dt_min_stock_csv_element = driver.find_element_by_xpath(dt_min_stock_csv_xpath)
        dt_max_stock_csv_element = driver.find_element_by_xpath(dt_max_stock_csv_xpath)
        loading_gif_element = driver.find_element_by_xpath(loading_gif_xpath)
        see_all_stock_csv_element = driver.find_element_by_xpath(see_all_stock_csv_xpath)
        tbody_element = driver.find_element_by_xpath(tbody_xpath)

        # types in the time period for the stock prices data
        driver.implicitly_wait(10)
        dt_min_stock_csv_element.send_keys('01/01/2015')
        dt_max_stock_csv_element.send_keys(self._ddMMyyyy(date.today()))
        dt_max_stock_csv_element.send_keys(Keys.TAB)
        time.sleep(1)

        # clicks on the button that shows the request historic data
        see_all_stock_csv_element.click()

        # waits until the historic data is loaded
        WebDriverWait(loading_gif_element, 150).until(StyleContaining(loading_gif_element, 'display: none'))
        
        # clicks the download file button
        download_file_element.click()


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

            data_collected.append(StockData(stock_name, stock_link))

        return data_collected

    def send_downloaded_data_to_api(self, download_dir, stock_data):
        with open(self._get_filename(download_dir), encoding='utf8') as f:
            csv_reader = csv.reader(f, delimiter=',')
            message = { 'stockData': [] }
            i = 0
            for row in csv_reader:
                if i is not 0:
                    if len(message['stockData']) is 50:
                        self.api_stub.persist_infomoney_ibovespa_historic_data(message)
                        message['stockData'] = []
                    message['stockData'].append({
                        'name': stock_data.name,
                        'date': row[0],
                        'open': row[1],
                        'close': row[2],
                        'variation': row[3],
                        'min': row[4],
                        'max': row[5],
                        'volume': row[6],
                    })
                i += 1
            self.api_stub.persist_infomoney_ibovespa_historic_data(message)
        
    def delete_downloaded_data(self, download_dir):
        os.remove(self._get_filename(download_dir))

    def _get_filename(self, download_dir):
        for root, dirs, files in os.walk(download_dir):
            for file in files:
                return os.path.join(download_dir, file)
    
    def _ddMMyyyy(self, date):
        day, month, year = str(date.day).zfill(2), str(date.month).zfill(2), str(date.year).zfill(4)
        return f'{day}/{month}/{year}'

class StockData(object):
    def __init__(self, name, link):
        self.name = name
        self.link = link

    def __str__(self):
        return f'{self.name} - {self.link}'

class StyleContaining(object):
    def __init__(self, element, style_containing):
        self.element = element
        self.style_containing = style_containing

    def __call__(self, driver):
        if self.style_containing in self.element.get_attribute('style'):
            return self.element
        else:
            return False
