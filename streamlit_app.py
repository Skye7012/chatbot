import streamlit as st
from PIL import Image
import numpy as np
import torch
from torchvision import transforms

# Заголовок приложения
st.title("🎨 AI-Художник: Генерация изображений в стиле аниме")

# Загрузка изображения
uploaded_file = st.file_uploader("Загрузите ваше фото:", type=["jpg", "png", "jpeg"])

@st.cache_resource
def load_model():
    """Загружаем предобученную модель AnimeGANv2 из torchhub"""
    model = torch.hub.load('bryandlee/animegan2-pytorch', 'generator').eval()
    return model

def stylize_image(image, model):
    """Применяем стилизацию"""
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

if uploaded_file is not None:
    # Показываем загруженное изображение
    image = Image.open(uploaded_file)
    st.image(image, caption="Ваше фото", use_column_width=True)

    # Кнопка для обработки
    if st.button("Преобразовать в стиль аниме"):
        st.write("⏳ Идёт обработка...")

        try:
            # Загружаем модель (кешируем, чтобы не грузить каждый раз)
            model = load_model()

            # Стилизуем изображение
            stylized_image = stylize_image(image, model)
            st.image(stylized_image, caption="Стиль: Аниме", use_column_width=True)

        except Exception as e:
            st.error(f"Ошибка: {e}")
            st.warning("Попробуйте другое изображение.")

    feedback = st.text_area("Ваши отзывы о стилизации")
    if st.button('Отправить отзыв'):
        with open('feedback.txt', 'a') as f:
            f.write(feedback + '\n')
        st.success('Спасибо за ваш отзыв!')
