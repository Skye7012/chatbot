import streamlit as st
from PIL import Image
from streamlit_star_rating import st_star_rating
from supabase_client import SupabaseClient
from model_utils import stylize_image

# Заголовок приложения
st.title("🎨 AI-Художник: Генерация изображений в стиле художников")

# Инициализация клиента Supabase
supabase = SupabaseClient()

# Отображаем среднюю оценку в правом верхнем углу
avg_rating = supabase.get_average_rating()
st.badge(f"⭐ Средняя оценка модели: {avg_rating}/10", color="gray")

# Выбор стиля
style = st.selectbox(
    "Выберите стиль художника:",
    ("Ван Гог", "Мунк", "Пикассо"),
    key="style_selectbox"
)

# Загрузка изображения
uploaded_file = st.file_uploader("Загрузите ваше фото:", type=[
                                 "jpg", "jpeg"], key="file_uploader")

# Используем session_state для сохранения состояния
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'feedback_sent' not in st.session_state:
    st.session_state.feedback_sent = False
if 'last_uploaded_file' not in st.session_state:
    st.session_state.last_uploaded_file = None
if 'last_style' not in st.session_state:
    st.session_state.last_style = style

# Проверяем, изменилось ли загруженное изображение ИЛИ стиль художника
if (uploaded_file != st.session_state.last_uploaded_file or
        style != st.session_state.last_style):

    st.session_state.last_uploaded_file = uploaded_file
    st.session_state.last_style = style
    st.session_state.processed = False
    st.session_state.feedback_sent = False
    if 'stylized_image' in st.session_state:
        del st.session_state.stylized_image

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
            style_image = {
                "Ван Гог": "artists/ван_гог.jpg", "Мунк": "artists/мунк.jpg", "Пикассо": "artists/пикассо.jpg"
            }[style]

            st.session_state.stylized_image = stylize_image(
                image, style_image)
        except Exception as e:
            st.error(f"Ошибка: {e}")
            st.warning("Попробуйте другое изображение.")
            st.session_state.processed = False

    if st.session_state.processed and 'stylized_image' in st.session_state:
        st.image(st.session_state.stylized_image,
                 caption=f"Стиль: {style}")

        # Форма для отзыва
        if not st.session_state.feedback_sent:
            st.subheader("Понравился результат?")

            # Рейтинг в виде 10 звёзд
            st.write("Оцените результат (от 1 до 10 звёзд):")
            stars = st_star_rating(label="", maxValue=10,
                                   defaultValue=8, key="rating")

            # Поле для комментария (опциональное)
            comment = st.text_area(
                "Ваш комментарий (необязательно):", key="comment")

            if st.button('Отправить отзыв'):
                if stars > 0:
                    if supabase.submit_feedback(stars, comment if comment else None):
                        st.success('Спасибо за ваш отзыв!')
                        st.session_state.feedback_sent = True
                    pass
                else:
                    st.warning("Пожалуйста, поставьте оценку")
