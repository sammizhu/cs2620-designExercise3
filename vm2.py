from utils import VirtualMachine

machine = VirtualMachine(machine_id=2, port=5002, peers=[5001, 5003])
machine.run()