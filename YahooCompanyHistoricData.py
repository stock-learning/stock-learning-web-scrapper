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

import DateUtils as du
import Decorators as dc
import FileUtils as fu


class YahooCompanyHistoricData(object):
    def __init__(self, server, api_stub):
        self.server = server
        self.primitive_name = 'yahoo-company-historic-data'
        self.api_stub = api_stub

    def consume(self, message):

        if 'initials' in message and len(message['initials']) > 0:
            
            # creates the historic_data directory if it does not exist
            historic_data_dir = os.path.join(os.path.dirname(__file__), 'historic_data')
            if not os.path.isdir(historic_data_dir):
                os.mkdir(historic_data_dir)

            # creates a id for the request and makes a folder inside of historic_data for it
            request_id = uuid.uuid4().__str__()
            download_dir = os.path.join(historic_data_dir, request_id)
            os.mkdir(download_dir)
            
            # initializes the chrome driver with the requires window size and position
            driver = webdriver.Chrome(executable_path='chromedriver.exe')
            driver.set_window_size(1080, 2500)
            driver.set_window_position(100, 0)
            
            # configures the download directory in which all files will be downloaded
            driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
            params = {'cmd':'Page.setDownloadBehavior', 'params': { 'behavior': 'allow', 'downloadPath': download_dir }}
            driver.execute("send_command", params)
            
            # iterates through all the collected companies retrieving it's historic data
            for initials in message['initials']:

                # tries up to 10 times to donwload csv
                self.download_historic_data(driver, f'https://finance.yahoo.com/quote/{initials}.SA/history?p={initials}.SA')
                # waits 5 seconds for download to finish (we could use some kind callback for when the downloaded file appears)
                time.sleep(5)

                # if the download occours successfuly, we build a message with that file, send to the API and delete it
                if fu.directory_has_file(download_dir):

                    # builds a message to send to the API
                    message = self.build_api_message_from_file_and_initials(fu.get_only_filename_in_directory(download_dir), initials)
                    # actually send the message to the API
                    self.api_stub.yahoo_company_historic_data(message)
                    # deletes the downloaded file
                    os.remove(fu.get_only_filename_in_directory(download_dir))
                
            # closes the chrome driver and removes the directory created for this request        
            driver.quit()
            os.rmdir(download_dir)


    @dc.retry(times=10, iter_message='{3} try number {0}', except_message='Error fetching data of {2}')
    def download_historic_data(self, driver, link):
        driver.get(link)
        
        # all of the xpaths used in this method
        time_period_btn_xpath = '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/div/div/div'
        max_btn_xpath = '//*[@id="dropdown-menu"]/div/ul[2]/li[4]/button'
        donwload_csv_btn_xpath = '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[2]/span[2]/a/span'
        
        driver.implicitly_wait(10)
        time_period_btn_element = driver.find_element_by_xpath(time_period_btn_xpath)
        time_period_btn_element.click()
        
        driver.implicitly_wait(10)
        max_btn_element = driver.find_element_by_xpath(max_btn_xpath)
        max_btn_element.click()
        
        driver.implicitly_wait(10)
        donwload_csv_btn_element = driver.find_element_by_xpath(donwload_csv_btn_xpath)
        donwload_csv_btn_element.click()


    def build_api_message_from_file_and_initials(self, downloaded_file_path, initials):
        with open(downloaded_file_path, encoding='utf8') as f:
            csv_reader = csv.reader(f, delimiter=',')
            message = { 'stockData': [] }
            first = True
            for row in csv_reader:
                if first:
                    first = False
                    continue
                message['stockData'].append({
                    'name': initials,
                    'date': row[0],
                    'open': row[1],
                    'close': row[4],
                    'min': row[3],
                    'max': row[2],
                    'volume': row[6],
                    'adjClose': row[5],
                })
            return message
