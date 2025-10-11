from dataclasses import dataclass, field
from typing import Dict, Tuple
import torch
from torch import nn

from ...agents.Agent import Agent
from ...utils.DataUtils import DataUtils
from ..DataElementConfig import DataElementConfig
from ..LearningElement import LearningElement

@dataclass
class CNN1DAutoencoder(LearningElement, nn.Module):
    """
    This `DataElement` represents a time series feature extraction model using a 1D CNN Autoencoder.
    """
    
    input_length : int = field(default=5, metadata={"description": ""})    
    input_features : int = field(default=1, metadata={"description":""})
    epochs : int = field(default=10, metadata={"description":""})
    batch_size : int = field(default=10, metadata={"description":""})
    learning_rate : float = field(default=0.001, metadata={"description":""})
    bottleneck_features : int = field(default = 2, metadata={"description":""})
    output_length : int = field(default=1, metadata={"description":""})
    apply_per_feature : bool = field(default=True, metadata={"description": ""})
    
    def __post_init__(self):
        super().__post_init__()
        self.encoder = None
        self.decoder = None
        self.len_orig_features = None
        self._to_linear = None
        self.fc_enc = None
        self.fc_dec = None
     
    def install(self, agent : Agent = None):
        super().install(agent)
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv1d(in_channels=self.input_features, out_channels=16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2, stride=2),
            nn.Conv1d(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv1d(in_channels=64, out_channels=32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv1d(in_channels=32, out_channels=16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2, stride=2),
            nn.Conv1d(in_channels=16, out_channels=8, kernel_size=3, stride=1, padding=1),
        )
           
        # Decoder: note that now the first conv's in_channels equals self.bottleneck_features
        self.decoder = nn.Sequential(
            nn.Conv1d(in_channels=8, out_channels=16, kernel_size=3, stride=1, padding=1),
            nn.Upsample(scale_factor=2, mode='nearest'),
            nn.ReLU(),
            nn.Conv1d(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv1d(in_channels=64, out_channels=32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv1d(in_channels=32, out_channels=16, kernel_size=3, stride=1, padding=1),
            nn.Upsample(scale_factor=2, mode='nearest'),
            nn.ReLU(),
            nn.Conv1d(in_channels=16, out_channels=self.input_features, kernel_size=3, stride=1, padding=1)
        )
        
        self.__get_conv_output_shape(self.input_features, self.input_length)  # Get the shape of the last convolution layer

        # Fully connected bottleneck: map _to_linear -> lower_dim and back -> _to_linear
        self.fc_enc = nn.Sequential(
            nn.Linear(self._to_linear, self.bottleneck_features)
        )
        
        self.fc_dec = nn.Sequential(
            nn.Linear(self.bottleneck_features, self._to_linear)
        )
        
    def learn(self, data : dict, meta : dict = None) -> bool:
        # rearrange data for Autoencoder
        # TODO
        x = self.__to_tensor(data)
        self.__fit(x)
        return False
    
    def infer(self, data : dict, meta : dict = None) -> Tuple[Dict, Dict]:
        # rearrange data for Autoencoder
        # TODO
        x = self.__to_tensor(data)
        self.eval()
        prediction = {}
        with torch.no_grad():
            prediction = self.__forward(x)
        
        # rearrange outputs to dict
        return prediction, None
    
    def __forward(self, x):
        prediction = {}
        # Encode (conv)
        conv_out = self.encoder(x)  # Shape: (batch, self.bottleneck_features, conv_length)
        batch_size = conv_out.size(0)
        
        # Flatten conv output
        flat = conv_out.view(batch_size, -1)  # Shape: (batch, _to_linear)
        
        # Bottleneck FC layers
        bottleneck = self.fc_enc(flat)        # Shape: (batch, 100)
        flat_decoded = self.fc_dec(bottleneck)  # Shape: (batch, _to_linear)
        
        # Unflatten back to conv shape
        #conv_shape = (self.bottleneck_features, self._to_linear // self.bottleneck_features)
        unflat = flat_decoded.view(batch_size, 8,-1)#flat_decoded.view(batch_size, *conv_shape)
        
        # Decode
        decoded = self.decoder(unflat)
        # Ensure output matches input length (crop or pad as needed)
        if decoded.shape[2] > x.shape[2]:
            decoded = decoded[:, :, : x.shape[2]]
        elif decoded.shape[2] < x.shape[2]:
            pad_amt = x.shape[2] - decoded.shape[2]
            decoded = nn.functional.pad(decoded, (0, pad_amt))
        prediction[DataElementConfig.FEATURES] = bottleneck.unsqueeze(1).swapaxes(1,2) # Shape before: (batch, 1, self.bottleneck_features), shape after: (self.bottleneck_features, 1, batch)
        prediction[DataElementConfig.Y_HAT] = decoded
        return prediction
    
    def __fit(self, x):
        """
        Train the autoencoder model.

        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, input_features, len_input).

        """
        assert x.dim() == 3, f"DataInnovator expects a 3D tensor but got a tensor with {x.dim} dimensions."
        assert type(x) == torch.Tensor, f"DataInnovator {self.name} expects the tensor to be of type torch.float32 but got tensor of type {type(self.features_data_torch)}."

        self.train()

        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.parameters(), lr=self.learning_rate, weight_decay=1e-5)

        if self.batch_size > int(len(x) / 10):
            print("Information: Drop last is set as True in the Dataloader. The last batch will get dropped. If the batch size is close to the dataset size, a large portion of the data is not used.")

        train_loader = torch.utils.data.DataLoader(x, batch_size=self.batch_size, shuffle=True, drop_last=True)

        for epoch in range(self.epochs):
            running_loss = 0.0
            for batch in train_loader:
                optimizer.zero_grad()
                outputs = self.forward(batch)[DataElementConfig.Y_HAT]
                loss = criterion(outputs, batch)
                loss.backward()
                optimizer.step()
                running_loss += loss.item()
            print(f"Epoch {epoch + 1}/{self.epochs}, Loss: {running_loss / len(train_loader)}")
        
    def __get_conv_output_shape(self, input_channels, input_length):
        """
        Helper function to determine the output shape after the convolutional layers.

        Args:
            input_channels (int): Number of input channels.
            input_length (int): Length of the input time series data.

        """
        if self.apply_per_feature:
            x = torch.rand(1, input_channels, input_length)
        else:
            x = torch.rand(1, input_channels, self.len_orig_features)
        x = self.encoder(x)
        self._to_linear = x.numel()
        
    def __to_tensor(self, data : dict) -> torch.Tensor:
        arr = DataUtils.dict_to_ndarray(data)
        tensor = torch.tensor(arr, dtype=torch.float32)  # (4,)
        tensor_view = tensor.view(self.input_length, self.batch_size, self.bottleneck_features)
        return tensor_view