# 모바일 청첩장

저장소 루트의 [invitation.json](invitation.json)을 수정한 뒤 생성 명령을 실행합니다. 이름, 예식 일시, 장소, 길찾기 링크, 표지 사진과 배경색이 `index.html`에 반영됩니다.

| 입력 항목 | 입력 예시 |
| --- | --- |
| `status` | 초안 검토 중에는 `"draft"` |
| `background_color` | 표지와 본문의 배경색. `"#f8f6f0"`처럼 6자리 색상 코드를 입력합니다. |
| `groom_name`, `bride_name` | `"예시 신랑"`, `"예시 신부"` |
| `groom_father_name`, `groom_mother_name` | 신랑 아버지와 어머니 성함 |
| `bride_father_name`, `bride_mother_name` | 신부 아버지와 어머니 성함 |
| `groom_phone`, `bride_phone` | 청첩장 하단의 신랑 측·신부 측 전화번호. 예시 형식 `"010-0000-0000"` |
| `groom_account`, `bride_account` | 신랑 측·신부 측 계좌 정보. 각 항목의 `bank`에 은행명, `number`에 계좌번호, `holder`에 예금주를 입력합니다. 계좌번호는 앞자리 0을 유지하도록 큰따옴표로 감쌉니다. |
| `date`, `time` | 예식장 현지 날짜와 24시간제 시작 시각 `"2027-03-13"`, `"14:30"` |
| `venue_name`, `venue_address` | `"예시 웨딩홀"`, `"예시 주소"` |
| `directions` | 예식장 좌표, 대표 지도 이미지와 서비스별 장소 링크 |
| `cover_photo` | 확정 사진의 상대 경로 `"assets/우리 사진.jpg"`. JPG, PNG, WebP 사용 가능 |
| `venue_hall`, `venue_floor` | 선택 항목 `"예시 홀"`, `"2층"` |
| `parking`, `shuttle` | 지도 버튼 아래에 표시할 주차와 셔틀 안내. 여러 줄은 문자열 안에 `\n`을 넣어 구분합니다. |
| `shuttle_photo` | 선택 항목. `"assets/shuttle-stop.jpg"`처럼 탑승지 사진의 상대 경로를 입력하면 셔틀 안내 아래에서 눌러 볼 수 있습니다. |
| `cover_photo_alt` | 선택 항목 `"예식장 정원에서 촬영한 웨딩 사진"` |

부모님 성함, 연락처, 계좌 정보, 주차·셔틀 안내는 공개할 내용만 입력하세요. 빈 항목은 화면에 표시되지 않습니다.

## 예식 일정 위에 사진 추가

공개할 JPG, JPEG, PNG, WebP 사진을 `assets/`에 넣고 청첩장을 다시 생성합니다. 하위 폴더와 표지 파일도 포함되며, 파일명 사전순으로 자동 배치합니다. 설정한 대표 지도와 셔틀 탑승지 사진은 오시는 길 영역에만 표시합니다. 영문 대소문자는 정렬에서 구분하지 않습니다. 원하는 순서가 있으면 `01-정원.jpg`, `02-입구.jpg`처럼 파일명 앞에 번호를 붙이세요.

`assets/`에 사진이 없으면 갤러리 영역을 생략합니다. 기존 `gallery_photos`를 사용하던 입력에서는 사진별 `alt` 설명을 계속 읽습니다. 기본 설명은 ‘웨딩 사진 1’처럼 표시 순서에 따라 붙습니다.

본문에는 대표 사진을 최대 5장 보여줍니다. 사진을 누르면 전체 비율로 크게 볼 수 있고, 이전·다음 버튼이나 좌우 방향키로 등록한 모든 사진을 볼 수 있습니다. 썸네일의 `+N`은 상세 보기에서 더 볼 수 있는 사진 수입니다.

아래 생성 명령으로 사진과 순서를 미리 봅니다. 게시 명령은 표지와 `assets/`에서 찾은 사진을 게시 번들에 담으므로 공개할 사진을 이 폴더에 넣어 두세요.

## 오시는 길 설정

`directions`에 도로명 주소와 대조한 위도 `latitude`와 경도 `longitude`, `assets/` 아래의 대표 지도 `map_image`, 네이버 지도 장소 상세 링크 `naver_place_url`을 입력합니다. 대표 지도는 PNG 또는 WebP를 사용합니다. 카카오맵 길찾기 링크는 예식장 이름과 좌표에서 생성합니다.

오시는 길 영역이 보이면 예식장 핀이 있는 지도를 불러옵니다. `NAVER_MAP_CLIENT_ID`가 설정되어 있으면 네이버 지도를 먼저 불러옵니다. 설정이 없거나 네이버 지도를 불러오지 못하면 Leaflet과 OpenStreetMap을 사용합니다. 지도를 불러오는 중이거나 두 지도를 불러올 수 없는 경우에는 대표 지도를 표시합니다.

네이버 클라우드 [Maps Application](https://guide.ncloud-docs.com/docs/application-maps-app-vpc)에서 Dynamic Map을 선택하고 Web 서비스 URL에 `https://usan96.github.io`를 등록합니다. 로컬 미리보기에 사용할 주소도 포트 없이 등록합니다. 인증 정보의 **Client ID**를 GitHub 저장소의 Actions 변수 `NAVER_MAP_CLIENT_ID`에 설정합니다. 로컬 미리보기에서는 같은 이름의 환경 변수를 생성 명령에 전달합니다. Client ID는 브라우저에 전달되며 Client Secret은 사용하지 않습니다. 대표 계정의 무료 범위로 제한하려면 Maps의 한도 설정에서 일별·월별 한도와 초과 사용 비허용을 확인합니다.

T맵 앱의 예식장 장소 상세에서 복사한 공유 링크는 `tmap_place_url`에 입력합니다. 공유 링크로 앱에 목적지를 넘길 수 없다면 T맵의 공식 경로 호출에 사용할 수 있는 공개 웹용 프로젝트 키를 `TMAP_PUBLIC_APP_KEY`로 설정합니다. 로컬에서는 생성 명령의 환경 변수로, GitHub Pages에서는 Actions 변수로 전달합니다. 이 키는 생성된 HTML에 보이므로 공개 웹 사용과 범위 제한이 확인된 키만 사용합니다.

T맵 연결값이 없는 초안은 T맵 버튼을 눌렀을 때 주소와 다른 지도 서비스를 안내합니다. 게시용 생성에는 T맵 장소 링크 또는 공식 경로 호출 설정이 필요합니다. 기존 `directions_url`만 가진 파일은 기존 링크로 미리 볼 수 있으며, 게시하려면 새 지도 설정을 입력하고 예시 링크를 삭제합니다.

예식장이 바뀌면 주소, 좌표, 지도 이미지와 장소 링크를 함께 바꿉니다. 대표 지도 핀과 세 서비스의 도착점이 같은 건물을 가리키는지 확인합니다. 자세한 방법은 [길찾기 검증 절차](specs/003-add-map-directions/quickstart.md)에 있습니다.

## 생성 및 미리보기

저장소 루트에서 실행합니다.

```sh
uv run --no-cache --python 3.11 python scripts/generate_invitation.py
uv run --no-cache --python 3.11 python -m http.server 8000 --bind 127.0.0.1
```

`http://localhost:8000/`에서 확인합니다. 정보를 바꿀 때마다 첫 번째 명령을 다시 실행하고 브라우저를 새로고침합니다. Python 3.11 이상이 설치되어 있다면 `python3 scripts/generate_invitation.py`로도 생성할 수 있습니다.

생성에 실패하면 터미널에 표시된 항목과 이유를 확인해 입력을 고친 뒤 같은 명령을 다시 실행합니다. 기존 미리보기는 마지막으로 성공한 내용을 표시합니다.

## GitHub Pages 게시

1. 확정한 정보를 입력하고 사진을 `assets/`에 넣습니다. 모바일과 데스크톱의 로컬 미리보기에서 이름, 일시, 장소, 사진을 확정 자료와 대조하고 길찾기 링크가 같은 예식장으로 열리는지 확인합니다.
2. `status`를 `"confirmed"`로 바꾸고 다시 생성합니다. 아래 명령으로 게시에 사용할 파일을 로컬에서도 준비할 수 있습니다.

   ```sh
   uv run --no-cache --python 3.11 python scripts/generate_invitation.py --publish-dir _site
   ```

   게시용 출력 경로는 아직 존재하지 않는 디렉터리를 지정합니다. 예시 입력이나 사진이 남아 있으면 게시용 생성이 실패합니다.
3. GitHub Pages 게시 소스를 GitHub Actions로 설정합니다. 검토한 `invitation.json`과 사진을 커밋하고, 해당 입력이 포함된 브랜치에서 **Deploy invitation to GitHub Pages**를 수동 실행합니다.
4. 워크플로가 완료되면 게시 주소를 모바일과 데스크톱에서 열어 확정 정보, 사진, 길찾기, 공유와 주소 복사를 확인합니다.
