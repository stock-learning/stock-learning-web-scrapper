class StockData(object):
    def __init__(self, name, link):
        self.name = name
        self.link = link

    def __str__(self):
        return f'{self.name} - {self.link}'
