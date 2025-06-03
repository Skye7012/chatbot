import streamlit as st
from PIL import Image
import numpy as np

# Заголовок приложения
st.title("🎨 AI-Художник: Генерация изображений в стиле художников")

# Выбор стиля
style = st.selectbox(
    "Выберите стиль художника:",
    ("Ван Гог", "Эдвард Мунк", "Пабло Пикассо", "Клод Моне")
)

# Загрузка изображения
uploaded_file = st.file_uploader("Загрузите ваше фото:", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Показываем загруженное изображение
    image = Image.open(uploaded_file)
    st.image(image, caption="Ваше фото", use_column_width=True)

    # Кнопка для обработки
    if st.button("Преобразовать в стиль " + style):
        # Здесь будет вызов модели (пока заглушка)
        st.write("⏳ Идёт обработка... (модель пока не подключена)")

        # Имитация работы: просто инвертируем цвета для примера
        inverted_image = Image.fromarray(255 - np.array(image))
        st.image(inverted_image, caption=f"Стиль: {style}", use_column_width=True)

    feedback = st.text_area("Ваши отзывы о стилизации")
    if st.button('Отправить отзыв'):
        # Сохраните отзыв в файл или базу данных
        with open('feedback.txt', 'a') as f:
            f.write(feedback + '\n')
        st.success('Спасибо за ваш отзыв!')
