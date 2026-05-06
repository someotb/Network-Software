import time
import grpc
import sys
import os

week_08_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, week_08_path)

from proto import service_pb2
from proto import service_pb2_grpc

def run_grpc_bench():
    print("Starting gRPC benchmark...")
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = service_pb2_grpc.OrdersServiceStub(channel)

        # Warmup
        for _ in range(100):
            stub.CreateOrder(service_pb2.CreateOrderRequest(text="warmup", priority=1))

        # Benchmark
        start = time.time()
        for i in range(1000):
            stub.CreateOrder(service_pb2.CreateOrderRequest(text=f"Order {i}", priority=i % 10))
        end = time.time()

        elapsed = end - start
        rps = 1000 / elapsed
        print(f"gRPC: {elapsed:.4f} sec")
        print(f"gRPC RPS: {rps:.2f} requests/sec")
        return elapsed, rps

if __name__ == "__main__":
    print("=== gRPC Benchmark ===")
    print("Make sure gRPC server is running on port 50051")
    print()

    grpc_time, grpc_rps = run_grpc_bench()

    print()
    print("=== Results ===")
    print(f"gRPC: {grpc_time:.4f} sec, {grpc_rps:.2f} RPS")
