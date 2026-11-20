# Research — 예식장 지도와 길찾기

## 대표 지도

- **결정** OpenStreetMap 데이터로 예식장 주변 지도 한 장을 만들어 `assets/`에 PNG 또는 WebP로 저장한다. 화면에서 읽을 수 있는 예식장 마커와 주변 도로를 넣고 지도 옆에 `© OpenStreetMap contributors`와 라이선스 링크를 표시한다.
- **근거** 청첩장과 같은 출처에서 제공하는 정적 이미지는 지도 키와 외부 타일 요청 없이 표시할 수 있다. 이미지 요청이 실패해도 예식장 정보와 각 지도 링크는 이용할 수 있다. [OpenStreetMap 저작권 안내](https://www.openstreetmap.org/copyright) · [OpenStreetMap Foundation 출처 표기 지침](https://osmfoundation.org/wiki/Licence/Attribution_Guidelines#Static_images)
- **검토한 대안** 카카오 정적 지도는 JavaScript 키와 호스트 등록이 필요하다. 카카오맵의 HTML 태그 복사 기능은 종료됐다. [카카오 정적 지도 안내](https://apis.map.kakao.com/web/sample/staticMap/) · [카카오맵 변경 공지](https://kakaomap.tistory.com/463)

## 예식장 위치 대조

- **결정** 청첩장에 적힌 도로명 주소를 사용자가 확정한 자료와 대조한 뒤, 해당 건물과 방문객이 도착할 위치를 확인해 좌표를 정한다. 각 서비스의 장소 화면에 표시되는 주소나 지도상 도착점을 같은 건물과 대조한다.
- **근거** 예식장 홈페이지의 지도에 쓰이는 좌표는 도로명 주소로 조회되는 건물 위치보다 약 800m 남쪽이다. 홈페이지 자료는 주변 접근 안내를 참고하는 데 사용하고, 목적지 좌표는 확정 주소와 각 지도 서비스에서 다시 대조한다. [예식장 오시는 길](https://www.w-square.kr/directions) · [도로명주소 안내시스템](https://www.juso.go.kr/) · [같은 도로명 주소가 표시된 OpenStreetMap 건물 데이터](https://api.openstreetmap.org/api/0.6/way/477387898/full.json) · [건물 안 예식장 지점 데이터](https://api.openstreetmap.org/api/0.6/node/7872165334.json)
- **검토한 대안** 업체 이름 검색은 동명이거나 비슷한 이름의 결과가 나올 수 있다. 네이버 웹 대체 경로에는 실제 예식장 상세 화면에서 확인한 장소 공유 링크를 사용한다.

## 네이버 지도

- **결정** 지원되는 모바일 브라우저에서 목적지 위도, 경도, 이름을 `nmap://route/car`에 전달한다. `appname`은 실행한 청첩장 URL로 채운다. Android Chrome은 공식 앱 패키지와 웹 대체 주소를 지정한 인텐트를 사용하고, iOS Safari는 직접 누른 동작으로 스킴을 실행한다. 데스크톱과 앱 실행 실패 시 네이버 지도의 예식장 상세 HTTPS 링크를 사용한다.
- **근거** 목적지 지정과 현재 위치 출발이 문서화되어 있다. 장소 상세 공유 링크는 앱 없이 해당 건물을 확인하는 경로로 검증할 수 있다. [네이버 지도 앱 연동](https://guide.ncloud-docs.com/docs/maps-url-scheme) · [네이버 장소 공유](https://help.naver.com/service/5637/contents/18766?osType=PC) · [Chrome Android 인텐트](https://developer.chrome.com/docs/android/intents)
- **검토한 대안** 장소 공유 링크만으로 모바일에서 네이버 지도 앱이 항상 열린다는 보장은 확인하지 못했다.

## 카카오맵

- **결정** 공식 목적지 전용 HTTPS 길찾기 링크 `https://map.kakao.com/link/to/{이름},{위도},{경도}`를 사용한다. 데스크톱과 앱이 없는 모바일에서 동일 서비스의 목적지 화면으로 연결되는지 확인한다. 설치된 앱으로 목적지가 전달되지 않는 모바일 환경에서는 앱의 `route` 스킴에 `ep`만 지정하는 경로를 실기기에서 검증하고, 통과한 환경에 적용한다. 웹 대체 경로는 공식 HTTPS 링크로 유지한다.
- **근거** 카카오의 Web 가이드가 목적지 전용 링크를 지원한다. 조사 중 iPhone 사용자 에이전트로 공식 예제 장소를 열었을 때 카카오의 연결 화면이 목적지 좌표를 보존했다. 이 확인은 앱 실행까지 포함하지 않는다. Android와 iOS 문서의 앱 스킴 예제는 출발지도 포함하므로 출발지를 생략한 앱 호출은 실기기에서 확인해야 한다. [카카오 지도 Web 가이드](https://apis.map.kakao.com/web/guide/#routeurl) · [Android URL 스킴](https://apis.map.kakao.com/android_v2/docs/api-guide/urlscheme/) · [iOS URL 스킴](https://apis.map.kakao.com/ios_v2/docs/getting-started/urlscheme/)
- **검토한 대안** 일반 공유 링크로 iOS 앱을 열면 목적지가 전달되지 않을 수 있다는 카카오 개발자 지원 답변이 있다. [카카오 데브톡](https://devtalk.kakao.com/t/url/144409)

## T맵

- **결정** T맵 앱의 장소 상세에서 발급받은 예식장 공유 링크를 웹 대체 후보로 확보한다. 이 링크가 지원 모바일에서 선택 한 번으로 T맵에 목적지를 넘기면 그대로 연결에 쓴다. 목적지를 넘기지 못하는 환경에서는 T맵의 공식 HTTPS 목적지 호출 `/tmap/app/routes`를 검증해 사용한다. 공식 호출에 키가 필요할 경우 공개 웹에서 사용할 수 있고 적용 범위를 제한할 수 있는 프로젝트 키를 발급받아 사용한다. 그러한 키를 사용할 수 없고 공유 링크도 통과하지 못하면 해당 앱 연결을 완료로 기록하지 않는다.
- **근거** T맵은 장소 링크 공유와 목적지 좌표를 넘기는 공식 호출을 제공한다. 공식 호출에는 발급된 키가 필요하다. 앱 미설치 상태에서 장소 공유 링크가 해당 예식장 정보까지 표시하는지는 데스크톱과 모바일에서 검증한다. 같은 서비스의 유효한 웹 화면이 없으면 청첩장의 주소와 다른 서비스 버튼을 안내한다. [T맵 장소 공유 안내](https://www.tmapmobility.com/story/microtip/detail/92) · [T맵 호출 공식 예제](https://tmapapi.tmapmobility.com/main.html#webv2/sample/webSample61) · [T맵 호출 관련 개발자 지원](https://openapi.sk.com/qnaCommunity/398)
- **검토한 대안** 비공식 `tmap://route` 형식은 Android에서 앱을 열어도 목적지가 전달되지 않았다는 사례가 있다. [SK Open API 문의](https://openapi.sk.com/qnaCommunity/716)

## 웹 연결과 복귀 처리

- **결정** 일반 HTTPS 링크를 기본으로 제공하고, 앱 실행이 검증된 모바일 경로만 사용자가 누를 때 실행한다. iOS 스킴 호출 후에는 `visibilitychange`의 `hidden` 상태나 `pagehide`를 받으면 예약한 웹 이동을 취소한다. 인앱 브라우저가 앱 열기를 차단하는 경우를 위해 해당 서비스의 웹 링크나 청첩장 주소를 이용하는 안내를 제공한다.
- **근거** 페이지가 숨겨졌는지는 감지할 수 있지만 앱 설치, 앱 전환 여부와 목적지 수신 여부를 웹에서 확정할 수 없다. 웹 링크는 자바스크립트를 쓸 수 없을 때도 이용할 수 있다. [HTML 표준의 페이지 가시성](https://html.spec.whatwg.org/multipage/interaction.html#page-visibility) · [Chrome Android 인텐트](https://developer.chrome.com/docs/android/intents)
- **검토한 대안** 앱 설치 여부를 타이머만으로 판정하면 앱 전환 중이거나 청첩장으로 돌아왔을 때 엉뚱한 화면으로 이동할 수 있다.

## 구현 중 확인 결과

- 청첩장 초안의 도로명 주소는 OpenStreetMap의 더블유스퀘어 건물 주소인 판교역로226번길 16과 일치한다. 지도 핀과 링크에 사용한 좌표 `37.4006298, 127.1114621`은 해당 건물 안의 예식장 지점이다. 차량 접근로는 실기기 길찾기에서 확인해야 한다. [건물 데이터](https://api.openstreetmap.org/api/0.6/way/477387898/full.json) · [예식장 지점 데이터](https://api.openstreetmap.org/api/0.6/node/7872165334.json)
- 네이버 검색의 장소 정보에서 위 도로명 주소와 장소 ID `36301790`을 확인했다. 카카오맵 목적지 링크는 iPhone과 Android 사용자 에이전트에서 모두 예식장 이름과 같은 좌표를 포함한 공식 앱 연결 화면으로 이어졌다. 카카오맵 데스크톱 응답에도 목적지 이름이 포함됐다. 앱 화면까지 연결되는지는 기기에서 확인해야 한다. [네이버 장소 상세](https://map.naver.com/p/entry/place/36301790) · [카카오맵 목적지 전용 링크 안내](https://apis.map.kakao.com/web/guide/#routeurl)
- T맵 공식 목적지 호출에 키 없이 접속한 결과 HTTP 401이 반환됐다. 예식장의 T맵 장소 공유 링크나 공개 웹용 프로젝트 키가 필요하다. 초안에서 둘 다 없으면 주소와 다른 지도 서비스를 안내한다. [T맵 공식 호출 예제](https://tmapapi.tmapmobility.com/main.html#webv2/sample/webSample61)
- 사용자가 제공한 T맵 장소 공유 링크를 등록했다. 데스크톱·iOS·Android 사용자 에이전트에서 모두 T맵 공식 주소로 이어졌고, 목적지 이름과 주소는 W스퀘어컨벤션, 경기 성남시 분당구 판교역로226번길 16으로 일치했다. Chromium에서 T맵 웹 화면에 이 이름과 주소가 표시되는 것도 확인했다. 게시 번들에는 공유 링크를 사용하므로 프로젝트 키가 필요하지 않다. [T맵 장소 공유 링크](https://tmap.life/0ffb7f67)
- 수렴 작업은 실기기를 사용할 수 없는 환경에서 진행했다. 네이버 지도·카카오맵·T맵이 설치된 기기에서 앱 전환과 목적지 전달을 확인할 수 없어 직접 실행 방식을 바꾸지 않았다.
