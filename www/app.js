const scrollMeter = document.querySelector(".scroll-meter span");
const executionMap = document.querySelector("[data-execution-map]");

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

if (executionMap && window.matchMedia("(prefers-reduced-motion: no-preference)").matches) {
  document.documentElement.classList.add("has-boundary-motion");
  window.requestAnimationFrame(() => executionMap.classList.add("is-ready"));
}
