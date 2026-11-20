const gallery = document.querySelector(".gallery");
const galleryDialog = gallery?.querySelector(".gallery-dialog");

if (typeof galleryDialog?.showModal === "function") {
  const photos = [...gallery.querySelectorAll(".gallery-photo")];
  const fullPhoto = galleryDialog.querySelector(".gallery-full-photo");
  const position = galleryDialog.querySelector(".gallery-position");
  const controls = galleryDialog.querySelector(".gallery-controls");
  const previewLimit = 5;
  let currentPhoto = 0;
  let opener;

  function showPhoto(index) {
    currentPhoto = (index + photos.length) % photos.length;
    const photo = photos[currentPhoto];
    const description = photo.querySelector("img").alt;
    fullPhoto.alt = description;
    fullPhoto.src = photo.href;
    position.textContent = `${currentPhoto + 1} / ${photos.length}`;
  }

  for (const [index, photo] of photos.entries()) {
    photo.addEventListener("click", (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      opener = photo;
      showPhoto(index);
      galleryDialog.showModal();
    });
  }

  if (photos.length > previewLimit) {
    for (const photo of photos.slice(previewLimit)) photo.hidden = true;

    const lastPreview = photos[previewLimit - 1];
    const remaining = photos.length - previewLimit;
    const count = document.createElement("span");
    count.className = "gallery-more";
    count.textContent = `+${remaining}`;
    count.setAttribute("aria-hidden", "true");
    lastPreview.append(count);
    lastPreview.setAttribute(
      "aria-label",
      `${lastPreview.querySelector("img").alt} 크게 보기, 이후 사진 ${remaining}장`,
    );
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
    try {
      await navigator.share({ title: document.title, url: url.href });
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
