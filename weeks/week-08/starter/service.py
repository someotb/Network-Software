import grpc
from concurrent import futures
import sys
import time
import os

week_08_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, week_08_path)

from proto import service_pb2
from proto import service_pb2_grpc

orders_db = []

class OrdersServiceServicer(service_pb2_grpc.OrdersServiceServicer):
    def CreateOrder(self, request, context):
        # Создаём новый заказ
        new_order = service_pb2.Order(
            id=str(len(orders_db) + 1),
            text=request.text,
            priority=request.priority
        )
        # Добавляем в базу
        orders_db.append(new_order)
        # Возвращаем Response
        return service_pb2.CreateOrderResponse(
            id=new_order.id,
            text=new_order.text,
            priority=new_order.priority
        )

    def GetOrders(self, request, context):
        return service_pb2.GetOrdersResponse(orders=orders_db)

    def SubscribeToOrders(self, request, context):
        # Отправляем текущие заказы
        for order in orders_db:
            yield service_pb2.OrderUpdate(
                id=order.id,
                text=order.text,
                priority=order.priority,
                action="existing"
            )

        # Симулируем новые заказы (для демонстрации)
        for i in range(5):
            time.sleep(1)  # Задержка 1 секунда
            yield service_pb2.OrderUpdate(
                id=f"stream-{i}",
                text=f"Streaming order {i}",
                priority=i,
                action="created"
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_OrdersServiceServicer_to_server(
        OrdersServiceServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    print("gRPC server started on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
