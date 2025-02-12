class WaitForGraph:
    def __init__(self):
        self.graph = {}  # process -> set of processes it's waiting for

    def add_process(self, process):
        if process not in self.graph:
            self.graph[process] = set()

    def add_edge(self, from_process, to_process):
        if from_process not in self.graph:
            self.add_process(from_process)
        if to_process not in self.graph:
            self.add_process(to_process)
        self.graph[from_process].add(to_process)

    def display(self):
        """Display the Wait-For Graph."""
        print("\nWait-For Graph:")
        for process, waiting_for in self.graph.items():
            if waiting_for:
                print(f"  {process} → {waiting_for}")
            else:
                print(f"  {process} → No dependencies")
