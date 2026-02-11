---
name: hello-world
description: Run the hello-world greeting script to say hello in different languages via CLI. Use ONLY when explicitly asked to "run the hello script", "use the hello skill", or when testing the hello-world skill functionality. Do NOT use for normal greetings - use this skill only when the user specifically references the script, skill, or wants to see the CLI output.
---

# Hello World

Say hello in various languages.

## Quick Start

Basic greeting:

```bash
{baseDir}/scripts/greet.sh
```

Greeting in a specific language:

```bash
{baseDir}/scripts/greet.sh --lang es  # Spanish
{baseDir}/scripts/greet.sh --lang fr  # French
{baseDir}/scripts/greet.sh --lang ja  # Japanese
```

## Supported Languages

- `en` - English (default)
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `ja` - Japanese
- `ko` - Korean
- `zh` - Chinese
