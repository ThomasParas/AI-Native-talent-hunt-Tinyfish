"""Hit each TinyFish primitive once to confirm the API key and SDK work.

    uv run python smoke_test.py
"""

import asyncio
from pathlib import Path

from growth_app import primitives as tf


def main() -> None:
    trace = tf.Trace()
    checks = [
        ("Search", lambda: tf.search("tinyfish web agent", trace, "smoke test", location="US", language="en")),
        ("Fetch", lambda: tf.fetch(["https://www.tinyfish.ai/"], trace, "smoke test")),
        ("Agent", lambda: tf.agent("https://scrapeme.live/shop", "Extract the first product name and price. Return JSON.", trace, "smoke test")),
        ("Browser", lambda: asyncio.run(tf.browser_screenshot("https://www.tinyfish.ai", Path("output/smoke.png"), trace, "smoke test", full_page=False))),
    ]
    for name, fn in checks:
        try:
            fn()
        except Exception as e:  # keep going so we see every primitive's status
            print(f"[{name}] error: {e}")
    print("\nprimitive  ok     secs  detail")
    for e in trace.entries:
        print(f"{e.primitive:<10} {str(e.ok):<6} {e.seconds:>5}  {e.detail[:80]}")


if __name__ == "__main__":
    main()
