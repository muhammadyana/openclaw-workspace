#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  greet.sh [--lang <code>]

Examples:
  greet.sh              # Hello in English
  greet.sh --lang es    # Hello in Spanish
  greet.sh --lang ja    # Hello in Japanese

Supported languages: en, es, fr, de, it, ja, ko, zh
EOF
  exit 2
}

lang="${1:-en}"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --lang)
      lang="${2:-en}"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      shift
      ;;
  esac
done

case "$lang" in
  en) echo "Hello!" ;;
  es) echo "¡Hola!" ;;
  fr) echo "Bonjour!" ;;
  de) echo "Hallo!" ;;
  it) echo "Ciao!" ;;
  ja) echo "こんにちは！" ;;
  ko) echo "안녕하세요!" ;;
  zh) echo "你好！" ;;
  *) echo "Hello! (Language '$lang' not supported, using English)" ;;
esac
