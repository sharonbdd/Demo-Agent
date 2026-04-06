from __future__ import annotations

import asyncio
import os

os.environ.setdefault("OPENCLAUDE_ACP_DEFAULT_CONTEXT_PROFILE", "high")

from openclaude_acp_bridge import main


if __name__ == "__main__":
    asyncio.run(main())
