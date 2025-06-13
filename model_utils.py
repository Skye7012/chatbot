import torch
from torchvision import transforms
import numpy as np
from PIL import Image
from nst.API import transfer_style


def load_model():
    """Загружаем предобученную модель AnimeGANv2 из torchhub"""
    # Path of the downloaded pre-trained model or 'model' directory
    pass


def stylize_image(image, author):
    # Path of the downloaded pre-trained model or 'model' directory
    model_path = "nst/model/arbitrary-image-stylization-v1-tensorflow1-256-v2"

    img = transfer_style(image, author, model_path)
    return img
