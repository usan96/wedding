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
