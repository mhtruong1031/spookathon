import torch
import torch.nn as nn

class ConvolutionalNeuralNetwork(torch.nn.Module):
    def __init__(self, input_size: int, output_size: int):
        self.network = torch.nn.Sequential([
            nn.Conv2d(input_size, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dense(128, 64),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dense(64, 32),
            nn.Conv2d(32, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        ])
        self.output_layer = nn.Linear(16, output_size)

    def forward(self, x):
        return self.output_layer(self.network(x))
        