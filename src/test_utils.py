"""
coverage run --source=utils -m unittest test_utils.py
coverage report -m
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import queue
import chat_pb2
import chat_pb2_grpc
from utils import LogicalClock, ChatService, VirtualMachine


class TestLogicalClock(unittest.TestCase):
    def test_tick_increments_time(self):
        clock = LogicalClock()
        self.assertEqual(clock.time, 0)
        clock.tick()
        self.assertEqual(clock.time, 1)

    def test_update_lower_timestamp(self):
        clock = LogicalClock()
        clock.time = 5
        clock.update(3)  # received < current
        self.assertEqual(clock.time, 6)  # max(5,3) + 1 = 6

    def test_update_higher_timestamp(self):
        clock = LogicalClock()
        clock.time = 5
        clock.update(10)  # received > current
        self.assertEqual(clock.time, 11)  # max(5,10) + 1 = 11


class TestChatService(unittest.TestCase):
    def test_SendMessage(self):
        """
        Unit test for ChatService.SendMessage. We do not spin up a real server;
        we directly instantiate ChatService and call SendMessage(...) as if from a stub.
        """
        mock_vm = MagicMock()
        mock_vm.machine_id = 123
        mock_vm.logical_clock.time = 999

        chat_service = ChatService(mock_vm)
        request = chat_pb2.Message(sender_id=42, timestamp=100)
        context = MagicMock()  # gRPC context object, not used here

        response = chat_service.SendMessage(request, context)

        # Ensure VM was told to receive_message with the correct values
        mock_vm.receive_message.assert_called_once_with(42, 100)
        # Response should reflect the VM's machine_id & clock
        self.assertEqual(response.sender_id, 123)
        self.assertEqual(response.timestamp, 999)


class TestVirtualMachine(unittest.TestCase):

    @patch('random.randint', return_value=3)
    def test_init_vm(self, mock_rand):
        """
        Test VM initializes the attributes properly.
        """
        vm = VirtualMachine(machine_id=1, port=50051, peers=[50052, 50053])
        self.assertEqual(vm.machine_id, 1)
        self.assertEqual(vm.port, 50051)
        self.assertEqual(vm.peers, [50052, 50053])
        self.assertEqual(vm.clock_speed, 3)    # from the mocked randint because it was hard to do actual random
        self.assertTrue(isinstance(vm.network_queue, queue.Queue))
        self.assertEqual(vm.log_file, "machine_1.log")

    @patch('builtins.open', new_callable=mock_open)
    def test_receive_message(self, mock_file):
        """
        Verify that receive_message puts a tuple into the queue and logs the event.
        """
        vm = VirtualMachine(machine_id=1, port=50051, peers=[])
        self.assertTrue(vm.network_queue.empty())

        vm.receive_message(sender_id=999, timestamp=50)
        self.assertFalse(vm.network_queue.empty())

        # Check content
        msg = vm.network_queue.get()
        self.assertEqual(msg, (999, 50))

        # Check logging
        handle = mock_file()
        written = handle.write.call_args_list[0][0][0]
        self.assertIn("Queued message from Machine 999 with timestamp 50", written)

    @patch('builtins.open', new_callable=mock_open)
    def test_process_network_queue(self, mock_file):
        """
        Check that process_network_queue pops from the queue and updates the clock.
        """
        vm = VirtualMachine(machine_id=1, port=50051, peers=[])
        vm.logical_clock.time = 5
        vm.network_queue.put((10, 20))  # (sender_id=10, timestamp=20)

        vm.process_network_queue()
        self.assertTrue(vm.network_queue.empty())
        # Clock should become max(5, 20) + 1 = 21
        self.assertEqual(vm.logical_clock.time, 21)

        # Check logging
        handle = mock_file()
        written = handle.write.call_args_list[-1][0][0]
        self.assertIn("Processed message from Machine 10 | Logical Clock: 21", written)

    @patch('builtins.open', new_callable=mock_open)
    @patch('random.randint', return_value=2)
    @patch('grpc.insecure_channel')
    def test_send_message_success(self, mock_channel, mock_rand, mock_file):
        """
        Test send_message logic via a mock insecure_channel.
        """
        vm = VirtualMachine(machine_id=1, port=50051, peers=[])
        vm.logical_clock.time = 10

        mock_stub_instance = MagicMock()
        # Arbitrary response,
        mock_stub_instance.SendMessage.return_value = chat_pb2.Message(sender_id=999, timestamp=999)
        mock_channel.return_value.__enter__.return_value = MagicMock()
        mock_channel.return_value.__enter__.return_value.__class__ = MagicMock

        with patch.object(chat_pb2_grpc, 'ChatServiceStub', return_value=mock_stub_instance):
            vm.send_message(9999)

        # Check that logical clock ticked
        self.assertEqual(vm.logical_clock.time, 11)

        # Check if log_event was written
        handle = mock_file()
        last_write = handle.write.call_args_list[-1][0][0]
        self.assertIn("Sent message to Machine 9999 | Logical Clock: 11", last_write)

    @patch('builtins.open', new_callable=mock_open)
    @patch('grpc.insecure_channel', side_effect=Exception("Connection error"))
    def test_send_message_failure(self, mock_channel, mock_file):
        """
        If channel fails, confirm we handle the exception  
        and still tick the clock.
        """
        vm = VirtualMachine(machine_id=1, port=50051, peers=[])
        vm.logical_clock.time = 10

        vm.send_message(8888)
        # Clock should have incremented even if we fail to send
        self.assertEqual(vm.logical_clock.time, 11)

    @patch('builtins.open', new_callable=mock_open)
    def test_log_event(self, mock_file):
        """
        Confirm that log_event writes to the correct file with correct content.
        """
        vm = VirtualMachine(machine_id=1, port=50051, peers=[])
        vm.log_event("Test Log")
        mock_file.assert_called_with("machine_1.log", "a")

        handle = mock_file()
        write_arg = handle.write.call_args_list[0][0][0]
        self.assertIn("Test Log", write_arg)

class TestVirtualMachineRunLoop(unittest.TestCase):
    @patch('time.sleep', side_effect=Exception("StopLoop"))
    @patch('random.randint', return_value=4)  # internal event path
    def test_run_one_iteration(self, mock_rand, mock_sleep):
        vm = VirtualMachine(machine_id=1, port=50051, peers=[])
        try:
            vm.run()
        except Exception as e:
            # Expect the "StopLoop" to break from the while True
            self.assertEqual(str(e), "StopLoop")

        # The VM will do exactly one iteration, see the queue is empty, 
        # call random.randint => 4 => internal event, then attempt time.sleep => exception
        self.assertEqual(vm.logical_clock.time, 1)  # started at 0, 1 internal event

if __name__ == "__main__":
    unittest.main()