import grpc
import time
import random
import threading
import queue
from concurrent import futures
import chat_pb2
import chat_pb2_grpc
import datetime

class LogicalClock:
    """Implements a logical clock using timestamps."""
    def __init__(self):
        self.time = 0

    def tick(self):
        """Advances time for an internal event."""
        self.time += 1

    def update(self, received_time):
        """Updates the clock based on received message timestamp."""
        self.time = max(self.time, received_time) + 1

class ChatService(chat_pb2_grpc.ChatServiceServicer):
    """Handles incoming RPC messages."""
    def __init__(self, vm):
        self.vm = vm 

    def SendMessage(self, request, context):
        """Receives a message and adds it to the network queue."""
        self.vm.receive_message(request.sender_id, request.timestamp)
        return chat_pb2.Message(sender_id=self.vm.machine_id, timestamp=self.vm.logical_clock.time)

class VirtualMachine:
    """Simulates a distributed machine with logical clocks using gRPC."""
    def __init__(self, machine_id, port, peers):
        self.machine_id = machine_id
        self.port = port
        self.peers = peers  # List of other machine ports
        self.clock_speed = random.randint(1, 6)  
        self.logical_clock = LogicalClock()
        self.log_file = f"machine_{machine_id}.log"
        self.network_queue = queue.Queue()

        # Start gRPC server thread
        self.server_thread = threading.Thread(target=self.start_grpc_server, daemon=True)
        self.server_thread.start()

    def start_grpc_server(self):
        """Starts the gRPC server to handle incoming messages."""
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
        chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(self), server)
        server.add_insecure_port(f"[::]:{self.port}")
        print(f"Machine {self.machine_id} gRPC server running on port {self.port}...")
        server.start()
        server.wait_for_termination()

    def send_message(self, target_port):
        """Sends a message to another machine using gRPC."""
        self.logical_clock.tick()
        message = chat_pb2.Message(sender_id=self.machine_id, timestamp=self.logical_clock.time)
        
        try:
            with grpc.insecure_channel(f"localhost:{target_port}") as channel:
                stub = chat_pb2_grpc.ChatServiceStub(channel)
                _ = stub.SendMessage(message)
                self.log_event(f"Sent message to Machine {target_port} | Logical Clock: {self.logical_clock.time}")
        except Exception as e:
            print(f"Failed to send message to Machine {target_port}: {e}")

    def receive_message(self, sender_id, timestamp):
        """Instead of processing immediately, queue the incoming message."""
        self.network_queue.put((sender_id, timestamp))
        self.log_event(f"Queued message from Machine {sender_id} with timestamp {timestamp}")

    def process_network_queue(self):
        """Processes one message from the network queue if available."""
        sender_id, timestamp = self.network_queue.get()
        self.logical_clock.update(timestamp)
        self.log_event(f"Processed message from Machine {sender_id} | Logical Clock: {self.logical_clock.time}")

    def log_event(self, event):
        """Logs events to a file."""
        with open(self.log_file, "a") as f:
            print(f"MachineID: {self.machine_id} [{datetime.datetime.now()}] {event}\n")
            f.write(f"[{datetime.datetime.now()}] {event}\n")

    def run(self):
        """Main execution loop (simulating machine operations)."""
        print(f"Machine {self.machine_id} running at {self.clock_speed} ticks/sec")
        self.log_event(f"Started with clock speed {self.clock_speed}")

        while True:
            start_time = time.time()
            if not self.network_queue.empty():
                # Check and process one message from the network queue per tick
                self.process_network_queue()
            else:
                # Decide next action if no message was processed
                action = random.randint(1, 10)
                if action == 1:
                    self.send_message(self.peers[0])
                elif action == 2:
                    self.send_message(self.peers[1])
                elif action == 3:
                    for peer in self.peers:
                        self.send_message(peer)
                else:
                    self.logical_clock.tick()
                    self.log_event(f"Internal Event | Logical Clock: {self.logical_clock.time}")
            
            # Simulate clock speed subtracted by processing time
            time.sleep(max(0, (1 / self.clock_speed) - (time.time() - start_time)))