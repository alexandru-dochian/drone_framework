import torch
import torch.nn as nn
import torch.nn.functional as F

HEAT_MAP_HEIGHT = 256
HEAT_MAP_WIDTH = 1024

class State:
    pos_x: list[float]
    pos_y: list[float]
    pos_z: list[float]

    # for the future
    camera: list[list[float]]
    camera_orientation: tuple[float, float, float]

class Command:
    v_x: float
    v_y: float
    v_z: float


class HeatMap:
    starting_point: tuple[float, float,float]
    ending_point: tuple[float, float,float]
    blocks: list[list[float]]

def create_heatmap() -> HeatMap:
    return HeatMap(
        torch.zeros(
            HEAT_MAP_HEIGHT,
            HEAT_MAP_WIDTH
        ).to_list()
    )


def update_heatmap(states: list[State], heatmap: HeatMap) -> HeatMap:
    ...

def predict(state: State, heatmap: HeatMap) -> Command:
    class DummyNN(nn.Module):
        def __init__(self, input_size, hidden_size, output_size):
            self.fc1 = nn.Linear(input_size, hidden_size)
            self.fc2 = nn.Linear(hidden_size, output_size)

        def forward(self, x):
            x = F.relu(self.fc1(x))
            x = self.fc2(x)
            return x

    input_size = 10
    hidden_size = 20
    output_size = 5
    model = DummyNN(input_size, hidden_size, output_size)

    output: Command = model.forward(state)
    return output


####################################################################################



def get_state() -> State:
    ...


def get_neigbours_states() -> State:
    ...



def update_agent(command: Command) -> State:
    ...

heatmap = create_heatmap()
while True:
    state: State = get_state()
    neigbours_states: list[State] = get_neigbours_states()
    
    all_states = state + neigbours_states
    heatmap = update_heatmap(all_states, heatmap)
    
    command: Command = predict(state, heatmap)

    update_agent(command)
    
