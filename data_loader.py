import requests
import sqlite3
import pandas as pd
KAKAO_REST_API_KEY = "2be30620c436a5c031c516dc8d71c19a"
KAKAO_COORD_URL = "https://dapi.kakao.com/v2/local/search/address.json"
DATABASE_FILE = "local_stores.db"
CSV_FILE = "data/stores.csv"
def get_coordinates_from_address(address):
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"query": address}
    try:
        response = requests.get(KAKAO_COORD_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data and data.get('documents'):
            doc = data['documents'][0]
            return float(doc['y']), float(doc['x'])
    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류: {e} (주소: {address})")
    except ValueError as e:
        print(f"JSON 파싱 오류: {e} (주소: {address})")
    return None, None
def load_initial_data():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        print(f"{CSV_FILE}로부터 데이터를 로딩중입니다...")
        df = pd.read_csv(CSV_FILE)
        for index, row in df.iterrows():
            name = row['name']
            category = row['category']
            address = row['address']
            district = row['district']
            phone = row.get('phone', None)
            description = row.get('description', None)
            lat, lon = get_coordinates_from_address(address)
            if lat is not None and lon is not None:
                try:
                    cursor.execute(
                        "INSERT INTO stores (name, category, address, district, latitude, longitude, phone, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (name, category, address, district, lat, lon, phone, description)
                    )
                    print(f"추가됨: {name}")
                except sqlite3.IntegrityError:
                    pass
            else:
                pass
        conn.commit()
        print("데이터 로딩 완료")
    except FileNotFoundError:
        print(f"'{CSV_FILE}' 파일을 찾을 수 없습니다. CSV 파일이 올바른 경로에 있는지 확인해주세요.")
    except pd.errors.EmptyDataError:
        print(f"'{CSV_FILE}' 파일이 비어있습니다. CSV 파일에 데이터를 추가해주세요.")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"예상치 못한 오류가 발생했습니다: {e}")
    finally:
        if conn:
            conn.close()
if __name__ == "__main__":
    load_initial_data()