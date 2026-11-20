# Phase 0 Research — 청첩장 정보 자동 반영

## R1. 입력 형식과 실행 환경

- **결정** — UTF-8 JSON 파일 `invitation.json` 하나와 Python 3.11 이상에서 실행하는 표준 라이브러리 스크립트를 사용한다. 저장소에는 채울 위치를 보여주는 초안 입력을 둔다.
- **근거** — 항목 수가 적고 필요한 자료형이 문자열 위주라 입력 예시를 복사해 관리할 수 있다. 로컬의 기존 `uv` 실행 방식과 맞고 Python이 준비된 환경에서는 생성할 때 패키지를 설치하거나 네트워크에 연결할 필요가 없다. JSON 파싱 시 중복 키를 검출해 작성자가 앞에서 입력한 값을 뒤의 값이 조용히 덮는 경우를 막는다. [Python JSON 문서](https://docs.python.org/3.11/library/json.html#standard-compliance-and-interoperability)
- **검토한 대안** — TOML은 주석을 값 옆에 둘 수 있다. 이번에는 짧은 입력 예시와 외부 안내로 충분해 JSON을 선택했다.

## R2. 정적 렌더링과 날짜 계산

- **결정** — 기존 HTML을 템플릿으로 옮기고 `string.Template.substitute`로 치환한다. 입력에서 유래한 텍스트와 인용된 속성값은 HTML 이스케이프하고, 달력과 선택 항목 마크업은 검증된 값에서 만든다. 날짜와 시각은 먼저 입력 형식을 검사한 뒤 실제 날짜와 시각으로 해석한다. 일요일부터 시작하는 달력과 한국어 요일·시각 표기는 같은 입력에서 계산한다.
- **근거** — 치환 위치가 적고 반복되는 달력 부분을 날짜 계산과 함께 처리할 수 있다. 누락된 템플릿 변수는 생성 실패로 처리한다. 시스템 언어나 시간대가 달라도 표시되는 예식장 현지 날짜와 시각은 같다. [Python 템플릿 문서](https://docs.python.org/3.11/library/string.html#template-strings) [HTML 이스케이프 문서](https://docs.python.org/3.11/library/html.html#html.escape) [Python 달력 문서](https://docs.python.org/3.11/library/calendar.html#calendar.Calendar.monthdayscalendar)
- **검토한 대안** — Jinja 같은 전용 엔진은 반복문과 조건문을 템플릿에 둘 수 있다. 현재 한 페이지에서 필요한 치환에는 표준 라이브러리로 충분하다.

## R3. 검증과 미리보기 파일 교체

- **결정** — 입력 오류에는 문제 항목과 이유를 출력한다. 입력 검증과 렌더링이 모두 끝난 뒤 `index.html`과 같은 디렉터리에 쓴 임시 파일로 결과를 교체한다. 길찾기 주소는 형식을 검증하고 목적지는 작성자가 확인한다. 일반 사진은 원본 비율을 유지하고 기존 확대 잘라내기는 예시 사진일 때만 적용한다.
- **근거** — 주소 파서는 유효성 검사를 대신하지 않으므로 URL의 스킴과 호스트 등을 별도로 확인한다. 같은 파일시스템에서 결과를 교체하면 렌더링 실패나 중간 내용이 기존 미리보기로 노출되는 일을 피할 수 있다. [URL 파싱 문서](https://docs.python.org/3.11/library/urllib.parse.html#url-parsing-security) [Python 파일 교체 문서](https://docs.python.org/3.11/library/os.html#os.replace)
- **검토한 대안** — 결과 파일에 직접 쓰는 방식은 구현이 짧지만 검증이나 쓰기 오류가 발생했을 때 마지막 성공 결과를 보존하기 어렵다.

## R4. GitHub Pages 게시 입력과 결과물

- **결정** — 기존 수동 워크플로의 준비 단계에서 체크아웃한 입력으로 게시용 번들을 새로 생성한다. 작성자 확정 상태와 필수 항목을 검증한 뒤 `index.html`, CSS, 공유용 JavaScript와 지정한 사진 파일 한 장만 준비한다.
- **근거** — 검증 실패 시 업로드가 시작되지 않으며, 이전 미리보기나 저장소의 다른 사진이 함께 올라가지 않는다. 기존 GitHub Pages 배포 단계와 프로젝트 경로를 그대로 사용할 수 있다. [GitHub Pages 게시 소스 구성](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#creating-a-custom-github-actions-workflow-to-publish-your-site)
- **검토한 대안** — 커밋된 미리보기 HTML을 그대로 게시하는 방식에서는 입력과 결과의 최신 여부를 별도로 관리해야 한다. 사진 디렉터리 전체를 복사하면 페이지가 쓰지 않는 사진도 산출물에 포함될 수 있다.
