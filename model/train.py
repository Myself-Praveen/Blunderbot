import torch
import torch.nn as nn
import torch.optim as optim
from network import ChessPositionalAutoencoder
import os

def train_autoencoder(epochs=10, batch_size=32, lr=1e-3):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")
    
    model = ChessPositionalAutoencoder(embedding_dim=128).to(device)
    criterion = nn.BCELoss() # Binary Cross Entropy since input/output are 0s and 1s
    optimizer = optim.AdamW(model.parameters(), lr=lr)
    
    # Placeholder for actual DataLoader
    # In Day 3, we will connect this to the Lichess PGN dataset
    print("Initializing dummy dataset for Day 2 testing...")
    dummy_dataset = torch.rand((100, 12, 8, 8)).to(device) # Replace with real data later
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        # Dummy batching loop
        for i in range(0, len(dummy_dataset), batch_size):
            batch = dummy_dataset[i:i+batch_size]
            
            optimizer.zero_grad()
            reconstructed, latent = model(batch)
            
            # Loss is calculated against the original input
            loss = criterion(reconstructed, batch)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        avg_loss = total_loss / (len(dummy_dataset) / batch_size)
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}")
        
    return model

def save_model(model, path="checkpoints/autoencoder_v1.pt"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save(model.state_dict(), path)
    print(f"Model successfully saved to {path}")

if __name__ == "__main__":
    trained_model = train_autoencoder(epochs=5)
    save_model(trained_model)
