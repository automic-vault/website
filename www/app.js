const toggle = document.querySelector(".nav-toggle");
const nav = document.querySelector(".nav");
const scrollMeter = document.querySelector(".scroll-meter span");

const copyCommand = document.querySelector(".brew-copy-command");
if (copyCommand && navigator.clipboard) {
  copyCommand.disabled = false;
  copyCommand.addEventListener("click", async () => {
    copyCommand.disabled = true;
    const status = copyCommand.querySelector('[role="status"]');
    try {
      await navigator.clipboard.writeText(document.querySelector(".brew-scanner-command code").textContent);
      copyCommand.dataset.state = "copied";
      status.textContent = copyCommand.dataset.copied;
    } catch {
      copyCommand.dataset.state = "failed";
      status.textContent = copyCommand.dataset.failed;
    } finally {
      copyCommand.disabled = false;
    }
  });
}

if (toggle && nav) {
  toggle.addEventListener("click", () => {
    const isOpen = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!isOpen));
    nav.classList.toggle("is-open", !isOpen);
  });

  nav.addEventListener("click", (event) => {
    if (event.target instanceof HTMLAnchorElement) {
      toggle.setAttribute("aria-expanded", "false");
      nav.classList.remove("is-open");
    }
  });
}

if (scrollMeter) {
  let frame = 0;

  const update = () => {
    frame = 0;
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    const progress = scrollable > 0 ? window.scrollY / scrollable : 0;
    scrollMeter.style.transform = `scaleX(${Math.min(1, Math.max(0, progress))})`;
  };

  const schedule = () => {
    if (!frame) frame = window.requestAnimationFrame(update);
  };

  update();
  window.addEventListener("scroll", schedule, { passive: true });
  window.addEventListener("resize", schedule);
}
