#!/usr/bin/env bash
# Build the Rhino 8/macOS wrapper and install its Grasshopper library link.
set -euo pipefail
SOLAR_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOLAR_DOTNET="${SOLAR_DOTNET:-dotnet}"
SOLAR_PYTHON="${SOLAR_PYTHON:-python3}"
SOLAR_OUTPUT="$SOLAR_ROOT/build/grasshopper"
SOLAR_LIBRARY="$HOME/Library/Application Support/McNeel/Rhinoceros/8.0/Plug-ins/Grasshopper (b45a29b1-4343-4035-989e-044e8580d9cf)/Libraries"
if ! command -v "$SOLAR_DOTNET" >/dev/null 2>&1; then
  echo 'Install the .NET 7 SDK, or set SOLAR_DOTNET to your dotnet executable.' >&2
  exit 1
fi
if [[ ! -x "$SOLAR_ROOT/.venv/bin/python" ]]; then
  "$SOLAR_PYTHON" -m venv "$SOLAR_ROOT/.venv"
fi
"$SOLAR_ROOT/.venv/bin/python" -m pip install "$SOLAR_ROOT"
"$SOLAR_DOTNET" build "$SOLAR_ROOT/grasshopper/compiled/PlugInSolar.csproj" \
  --configuration Release --output "$SOLAR_OUTPUT" -p:UseSharedCompilation=false
mkdir -p "$SOLAR_LIBRARY"
printf '%s\n' "$SOLAR_OUTPUT" > "$SOLAR_LIBRARY/PlugInSolar.ghlink"
printf '%s\n' "$SOLAR_OUTPUT" > "$SOLAR_ROOT/grasshopper/PlugInSolar.ghlink"
echo "Built: $SOLAR_OUTPUT/PlugInSolar.gha"
echo "Installed: $SOLAR_LIBRARY/PlugInSolar.ghlink"
echo 'Restart Rhino after rebuilding a loaded plugin.'
