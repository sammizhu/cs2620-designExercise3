from utils import VirtualMachine

machine = VirtualMachine(machine_id=3, port=5003, peers=[5001, 5002])
machine.run()