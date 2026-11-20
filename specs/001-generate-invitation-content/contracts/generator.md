# 작성자 명령과 게시 산출물 계약

저장소 루트에서 실행한다. Python 3.11 이상이 직접 준비되어 있다면 앞의 `uv run --no-cache --python 3.11`을 생략할 수 있다.

```sh
uv run --no-cache --python 3.11 python scripts/generate_invitation.py
uv run --no-cache --python 3.11 python scripts/generate_invitation.py --publish-dir 경로
```

## 입력

두 명령은 모두 루트의 `invitation.json`과 페이지 템플릿을 읽는다. 필드는 [데이터 모델](../data-model.md)을 따른다. 예시 입력 형식은 다음과 같다.

```json
{
  "status": "draft",
  "groom_name": "예시 신랑",
  "bride_name": "예시 신부",
  "date": "2027-03-13",
  "time": "14:30",
  "venue_name": "예시 웨딩홀",
  "venue_address": "예시 주소",
  "venue_hall": "예시 홀",
  "venue_floor": "2층",
  "directions_url": "https://example.com/directions",
  "cover_photo": "sample.png",
  "cover_photo_alt": "예시 웨딩 사진"
}
```

## 출력과 실패

| 실행 방식 | 성공 | 실패 |
| --- | --- | --- |
| 인자 없이 실행 | 종료 코드 0. 루트의 `index.html`을 교체하고 생성 위치를 알린다. 초안과 확정 입력을 모두 미리볼 수 있다. | 0이 아닌 종료 코드. 표준 오류에 문제 항목과 이유를 표시하고 이전 `index.html`을 보존한다. |
| `--publish-dir 경로` | 종료 코드 0. 지정한 새 디렉터리에 `index.html`, `styles.css`, `invitation.js`, `assets/cover.<확장자>`를 준비하고 출력 위치를 알린다. 경로는 작업 디렉터리 기준 상대 경로나 절대 경로로 전달할 수 있다. | 0이 아닌 종료 코드. 초안·예시 값, 입력 오류, 쓰기 오류 또는 기존 출력 경로가 있으면 실패한다. 기존 파일과 루트 미리보기를 건드리지 않고 실패한 새 번들을 남기지 않는다. |

게시 모드는 새 디렉터리를 받으므로 이전 빌드에서 남은 파일이 함께 게시될 여지가 없다. 스테이징은 출력 디렉터리의 부모에서 진행하며 모든 파일을 준비한 뒤 지정 경로로 이동한다. Actions는 준비 단계가 성공한 경우에만 그 디렉터리를 업로드한다.

브라우저 진입점은 배포 산출물 최상위의 `index.html`이다. CSS, JS, 사진 주소는 상대 경로로 표시하며 길찾기 링크만 입력한 외부 URL을 사용한다. 개발용 입력 파일과 이미지, 템플릿은 배포 산출물에 넣지 않는다.
