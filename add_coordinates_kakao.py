"""
지번주소를 위도/경도로 변환하는 스크립트
카카오 Local API를 사용하여 주소를 좌표로 변환합니다.
"""

import pandas as pd
import requests
import time
from typing import Tuple, Optional

def get_coordinates(address: str, api_key: str) -> Tuple[Optional[float], Optional[float]]:
    """
    카카오 Local API를 사용하여 주소를 위도/경도로 변환

    Args:
        address: 지번주소
        api_key: 카카오 REST API 키

    Returns:
        (위도, 경도) 튜플. 실패시 (None, None) 반환
    """
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": address}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()

        # 검색 결과가 있는지 확인
        if data['documents']:
            # 첫 번째 결과 사용
            result = data['documents'][0]

            # 지번 주소 정보가 있으면 사용, 없으면 도로명 주소 정보 사용
            if result.get('address'):
                lat = float(result['address']['y'])  # 위도
                lng = float(result['address']['x'])  # 경도
            elif result.get('road_address'):
                lat = float(result['road_address']['y'])
                lng = float(result['road_address']['x'])
            else:
                lat = float(result['y'])
                lng = float(result['x'])

            return lat, lng
        else:
            print(f"⚠️  주소를 찾을 수 없음: {address}")
            return None, None

    except Exception as e:
        print(f"❌ 에러 발생 ({address}): {str(e)}")
        return None, None


def process_excel_file(input_file: str, output_file: str, api_key: str):
    """
    엑셀 파일에서 지번주소를 읽어 위도/경도를 추가하고 저장

    Args:
        input_file: 입력 엑셀 파일 경로
        output_file: 출력 엑셀 파일 경로
        api_key: 카카오 REST API 키
    """
    # 엑셀 파일 읽기
    print(f"📖 파일 읽는 중: {input_file}")
    df = pd.read_excel(input_file)

    print(f"📊 총 {len(df)}개의 주소를 처리합니다.")
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
        lat, lng = get_coordinates(address, api_key)

        if lat and lng:
            df.at[idx, '위도'] = lat
            df.at[idx, '경도'] = lng
            print(f"✅ 성공: 위도={lat}, 경도={lng}")
            success_count += 1
        else:
            fail_count += 1

        # API 호출 제한을 위해 잠시 대기 (초당 10회 제한)
        time.sleep(0.1)

    # 결과 저장
    print("-" * 50)
    print(f"💾 결과 저장 중: {output_file}")
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
    import sys
    import os

    # 설정
    INPUT_FILE = "/Users/foodie/Downloads/서울.xlsx"
    OUTPUT_FILE = "/Users/foodie/Downloads/서울_좌표추가.xlsx"

    # 카카오 REST API 키 가져오기
    # 방법 1: 명령줄 인수로 전달
    # 방법 2: 환경변수 KAKAO_API_KEY 사용
    KAKAO_API_KEY = None

    if len(sys.argv) > 1:
        KAKAO_API_KEY = sys.argv[1]
    elif os.getenv('KAKAO_API_KEY'):
        KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')
    else:
        print("❌ 카카오 REST API 키를 제공해주세요.")
        print("\n사용 방법:")
        print("  1. 명령줄 인수: python add_coordinates.py YOUR_API_KEY")
        print("  2. 환경변수: export KAKAO_API_KEY=YOUR_API_KEY && python add_coordinates.py")
        print("\nAPI 키 발급: https://developers.kakao.com/")
        exit(1)

    if not KAKAO_API_KEY:
        print("❌ API 키가 입력되지 않았습니다.")
        exit(1)

    # 처리 시작
    print("\n🚀 주소 좌표 변환을 시작합니다...\n")
    process_excel_file(INPUT_FILE, OUTPUT_FILE, KAKAO_API_KEY)
