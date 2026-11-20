# 모바일 청첩장

저장소 루트에서 미리보기 서버를 실행한 뒤 `http://localhost:8000/`을 엽니다.

```sh
uv run --no-cache python -m http.server 8000
```

## 게시 준비

이름, 예식 일시와 장소가 확정되면 `index.html`의 표지와 일정표를 함께 수정합니다.
확정 사진은 `assets/`에 넣고 상대 경로로 연결한 뒤 `styles.css`의 예시 이미지 자르기 규칙을 정리합니다.
확정한 장소로 길찾기 링크를 연결하고 초안 문구, `data-draft`, `noindex` 설정을 제거합니다.

GitHub Pages 게시 소스를 GitHub Actions로 설정한 뒤 Actions 탭에서 **Deploy invitation to GitHub Pages**를 실행합니다.
