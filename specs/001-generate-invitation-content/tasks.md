---
description: "청첩장 정보 자동 반영 구현 작업"
---

# Tasks: 청첩장 정보 자동 반영

**Input** — `specs/001-generate-invitation-content/`의 설계 문서  
**Prerequisites** — [구현 계획](plan.md), [기능 명세](spec.md), [기술 검토](research.md), [데이터 모델](data-model.md), [생성 명령 계약](contracts/generator.md), [검증 가이드](quickstart.md)

## Format

`- [X] T001 [P] [US1] 작업과 파일 경로` 형태를 사용한다. `[P]`는 선행 작업이 끝나면 다른 파일의 작업과 병행할 수 있음을, `[USn]`은 해당 사용자 스토리를 뜻한다. 파일 경로는 저장소 루트 기준이다.

## Phase 1: Setup

**목표** — 작성자가 바로 생성에 사용할 예시 입력을 준비한다.

- [X] T001 [생성 명령 계약](contracts/generator.md)의 초안 예시를 루트의 `invitation.json`에 저장하고 `sample.png`를 참조한다.

## Phase 2: Foundational

**목표** — 미리보기와 게시 모드가 공유할 JSON 판독과 검증 경계를 만든다.

- [X] T002 Python 3.11 표준 라이브러리로 `scripts/generate_invitation.py`의 입력 판독부를 만들고 UTF-8 JSON 객체, 중복 키, 알 수 없는 키를 [데이터 모델](data-model.md#청첩장-입력-정보)에 따라 처리한다.
- [X] T003 `scripts/generate_invitation.py`에서 [청첩장 입력 정보.status, 청첩장 입력 정보.groom_name, 청첩장 입력 정보.bride_name, 청첩장 입력 정보.venue_name, 청첩장 입력 정보.venue_address, 청첩장 입력 정보.venue_hall, 청첩장 입력 정보.venue_floor, 청첩장 입력 정보.cover_photo_alt](data-model.md#청첩장-입력-정보)를 검증하고 렌더링에서 재사용할 값으로 정리한다.
- [X] T004 `scripts/generate_invitation.py`에서 [청첩장 입력 정보.date, 청첩장 입력 정보.time, 청첩장 입력 정보.directions_url, 청첩장 입력 정보.cover_photo](data-model.md#청첩장-입력-정보)를 검증하고 날짜·시각의 파싱 결과와 지도 URL·사진 경로를 공유 입력에 담는다. 확정 상태에 적용되는 예시 URL과 사진 검증도 같은 경계에 둔다.

## Phase 3: User Story 1 — 확정 정보를 입력해 청첩장 생성 (P1, MVP)

**목표** — 한 파일을 편집하고 명령 한 번으로 정적 청첩장을 생성한다.  
**독립 검증** — [검증 가이드 1단계](quickstart.md)에서 날짜를 다른 달로 옮기고 이름, 장소, 시각, 링크를 바꾼다. 한 번의 실행으로 제목, 표지, 인사말, 일정과 달력이 갱신되고 선택 항목과 특수문자가 의도대로 표시되는지 확인한다. 이 검증은 로컬에서 끝난다.

- [X] T005 [P] [US1] `index.html`의 레이아웃, 초대 문구와 공유 마크업을 바탕으로 `templates/invitation.html`을 만든다. 동적 값과 달력 행의 치환 위치, 초안 표시와 `noindex`, 사진과 외부 길찾기 링크, 상대 CSS·JS 경로를 둔다.
- [X] T006 [P] [US1] `styles.css`에서 예시 사진 확대 규칙을 예시 사진에 한정하고, 일반 사진 비율과 좁은 화면의 주소 줄바꿈을 처리한다. 길찾기 링크에 모바일 터치 영역과 키보드 초점 표시를 제공한다. T005와 길찾기 및 예시 사진의 선택자 이름을 먼저 맞춘다.
- [X] T007 [P] [US1] `README.md`에 `invitation.json`의 필수·선택 입력 예시, 사진 위치, 생성 명령과 로컬 미리보기 절차를 적고 기존 HTML 직접 편집 안내를 이 흐름에 맞게 고친다.
- [X] T008 [US1] `scripts/generate_invitation.py`에서 검증 결과로 한국어 날짜와 오전·오후 시각, 일요일부터 시작하는 달력과 예식일 한 칸, 선택 항목과 사진 상대 URL을 만든다. 사용자 텍스트와 속성을 이스케이프하여 `templates/invitation.html`을 엄격 치환하고, 인자 없는 명령을 연결해 루트의 `index.html`을 예시 입력으로 한 번 생성한다.

## Phase 4: User Story 2 — 잘못된 입력을 찾아 수정 (P2)

**목표** — 작성자가 오류 위치와 이유를 확인할 수 있고 마지막 생성 결과를 열 수 있다.  
**독립 검증** — [검증 가이드 2단계](quickstart.md)에 따라 필수 값, 날짜, 시각, 링크, 사진 오류를 한 건씩 재현한다. 0이 아닌 종료 상태, 필드와 이유, 이전 HTML 해시 보존을 확인하고 정정 후 다시 생성한다.

- [X] T009 [US2] `scripts/generate_invitation.py`에서 입력 구문과 필드 오류, 템플릿과 파일 쓰기 오류를 실행 경계에서 처리한다. 오류를 표준 오류에 원인과 필드명 또는 파일명으로 표시하고 실패 종료하며, 정상 실행 시 출력 위치를 알려준다.
- [X] T010 [US2] `scripts/generate_invitation.py`에서 검증과 렌더링이 모두 끝난 HTML을 `index.html`과 같은 디렉터리의 임시 파일에 기록하고 원자적으로 교체한다. 최초 실패와 기존 성공 이후 실패에서 불완전한 결과나 임시 파일이 남지 않도록 한다.
- [X] T011 [P] [US2] `README.md`에 오류 메시지에서 해당 입력을 찾아 수정하고 재실행하는 절차와 마지막 성공 미리보기의 보존 동작을 설명한다.

## Phase 5: User Story 3 — 초안을 미리보고 확정 정보만 게시 (P3)

**목표** — 초안은 로컬에서 표시하고 확정된 현재 입력으로 만든 파일만 업로드한다.  
**독립 검증** — [검증 가이드 3단계](quickstart.md)에 따라 초안 미리보기와 초안·무효 입력의 게시 거부를 확인한다. 유효한 확정 입력으로 만든 번들을 로컬 `/wedding/`에 올려 허용된 네 파일과 모바일·데스크톱 링크를 검증한다.

- [X] T012 [US3] `scripts/generate_invitation.py`의 `--publish-dir`에 [생성 명령 계약](contracts/generator.md)을 적용한다. 현재 확정 입력을 검증하고 같은 렌더러로 게시 HTML을 만든 뒤, 지정된 새 디렉터리에 HTML, CSS, JS, 선택된 사진 한 장을 스테이징한다. 실패 시 부모 디렉터리의 임시 산출물을 정리하고 이전 미리보기나 다른 번들을 보존한다.
- [X] T013 [P] [US3] `.github/workflows/pages.yml`의 준비 단계에서 체크아웃한 현재 입력으로 Python 3.11 이상과 `--publish-dir _site`를 실행하도록 연결한다. 기존 수동 실행과 업로드·배포 흐름을 유지하고, 생성이 성공한 `_site`만 업로드하도록 루트 HTML과 전체 사진 디렉터리를 복사하던 단계를 교체한다.
- [X] T014 [P] [US3] `README.md`에 확정 자료 대조, 지도 목적지 확인, 상태 변경, 검토한 입력과 사진이 담긴 커밋의 수동 배포, 게시 후 리소스·링크·공유 확인을 안내한다.

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T015 `specs/001-generate-invitation-content/quickstart.md`의 로컬 검증 절차로 SC-001~SC-004의 생성, 오류 복구, 게시용 파일 목록과 `/wedding/` 경로를 확인한다. 모바일·데스크톱에서 가로 스크롤, 터치 및 키보드 길찾기, 기존 공유를 확인한다. 실제 배포 후 점검은 작성자가 확정 자료로 게시할 때 적용한다.

## Dependencies & Execution Order

- **공통 선행** — T001 → T002 → T003 → T004.
- **US1** — 공통 선행 후 T005·T006·T007을 병행할 수 있다. T008은 T005·T006 이후에 실행하며, 문서까지 반영되면 US1 검증이 가능하다.
- **US2** — US1의 생성 명령을 바탕으로 T009 → T010을 수행한다. T011은 US1 문서가 준비된 뒤 T009·T010과 병행할 수 있다.
- **US3** — US2의 오류 처리와 스테이징 정책을 바탕으로 T012를 수행한다. 계약이 정해져 있으므로 T013·T014는 각각 별도 파일에서 T012와 병행할 수 있다. 통합 검증은 세 작업이 모두 끝난 뒤 수행한다.
- **최종 검증** — US1 → US2 → US3를 완료한 뒤 T015에서 단계별 검증을 다시 수행한다.

## Parallel Examples

- **US1** — T005 템플릿, T006 스타일, T007 작성자 안내를 동시에 작업한다.
- **US2** — T009·T010 스크립트 작업과 T011 오류 안내를 동시에 진행한다.
- **US3** — T012 게시 명령, T013 워크플로 연결, T014 게시 안내를 동시에 진행한다.

## Implementation Strategy

### MVP First

T001~T008을 완료하고 US1의 독립 검증으로 로컬 청첩장 갱신을 시연한다.

### Incremental Delivery

US2에서 입력 오류와 복구 흐름을 추가한 뒤 US3에서 확정 결과의 게시 연결을 완료한다. 각 단계의 독립 검증을 통과한 후 최종 검증으로 이어간다.

## Phase 7: Convergence

- [X] T016 CRITICAL — `scripts/generate_invitation.py`의 기본 예시 미리보기에 표시된 일시를 비롯한 정보가 예시임을 명시하고, 생성 명령으로 `index.html`의 초기 초안을 갱신한다. 작성자 자료로 검토 중인 초안의 상태 표시도 확인한다. per Constitution IV, FR-005, US3/AC1 (contradicts)
- [X] T017 `scripts/generate_invitation.py`의 `directions_url` 검증에서 브라우저가 해석할 수 없는 호스트 형식을 거부한다. 잘못 닫힌 IPv6 호스트 뒤에 문자가 붙은 주소는 필드 오류로 반환하고, 정상 도메인과 IPv6 주소는 허용하며 실패 시 기존 미리보기를 보존하는지 확인한다. per FR-004, US2/AC1, T004 (partial)
- [X] T018 `scripts/generate_invitation.py`의 `cover_photo` 검증에서 실제 지원 이미지 형식인지 확인하고, 확장자만 이미지인 텍스트 파일이나 빈 파일에는 필드 오류를 표시한다. 지원 형식의 정상 사진은 생성되며 실패 시 미리보기와 기존 게시 번들을 보존하는지 확인한다. per FR-005, FR-006, T004 (partial)

## Phase 8: Convergence

- [X] T019 `scripts/generate_invitation.py`에서 브라우저가 IPv4로 해석하는 숫자 호스트를 검증한다. `https://256.1.2.3/route`와 `https://maps.example.123/route`는 `directions_url` 오류로 거부하고 유효한 DNS·IPv4·IPv6 URL은 계속 허용한다. 실패한 생성에서 이전 미리보기와 게시용 파일이 보존되는지 확인한다. per FR-004, US2/AC1, T017 (partial)
- [X] T020 `scripts/generate_invitation.py`의 사진 검증을 보강해 이미지 데이터가 없는 잘린 JPEG, IDAT가 없는 PNG, 프레임이 없는 WebP를 `cover_photo` 오류로 거부한다. 정상 JPG·JPEG·PNG·WebP와 예시 PNG를 계속 읽고, 잘못된 파일로는 미리보기 교체나 게시용 파일 생성이 일어나지 않는지 확인한다. per FR-005, FR-006, T018 (partial)
