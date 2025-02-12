# Resource Allocation Graph Implementation

class ResourceAllocationGraph:
    def __init__(self):
        # Adjacency lists
        self.processes = set()
        self.resources = set()
        self.assignment_edges = {}  # resource -> set of processes
        self.request_queue = {}      # resource -> list of processes waiting

    def add_process(self, process):
        self.processes.add(process)
        if process not in self.processes:
            self.processes.add(process)

    def add_resource(self, resource):
        if resource not in self.resources:
            self.resources.add(resource)
            self.assignment_edges[resource] = None  # None indicates free
            self.request_queue[resource] = []

    def add_request(self, resource, process):
        if process not in self.processes:
            self.add_process(process)
        if resource not in self.resources:
            self.add_resource(resource)
        if process not in self.request_queue[resource]:
            self.request_queue[resource].append(process)

    def add_assignment(self, resource, process):
        if resource not in self.resources:
            self.add_resource(resource)
        if process not in self.processes:
            self.add_process(process)

        if self.assignment_edges.get(resource) is None:
            self.assignment_edges[resource] = process
            if process in self.request_queue[resource]:
                self.request_queue[resource].remove(process)
         #   print(f"Resource '{resource}' has been allocated to Process '{process}'.")
        else:
            current_process = self.assignment_edges[resource]
            print(f"Error: Resource '{resource}' is already assigned to Process '{current_process}'.")

    def release_resource(self, resource, process):
        # Check if the resource is actually assigned to the process
        if self.assignment_edges.get(resource) != process:
            current_process = self.assignment_edges.get(resource)
            if current_process is not None:
                print(
                    f"Error: Resource '{resource}' is not assigned to Process '{process}', but to Process '{current_process}'.")
            else:
                print(f"Error: Resource '{resource}' is already free.")
            return

        # Free the resource
        self.assignment_edges[resource] = None
      #  print(f"Resource '{resource}' has been freed from Process '{process}'.")

        # Allocate to the next process in the waiting queue, if any
        if self.request_queue.get(resource):
            next_process = self.request_queue[resource].pop(0)  # FIFO allocation
            self.assignment_edges[resource] = next_process
        #    print(f"Resource '{resource}' has been allocated to waiting Process '{next_process}'.")

    def resource_used_by(self, resource):
        assigned_process = self.assignment_edges.get(resource)
        if assigned_process is not None:
            return assigned_process
        else:
            return None

    def display(self):
        print("Resource Allocation Graph:")
        print("Processes:", self.processes)
        print("Resources:", self.resources)
        print("Requests:")
        for res, processes in self.request_queue.items():
            for p in processes:
                print(f"  {p} → {res}")
        print("Assignments:")
        for r, procs in self.assignment_edges.items():
           # for p in procs:
                print(f"  {r} → {procs}")
