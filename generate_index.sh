#!/usr/bin/env bash
# Reads experiments.json and writes index.html.
# Requires: jq
set -euo pipefail

MANIFEST="${1:-experiments.json}"
OUTPUT="index.html"
COLORS=("#59f" "#f95" "#5f9" "#f59" "#95f" "#9f5")

if ! command -v jq &>/dev/null; then
  echo "Error: jq is required" >&2
  exit 1
fi

cat > "$OUTPUT" <<'EOF'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Peter Braden — Experiments</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: #111;
      color: #fff;
      font-family: 'Gill Sans', Helvetica, Arial, sans-serif;
      font-variant: small-caps;
      letter-spacing: 0.15em;
      min-height: 100vh;
      padding: 2rem;
    }

    header {
      text-align: center;
      margin-bottom: 3rem;
      padding-top: 1.5rem;
    }

    h1 {
      font-size: 2.2rem;
      letter-spacing: 0.4em;
      margin-bottom: 0.75rem;
    }

    nav {
      display: flex;
      gap: 2rem;
      justify-content: center;
      font-size: 0.85rem;
    }

    nav a {
      color: #777;
      text-decoration: none;
    }

    nav a:hover { color: #fff; }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 1px;
      max-width: 1100px;
      margin: 0 auto;
      background: #333;
    }

    .card {
      display: block;
      background: #000;
      padding: 1.5rem;
      text-decoration: none;
      color: #fff;
      border-top: 4px solid var(--accent);
      transition: background 0.15s;
    }

    .card:hover {
      background: #1a1a1a;
      text-shadow: 0 0 12px var(--accent);
    }

    .card-title {
      font-size: 1.1rem;
      margin-bottom: 0.5rem;
      color: var(--accent);
    }

    .card-desc {
      font-size: 0.72rem;
      font-variant: normal;
      letter-spacing: 0.04em;
      line-height: 1.55;
      color: #999;
      margin-bottom: 0.75rem;
    }

    .card-date {
      font-size: 0.68rem;
      color: #444;
    }
  </style>
</head>
<body>
  <header>
    <h1>Peter Braden</h1>
    <nav>
      <a href="http://peterbraden.co.uk">peterbraden.co.uk</a>
      <a href="https://github.com/peterbraden">github</a>
    </nav>
  </header>
  <main class="grid">
EOF

i=0
while IFS= read -r entry; do
  title=$(printf '%s' "$entry" | jq -r '.title')
  url=$(printf '%s' "$entry" | jq -r '.url')
  description=$(printf '%s' "$entry" | jq -r '.description // ""')
  date=$(printf '%s' "$entry" | jq -r '.date // ""')
  color=${COLORS[$((i % ${#COLORS[@]}))]}

  printf '    <a href="%s" class="card" style="--accent: %s">\n' "$url" "$color" >> "$OUTPUT"
  printf '      <div class="card-title">%s</div>\n' "$title" >> "$OUTPUT"
  if [ -n "$description" ]; then
    printf '      <div class="card-desc">%s</div>\n' "$description" >> "$OUTPUT"
  fi
  if [ -n "$date" ]; then
    printf '      <div class="card-date">%s</div>\n' "$date" >> "$OUTPUT"
  fi
  printf '    </a>\n' >> "$OUTPUT"

  i=$(( i + 1 ))
done < <(jq -c '.[]' "$MANIFEST")

cat >> "$OUTPUT" <<'EOF'
  </main>
</body>
</html>
EOF

echo "Generated $OUTPUT ($i experiments)."
