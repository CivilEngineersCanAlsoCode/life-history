---
description: Claude terminal history ko ek kahani (story) ki tarah session_history.md mein record karna
---

Ye workflow Claude ki terminal activity ko monitor karta hai aur use ek chronological story ki tarah Romanized Hindi mein update karta hai.

// turbo-all
1. Get the full Claude terminal history:
   `cat ~/.claude/history.jsonl`

2. Update the `session_history.md` file:
   - Agent ko terminal history analyze karni hai.
   - Har ek interaction ko third-person Romanized Hindi mein likhna hai (e.g., "User ne poocha...", "Claude ne file edit kari...").
   - Isko ek story format mein table mein update karna hai.

3. Report the latest status to the user in Romanized Hindi.
