import json

class SignalInformation:
    def __init__(self, signal_power: float, path: list[str]):
        self.signal_power = signal_power  # Signal power in Watts
        self.noise_power = 0.0            # Noise power in Watts, initialized to 0
        self.latency = 0.0                # Latency in seconds, initialized to 0
        self.path = path                  # Path as a list of node labels

    def update_signal_power(self, increment: float):
        self.signal_power += increment

    def update_noise_power(self, increment: float):
        self.noise_power += increment

    def update_latency(self, increment: float):
        self.latency += increment

    def update_path(self):
        if self.path:
            self.path.pop(0)

###################################################################################################

class Node(object):
        def __init__(self, label: str, position: tuple, connected_nodes: list):
        self.label = label
        self.position = position
        self.connected_nodes = connected_nodes
        self.successive = {}

    def propagate(self, signal: 'SignalInformation'):
        if signal.path:
            signal.update_path()
            next_node_label = signal.path[0] if signal.path else None
            if next_node_label and next_node_label in self.successive:
                next_line = self.successive[next_node_label]
                next_line.propagate(signal)

###############################################################################################

class Line(object):
    LIGHT_SPEED = 3 * 10**8
    FIBER_SPEED = LIGHT_SPEED * 2 / 3

    def __init__(self, label: str, length: float):
        self.label = label
        self.length = length
        self.successive = {}

    def latency_generation(self) -> float:
        return self.length / Line.FIBER_SPEED

    def noise_generation(self, signal_power: float) -> float:
        return 1e-9 * signal_power * self.length

    def propagate(self, signal: 'SignalInformation'):
        signal.update_latency(self.latency_generation())
        signal.update_noise_power(self.noise_generation(signal.signal_power))
        if signal.path:
            next_node_label = signal.path[0]
            if next_node_label in self.successive:
                next_node = self.successive[next_node_label]
                next_node.propagate(signal)

########################################################################################################
class Network(object):
   class Network:
    def __init__(self, json_file: str = None):
        self._nodes = {}
        self._lines = {}
        if json_file:
            self._load_nodes(json_file)
            self.connect()

    def _load_nodes(self, json_file: str):
        with open(json_file, 'r') as file:
            data = json.load(file)
        for node_label, node_info in data.items():
            self._nodes[node_label] = Node(
                label=node_label,
                position=tuple(node_info['position']),
                connected_nodes=node_info['connected_nodes']
            )
        for node_label, node in self._nodes.items():
            for connected_node_label in node.connected_nodes:
                if connected_node_label in self._nodes:
                    line_label = node_label + connected_node_label
                    if line_label not in self._lines:
                        pos1 = node.position
                        pos2 = self._nodes[connected_node_label].position
                        length = math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)
                        self._lines[line_label] = Line(label=line_label, length=length)
                        reverse_label = connected_node_label + node_label
                        self._lines[reverse_label] = Line(label=reverse_label, length=length)

    @property
    def nodes(self):
        return self._nodes

    @property
    def lines(self):
        return self._lines

    def connect(self):
        for line_label, line in self._lines.items():
            node1_label = line_label[0]
            node2_label = line_label[1]
            if node1_label in self._nodes:
                self._nodes[node1_label].successive[node2_label] = line
            line.successive[node2_label] = self._nodes[node2_label]

    def draw(self):
        plt.figure(figsize=(8, 8))
        for node_label, node in self._nodes.items():
            plt.plot(node.position[0], node.position[1], 'o', label=node_label)
            plt.text(node.position[0], node.position[1], node_label, fontsize=12, ha='right')
        for line_label, line in self._lines.items():
            node1_label = line_label[0]
            node2_label = line_label[1]
            if node1_label in self._nodes and node2_label in self._nodes:
                pos1 = self._nodes[node1_label].position
                pos2 = self._nodes[node2_label].position
                plt.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 'k-')
        plt.xlabel("X Position")
        plt.ylabel("Y Position")
        plt.title("Network Topology")
        plt.legend()
        plt.grid(True)
        plt.show()

    def find_paths(self, start: str, end: str, path=None) -> List[List[str]]:
        if path is None:
            path = [start]
        if start == end:
            return [path]
        paths = []
        for node in self._nodes[start].connected_nodes:
            if node not in path:
                new_paths = self.find_paths(node, end, path + [node])
                for p in new_paths:
                    paths.append(p)
        return paths

    def propagate(self, signal: SignalInformation) -> SignalInformation:
        current_node = signal.path[0]
        if current_node in self._nodes:
            self._nodes[current_node].propagate(signal)
        return signal
