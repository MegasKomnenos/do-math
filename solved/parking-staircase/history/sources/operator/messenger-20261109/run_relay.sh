#!/usr/bin/env bash
# One-off relay: a Claude CLI in the same permission mode as the do-math workers sends the
# prepared messages in messages.json to the running sessions. Run it yourself:
#   ! bash /c/math/.skill-workspace/do-math/operator-inputs/messenger-20261109/run_relay.sh
cd /c/math/.skill-workspace/do-math/operator-inputs/messenger-20261109 || exit 1
W=$(cygpath -w "$(pwd)")
timeout 900 "C:/Users/<account>/.local/bin/claude.exe" --print --model sonnet \
  --dangerously-skip-permissions --permission-prompts none \
  --setting-sources "" --settings "$W\\settings.json" \
  --disable-slash-commands --strict-mcp-config --mcp-config '{"mcpServers":{}}' --no-chrome \
  --output-format text < prompt.txt > relay-output.txt 2> relay-stderr.txt
echo "exit=$?"
tail -20 relay-output.txt
tail -5 relay-stderr.txt
