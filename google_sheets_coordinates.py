"""
구글 시트에 위도/경도를 추가하는 스크립트
카카오 Local API를 사용하여 주소를 좌표로 변환합니다.
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import time
from typing import Tuple, Optional

# 구글 시트 URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1y1S8YIjsEpvaeyxDRokJToS65RE4KD9hxq6KWIemwgk/edit?gid=0#gid=0"
SHEET_ID = "1y1S8YIjsEpvaeyxDRokJToS65RE4KD9hxq6KWIemwgk"


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

        if data['documents']:
            result = data['documents'][0]

            if result.get('address'):
                lat = float(result['address']['y'])
                lng = float(result['address']['x'])
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


def process_google_sheet_with_credentials(creds_file: str, kakao_api_key: str):
    """
    서비스 계정을 사용하여 구글 시트에 접근하고 위도/경도 업데이트

    Args:
        creds_file: 구글 서비스 계정 JSON 파일 경로
        kakao_api_key: 카카오 REST API 키
    """
    print("🔐 구글 시트 인증 중...")

    # 구글 시트 API 인증
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)

    print("📖 구글 시트 열기...")
    sheet = client.open_by_key(SHEET_ID).sheet1

    # 모든 데이터 가져오기
    all_data = sheet.get_all_values()
    headers = all_data[0]

    print(f"컬럼: {headers}")

    # 주소, 위도, 경도 컬럼 인덱스 찾기
    try:
        address_col = headers.index('주소')
        lat_col = headers.index('위도')
        lng_col = headers.index('경도')
    except ValueError as e:
        print(f"❌ 필요한 컬럼을 찾을 수 없습니다: {e}")
        print(f"현재 컬럼: {headers}")
        return

    print(f"\n📊 총 {len(all_data) - 1}개의 주소를 처리합니다.")
    print("-" * 50)

    success_count = 0
    fail_count = 0

    # 헤더 제외하고 처리
    for idx, row in enumerate(all_data[1:], start=2):  # 2부터 시작 (1은 헤더)
        if idx - 1 > len(row):
            continue

        address = row[address_col] if len(row) > address_col else ""

        if not address:
            continue

        # 이미 좌표가 있으면 건너뛰기
        has_lat = len(row) > lat_col and row[lat_col]
        has_lng = len(row) > lng_col and row[lng_col]

        if has_lat and has_lng:
            print(f"⏭️  [{idx-1}/{len(all_data)-1}] 이미 좌표 있음: {address}")
            success_count += 1
            continue

        print(f"🔍 [{idx-1}/{len(all_data)-1}] 검색 중: {address}")

        # 좌표 가져오기
        lat, lng = get_coordinates(address, kakao_api_key)

        if lat and lng:
            # 구글 시트 업데이트 (A1 표기법 사용)
            lat_cell = f"{chr(65 + lat_col)}{idx}"  # 예: B2
            lng_cell = f"{chr(65 + lng_col)}{idx}"  # 예: C2

            sheet.update(lat_cell, [[lat]])
            sheet.update(lng_cell, [[lng]])

            print(f"✅ 성공: 위도={lat:.6f}, 경도={lng:.6f}")
            success_count += 1
        else:
            fail_count += 1

        # API 호출 제한 고려
        time.sleep(0.5)

    print("\n" + "=" * 50)
    print("📊 처리 결과")
    print("=" * 50)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print(f"🔗 시트: {SHEET_URL}")
    print("=" * 50)


def process_google_sheet_public(kakao_api_key: str):
    """
    공개 구글 시트에 접근 (읽기 전용)

    주의: 이 방법은 시트가 "링크가 있는 모든 사용자"로 공개되어 있어야 하며,
    읽기만 가능합니다. 쓰기를 위해서는 서비스 계정이 필요합니다.
    """
    print("❌ 구글 시트에 쓰기 권한이 필요합니다.")
    print("\n다음 방법 중 하나를 선택해주세요:")
    print("\n1. 서비스 계정 사용 (권장):")
    print("   - Google Cloud Console에서 서비스 계정 생성")
    print("   - JSON 키 파일 다운로드")
    print("   - 시트를 서비스 계정 이메일과 공유")
    print("\n2. OAuth 2.0 사용:")
    print("   - 본인 구글 계정으로 인증")
    print("   - credentials.json 파일 필요")


if __name__ == "__main__":
    import sys

    print("\n🚀 구글 시트 좌표 변환을 시작합니다...\n")

    # 카카오 API 키
    if len(sys.argv) < 2:
        print("❌ 카카오 REST API 키를 제공해주세요.")
        print("\n사용 방법:")
        print("  python google_sheets_coordinates.py KAKAO_API_KEY [GOOGLE_CREDS_FILE]")
        exit(1)

    kakao_api_key = sys.argv[1]

    # 구글 서비스 계정 JSON 파일
    if len(sys.argv) >= 3:
        creds_file = sys.argv[2]
        process_google_sheet_with_credentials(creds_file, kakao_api_key)
    else:
        print("\n⚠️  구글 서비스 계정 인증 파일이 필요합니다.\n")
        print("=" * 60)
        print("구글 서비스 계정 설정 방법:")
        print("=" * 60)
        print("\n1. Google Cloud Console 접속:")
        print("   https://console.cloud.google.com/")
        print("\n2. 프로젝트 생성 (또는 기존 프로젝트 선택)")
        print("\n3. APIs & Services > Library 에서 검색:")
        print("   - Google Sheets API 활성화")
        print("   - Google Drive API 활성화")
        print("\n4. APIs & Services > Credentials:")
        print("   - CREATE CREDENTIALS > Service Account")
        print("   - 서비스 계정 이름 입력 후 생성")
        print("\n5. 생성된 서비스 계정 클릭:")
        print("   - Keys 탭 > ADD KEY > Create new key")
        print("   - JSON 선택 > Create")
        print("   - 다운로드된 JSON 파일을 안전한 곳에 저장")
        print("\n6. 구글 시트 공유:")
        print("   - 구글 시트 열기")
        print("   - 공유 버튼 클릭")
        print("   - 서비스 계정 이메일 추가 (예: xxx@xxx.iam.gserviceaccount.com)")
        print("   - 편집자 권한 부여")
        print("\n7. 스크립트 실행:")
        print(f"   python google_sheets_coordinates.py {kakao_api_key} credentials.json")
        print("\n" + "=" * 60)
