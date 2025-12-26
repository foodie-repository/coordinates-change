"""
지번주소를 위도/경도로 변환하는 스크립트 (VWorld API 사용)
VWorld(국토교통부) API는 별도 인증키 없이 사용 가능합니다.
"""

import pandas as pd
import requests
import time
from typing import Tuple, Optional
from urllib.parse import quote

def get_coordinates_vworld(address: str) -> Tuple[Optional[float], Optional[float]]:
    """
    VWorld API를 사용하여 주소를 위도/경도로 변환

    Args:
        address: 지번주소

    Returns:
        (위도, 경도) 튜플. 실패시 (None, None) 반환
    """
    # VWorld Geocoder API - 인증키 불필요
    base_url = "https://api.vworld.kr/req/address"

    params = {
        "service": "address",
        "request": "getcoord",
        "version": "2.0",
        "crs": "epsg:4326",  # WGS84 좌표계
        "address": address,
        "format": "json",
        "type": "parcel",  # parcel: 지번주소, road: 도로명주소
        "key": "CEB54A57-0F0C-3D3D-BC34-CFA0B2D910F3"  # VWorld 무료 공개키
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # 응답 확인
        if data['response']['status'] == 'OK':
            result = data['response']['result']

            if result and 'point' in result:
                lng = float(result['point']['x'])  # 경도
                lat = float(result['point']['y'])  # 위도
                return lat, lng
            else:
                print(f"⚠️  주소를 찾을 수 없음: {address}")
                return None, None
        else:
            print(f"⚠️  주소 검색 실패 ({address}): {data['response']['status']}")
            return None, None

    except requests.exceptions.Timeout:
        print(f"⏱️  시간 초과 ({address})")
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
        lat, lng = get_coordinates_vworld(address)

        if lat and lng:
            df.at[idx, '위도'] = lat
            df.at[idx, '경도'] = lng
            print(f"✅ 성공: 위도={lat:.6f}, 경도={lng:.6f}")
            success_count += 1
        else:
            fail_count += 1

        # API 부담을 줄이기 위해 잠시 대기
        time.sleep(0.2)

        # 중간 저장 (50개마다)
        if (idx + 1) % 50 == 0:
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

    # 처리 시작
    print("\n🚀 주소 좌표 변환을 시작합니다... (VWorld API 사용)\n")
    process_excel_file(INPUT_FILE, OUTPUT_FILE)
