import csv
import datetime
import os
import time
import uuid

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import CompanyData as cd
import DateUtils as du
import Decorators as dc
import FileUtils as fu


class InfomoneyIbovespaInitialLoad(object):
    def __init__(self, server, api_stub):
        self.server = server
        self.primitive_name = 'infomoney-ibovespa-initial-load'
        self.api_stub = api_stub

    def consume(self, message):
        # creates the initial_load directory if it does not exist
        initial_load_dir = os.path.join(os.path.dirname(__file__), 'initial_load')
        if not os.path.isdir(initial_load_dir):
            os.mkdir(initial_load_dir)

        # creates a id for the request and makes a folder inside of initial_load for it
        request_id = uuid.uuid4().__str__()
        download_dir = os.path.join(initial_load_dir, request_id)
        os.mkdir(download_dir)
        
        # initializes the chrome driver with the requires window size and position
        driver = webdriver.Chrome(executable_path='chromedriver.exe')
        driver.set_window_size(1080, 2500)
        driver.set_window_position(100, 0)
        
        # uses the drive to fetch all the companies available for web scrapping
        collected_data = cd.fetch_company_data_from_ibovespa_page(driver)
        
        # configures the download directory in which all files will be downloaded
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd':'Page.setDownloadBehavior', 'params': { 'behavior': 'allow', 'downloadPath': download_dir }}
        driver.execute("send_command", params)
        
        # iterates through all the collected companies retrieving it's historic data
        for stock_data in collected_data:

            # tries up to 10 times to donwload csv
            self.download_historic_data(driver, stock_data)
            # waits 5 seconds for download to finish (we could use some kind callback for when the downloaded file appears)
            time.sleep(5)

            # if the download occours successfuly, we build a message with that file, send to the API and delete it
            if fu.directory_has_file(download_dir):

                # builds a message to send to the API
                message = self.build_api_message_from_file_and_stock_data(fu.get_only_filename_in_directory(download_dir), stock_data)
                # actually send the message to the API
                self.api_stub.infomoney_ibovespa_initial_load(message)
                # deletes the downloaded file
                os.remove(fu.get_only_filename_in_directory(download_dir))
            
        # closes the chrome driver and removes the directory created for this request        
        driver.quit()
        os.rmdir(download_dir)


    @dc.retry(times=10, iter_message='{3} try number {0}', except_message='Error fetching data of {2}')
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
        dt_max_stock_csv_element.send_keys(du.date_to_str_ddMMyyyy(datetime.date.today()))
        dt_max_stock_csv_element.send_keys(Keys.TAB)
        time.sleep(1)

        # clicks on the button that shows the request historic data
        see_all_stock_csv_element.click()

        # waits until the historic data is loaded
        WebDriverWait(loading_gif_element, timeout=60).until(StyleContaining(loading_gif_element, 'display: none'))
        
        # clicks the download file button
        download_file_element.click()

    def build_api_message_from_file_and_stock_data(self, downloaded_file_path, stock_data):
        with open(downloaded_file_path, encoding='utf8') as f:
            csv_reader = csv.reader(f, delimiter=',')
            message = { 'stockData': [] }
            for row in csv_reader:
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
            return message


class StyleContaining(object):
    def __init__(self, element, style_containing):
        self.element = element
        self.style_containing = style_containing

    def __call__(self, driver):
        if self.style_containing in self.element.get_attribute('style'):
            return self.element
        else:
            return False