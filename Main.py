from stock_learning_rabbitmq.ApiStub import ApiStub
from stock_learning_rabbitmq.RabbitMQServer import RabbitMQServer

from InfomoneyIbovespaHistoricData import InfomoneyIbovespaHistoricData
from InfomoneyIbovespaLiveUpdate import InfomoneyIbovespaLiveUpdate

server = RabbitMQServer('stock-learning-web-scrapper', 'localhost')
api_stub = ApiStub(server)

server.register(InfomoneyIbovespaHistoricData(server, api_stub))
server.register(InfomoneyIbovespaLiveUpdate(server, api_stub))

server.disable_heartbeat()
server.start_listening()
