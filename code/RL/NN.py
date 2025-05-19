import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class NeuralNetwork:
    def __init__(self, input_size=12, hidden_size=10, output_size=3):
        # Random initialization of weights
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        # Weights: input → hidden
        self.w1 = np.random.randn(hidden_size, input_size)*0.1
        # Weights: hidden → output
        self.w2 = np.random.randn(output_size, hidden_size)*0.1

    def forward(self, inputs):
        # Convert to numpy array
        inputs = np.array(inputs).reshape(-1, 1)  # Shape: (input_size, 1)

        # Hidden layer activation
        z1 = np.dot(self.w1, inputs)
        a1 = sigmoid(z1)

        # Output layer
        z2 = np.dot(self.w2, a1)
        output = sigmoid(z2)

        return output.flatten()  # Output shape: (3,)
