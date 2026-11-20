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
