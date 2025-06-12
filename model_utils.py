import torch
from torchvision import transforms
import numpy as np
from PIL import Image


def load_model():
    """Загружаем предобученную модель AnimeGANv2 из torchhub"""
    model = torch.hub.load('bryandlee/animegan2-pytorch', 'generator').eval()
    return model


def stylize_image(image, model):
    """Применяем стилизацию к изображению"""
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.ToTensor(),
    ])
    input_tensor = preprocess(image).unsqueeze(0)
    with torch.no_grad():
        output = model(input_tensor)
    output_image = output.squeeze().permute(1, 2, 0).numpy()
    output_image = np.clip(output_image, 0, 1)
    return (output_image * 255).astype(np.uint8)
