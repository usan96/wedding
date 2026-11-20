# Implementation Plan — 예식장 지도와 길찾기

**Branch** `main` · **Feature** `003-add-map-directions` · **Date** 2026-11-20 · **Spec** [spec.md](spec.md)

## Summary

예식 안내 영역에 예식장 핀이 있는 대표 지도 한 장과 네이버 지도, 카카오맵, T맵 버튼을 배치한다. 기존 Python 생성기에서 예식장 입력값과 서비스별 링크를 검증해 정적 페이지와 게시 번들을 생성한다. 모바일에서 검증된 앱 연결 경로를 적용한다. 앱 실행이 불가능하면 같은 서비스의 웹 화면이나 청첩장의 주소를 안내한다.

## Technical Context

| 항목 | 계획 |
| --- | --- |
| 언어와 버전 | Python 3.11, HTML, CSS, 브라우저 JavaScript |
| 주요 의존성 | 기존 Python 표준 라이브러리와 GitHub Pages 워크플로, 지도 서비스별 공식 연결 또는 공유 링크 |
| 입력과 리소스 | `invitation.json`의 예식장 이름·주소와 지도 설정, `assets/`의 정적 지도 이미지 |
| 대상 환경 | iOS Safari, Android Chrome, 데스크톱 브라우저, 카카오톡 등 인앱 브라우저, GitHub Pages `/wedding/` |
| 검증 | 기존 CLI로 미리보기 및 게시 번들 생성, 입력 오류 검사, 실기기 앱 전환과 미설치 시 대체 경로, 키보드·터치 검증 |
| 성능과 가용성 | 대표 지도 이미지 한 장을 같은 출처에서 제공한다. 주소와 버튼은 이미지를 기다리지 않고 표시한다. |
| 범위 | 예식장 한 곳, 대표 지도 한 장, 세 서비스 버튼, 기존 미리보기와 게시 번들 |

## Constitution Check

| 헌장 원칙 | 연구 전 검토와 설계 반영 |
| --- | --- |
| I. 예식 일시와 장소 | 예식 정보는 기존 입력을 사용한다. 대표 지도와 세 서비스의 도착점은 같은 확정 주소와 대조한다. 예식장 홈페이지 핀과 도로명주소 위치의 차이는 게시 전 확인한다. |
| II. 신랑·신부와 가족 이름 | 이름이나 가족 정보는 이 기능의 입력 또는 표시 변경에 포함되지 않는다. |
| III. 계좌번호와 연락처 | 연락처와 계좌 정보는 지도 설정에 포함되지 않는다. |
| IV. 변경 시 재검증 | 예식장 변경 시 대표 지도와 버튼의 목적지를 함께 대조한다. 기존 초안은 미리볼 수 있다. 지도 설정과 예식장 정보가 준비된 확정본으로 게시 번들을 검증한다. |
| V. 모바일·데스크톱 호환 | 320·390·1280픽셀에서 배치와 이미지 실패 시의 동작을 확인한다. 모바일 터치 영역과 데스크톱 키보드 포커스를 검증한다. |
| 구현 및 게시 | `index.html`과 상대 리소스 경로를 사용한다. 기존 Pages 워크플로로 만든 번들을 로컬의 `/wedding/`과 실제 배포 주소에서 검증한다. |

연구 전과 설계 후 검토에서 헌장 위반을 발견하지 않았다. 실제 목적지 일치와 서비스별 앱 실행은 [검증 절차](quickstart.md)의 게시 전 확인 항목이다.

## Project Structure

### Documentation (this feature)

```text
specs/003-add-map-directions/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── directions.md
```

### Source Code (repository root)

```text
invitation.json
scripts/generate_invitation.py
templates/invitation.html
assets/                   # 예식장 지도 이미지
styles.css
invitation.js
index.html                # 로컬 미리보기 생성물
README.md                # 지도 설정, 링크 확인 및 게시 절차
.github/workflows/pages.yml
```

**구조 결정** 기존 생성기와 템플릿에서 예식장 정보와 지도 영역을 렌더링한다. CSS로 반응형 배치와 포커스 표시를 적용하고, 기존 JavaScript에서 필요한 모바일 앱 연결만 처리한다. 생성기가 지도 이미지를 게시 번들에 복사하므로 GitHub Pages의 기존 빌드·게시 진입점을 그대로 사용한다.

## Phase 0 — Research

[research.md](research.md)에 대표 지도와 서비스별 연결 방식을 기록했다. T맵 공유 링크가 설치된 앱에 목적지를 전달하는지, 카카오맵 연결이 iOS에서도 목적지를 보존하는지 실기기에서 확인한다. 아래 순서에서는 두 검증을 화면 완료와 별개로 초기에 수행한다.

## Phase 1 — Design & Contracts

1. [데이터 모델](data-model.md)에 따라 도로명 주소, 좌표, 대표 지도 이미지, 서비스별 연결 정보를 확인한다. 앱 연결과 웹 대체를 실기기에서 검증하고 결과를 기록한다.
2. 기존 CLI에서 지도 설정을 검증해 미리보기와 게시 번들을 생성한다. 템플릿에서 지도와 세 버튼을 출력하고, 이미지 경로를 각 출력 위치에 맞춰 계산한다.
3. [화면 및 연결 계약](contracts/directions.md)에 따라 표시, 터치 영역, 모바일 앱 열기, 웹 또는 주소 안내를 연결한다. 지도 실패와 앱 전환이 주소 및 다른 버튼 사용을 가로막지 않도록 한다.
4. [검증 절차](quickstart.md)로 생성물, 화면, 목적지, 게시 경로를 확인한다.
