"""
지번주소를 위도/경도로 변환하는 스크립트 (Nominatim/OpenStreetMap 사용)
완전 무료이며 API 키가 필요 없습니다.
"""

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
from typing import Tuple, Optional

# Nominatim 지오코더 초기화 (User-Agent 필수)
geolocator = Nominatim(user_agent="seoul-address-converter")

def get_coordinates_nominatim(address: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Nominatim(OpenStreetMap)을 사용하여 주소를 위도/경도로 변환

    Args:
        address: 지번주소

    Returns:
        (위도, 경도) 튜플. 실패시 (None, None) 반환
    """
    try:
        # 주소 검색 (한국 내 검색으로 제한)
        location = geolocator.geocode(
            address,
            timeout=10,
            language='ko',
            country_codes='kr'  # 대한민국으로 제한
        )

        if location:
            lat = location.latitude
            lng = location.longitude
            return lat, lng
        else:
            print(f"⚠️  주소를 찾을 수 없음: {address}")
            return None, None

    except GeocoderTimedOut:
        print(f"⏱️  시간 초과 ({address})")
        return None, None
    except GeocoderServiceError as e:
        print(f"❌ 서비스 에러 ({address}): {str(e)}")
        return None, None
    except Exception as e:
        print(f"❌ 에러 발생 ({address}): {str(e)}")
        return None, None


def process_excel_file(input_file: str, output_file: str):
    """
    엑셀 파일에서 지번주소를 읽어 위도/경도를 추가하고 저장

    Args:
        input_file: 입력 엑셀 파일 경로
        output_file: 출력 엑셀 파일 경로
    """
    # 엑셀 파일 읽기
    print(f"📖 파일 읽는 중: {input_file}")
    df = pd.read_excel(input_file)

    print(f"📊 총 {len(df)}개의 주소를 처리합니다.")
    print("-" * 50)
    print("⚠️  OpenStreetMap 서비스 정책상 요청 간 1초 대기가 필요합니다.")
    print("   (처리 시간: 약 {:.1f}분 소요 예상)".format(len(df) / 60))
    print("-" * 50)

    # 각 주소에 대해 좌표 가져오기
    success_count = 0
    fail_count = 0

    for idx, row in df.iterrows():
        address = row['지번주소']

        # 이미 좌표가 있으면 건너뛰기
        if pd.notna(row['위도']) and pd.notna(row['경도']):
            print(f"⏭️  [{idx+1}/{len(df)}] 이미 좌표 있음: {address}")
            success_count += 1
            continue

        print(f"🔍 [{idx+1}/{len(df)}] 검색 중: {address}")

        # 좌표 가져오기
        lat, lng = get_coordinates_nominatim(address)

        if lat and lng:
            df.at[idx, '위도'] = lat
            df.at[idx, '경도'] = lng
            print(f"✅ 성공: 위도={lat:.6f}, 경도={lng:.6f}")
            success_count += 1
        else:
            fail_count += 1

        # OpenStreetMap 사용 정책: 1초당 최대 1회 요청
        time.sleep(1)

        # 중간 저장 (20개마다)
        if (idx + 1) % 20 == 0:
            print(f"💾 중간 저장 중... ({idx+1}개 처리됨)")
            df.to_excel(output_file, index=False)

    # 최종 결과 저장
    print("-" * 50)
    print(f"💾 최종 결과 저장 중: {output_file}")
    df.to_excel(output_file, index=False)

    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 처리 결과")
    print("=" * 50)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print(f"📁 저장 위치: {output_file}")
    print("=" * 50)


if __name__ == "__main__":
    # 설정
    INPUT_FILE = "/Users/foodie/Downloads/서울.xlsx"
    OUTPUT_FILE = "/Users/foodie/Downloads/서울_좌표추가.xlsx"

    # geopy 설치 확인
    print("🔧 geopy 라이브러리를 확인하는 중...")
    try:
        from geopy.geocoders import Nominatim
        print("✅ geopy가 설치되어 있습니다.\n")
    except ImportError:
        print("❌ geopy가 설치되어 있지 않습니다.")
        print("다음 명령어로 설치해주세요:")
        print("  pip install geopy")
        exit(1)

    # 처리 시작
    print("🚀 주소 좌표 변환을 시작합니다... (Nominatim/OpenStreetMap 사용)\n")
    process_excel_file(INPUT_FILE, OUTPUT_FILE)
