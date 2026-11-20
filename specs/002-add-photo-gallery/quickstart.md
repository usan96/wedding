# Quickstart: 예식 일정 위 사진 갤러리 검증

## 준비

구현 후 실행한다. Python 3.11과 `uv`, 모바일·데스크톱 브라우저, 화면 읽기 프로그램을 준비한다. 작성자가 선택한 사진 3장과 게시 제외 확인에 쓸 미등록 사진 1장을 준비한다. 게시 번들을 확인할 때는 작성자가 확정한 표지 사진, 예식 정보, 길찾기 링크도 사용한다.

저장소 루트에서 임시 검증 폴더를 만든다. 명령은 같은 셸에서 실행한다.

```bash
gallery_check=$(mktemp -d)
cp -R invitation.json sample.png styles.css invitation.js scripts templates "$gallery_check/"
mkdir -p "$gallery_check/assets" "$gallery_check/site"
cd "$gallery_check"
```

검증 폴더의 `assets/`에 준비한 사진을 넣는다. `invitation.json`에는 [입력 계약](contracts/gallery.md)에 따라 갤러리 사진 3장과 각각 다른 설명을 입력한다. 이미지 주소 인코딩을 확인하려면 입력 파일명 하나에 공백과 한글을 넣는다.

## 미리보기 확인

```bash
uv run python scripts/generate_invitation.py
uv run python -m http.server 8000 --bind 127.0.0.1
```

1. `http://127.0.0.1:8000/`을 열어 320·390·1280px 너비에서 인사말, 사진 3장, 예식 일정 순으로 표시되는지 확인한다.
2. 화면의 가로 스크롤 여부와 사진 비율을 확인한다. 화면 읽기 프로그램으로 입력한 설명 3개가 목록 순서대로 읽히는지 확인한다.
3. 길찾기가 모바일 터치와 데스크톱 키보드로 열리는지 확인하고 확정 링크를 사용하는 경우 목적지를 대조한다.
4. 브라우저 개발 도구에서 갤러리 이미지 요청 하나를 차단하고 새로고침한다. 나머지 두 사진과 예식 일시·장소, 길찾기를 확인한다.

## 입력별 결과 확인

서버를 종료한 뒤 검증 폴더의 `invitation.json`을 표의 각 조건으로 수정하고 생성 명령을 다시 실행한다.

| 조건 | 기대 결과 |
| --- | --- |
| `gallery_photos` 생략 또는 `[]` | 두 경우 모두 갤러리 영역과 제목이 생략되고 예식 일정이 표시된다. |
| 사진 1장 등록 | 예식 일정 위에 사진 1장이 표시된다. |
| 사진 순서를 변경 | 표시 순서가 바뀌고 표지 사진은 기존 설정을 따른다. |
| 사진 경로를 존재하지 않는 파일로 변경 | 종료 코드 1과 해당 `path`의 위치 및 원인이 표시된다. 직전 성공 시점의 `index.html`과 내용이 일치한다. |
| 초안의 갤러리에 `sample.png` 등록 | 미리보기에서 예시 사진을 볼 수 있고 초안 안내에 예시 사진이 포함되었다고 표시된다. |

누락 사진 검증 직전에 `cp index.html before-missing.html`로 성공 결과를 저장하고 실패 후 `cmp index.html before-missing.html`로 대조한다.

## 게시 번들과 프로젝트 하위 경로 확인

실제 게시에 사용할 설정으로 검증 폴더의 입력을 바꾼다. `status`는 `confirmed`로 지정하고 표지 사진과 갤러리용 사진 3장은 작성자가 확정한 자료로 설정한다.

```bash
uv run python scripts/generate_invitation.py --publish-dir site/wedding
find site/wedding/assets -type f -print
uv run python -m http.server 8000 --bind 127.0.0.1 --directory site
```

1. 번들의 `assets/`에는 표지와 순서대로 번호가 붙은 갤러리 사진 3장만 있는지 확인한다.
2. `http://127.0.0.1:8000/wedding/`에서 사진, CSS, 기존 공유 기능이 로드되는지 확인한다. 표지와 예식 일시·장소를 확정 자료와 대조하고 길찾기 링크가 해당 예식장을 가리키는지 확인한다.
3. 갤러리의 한 경로를 `sample.png`로 바꾼 뒤 `uv run python scripts/generate_invitation.py --publish-dir site/rejected-sample`을 실행한다. 예시 사진의 항목 위치가 오류에 표시되고 해당 출력 경로가 생성되지 않아야 한다. 별도 경로에 복사한 동일한 예시 사진으로도 반복한다.
4. 실제 게시가 승인되어 GitHub Actions 배포가 끝나면 모바일과 데스크톱에서 배포 주소를 열어 사진 순서와 로드, 예식 정보, 길찾기와 공유 동작을 다시 확인한다.

## 화면 읽기 검증 결과

Chrome의 [Accessibility Screen Reader 1.1.0](https://chromewebstore.google.com/detail/accessibility-screen-read/bgbbiljbhllbddmafaaooonjkjlhijnb)을 켠 채 로컬 미리보기의 갤러리 사진을 위에서부터 선택했다. 음성 합성 요청을 기록해 다음 순서와 문장이 입력값과 일치함을 확인했다.

1. Image, 정원에서 나란히 서 있는 모습
2. Image, 예식장 입구에서 인사하는 모습
3. Image, 햇살 아래 산책하는 모습

검증 범위는 화면 읽기 확장이 전달한 문장과 순서다. 음성 재생과 발음은 별도 확인 대상이다.
