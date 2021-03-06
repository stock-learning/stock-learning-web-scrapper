from stock_learning_rabbitmq.ApiStub import ApiStub
from stock_learning_rabbitmq.RabbitMQServer import RabbitMQServer

from InfomoneyIbovespaCompanyData import InfomoneyIbovespaCompanyData
from InfomoneyIbovespaHistoricData import InfomoneyIbovespaHistoricData
from InfomoneyIbovespaLiveUpdate import InfomoneyIbovespaLiveUpdate
from YahooCompanyHistoricData import YahooCompanyHistoricData

server = RabbitMQServer('stock-learning-web-scrapper', 'localhost')
api_stub = ApiStub(server)

server.register(InfomoneyIbovespaCompanyData(server, api_stub))
server.register(InfomoneyIbovespaHistoricData(server, api_stub))
server.register(InfomoneyIbovespaLiveUpdate(server, api_stub))
server.register(YahooCompanyHistoricData(server, api_stub))

server.disable_heartbeat()
server.start_listening()
