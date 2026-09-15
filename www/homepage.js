// An illustration only: no commands execute and no credentials are requested.
const demo = document.querySelector('.aws-demo');
if (demo) {
  const field = name => demo.querySelector(`[data-${name}]`);
  const play = field('demo-play');
  const scenes = [
    {
      launcher: 'Terminal', identity: 'Terminal · Apple', tool: 'AWS',
      icon: '/assets/icon@2x.webp?v=3', policy: 'Read Only',
      read: 'aws s3 ls', output: '2026-09-15 09:41:00 acme-assets\n2026-09-15 09:41:00 acme-backups',
      write: 'aws ec2 terminate-instances --instance-ids i-0123456789abcdef0',
      secrets: 'AWS_ACCESS_KEY_ID\nAWS_SECRET_ACCESS_KEY',
    },
    {
      launcher: 'Claude Code', identity: 'Claude Code · Launcher Bundle', tool: 'GitHub',
      icon: '/assets/claude-icon.svg', policy: 'Allow Authentication',
      read: 'ssh deploy@staging.example.com uptime', output: '09:41:00 up 12 days, 3 users\nload average: 0.12, 0.08, 0.06',
      write: 'gh pr merge 42 --squash --repo acme/web', secrets: 'GH_TOKEN',
    },
  ];
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let scene = 0;
  let tick = 0;
  let timer;
  let inView = false;
  let paused = false;

  function timing() {
    const readStart = scene === 1 ? 32 : 4;
    const readDone = readStart + scenes[scene].read.length;
    const writeStart = readDone + 40;
    return { readStart, readDone, writeStart, approvalAt: writeStart + scenes[scene].write.length + 6 };
  }

  function render() {
    const current = scenes[scene];
    const { readStart, readDone, writeStart, approvalAt } = timing();
    const agent = scene === 1;
    field('terminal').dataset.agent = String(agent);
    field('agent-intro').hidden = !agent;
    field('thinking').hidden = !agent || tick >= readStart;
    field('read-line').hidden = agent && tick < readStart;
    field('session').textContent = `${current.launcher} — ~/projects/acme`;
    field('session-icon').src = current.icon;
    field('session-icon').hidden = scene === 0;
    field('read-command').textContent = agent ? current.read : current.read.slice(0, Math.max(0, tick - readStart));
    field('write-command').textContent = agent ? current.write : current.write.slice(0, Math.max(0, tick - writeStart));
    field('output').textContent = current.output;
    field('output').hidden = tick < readDone + 6;
    field('write-line').hidden = tick < writeStart;
    field('notification').hidden = tick < readDone + 4 || tick >= writeStart + 6;
    field('policy').textContent = `Authorized by ${current.policy} policy`;
    field('notification-command').textContent = `${current.read} · ${current.launcher}`;
    field('approval-icon').src = current.icon;
    field('approval-title').textContent = `${current.launcher} wants to use ${current.tool}`;
    field('approval-command').textContent = current.write;
    field('launcher').textContent = current.identity;
    field('secrets').textContent = current.secrets;
    field('approval').hidden = tick < approvalAt;
    field('wait').hidden = tick < approvalAt;
  }

  function stop() {
    clearInterval(timer);
    timer = undefined;
    play.textContent = reducedMotion.matches ? 'Next demo →' : 'Resume demo ▶';
  }

  function start() {
    stop();
    if (reducedMotion.matches) {
      tick = timing().approvalAt;
      render();
      return;
    }
    play.textContent = 'Pause demo Ⅱ';
    render();
    timer = setInterval(() => {
      tick += 1;
      // Hold the pending human decision for five seconds before the next scene.
      if (tick >= timing().approvalAt + 72) {
        scene = (scene + 1) % scenes.length;
        tick = 0;
      }
      render();
    }, 70);
  }

  function syncPlayback() {
    if (inView && !document.hidden && !paused) start();
    else stop();
  }

  play.disabled = false;
  play.addEventListener('click', () => {
    if (reducedMotion.matches) {
      scene = (scene + 1) % scenes.length;
      start();
    } else {
      paused = !paused;
      syncPlayback();
    }
  });
  reducedMotion.addEventListener('change', () => {
    tick = timing().approvalAt;
    render();
    syncPlayback();
  });
  document.addEventListener('visibilitychange', syncPlayback);
  const observer = new IntersectionObserver(entries => {
    inView = entries.some(entry => entry.isIntersecting);
    syncPlayback();
  }, { threshold: .35 });
  observer.observe(demo);
}
