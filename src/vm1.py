from utils import VirtualMachine

machine = VirtualMachine(machine_id=1, port=5001, peers=[5002, 5003])
machine.run()