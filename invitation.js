const gallery = document.querySelector(".gallery");
const galleryDialog = gallery?.querySelector(".gallery-dialog");

if (typeof galleryDialog?.showModal === "function") {
  const photos = [...gallery.querySelectorAll(".gallery-photo")];
  const fullPhoto = galleryDialog.querySelector(".gallery-full-photo");
  const message = galleryDialog.querySelector(".gallery-message");
  const position = galleryDialog.querySelector(".gallery-position");
  const controls = galleryDialog.querySelector(".gallery-controls");
  let currentPhoto = 0;
  let opener;

  function updatePhotoState() {
    if (!fullPhoto.complete) {
      fullPhoto.hidden = true;
      message.textContent = "사진을 불러오는 중이에요.";
      return;
    }

    const loaded = fullPhoto.naturalWidth > 0;
    fullPhoto.hidden = !loaded;
    message.textContent = loaded ? "" : "사진을 불러오지 못했어요.";
  }

  function showPhoto(index) {
    currentPhoto = (index + photos.length) % photos.length;
    const photo = photos[currentPhoto];
    const description = photo.querySelector("img").alt;
    fullPhoto.alt = description;
    fullPhoto.src = photo.href;
    updatePhotoState();
    position.textContent = `${currentPhoto + 1} / ${photos.length}`;
  }

  fullPhoto.addEventListener("load", updatePhotoState);
  fullPhoto.addEventListener("error", updatePhotoState);

  for (const [index, photo] of photos.entries()) {
    photo.addEventListener("click", (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      opener = photo;
      showPhoto(index);
      galleryDialog.showModal();
    });
  }

  controls.hidden = photos.length === 1;
  for (const button of controls.querySelectorAll("button")) {
    button.addEventListener("click", () => showPhoto(currentPhoto + Number(button.dataset.galleryStep)));
  }

  galleryDialog.querySelector(".gallery-close").addEventListener("click", () => galleryDialog.close());
  galleryDialog.addEventListener("close", () => opener?.focus({ preventScroll: true }));
  galleryDialog.addEventListener("click", (event) => {
    if (event.target === galleryDialog) galleryDialog.close();
  });
  galleryDialog.addEventListener("keydown", (event) => {
    if (photos.length === 1 || !["ArrowLeft", "ArrowRight"].includes(event.key)) return;
    event.preventDefault();
    showPhoto(currentPhoto + (event.key === "ArrowLeft" ? -1 : 1));
  });
}

const countdown = document.querySelector(".countdown");

if (countdown) {
  const eventTime = Date.parse(`${countdown.dataset.event}+09:00`);
  const dayMs = 86400000;
  const koreaOffsetMs = 9 * 60 * 60 * 1000;
  const status = document.querySelector(".wedding-status");
  const statusText = status.querySelector(".wedding-status-text");
  const daysLabel = document.createElement("strong");
  const parts = [...countdown.querySelectorAll("dd")];
  let previousDays;

  function updateCountdown() {
    const now = Date.now();
    const seconds = Math.max(0, Math.floor((eventTime - now) / 1000));
    const values = [
      Math.floor(seconds / 86400),
      Math.floor(seconds / 3600) % 24,
      Math.floor(seconds / 60) % 60,
      seconds % 60,
    ];
    parts.forEach((part, index) => {
      part.textContent = String(values[index]).padStart(2, "0");
    });

    const days = Math.floor((eventTime + koreaOffsetMs) / dayMs) - Math.floor((now + koreaOffsetMs) / dayMs);
    if (days === previousDays) return;
    previousDays = days;
    if (days > 0) {
      daysLabel.textContent = `${days}일`;
      statusText.replaceChildren("의 결혼식이 ", daysLabel, " 남았습니다.");
    } else {
      statusText.textContent = days === 0 ? "의 결혼식은 오늘입니다." : "의 결혼식이 열렸습니다.";
    }
  }

  if (Number.isFinite(eventTime)) {
    updateCountdown();
    countdown.hidden = false;
    status.hidden = false;
    window.setInterval(updateCountdown, 1000);
  }
}

const copyAddress = document.querySelector(".address-copy");

function selectText(element) {
  const selection = window.getSelection();
  const range = document.createRange();
  range.selectNodeContents(element);
  selection.removeAllRanges();
  selection.addRange(range);
}

if (copyAddress) {
  const address = document.querySelector(".venue-address");
  const status = document.querySelector(".address-status");
  copyAddress.hidden = false;
  copyAddress.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(address.textContent.trim());
      status.textContent = "예식장 주소를 복사했어요.";
    } catch {
      selectText(address);
      status.textContent = "선택된 주소를 복사해 주세요.";
    }
  });
}

for (const button of document.querySelectorAll(".account-copy")) {
  const card = button.closest(".contact-card");
  const number = card.querySelector(".account-number");
  const status = card.querySelector(".account-status");
  button.hidden = false;
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(number.textContent.trim());
      status.textContent = "계좌번호를 복사했어요.";
    } catch {
      selectText(number);
      status.textContent = "선택된 계좌번호를 복사해 주세요.";
    }
  });
}

const venueMap = document.querySelector(".venue-map-interactive");

if (venueMap && /^https?:$/.test(location.protocol)) {
  const { latitude, longitude, venue, naverClientId } = venueMap.dataset;
  const center = [Number(latitude), Number(longitude)];
  const figure = venueMap.closest(".venue-map");
  const preview = figure.querySelector(".venue-map-preview");

  function showVenueMap(provider) {
    figure.classList.add("is-interactive");
    figure.dataset.mapProvider = provider;
    preview.hidden = true;
    venueMap.removeAttribute("inert");
  }

  function loadOpenStreetMap() {
    const leaflet = window.L;
    if (!leaflet) return;
    const map = leaflet.map(venueMap, {
      attributionControl: false,
      zoomControl: false,
      scrollWheelZoom: false,
    }).setView(center, 16);

    leaflet.control.zoom({ zoomInTitle: "확대", zoomOutTitle: "축소" }).addTo(map);
    const pinLabel = document.createElement("span");
    pinLabel.textContent = venue;
    leaflet.marker(center, { alt: venue, title: venue }).addTo(map).bindPopup(pinLabel);

    const tiles = leaflet.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19 });
    const fallback = window.setTimeout(() => map.remove(), 8000);
    let tileFailed = false;
    tiles.on("tileerror", () => { tileFailed = true; });
    tiles.once("load", () => {
      window.clearTimeout(fallback);
      if (tileFailed) {
        // Let Leaflet finish dispatching the tile load event before removing the layer.
        queueMicrotask(() => map.remove());
        return;
      }
      showVenueMap("openstreetmap");
    });
    tiles.addTo(map);
  }

  function loadNaverMap() {
    const container = document.createElement("div");
    container.className = "venue-map-naver";
    const script = document.createElement("script");
    const params = new URLSearchParams({ ncpKeyId: naverClientId });
    script.src = `https://oapi.map.naver.com/openapi/v3/maps.js?${params}`;
    let map;
    let failed = false;
    const resizeMap = () => map.autoResize();
    const timeout = window.setTimeout(useOpenStreetMap, 5000);

    function useOpenStreetMap() {
      if (failed) return;
      failed = true;
      window.clearTimeout(timeout);
      queueMicrotask(() => {
        window.removeEventListener("resize", resizeMap);
        figure.classList.remove("is-interactive");
        delete figure.dataset.mapProvider;
        preview.hidden = false;
        venueMap.setAttribute("inert", "");
        map?.destroy();
        container.remove();
        script.remove();
        loadOpenStreetMap();
      });
    }

    window.navermap_authFailure = useOpenStreetMap;
    script.addEventListener("load", () => {
      if (failed) return;
      try {
        const maps = window.naver.maps;
        const position = new maps.LatLng(...center);
        map = new maps.Map(container, {
          center: position,
          zoom: 16,
          zoomControl: false,
          scrollWheel: false,
        });
        new maps.Marker({ map, position, title: venue });
        maps.Event.once(map, "tilesloaded", () => {
          if (failed) return;
          window.clearTimeout(timeout);
          showVenueMap("naver");
        });
        window.addEventListener("resize", resizeMap);
      } catch {
        useOpenStreetMap();
      }
    }, { once: true });

    script.addEventListener("error", useOpenStreetMap);
    container.addEventListener("error", useOpenStreetMap, true);
    venueMap.append(container);
    document.head.append(script);
  }

  const loadVenueMap = naverClientId ? loadNaverMap : loadOpenStreetMap;
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(([entry]) => {
      if (!entry.isIntersecting) return;
      observer.disconnect();
      loadVenueMap();
    });
    observer.observe(venueMap);
  } else {
    loadVenueMap();
  }
}

const directions = document.querySelector(".directions-actions");

if (directions) {
  const agent = navigator.userAgent;
  const inApp = /KAKAOTALK|NAVER|Instagram|FBAN|FBAV|; wv\b/i.test(agent);
  const androidChrome = !inApp && /Android/.test(agent) && /Chrome\//.test(agent);
  const iosSafari = !inApp && /iPhone|iPad|iPod/.test(agent) && /Version\/.*Safari\//.test(agent);
  let webFallback;

  function cancelWebFallback() {
    window.clearTimeout(webFallback);
  }

  window.addEventListener("pagehide", cancelWebFallback);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) cancelWebFallback();
  });

  directions.addEventListener("click", (event) => {
    const anchor = event.target.closest(".directions-link");
    if (!anchor || event.defaultPrevented || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    cancelWebFallback();

    if (anchor.dataset.naverQuery && (androidChrome || iosSafari)) {
      const parameters = new URLSearchParams(anchor.dataset.naverQuery);
      parameters.set("appname", location.origin + location.pathname);
      const route = `route/car?${parameters}`;
      event.preventDefault();

      if (androidChrome) {
        const fallback = encodeURIComponent(anchor.href);
        location.assign(
          `intent://${route}#Intent;scheme=nmap;action=android.intent.action.VIEW;` +
          `category=android.intent.category.BROWSABLE;package=com.nhn.android.nmap;S.browser_fallback_url=${fallback};end`,
        );
      } else {
        webFallback = window.setTimeout(() => {
          if (!document.hidden) location.assign(anchor.href);
        }, 1600);
        location.assign(`nmap://${route}`);
      }
    } else if (anchor.dataset.tmapRoute && (androidChrome || iosSafari)) {
      event.preventDefault();
      location.assign(anchor.dataset.tmapRoute);
    }
  });
}

const share = document.querySelector(".share");
const shareButton = share.querySelector(".share-button");
const status = share.querySelector(".share-status");
const link = share.querySelector(".share-link");
const address = link.querySelector("input");

if (location.protocol === "https:" || location.protocol === "http:") {
  share.hidden = false;
}

shareButton.addEventListener("click", async () => {
  const url = new URL(location.href);
  url.hash = "";
  status.textContent = "";
  link.hidden = true;

  if (navigator.share) {
    const title = document.querySelector('meta[property="og:title"]')?.content || document.title;
    try {
      await navigator.share({ title, url: url.href });
      return;
    } catch (error) {
      if (error.name === "AbortError") return;
    }
  }

  try {
    await navigator.clipboard.writeText(url.href);
    status.textContent = "청첩장 주소를 복사했어요.";
  } catch {
    address.value = url.href;
    link.hidden = false;
    address.focus();
    address.select();
    status.textContent = "아래 주소를 복사해 주세요.";
  }
});
