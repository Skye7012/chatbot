from st_supabase_connection import SupabaseConnection
import streamlit as st

class SupabaseClient:
    def __init__(self):
        self.conn = st.connection("supabase", type=SupabaseConnection)
    
    def get_average_rating(self):
        """Получает среднюю оценку из базы данных"""
        try:
            result = self.conn.table("Feedback").select("rating.avg()").execute()
            avg_rating = result.data[0]['avg']
            return round(avg_rating, 2) if avg_rating else 0
        except Exception as e:
            st.error(f"Ошибка при получении средней оценки: {e}")
            return 0
    
    def submit_feedback(self, rating, comment=None):
        """Отправляет отзыв в базу данных"""
        try:
            feedback_data = {"rating": rating}
            if comment:
                feedback_data["comment"] = comment
                
            response = self.conn.table("Feedback").insert(feedback_data).execute()
            return True
        except Exception as e:
            st.error(f"Ошибка при отправке отзыва: {e}")
            return False