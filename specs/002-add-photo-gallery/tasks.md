---
description: "예식 일정 위 사진 갤러리 구현 작업"
---

# Tasks: 예식 일정 위 사진 갤러리

**입력** — `specs/002-add-photo-gallery/`의 [명세](spec.md), [계획](plan.md), [연구](research.md), [데이터 모델](data-model.md), [갤러리 계약](contracts/gallery.md), [검증 절차](quickstart.md)

## 체크리스트 형식

`[P]`는 선행 작업이 끝나면 다른 파일을 다루는 작업과 병행할 수 있다는 뜻이다. `[US1]`과 `[US2]`는 명세의 사용자 스토리를 가리킨다. 작업에 적힌 소스 경로는 저장소 루트 기준이다.

## Phase 1: Setup

- [X] T001 [quickstart.md](quickstart.md)의 준비 절차에 따라 임시 복사본에서 현재 `invitation.json`과 `scripts/generate_invitation.py`로 갤러리 없는 기준 `index.html`을 생성한다. 후속 검증에서 표지와 일정·길찾기를 비교할 수 있도록 기준 결과를 보관한다.

## Phase 2: Foundational

- [X] T002 `scripts/generate_invitation.py`의 기존 사진 검증이 호출자가 전달한 필드 위치를 오류에 사용하도록 하되, `cover_photo`의 검증과 메시지는 보존한다. [data-model.md](data-model.md#갤러리-사진)의 `갤러리 사진.path` 검증과 확정 입력의 예시 사진 거부 규칙을 공통 검증에 연결한다.
- [X] T003 `scripts/generate_invitation.py`에서 `gallery_photos`를 허용하고 읽어서 검증된 사진을 입력 순서대로 `Invitation`에 담는다. [data-model.md](data-model.md#청첩장-입력)의 `Invitation.gallery_photos`와 [data-model.md](data-model.md#갤러리-사진)의 `갤러리 사진.path` 및 `갤러리 사진.alt`를 적용한다. 오류는 [CLI 계약](contracts/gallery.md#생성-cli)에 따라 해당 항목을 가리키며 출력 파일을 쓰기 전에 반환한다.

## Phase 3: User Story 1 — 예식 일정 위에서 사진 보기 (P1, MVP)

**목표** — 하객이 일정 바로 위에서 사진을 순서대로 보고 예식 일시·장소와 길찾기에 접근할 수 있다.

**독립 검증** — 설명이 서로 다른 사진 3장을 등록한 미리보기를 320·390·1280px에서 연다. 사진 위치와 순서, 화면 읽기 설명, 가로 스크롤, 길찾기를 확인한다. 사진 요청 한 건을 차단한 뒤 나머지 사진과 예식 정보를 확인한다.

- [X] T004 [P] [US1] `templates/invitation.html`에서 인사말 직후와 일정 직전에 조건부 갤러리 결과가 들어갈 자리표시자를 추가한다.
- [X] T005 [P] [US1] `styles.css`에 갤러리 전용 스타일을 추가해 반응형 한 열에 사진을 배치하고 원래 비율을 유지한다. 렌더링에 사용할 선택자는 `.gallery`와 `.gallery-photos`로 맞춘다.
- [X] T006 [US1] `scripts/generate_invitation.py`에서 검증된 목록으로 ‘사진’ 제목이 연결된 섹션과 지연 로드 이미지를 렌더링한다. [data-model.md](data-model.md#갤러리-사진)의 `갤러리 사진.alt`를 이스케이프해 출력하고 기본 설명을 적용한다. 미리보기 이미지에는 인코딩한 상대 경로를 사용하며 빈 목록이면 T004의 자리표시자를 빈 문자열로 채운다.

## Phase 4: User Story 2 — 공개할 갤러리 사진 관리하기 (P2)

**목표** — 작성자가 기존 생성 명령으로 선택한 사진과 순서를 미리 확인하고, 확정한 사진만 포함된 게시 번들을 만들 수 있다.

**독립 검증** — 임시 복사본에서 입력 생략·빈 배열·사진 한 장·순서 변경·누락 사진을 각각 확인한다. 정상 게시 번들에 미등록 사진이 섞이지 않고, 직접 지정하거나 복사한 예시 사진은 게시 단계에서 거부되는지 확인한다.

- [X] T007 [P] [US2] `scripts/generate_invitation.py`에서 갤러리에 기본 예시 사진 또는 내용이 같은 복사본이 포함된 초안에 예시 사진 안내를 표시한다. 확정 입력 검증은 T002~T003의 공통 경로를 사용한다.
- [X] T008 [P] [US2] `README.md`에 [입력 계약](contracts/gallery.md#작성자-입력)을 바탕으로 사진 준비, `invitation.json` 등록, 순서와 설명 변경, 미리보기 및 게시 번들 생성을 안내한다.
- [X] T009 [US2] `scripts/generate_invitation.py`에서 게시 갤러리의 상대 주소와 복사 목적지를 하나의 순번 매핑으로 만든다. [CLI 계약](contracts/gallery.md#생성-cli)에 맞춰 등록 사진만 기존 임시 번들에 복사하고 완성된 번들을 지정 경로에 옮긴다. T006의 렌더러를 재사용한다.

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T010 [quickstart.md](quickstart.md)의 미리보기와 입력별 확인을 임시 복사본에서 실행한다. 갤러리 없는 결과의 표지·일정·길찾기를 T001의 기준과 대조하고, 사진 로드 실패와 누락 입력 조건에서 각각 페이지 이용과 이전 `index.html` 보존을 확인한다.
- [X] T011 [quickstart.md](quickstart.md)의 게시 번들과 하위 경로 검증을 실행한다. `scripts/generate_invitation.py --publish-dir`로 만든 번들을 로컬 `/wedding/`에 놓고 사진, CSS, 공유, 길찾기와 번들 파일 목록을 확인한다. 실제 게시가 승인되어 배포된 경우 같은 항목을 GitHub Pages 주소에서 확인한다.

## Dependencies & Execution Order

| 단계 | 선행 작업 | 완료 기준 |
| --- | --- | --- |
| 준비 | 없음 | T001의 기준 결과를 확보했다. |
| 공통 기반 | T001 | T002 → T003 순으로 검증과 데이터 준비를 마쳤다. |
| US1 | T003 | T004와 T005를 병행할 수 있다. 둘 다 완료한 뒤 T006으로 갤러리 미리보기를 완성한다. |
| US2 | T006 | T007과 T008을 병행할 수 있다. T009는 같은 생성기 파일을 다루므로 T007 이후에 진행한다. |
| 최종 검증 | T008, T009 | T010에서 미리보기와 입력 변경을 확인하고 T011에서 게시 번들을 확인한다. |

## Parallel Example: User Story 1

T004에서 `templates/invitation.html`의 삽입 위치를 준비하는 동안 T005에서 `styles.css`의 사진 표시를 구현한다. 두 변경을 합친 뒤 T006으로 렌더링을 연결한다.

## Parallel Example: User Story 2

T007에서 `scripts/generate_invitation.py`의 초안 안내를 구현하는 동안 T008에서 `README.md`의 작성자 안내를 갱신한다. T007이 끝나면 같은 생성기 파일에서 T009를 진행한다.

## Implementation Strategy

1. T001~T006을 완료해 일정 위에서 사진을 볼 수 있는 미리보기를 만든다. US1의 기준으로 위치, 화면 폭, 설명, 길찾기를 먼저 확인한다.
2. T007~T009를 완료해 작성자 안내와 확정 사진 게시 번들을 제공한다. US2의 기준으로 등록 순서, 예시 차단, 파일 선별을 확인한다.
3. T010~T011로 기존 청첩장 동작과 GitHub Pages 프로젝트 하위 경로 호환성을 검증한다.

## Phase 6: Convergence

- [X] T012 `scripts/generate_invitation.py`에서 갤러리 객체의 중복 키를 거부할 때 배열 위치와 키를 함께 표시하도록 입력 오류를 보완한다. 두 번째 사진에서 각각 `path`와 `alt`를 중복 지정해 `gallery_photos[1].path` 또는 `gallery_photos[1].alt`가 표시되고 이전 미리보기가 보존되는지 확인한다. 근거 T003 (partial)
- [X] T013 `specs/002-add-photo-gallery/quickstart.md`의 미리보기 단계대로 서로 다른 설명이 등록된 사진 3장을 화면 읽기 프로그램으로 탐색해 각 설명이 지정 순서대로 읽히는지 확인하고 결과를 기록한다. 근거 T010, SC-001 (partial)
