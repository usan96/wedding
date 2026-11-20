# 모바일 청첩장

저장소 루트의 [invitation.json](invitation.json)을 수정한 뒤 생성 명령을 실행합니다. 이름, 예식 일시, 장소, 길찾기 링크와 표지 사진이 `index.html`에 반영됩니다.

| 입력 항목 | 입력 예시 |
| --- | --- |
| `status` | 초안 검토 중에는 `"draft"` |
| `groom_name`, `bride_name` | `"예시 신랑"`, `"예시 신부"` |
| `date`, `time` | 예식장 현지 날짜와 24시간제 시작 시각 `"2027-03-13"`, `"14:30"` |
| `venue_name`, `venue_address` | `"예시 웨딩홀"`, `"예시 주소"` |
| `directions_url` | 전체 지도 링크 `"https://example.com/directions"` |
| `cover_photo` | 확정 사진의 상대 경로 `"assets/우리 사진.jpg"`. JPG, PNG, WebP 사용 가능 |
| `venue_hall`, `venue_floor` | 선택 항목 `"예시 홀"`, `"2층"` |
| `cover_photo_alt` | 선택 항목 `"예식장 정원에서 촬영한 웨딩 사진"` |

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
