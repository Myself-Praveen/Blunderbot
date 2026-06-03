import torch
import torch.nn as nn

class ChessPositionalAutoencoder(nn.Module):
    def __init__(self, embedding_dim=128):
        super(ChessPositionalAutoencoder, self).__init__()
        
        # Encoder: Compress 12x8x8 -> 128-d vector
        self.encoder = nn.Sequential(
            # Input: [Batch, 12, 8, 8]
            nn.Conv2d(12, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            # [Batch, 64, 8, 8]
            
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            # [Batch, 128, 4, 4]
            
            nn.Flatten(),
            nn.Linear(128 * 4 * 4, embedding_dim),
            # Output: [Batch, 128] - The latent positional representation
            nn.LayerNorm(embedding_dim),
            nn.Tanh() # Keep embeddings bounded between -1 and 1
        )
        
        # Decoder: Reconstruct 128-d vector -> 12x8x8
        self.decoder = nn.Sequential(
            nn.Linear(embedding_dim, 128 * 4 * 4),
            nn.ReLU(),
            nn.Unflatten(1, (128, 4, 4)),
            # [Batch, 128, 4, 4]
            
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            # [Batch, 64, 8, 8]
            
            nn.Conv2d(64, 12, kernel_size=3, padding=1),
            # Output: [Batch, 12, 8, 8]
            nn.Sigmoid() # Binary output (0 or 1 for piece presence)
        )

    def forward(self, x):
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed, latent
