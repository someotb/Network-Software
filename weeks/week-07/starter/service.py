import grpc
from concurrent import futures
import sys
sys.path.append("proto")
import service_pb2
import service_pb2_grpc

tickets_db = []

class TicketsServiceServicer(service_pb2_grpc.TicketsServiceServicer):
    def CreateTicket(self, request, context):
        # Создаём новый тикет
        new_ticket = service_pb2.Ticket(
            id=str(len(tickets_db) + 1),
            text=request.text,
            status=request.status
        )
        # Добавляем в базу
        tickets_db.append(new_ticket)
        # Возвращаем Response
        return service_pb2.CreateTicketResponse(
            id=new_ticket.id,
            text=new_ticket.text,
            status=new_ticket.status
        )

    def GetTickets(self, request, context):
        # Возвращаем все тикеты
        return service_pb2.GetTicketsResponse(tickets=tickets_db)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_TicketsServiceServicer_to_server(
        TicketsServiceServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
