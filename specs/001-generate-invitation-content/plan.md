# Implementation Plan: 청첩장 정보 자동 반영

**Branch** `main` · **Date** 2026-11-20 · **Spec** [기능 명세](spec.md)

**Input** `specs/001-generate-invitation-content/spec.md`

## Summary

작성자가 `invitation.json`을 편집하고 생성 스크립트를 실행하면 저장소 루트의 `index.html`에 정보가 반영된다. 기존 정적 청첩장의 레이아웃과 공유 동작을 활용한다. 수동 배포 워크플로는 체크아웃한 입력으로 게시용 번들을 작성하고, 입력과 산출물 준비가 성공한 경우에만 업로드한다.

## Technical Context

- **Language/Version** — 생성은 Python 3.11 이상. 하객용 페이지는 기존 HTML, CSS, JavaScript를 사용한다.
- **Primary Dependencies** — Python 표준 라이브러리와 기존 GitHub Pages Actions. 로컬에서는 `uv` 또는 설치된 Python으로 실행한다.
- **Storage** — UTF-8 JSON 입력, 저장소 내 표지 사진, 정적 출력 파일.
- **Testing** — 날짜 변경, 필수 값·날짜·시각·링크·사진 오류, 출력 보존, 초안 게시 거부, 게시 파일 목록을 검증한다. 모바일·데스크톱에서 레이아웃, 길찾기와 공유를 확인한다.
- **Target Platform** — 작성자 로컬 환경, GitHub Actions Linux 실행기, 모바일과 데스크톱 브라우저.
- **Project Type** — 생성 명령을 갖춘 한국어 정적 단일 페이지 사이트.
- **Performance Goals** — 정보 갱신은 입력 저장 후 명령 한 번으로 완료한다. 생성된 정적 페이지는 문서가 로드되는 시점에 예식 정보를 표시한다.
- **Constraints** — 생성 중 AI나 외부 API를 호출하지 않는다. `index.html`과 `/wedding/` 아래 상대 리소스 경로를 유지한다. 게시용 번들은 현재 입력을 검증해 새로 만든다.
- **Scale/Scope** — 예식 한 건, 표지 사진 한 장, 예식일 달력 하나.

## Constitution Check

| 헌장 항목 | 설계와 검증 | 설계 전 / 후 |
| --- | --- | --- |
| I. 예식 일시와 장소 | 날짜에서 요일과 달력을 생성하고 시각 표기를 계산한다. 주소와 홀·층은 해당 입력에서 표시한다. 작성자가 확정 안내와 지도 목적지를 대조한다. | 통과 / 통과 |
| II. 신랑·신부와 가족 이름 | 이름 입력을 제목, 표지, 인사말에 재사용한다. 작성자가 철자와 순서를 대조한다. | 통과 / 통과 |
| III. 계좌번호와 연락처 | 이 기능의 입력은 이름, 예식 안내와 표지 사진을 다룬다. 정의하지 않은 입력 키는 오류로 안내한다. | 통과 / 통과 |
| IV. 변경 시 재검증 | 로컬에서 변경된 값을 확인하고 동일한 커밋의 입력으로 게시본을 생성한다. 초안 상태, 기본 예시 사진 및 예시 길찾기 주소는 게시 검증에서 거부한다. | 통과 / 통과 |
| V. 모바일·데스크톱 호환 | 길찾기는 키보드 초점이 보이는 링크로 제공하고 모바일에서 터치 영역을 확보한다. 두 환경에서 일시와 장소를 가로 스크롤 없이 읽을 수 있는지 확인한다. | 통과 / 통과 |
| 구현 및 게시 검증 절차 | 정적 진입점과 상대 경로를 유지하고 기존 수동 Actions 배포를 이용한다. 로컬 미리보기와 배포 후 검증 절차를 안내한다. | 통과 / 통과 |

헌장 v1.1.0 기준으로 설계 전후 검토를 완료했다. 실제 표시값과 지도 목적지 대조는 작성자가 게시 전에 수행한다.

## Project Structure

### Documentation (this feature)

```text
specs/001-generate-invitation-content/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── generator.md
```

### Source Code (repository root)

```text
.github/workflows/pages.yml    # 배포 준비 단계에서 게시용 생성 호출
assets/                        # 작성자가 제공하는 확정 표지 사진
scripts/generate_invitation.py # 입력 검증, 렌더링, 미리보기와 게시용 출력
templates/invitation.html      # 기존 페이지 구조에서 추출한 템플릿
invitation.json                # 작성자가 편집하는 입력과 초기 초안
index.html                     # 기존 진입점, 초기 초안과 로컬 미리보기
styles.css                     # 기존 스타일, 사진과 길찾기 표시
invitation.js                  # 기존 공유 동작
sample.png                     # 로컬에 제공하는 예시 사진
README.md                      # 정보 입력, 생성, 미리보기, 게시 절차
```

**Structure Decision** — 루트의 미리보기 진입점을 유지한다. 워크플로가 지정한 `_site`는 배포 실행 중에 준비되는 출력이다.

## Phase 0 — 연구

[기술 검토](research.md)에서 입력 형식, 템플릿, 날짜 계산, 검증과 게시 방식의 결정을 기록했다.

## Phase 1 — 설계 및 검증

1. 입력 파일을 [데이터 모델](data-model.md)에 따라 검증하고, 날짜와 시각에서 달력과 표시 문자열을 계산한다.
2. 기존 페이지 구조를 활용해 템플릿을 만들고, 치환값을 문맥에 맞게 이스케이프한다. 일반 사진에 맞는 표시 규칙과 길찾기 링크를 추가한다.
3. [생성 명령 계약](contracts/generator.md)에 따라 미리보기는 검증과 렌더링을 끝내고 교체한다. 게시용 번들은 같은 렌더링으로 확정 정보와 사용할 리소스를 담는다.
4. GitHub Actions의 기존 준비 단계를 게시용 명령으로 교체한다. 성공한 산출물만 기존 업로드·배포 단계로 전달하고, README에 로컬 작성 및 동일 커밋의 수동 게시 흐름을 안내한다.
5. [검증 가이드](quickstart.md)에 따라 명세의 SC-001~SC-004를 검증한다.
