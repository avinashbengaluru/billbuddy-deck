import re
from pathlib import Path

root = Path(__file__).parent

SLIDES = [
    {"file": "intro-tally.html", "id": "slide-intro"},
    {"file": "why-billbuddy.html", "id": "slide-why", "svg_prefix": "why-"},
    {"file": "architecture.html", "id": "slide-architecture", "arch": True},
    {"file": "tally-data-sync.html", "id": "slide-data", "svg_prefix": "sync-"},
    {"file": "ai-integration.html", "id": "slide-ai"},
    {"file": "improvements.html", "id": "slide-improvements"},
]


def extract(html: str, tag: str) -> str:
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", html, re.S)
    return m.group(1).strip() if m else ""


def prepare_body(html: str) -> str:
    body = re.search(r"<body[^>]*>(.*?)</body>", html, re.S).group(1).strip()
    body = re.sub(r'^<main class="slide">', '<div class="slide-inner">', body)
    body = re.sub(r"</main>\s*(?:<script>.*?</script>\s*)?$", "</div>", body, flags=re.S)
    return body


def prepare_css(css: str) -> str:
    return re.sub(r"\.slide\s*\{[^}]+\}", "", css, count=1)


def prefix_svg_ids(body: str, prefix: str) -> str:
    def repl_id(m):
        return f'id="{prefix}{m.group(1)}"'

    def repl_href(m):
        return f'href="#{prefix}{m.group(1)}"'

    for pat in (r"(?:bf|af)", r"(?:sy|s)", r"(?:dc)"):
        body = re.sub(rf'id="({pat}-[^"]+)"', repl_id, body)
        body = re.sub(rf'href="#({pat}-[^"]+)"', repl_href, body)
    return body


def prepare_arch(body: str, css: str) -> tuple[str, str]:
    css = css.replace("body.tally-offline", "#slide-architecture.tally-offline")
    css = css.replace("body.flushing", "#slide-architecture.flushing")
    for pid in ["p-wa", "p-phonepe", "p-pay-link", "p-tally", "p-sync", "p-books"]:
        body = body.replace(f'id="{pid}"', f'id="arch-{pid}"')
        body = body.replace(f'href="#{pid}"', f'href="#arch-{pid}"')
    return body, css


deck_css = """
    :root { --deck-nav-clearance: 3.35rem; }
    .deck { position: relative; height: 100dvh; max-height: 100vh; overflow: hidden; }
    .deck-slide {
      position: absolute; top: 0; left: 0; right: 0;
      bottom: var(--deck-nav-clearance);
      opacity: 0; visibility: hidden; pointer-events: none;
      transition: opacity 0.4s ease, visibility 0.4s;
    }
    .deck-slide.active { opacity: 1; visibility: visible; pointer-events: auto; }
    .deck-slide .slide-inner {
      position: relative;
      height: 100%; max-height: 100%;
      max-width: 1280px; margin: 0 auto;
      padding: 0.55rem 1rem 0.45rem;
      display: grid; grid-template-rows: auto auto minmax(0, 1fr) auto;
      gap: 0.4rem; overflow: hidden;
      box-sizing: border-box;
    }
    #slide-architecture .slide-inner { gap: 0.45rem; }
    #slide-data .slide-inner { gap: 0.35rem; grid-template-rows: auto auto minmax(0, 1fr) auto; }
    #slide-ai .slide-inner { gap: 0.35rem; grid-template-rows: auto minmax(0, 1fr) auto; }
    .deck-slide .footer-note,
    .deck-slide .foundation { flex-shrink: 0; }
    .deck-slide .slide-num {
      bottom: 0.35rem !important;
      z-index: 2;
    }
    .why-matters-morph {
      position: fixed; z-index: 160; pointer-events: none; margin: 0;
      transition: left 0.62s cubic-bezier(0.4, 0, 0.2, 1),
                  top 0.62s cubic-bezier(0.4, 0, 0.2, 1),
                  width 0.62s cubic-bezier(0.4, 0, 0.2, 1),
                  height 0.62s cubic-bezier(0.4, 0, 0.2, 1);
      overflow: hidden; box-sizing: border-box;
    }
    .deck.is-morphing .deck-slide { transition: opacity 0.35s ease, visibility 0.35s; }
    #slide-data .why-matters-panel .benefit-grid { grid-template-columns: repeat(3, 1fr); }
    #slide-data.morph-dim .value-sync { opacity: 0.12; transition: opacity 0.35s ease; }
    #slide-ai #why-matters-panel { visibility: hidden; }
    #slide-ai.revealed #why-matters-panel { visibility: visible; }
    #slide-ai .ai-reveal {
      opacity: 0; transform: translateY(16px);
      transition: opacity 0.45s ease, transform 0.45s cubic-bezier(0.4, 0, 0.2, 1);
    }
    #slide-ai.revealed .ai-reveal { opacity: 1; transform: none; }
    #slide-ai.revealed .ai-intro.ai-reveal { transition-delay: 0.1s; }
    #slide-ai.revealed .ai-card.ai-reveal:nth-child(1) { transition-delay: 0.18s; }
    #slide-ai.revealed .ai-card.ai-reveal:nth-child(2) { transition-delay: 0.28s; }
    #slide-ai.revealed .ai-card.ai-reveal:nth-child(3) { transition-delay: 0.38s; }
    #slide-ai.revealed .foundation.ai-reveal { transition-delay: 0.48s; }
    @media (prefers-reduced-motion: reduce) {
      .why-matters-morph { transition: none !important; }
      #slide-ai .ai-reveal { opacity: 1; transform: none; transition: none; }
    }
    .deck-nav {
      position: fixed; left: 50%; bottom: 0.65rem; transform: translateX(-50%);
      z-index: 200; display: flex; align-items: center; gap: 0.55rem;
      padding: 0.35rem 0.55rem; border-radius: 999px;
      background: rgba(7, 19, 31, 0.92); border: 1px solid rgba(255,255,255,0.14);
      backdrop-filter: blur(12px); box-shadow: 0 8px 28px rgba(0,0,0,0.35);
      pointer-events: auto;
    }
    .deck-nav button.nav-arrow {
      width: 2rem; height: 2rem; border-radius: 999px; border: 1px solid rgba(255,255,255,0.16);
      background: rgba(255,255,255,0.06); color: #e8f2f7; cursor: pointer;
      font-size: 1rem; line-height: 1; display: flex; align-items: center; justify-content: center;
    }
    .deck-nav button.nav-arrow:hover:not(:disabled) {
      background: rgba(45, 212, 191, 0.18); border-color: rgba(45, 212, 191, 0.4);
    }
    .deck-nav button.nav-arrow:disabled { opacity: 0.35; cursor: default; }
    .deck-nav .counter {
      font-size: 0.62rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
      color: rgba(210,224,234,0.65); min-width: 5rem; text-align: center;
    }
    .deck-dots { display: flex; gap: 0.35rem; align-items: center; }
    .deck-dots button {
      width: 7px; height: 7px; padding: 0; border-radius: 50%; border: none;
      background: rgba(255,255,255,0.25); cursor: pointer;
    }
    .deck-dots button.active { background: #5eead4; box-shadow: 0 0 10px rgba(45,212,191,0.7); }
"""

arch_script = """
    (function () {
      const svgNS = 'http://www.w3.org/2000/svg';
      const slide = document.getElementById('slide-architecture');
      const tallyNode = document.getElementById('tallyNode');
      const queueBadge = document.getElementById('queueBadge');
      const queueBanner = document.getElementById('queueBanner');
      const hubCopy = document.getElementById('hubCopy');
      const hubPill = document.getElementById('hubPill');
      const subtitle = document.getElementById('subtitle');
      const footerNote = document.getElementById('footerNote');
      const legendMode = document.getElementById('legendMode');
      const tallyStatusText = document.getElementById('tallyStatusText');
      const tallyHint = document.getElementById('tallyHint');
      const syncLabel = document.getElementById('syncLabel');
      const flushLayer = document.getElementById('flushLayer');

      let offline = false, queued = 0, queueTimer = null, flushTimers = [], flushing = false;

      const copy = {
        online: {
          subtitle: 'BillBuddy sits in the middle — WhatsApp, payments, books, and sync stay aligned without the clerk juggling systems.',
          hub: 'Orders, customers, process to books', pill: 'Hub',
          footer: '<strong>Black box on purpose:</strong> clerks work in BillBuddy and WhatsApp — Tally stays the books, sync stays under the hood.',
          legend: 'Live sync · data flowing both ways', status: 'Online', hint: 'Click → go offline', title: 'Click to take Tally offline',
        },
        offline: {
          subtitle: 'Tally is offline — BillBuddy keeps working. New bills queue locally and submit when books come back.',
          hub: 'Working independently · bills queued for Tally', pill: 'Queuing',
          footer: '<strong>Tally offline:</strong> clerks keep quoting, collecting, and creating bills in BillBuddy — submission waits in queue until Tally is back.',
          legend: 'Independent mode · bills queued for Tally', status: 'Offline', hint: 'Click → bring online', title: 'Click to bring Tally back online',
        },
      };

      function setQueue(n) {
        queued = Math.max(0, n);
        queueBadge.textContent = String(queued);
        if (flushing) {
          queueBanner.textContent = queued === 0 ? 'All queued bills submitted to Tally' : (queued === 1 ? 'Submitting 1 bill to Tally…' : 'Submitting ' + queued + ' bills to Tally…');
          return;
        }
        queueBanner.textContent = queued === 1 ? '1 bill queued in BillBuddy · submit when Tally is back' : queued + ' bills queued in BillBuddy · submit when Tally is back';
      }

      function startQueueing() {
        setQueue(Math.max(queued, 1));
        clearInterval(queueTimer);
        queueTimer = setInterval(function () { if (offline && queued < 12) setQueue(queued + 1); }, 2200);
      }
      function stopQueueing() { clearInterval(queueTimer); queueTimer = null; }

      function clearFlush() {
        flushTimers.forEach(clearTimeout); flushTimers = [];
        while (flushLayer.firstChild) flushLayer.removeChild(flushLayer.firstChild);
        flushing = false; slide.classList.remove('flushing');
      }

      function spawnFlushPacket() {
        const g = document.createElementNS(svgNS, 'g');
        const dur = '1.65s';
        [['packet-flush-halo', '10', '0;0.7;0.7;0'], ['packet-flush-core', '5', '0;1;1;0']].forEach(function (cfg) {
          const el = document.createElementNS(svgNS, 'circle');
          el.setAttribute('class', cfg[0]); el.setAttribute('r', cfg[1]); el.setAttribute('opacity', '0');
          const fade = document.createElementNS(svgNS, 'animate');
          fade.setAttribute('attributeName', 'opacity'); fade.setAttribute('values', cfg[2]);
          fade.setAttribute('keyTimes', '0;0.1;0.85;1'); fade.setAttribute('dur', dur); fade.setAttribute('fill', 'freeze');
          const motion = document.createElementNS(svgNS, 'animateMotion');
          motion.setAttribute('dur', dur); motion.setAttribute('fill', 'freeze');
          motion.setAttribute('calcMode', 'spline'); motion.setAttribute('keyTimes', '0;1');
          motion.setAttribute('keySplines', '0.4 0 0.2 1');
          const mpath = document.createElementNS(svgNS, 'mpath');
          mpath.setAttribute('href', '#arch-p-tally');
          motion.appendChild(mpath);
          el.appendChild(fade); el.appendChild(motion); g.appendChild(el);
        });
        flushLayer.appendChild(g);
        g.querySelectorAll('animate, animateMotion').forEach(function (a) { if (a.beginElement) a.beginElement(); });
        setTimeout(function () { if (g.parentNode) g.parentNode.removeChild(g); }, 1650);
      }

      function flushQueue() {
        clearFlush();
        const count = queued;
        if (count <= 0) { setQueue(0); return; }
        flushing = true; slide.classList.add('flushing');
        hubPill.textContent = 'Submitting';
        hubCopy.textContent = count === 1 ? 'Sending 1 queued bill to Tally' : 'Sending ' + count + ' queued bills to Tally';
        legendMode.textContent = count === 1 ? 'Submitting 1 queued bill to Tally…' : 'Submitting ' + count + ' queued bills to Tally…';
        for (let i = 0; i < count; i++) {
          const t = setTimeout(function () {
            if (offline) return;
            setQueue(count - (i + 1));
            spawnFlushPacket();
            if (i === count - 1) {
              flushTimers.push(setTimeout(function () {
                if (offline) return;
                flushing = false; slide.classList.remove('flushing'); setQueue(0);
                const c = copy.online;
                hubCopy.textContent = c.hub; hubPill.textContent = c.pill; legendMode.textContent = c.legend;
              }, 1700));
            }
          }, i * 320);
          flushTimers.push(t);
        }
      }

      function applyState() {
        if (offline) clearFlush();
        slide.classList.toggle('tally-offline', offline);
        tallyNode.setAttribute('aria-pressed', offline ? 'true' : 'false');
        const c = offline ? copy.offline : copy.online;
        subtitle.textContent = c.subtitle;
        footerNote.innerHTML = c.footer;
        tallyStatusText.textContent = c.status;
        tallyHint.textContent = c.hint;
        tallyNode.title = c.title;
        syncLabel.textContent = offline ? 'Paused' : '⟷ Sync';
        if (offline) { hubCopy.textContent = c.hub; hubPill.textContent = c.pill; legendMode.textContent = c.legend; startQueueing(); }
        else {
          stopQueueing();
          if (queued > 0) flushQueue();
          else { hubCopy.textContent = c.hub; hubPill.textContent = c.pill; legendMode.textContent = c.legend; setQueue(0); }
        }
      }

      function toggle(e) { if (e) e.stopPropagation(); offline = !offline; applyState(); }
      tallyNode.addEventListener('click', toggle);
      tallyNode.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.stopPropagation(); toggle(); }
      });
    })();
"""

deck_script = """
    (function () {
      const slides = Array.from(document.querySelectorAll('.deck-slide'));
      const deck = document.getElementById('deck');
      const prevBtn = document.getElementById('prevBtn');
      const nextBtn = document.getElementById('nextBtn');
      const counter = document.getElementById('slideCounter');
      const dots = document.getElementById('deckDots');
      const DATA_IDX = 3;
      const AI_IDX = 4;
      let index = 0;
      let introAnimated = false;
      let morphing = false;

      function animateIntro() {
        if (introAnimated) return;
        introAnimated = true;
        document.getElementById('slide-intro').querySelectorAll('[data-count]').forEach(function (el) {
          const target = parseFloat(el.getAttribute('data-count'));
          const decimals = parseInt(el.getAttribute('data-decimals') || '0', 10);
          const duration = 1200;
          const start = performance.now();
          function frame(now) {
            const t = Math.min(1, (now - start) / duration);
            const eased = 1 - Math.pow(1 - t, 3);
            const val = target * eased;
            el.textContent = decimals ? val.toFixed(decimals) : String(Math.round(val));
            if (t < 1) requestAnimationFrame(frame);
          }
          requestAnimationFrame(frame);
        });
      }

      function updateNav() {
        prevBtn.disabled = index === 0 || morphing;
        nextBtn.disabled = index === slides.length - 1 || morphing;
        counter.textContent = (index + 1) + ' / ' + slides.length;
        dots.querySelectorAll('button').forEach(function (b, n) {
          b.classList.toggle('active', n === index);
        });
        if (index === 0) animateIntro();
      }

      function setActiveSlide(i) {
        slides.forEach(function (s, n) {
          const on = n === i;
          s.classList.toggle('active', on);
          s.setAttribute('aria-hidden', on ? 'false' : 'true');
        });
        index = i;
        updateNav();
      }

      function revealAiSlide() {
        const ai = document.getElementById('slide-ai');
        if (ai) ai.classList.add('revealed');
      }

      function resetAiSlide() {
        const ai = document.getElementById('slide-ai');
        if (ai) ai.classList.remove('revealed');
      }

      function morphToAi(prevIdx, nextIdx) {
        if (morphing) return;
        const fromSlide = slides[prevIdx];
        const toSlide = slides[nextIdx];
        const source = fromSlide.querySelector('#why-matters-panel');
        const target = toSlide.querySelector('#why-matters-panel');
        const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        if (!source || !target || reduced) {
          resetAiSlide();
          setActiveSlide(nextIdx);
          requestAnimationFrame(revealAiSlide);
          return;
        }

        morphing = true;
        deck.classList.add('is-morphing');
        fromSlide.classList.add('morph-dim');

        const sRect = source.getBoundingClientRect();
        const clone = source.cloneNode(true);
        clone.removeAttribute('id');
        clone.classList.add('why-matters-morph');
        clone.style.left = sRect.left + 'px';
        clone.style.top = sRect.top + 'px';
        clone.style.width = sRect.width + 'px';
        clone.style.height = sRect.height + 'px';
        document.body.appendChild(clone);

        source.style.visibility = 'hidden';
        resetAiSlide();
        setActiveSlide(nextIdx);

        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            const tRect = target.getBoundingClientRect();
            clone.style.left = tRect.left + 'px';
            clone.style.top = tRect.top + 'px';
            clone.style.width = tRect.width + 'px';
            clone.style.height = tRect.height + 'px';
          });
        });

        setTimeout(function () {
          clone.remove();
          source.style.visibility = '';
          fromSlide.classList.remove('morph-dim');
          deck.classList.remove('is-morphing');
          revealAiSlide();
          morphing = false;
          updateNav();
        }, 660);
      }

      function goTo(i) {
        const next = Math.max(0, Math.min(slides.length - 1, i));
        if (next === index || morphing) return;

        if (index === DATA_IDX && next === AI_IDX) {
          morphToAi(index, next);
          return;
        }

        if (next !== AI_IDX) resetAiSlide();
        setActiveSlide(next);
        if (next === AI_IDX) requestAnimationFrame(revealAiSlide);
      }

      prevBtn.addEventListener('click', function () { goTo(index - 1); });
      nextBtn.addEventListener('click', function () { goTo(index + 1); });
      dots.addEventListener('click', function (e) {
        const btn = e.target.closest('button[data-goto]');
        if (btn) goTo(parseInt(btn.getAttribute('data-goto'), 10));
      });

      window.addEventListener('keydown', function (e) {
        if (e.target.closest('#tallyNode') || morphing) return;
        if (e.key === 'ArrowRight' || e.key === 'PageDown') {
          e.preventDefault();
          if (index < slides.length - 1) goTo(index + 1);
        } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
          e.preventDefault();
          if (index > 0) goTo(index - 1);
        } else if (e.key === 'Home') {
          e.preventDefault(); goTo(0);
        } else if (e.key === 'End') {
          e.preventDefault(); goTo(slides.length - 1);
        }
      });

      animateIntro();
    })();
"""

all_css = []
slide_sections = []

for i, spec in enumerate(SLIDES):
    html = (root / spec["file"]).read_text(encoding="utf-8")
    css = prepare_css(extract(html, "style"))
    body = prepare_body(html)

    if spec.get("svg_prefix"):
        body = prefix_svg_ids(body, spec["svg_prefix"])

    if spec.get("arch"):
        body, css = prepare_arch(body, css)

    all_css.append(f"/* --- {spec['file']} --- */\n{css}")
    active = " active" if i == 0 else ""
    hidden = "false" if i == 0 else "true"
    slide_sections.append(
        f'    <section class="deck-slide{active}" id="{spec["id"]}" data-slide="{i}" aria-hidden="{hidden}">\n{body}\n    </section>'
    )

dots_html = "\n".join(
    f'      <button type="button"{" class=\"active\"" if i == 0 else ""} data-goto="{i}" aria-label="Slide {i + 1}"></button>'
    for i in range(len(SLIDES))
)

html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>BillBuddy Demo</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,500;6..72,600;6..72,700&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --ink: #07131f; --glow: #5eead4; --amber: #fbbf24;
      --line: rgba(148, 193, 210, 0.35); --packet: #2dd4bf;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      height: 100%; overflow: hidden;
      font-family: "Instrument Sans", system-ui, sans-serif;
      color: #e8f2f7; background: #061018;
    }}
    body {{
      background:
        radial-gradient(900px 520px at 12% -8%, rgba(13, 148, 136, 0.26), transparent 55%),
        radial-gradient(700px 480px at 92% 12%, rgba(245, 158, 11, 0.12), transparent 50%),
        linear-gradient(165deg, #07131f 0%, #0b1c2a 45%, #102433 100%);
    }}
{deck_css}
{chr(10).join(all_css)}
  </style>
</head>
<body>
  <div class="deck" id="deck">
{chr(10).join(slide_sections)}
  </div>

  <nav class="deck-nav" aria-label="Slide navigation">
    <button type="button" class="nav-arrow" id="prevBtn" aria-label="Previous slide" disabled>&#8249;</button>
    <div class="deck-dots" id="deckDots" aria-hidden="true">
{dots_html}
    </div>
    <span class="counter" id="slideCounter">1 / {len(SLIDES)}</span>
    <button type="button" class="nav-arrow" id="nextBtn" aria-label="Next slide">&#8250;</button>
  </nav>

  <script>
{deck_script}
{arch_script}
  </script>
</body>
</html>
"""

out = root / "deck.html"
out.write_text(html_out, encoding="utf-8")
out_index = root / "index.html"
out_index.write_text(html_out, encoding="utf-8")
print(f"Wrote {out} and {out_index} ({len(html_out.encode()):,} bytes) — {len(SLIDES)} slides")
