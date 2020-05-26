from StockData import StockData


def fetch_company_data_from_ibovespa_page(driver):
    driver.get('https://www.infomoney.com.br/cotacoes/ibovespa/')

    tbbody_low_xpath = '//*[@id="low"]/tbody'
    tbbody_high_xpath =  '//*[@id="high"]/tbody'

    data_collected = []

    data_collected.extend(_find_companies_data(driver, tbbody_high_xpath))
    data_collected.extend(_find_companies_data(driver, tbbody_low_xpath))

    return data_collected

def _find_companies_data(driver, tbody_xpath):
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
