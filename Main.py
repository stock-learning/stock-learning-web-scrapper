from stock_learning_rabbitmq.RabbitMQ import RabbitMQ
from FetchInfomoneyIbovespaHistoricDataHandler import FetchInfomoneyIbovespaHistoricDataHandler
from stock_learning_rabbitmq.ApiStub import ApiStub


server = RabbitMQ('stock-learning-web-scrapper', 'localhost')
api_stub = ApiStub(server)

teste = FetchInfomoneyIbovespaHistoricDataHandler(server, api_stub)

server.register(teste)

teste.consume({})

server.start_listening()
