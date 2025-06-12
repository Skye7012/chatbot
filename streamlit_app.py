import streamlit as st
from PIL import Image
import numpy as np
import torch
from torchvision import transforms
from st_supabase_connection import SupabaseConnection
from streamlit_star_rating import st_star_rating

# Заголовок приложения
st.title("🎨 AI-Художник: Генерация изображений в стиле художников")

# Функция для получения средней оценки из базы данных
def get_average_rating():
    try:
        conn = st.connection("supabase", type=SupabaseConnection)
        result = conn.table("Feedback").select("rating.avg()").execute()
        avg_rating = result.data[0]['avg']
        if avg_rating:
            return round(avg_rating, 2)
        return 0
    except Exception as e:
        st.error(f"Ошибка при получении средней оценки: {e}")
        return 0

# Отображаем среднюю оценку в правом верхнем углу
avg_rating = get_average_rating()
st.badge(f"⭐ Средняя оценка модели: {avg_rating}/10", color="gray")

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
if 'rating' not in st.session_state:
    st.session_state.rating = 0

if uploaded_file is not None:
    # Показываем загруженное изображение
    image = Image.open(uploaded_file)
    st.image(image, caption="Ваше фото", use_container_width=True)

    # Кнопка для обработки
    if not st.session_state.processed and st.button("Преобразовать в стиль " + style):
        st.session_state.processed = True
        st.session_state.feedback_sent = False
        st.session_state.rating = 0

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

            # Рейтинг в виде 10 звёзд
            st.write("Оцените результат (от 1 до 10 звёзд):")

            stars = st_star_rating(label="", maxValue=10, defaultValue=8, key="rating")

            # Поле для комментария (опциональное)
            comment = st.text_area(
                "Ваш комментарий (необязательно):", key="comment")

            if st.button('Отправить отзыв'):
                if st.session_state.rating > 0:
                    try:
                        conn = st.connection(
                            "supabase", type=SupabaseConnection)
                        response = conn.table("Feedback").insert({
                            "rating": stars,
                            "comment": comment if comment else None
                        }).execute()

                        st.success('Спасибо за ваш отзыв!')
                        st.session_state.feedback_sent = True
                    except Exception as e:
                        st.error(f"Ошибка при отправке отзыва: {e}")
                else:
                    st.warning("Пожалуйста, поставьте оценку")