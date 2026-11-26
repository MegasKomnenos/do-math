"""The hook a worker session's CLI runs after each batch of its tool calls: it hands the session the messages that wait for it.

A session that receives messages has the folder WAITING in its session folder. launch.py makes that folder,
names this file in the worker's settings and writes the messages. A message waits as one JSON file with
the keys `from` and `text`, under a name that sorts by the time it was sent, and is moved to DELIVERED
when it is handed over. The CLI's stream does not show what a hook returned, so that folder is the only
record of what a session was told.

The CLI starts this file after every batch of tool calls of every such session, so it imports nothing of
the runtime. It ends with exit code 2 on no path: at this event the CLI takes that code as an order to end
the turn, and reports the turn as a success.
"""
import json
import os
import sys

WAITING = 'messages'
DELIVERED = 'delivered'  # a folder inside WAITING
# The CLI passes on what a hook returns whole only up to this many characters. A longer text it writes to a
# file, and the session receives the path with the first 2,000 characters and is not asked to read the file.
WHOLE = 10_000


def deliver(session):
    """Move the messages that wait for a session to DELIVERED, oldest first, and return their texts as one
    text, each under a line that names its sender; None when none was moved. A message that cannot be read
    or moved now stays where it waits. So does a message that would carry the text past WHOLE, with those
    after it: they are handed over after a later batch, so that no message is cut because another waited
    with it. A message that is longer than WHOLE by itself is handed over alone."""
    waiting = os.path.join(session, WAITING)
    texts = []
    for name in sorted(os.listdir(waiting)):
        if not name.endswith('.json'):
            continue  # the folder DELIVERED, or a message that is still being written
        path = os.path.join(waiting, name)
        try:
            with open(path, encoding='utf-8') as stream:
                message = json.load(stream)
            text = 'Message from the %s of this research:\n%s' % (message['from'], message['text'])
            if texts and len('\n\n'.join(texts + [text])) > WHOLE:
                break
            os.replace(path, os.path.join(waiting, DELIVERED, name))
        except (OSError, ValueError, KeyError, TypeError):
            continue
        texts.append(text)
    return '\n\n'.join(texts) or None


def main():
    """Read the event to its end, since it carries the results of the batch, and print what the CLI is to
    add to the conversation. The session's folder is the last argument."""
    try:
        event = json.loads(sys.stdin.buffer.read())
        # Inside a sub-agent the event names that agent. A message is for the session itself, and waits.
        text = deliver(sys.argv[-1]) if isinstance(event, dict) and 'agent_id' not in event else None
    except (OSError, ValueError):
        return
    if text:
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PostToolBatch', 'additionalContext': text}}))


if __name__ == '__main__':
    main()
