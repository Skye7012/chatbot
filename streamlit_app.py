import streamlit as st
from PIL import Image
import numpy as np
import torch
from torchvision import transforms
from st_supabase_connection import SupabaseConnection

# Заголовок приложения
st.title("🎨 AI-Художник: Генерация изображений в стиле художников")

# Выбор стиля
style = st.selectbox(
    "Выберите стиль художника:",
    ("Ван Гог", "Мунк", "Пикассо", "Моне")
)

# Загрузка изображения
uploaded_file = st.file_uploader("Загрузите ваше фото:", type=["jpg", "jpeg"])


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


# Используем session_state для сохранения состояния
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'feedback_sent' not in st.session_state:
    st.session_state.feedback_sent = False

if uploaded_file is not None:
    # Показываем загруженное изображение
    image = Image.open(uploaded_file)
    st.image(image, caption="Ваше фото", use_container_width=True)

    # Кнопка для обработки
    if not st.session_state.processed and st.button("Преобразовать в стиль " + style):
        st.session_state.processed = True
        st.session_state.feedback_sent = False

        st.write("⏳ Идёт обработка...")
        try:
            model = load_model()
            st.session_state.stylized_image = stylize_image(image, model)
        except Exception as e:
            st.error(f"Ошибка: {e}")
            st.warning("Попробуйте другое изображение.")
            st.session_state.processed = False

    if st.session_state.processed and 'stylized_image' in st.session_state:
        st.image(st.session_state.stylized_image,
                 caption=f"Стиль: {style}", use_container_width=True)

        # Форма для отзыва
        if not st.session_state.feedback_sent:
            st.subheader("Понравился результат?")
            feedback = st.text_area("Оставьте ваш отзыв о стилизации:")

            if st.button('Отправить отзыв'):
                if feedback:
                    try:
                        conn = st.connection(
                            "supabase", type=SupabaseConnection)
                        response = conn.table("Feedback").insert(
                            {"rating": 1, "comment": feedback}).execute()
                        st.success('Спасибо за ваш отзыв!')
                        st.session_state.feedback_sent = True
                    except Exception as e:
                        st.error(f"Ошибка при отправке отзыва: {e}")
                else:
                    st.warning("Пожалуйста, напишите отзыв перед отправкой")
