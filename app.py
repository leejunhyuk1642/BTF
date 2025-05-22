import streamlit as st
import sqlite3
import pandas as pd
from streamlit_folium import folium_static
import folium
DATABASE_FILE = "local_stores.db"
@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
st.set_page_config(page_title="상인동, 월성동 맛집 추천", layout="centered")
st.title("상인동, 월성동 맛집 추천 🍴")
st.markdown("대구 상인동, 월성동 맛집을 추천해 드립니다!")
st.header("1. 동 이름 입력")
selected_district = st.radio(
    "어떤 동의 정보를 원하시나요?",
    ('상인동', '월성동'),
    index=None
)
processed_district = selected_district
if processed_district:
    if processed_district not in ['상인동', '월성동']:
        st.error("죄송합니다. '상인동' 또는 '월성동'만 검색할 수 있습니다.")
    else:
        st.header(f"2. {processed_district} 상점 목록")
        conn = get_db_connection()
        stores_data = []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name, category, address, phone, description, latitude, longitude FROM stores WHERE district = ?", (processed_district,))
            stores_data = cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"상점 정보를 불러오는 중 데이터베이스 오류가 발생했습니다: {e}")
        except Exception as e:
            st.error(f"예상치 못한 오류가 발생했습니다: {e}")
        if stores_data:
            df = pd.DataFrame(stores_data, columns=['상점명', '카테고리', '주소', '전화번호', '설명', '위도', '경도'])
            st.dataframe(df, use_container_width=True)
            st.markdown("---")
            st.subheader("상점 위치 지도")
            if processed_district == '상인동':
                map_center = [35.823, 128.535]
            elif processed_district == '월성동':
                map_center = [35.835, 128.520]
            else:
                map_center = [35.85, 128.6] 
            m = folium.Map(location=map_center, zoom_start=14)
            for store in stores_data:
                lat = store['latitude']
                lon = store['longitude']
                name = store['name']
                category = store['category']
                address = store['address']
                phone = store['phone'] if store['phone'] else "정보 없음"
                description = store['description'] if store['description'] else "정보 없음"
                popup_html = f"""
                <b>{name}</b><br>
                카테고리: {category}<br>
                주소: {address}<br>
                전화번호: {phone}<br>
                설명: {description}
                """
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=name
                ).add_to(m)
            folium_static(m)
            st.markdown("---")
            st.subheader("상점 상세 정보")
            for store in stores_data:
                with st.expander(f"**{store['name']}** - {store['category']}"):
                    st.write(f"**주소:** {store['address']}")
                    if store['phone']:
                        st.write(f"**전화번호:** {store['phone']}")
                    if store['description']:
                        st.write(f"**설명:** {store['description']}")
        else:
            st.info(f"죄송합니다. {processed_district}에는 아직 등록된 상점이 없습니다.")
st.markdown("---")
st.caption("✨여러분의 소중한 의견은 서비스 개선에 큰 힘이 됩니다.✨")