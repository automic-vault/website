// An illustration only: no commands execute and no credentials are requested.
const demo = document.querySelector('.aws-demo');
if (demo) {
  const play = demo.querySelector('[data-demo-play]');
  const read = demo.querySelector('[data-read-command]');
  const write = demo.querySelector('[data-write-command]');
  const output = demo.querySelector('[data-output]');
  const notification = demo.querySelector('[data-notification]');
  const approval = demo.querySelector('[data-approval]');
  const waiting = demo.querySelector('[data-wait]');
  const readCommand = read.textContent;
  const writeCommand = write.textContent;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let timer;
  let tick = 0;
  let playing = false;

  function render() {
    read.textContent = readCommand.slice(0, Math.max(0, tick - 4));
    write.textContent = writeCommand.slice(0, Math.max(0, tick - 46));
    output.hidden = tick < 24;
    notification.hidden = tick < 22 || tick >= 52;
    approval.hidden = tick < 116;
    waiting.hidden = tick < 116;
  }

  function stop() {
    clearInterval(timer);
    playing = false;
    play.textContent = 'Replay demo ↻';
  }

  function finish() {
    stop();
    tick = 116;
    render();
  }

  function start() {
    if (reducedMotion.matches) return finish();
    tick = 0;
    playing = true;
    play.textContent = 'Pause demo Ⅱ';
    render();
    timer = setInterval(() => {
      tick += 1;
      render();
      if (tick >= 116) stop();
    }, 70);
  }

  play.disabled = false;
  play.addEventListener('click', () => playing ? stop() : start());
  reducedMotion.addEventListener('change', finish);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) finish();
  });
  // Play once on arrival; leave the human decision pending at the end.
  const observer = new IntersectionObserver(entries => {
    if (entries.some(entry => entry.isIntersecting)) {
      start();
      observer.disconnect();
    }
  }, { threshold: .35 });
  observer.observe(demo);
}
