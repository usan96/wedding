# Implementation Plan: 예식 일정 위 사진 갤러리

**Branch** — `main` | **Date** — 2026-11-20 | **Spec** — [spec.md](spec.md)

**Input** — `specs/002-add-photo-gallery/spec.md`

## Summary

생성기는 `assets/`에서 지원하는 이미지 파일을 찾아 검증하고, 파일명 사전순으로 인사말과 ‘예식 일정’ 사이에 갤러리를 렌더링한다. 미리보기와 게시본 모두 기존 청첩장 생성 명령으로 만든다.

## Technical Context

| 항목 | 설계 |
| --- | --- |
| 언어와 버전 | Python 3.11, HTML, CSS |
| 주요 의존성 | Python 표준 라이브러리, 기존 생성기와 HTML 템플릿, GitHub Actions |
| 저장 | `assets/` 아래의 이미지 파일과 선택적으로 사용하는 기존 사진 설명 |
| 검증 | 임시 디렉터리에서 생성 명령의 성공·실패 경로를 검증하고, 로컬 HTTP 미리보기에서 화면과 이미지 로드를 확인 |
| 대상 | 모바일·데스크톱 브라우저와 GitHub Pages 프로젝트 경로 `/wedding/` |
| 프로젝트 유형 | 정적 청첩장과 생성 CLI |
| 성능 목표 | 갤러리 사진 일부가 늦게 로드되거나 실패해도 일정과 길찾기를 이용할 수 있음 |
| 제약 | 상대 리소스 경로, 확정 자료만 게시, 기존 갤러리 없는 입력과 호환 |
| 범위 | 본문 사진 영역 한 곳, 이미지 자동 검색, 미리보기·게시 결과물 |

## Constitution Check

| 헌장 기준 | 연구 전 판정 | 설계 후 확인 |
| --- | --- | --- |
| I. 예식 일시와 장소 | 통과 | 기존 일정·장소·길찾기 생성 경로를 사용하고 갤러리 유무 및 이미지 로드 실패 조건에서 같은 값과 링크를 검증한다. |
| II. 신랑·신부와 가족 이름 | 통과 | 기존 입력과 출력 경로를 사용하고 미리보기에서 게시용 확정 자료와 대조한다. |
| III. 계좌번호와 연락처 | 적용 대상 없음 | 갤러리 계약의 입력은 사진 경로와 대체 설명이다. |
| IV. 변경 시 재검증 | 통과 | 갤러리 입력 검증을 생성 전 수행하고, 개발용 예시 사진을 포함한 입력은 게시 단계에서 거부한다. |
| V. 모바일·데스크톱 호환 | 통과 | 320·390·1280px에서 가로 스크롤을 확인하고 모바일 터치 및 데스크톱 키보드로 길찾기를 검증한다. |
| 구현 제약과 게시 절차 | 통과 | 정적 `index.html`과 프로젝트 하위에서도 동작하는 상대 경로를 사용한다. 게시 전 로컬 검증과 게시 후 GitHub Pages 확인을 안내에 포함한다. |

## Project Structure

### Documentation (this feature)

```text
specs/002-add-photo-gallery/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── gallery.md
└── quickstart.md
```

### Source Code (repository root)

```text
invitation.json                 # 작성자 입력
assets/                         # 작성자가 등록할 사진
scripts/generate_invitation.py   # 검증, 미리보기 생성, 게시 번들 생성
templates/invitation.html        # 갤러리와 예식 일정 배치
styles.css                      # 갤러리의 반응형 배치
README.md                       # 작성자 입력과 미리보기 안내
```

**구조 결정** — 기존 생성기가 검증한 사진 목록을 한 번 렌더링하고, 같은 목록의 파일만 게시 번들에 복사한다. 화면은 최대 5장의 반응형 모자이크와 전체 사진을 순서대로 볼 수 있는 상세 보기로 구성한다. GitHub Actions는 기존 게시 명령으로 번들을 생성한다.

## Design Artifacts

- [설계 결정과 대안](research.md)
- [입력과 생성 상태](data-model.md)
- [작성자·생성 명령·화면 계약](contracts/gallery.md)
- [구현 후 검증 절차](quickstart.md)
