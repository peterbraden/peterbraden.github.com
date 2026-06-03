#!/usr/bin/env bash
# Reads experiments.json and writes index.html (Ledger design).
# Requires: jq
set -euo pipefail

MANIFEST="${1:-experiments.json}"
OUTPUT="index.html"

if ! command -v jq &>/dev/null; then
  echo "Error: jq is required" >&2; exit 1
fi

HUES=(12 48 92 152 196 238 286 330)

get_pattern() {
  local fg='rgba(0,0,0,.16)'
  case $(( $1 % 4 )) in
    0) printf '%s' "radial-gradient(${fg} 1.5px,transparent 1.7px) 0 0/13px 13px" ;;
    1) printf '%s' "repeating-linear-gradient(45deg,${fg} 0 1.5px,transparent 1.5px 11px)" ;;
    2) printf '%s' "linear-gradient(${fg} 1px,transparent 1px) 0 0/100% 11px" ;;
    3) printf '%s' "conic-gradient(${fg} 0 25%,transparent 0 50%,${fg} 0 75%,transparent 0) 0 0/16px 16px" ;;
  esac
}

# ---- header ----
cat > "$OUTPUT" <<'HEADER'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>peterbraden — workshop</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Spline+Sans+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
HEADER

cat ledger.css >> "$OUTPUT"

cat >> "$OUTPUT" <<'HEADER'
  </style>
</head>
<body>
<div class="led-root">
  <div class="led-aurora"></div>
  <div class="led-inner">
    <aside class="led-rail">
      <div>
        <div class="led-tag">// a workshop for small things</div>
        <h1 class="led-name">Peter Braden<span class="blink">_</span></h1>
        <p class="led-intro" id="led-intro"></p>
      </div>
      <div class="led-rail-bot">
        <div class="led-links-label">// elsewhere</div>
        <div class="led-links">
          <a class="led-link" href="https://github.com/peterbraden">
            <span>GitHub</span>
            <span class="led-link-handle">@peterbraden</span>
          </a>
          <a class="led-link" href="https://peterbraden.co.uk">
            <span>Homepage</span>
            <span class="led-link-handle">peterbraden.co.uk</span>
          </a>
        </div>
        <div class="led-sig">
          <span class="led-count" id="led-count">0</span> experiments · kept since 2008
        </div>
      </div>
    </aside>
    <main class="led-list">
HEADER

# ---- experiment rows ----
i=0
while IFS= read -r entry; do
  title=$(printf '%s' "$entry" | jq -r '.title')
  url=$(printf '%s' "$entry" | jq -r '.url')
  desc=$(printf '%s' "$entry" | jq -r '.desc // ""')
  dateLong=$(printf '%s' "$entry" | jq -r '.dateLong // .date // ""')
  tags=$(printf '%s' "$entry" | jq -r '.tags // [] | map("·" + .) | join(" ")')

  hue=${HUES[$((i % 8))]}
  hue2=$(( (hue + 26) % 360 ))
  pat=$(get_pattern $i)
  row_delay=$(( 600 + i * 70 ))
  tile_delay=$(( 680 + i * 70 ))
  num=$(printf '%02d' $(( i + 1 )))

  printf '%s\n' "      <a href=\"${url}\" class=\"led-row\" style=\"animation-delay: ${row_delay}ms; --glow: oklch(0.64 0.16 ${hue} / 0.55)\">" >> "$OUTPUT"
  printf '%s\n' "        <div class=\"led-tile\" style=\"background: linear-gradient(145deg, oklch(0.64 0.15 ${hue}), oklch(0.52 0.16 ${hue2})); animation-delay: ${tile_delay}ms\">" >> "$OUTPUT"
  printf '%s\n' "          <span class=\"led-tile-pat\" style=\"background-image: ${pat}\"></span>" >> "$OUTPUT"
  printf '%s\n' "          <span class=\"led-tile-num\">${num}</span>" >> "$OUTPUT"
  printf '%s\n' "        </div>" >> "$OUTPUT"
  printf '%s\n' "        <div class=\"led-body\">" >> "$OUTPUT"
  printf '%s\n' "          <div class=\"led-title\">${title}</div>" >> "$OUTPUT"
  [ -n "$desc" ] && printf '%s\n' "          <div class=\"led-desc\">${desc}</div>" >> "$OUTPUT"
  printf '%s\n' "        </div>" >> "$OUTPUT"
  printf '%s\n' "        <div class=\"led-meta\">" >> "$OUTPUT"
  [ -n "$dateLong" ] && printf '%s\n' "          <span class=\"led-date\">${dateLong}</span>" >> "$OUTPUT"
  [ -n "$tags" ] && printf '%s\n' "          <span class=\"led-tags\">${tags}</span>" >> "$OUTPUT"
  printf '%s\n' "        </div>" >> "$OUTPUT"
  printf '%s\n' "        <span class=\"led-arrow\">→</span>" >> "$OUTPUT"
  printf '%s\n' "      </a>" >> "$OUTPUT"

  i=$(( i + 1 ))
done < <(jq -c '.[]' "$MANIFEST")

TOTAL=$i

# ---- footer with inline JS ($TOTAL expands here) ----
cat >> "$OUTPUT" <<FOOTER
    </main>
  </div>
</div>
<script>
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Typewriter intro
  var text = 'A workshop for small experiments. Pages here are vibe-coded, mostly unfinished, kept around because they were fun to make.';
  var el = document.getElementById('led-intro');
  if (reduce) {
    el.textContent = text;
  } else {
    var i = 0;
    var caret = document.createElement('span');
    caret.className = 'led-caret';
    el.appendChild(caret);
    var timer;
    function tick() {
      el.textContent = text.slice(0, i);
      el.appendChild(caret);
      i++;
      if (i <= text.length) {
        timer = setTimeout(tick, 22 + (text[i - 1] === ' ' ? 18 : 0));
      } else {
        caret.remove();
      }
    }
    setTimeout(tick, 450);
  }

  // Count-up
  var countEl = document.getElementById('led-count');
  var target = ${TOTAL};
  if (reduce) {
    countEl.textContent = target;
  } else {
    var t0 = null;
    setTimeout(function () {
      requestAnimationFrame(function step(t) {
        if (!t0) t0 = t;
        var p = Math.min((t - t0) / 1100, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        countEl.textContent = Math.round(eased * target);
        if (p < 1) requestAnimationFrame(step);
      });
    }, 950);
  }
})();
</script>
</body>
</html>
FOOTER

echo "Generated $OUTPUT ($TOTAL experiments)."
