#!/usr/bin/env python3
# ruff: noqa: T201

"""Playwright-powered web adapter with optional persistent auth context."""

from contextlib import suppress
from playwright.async_api import async_playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError


class WebAdapter:
    """Adapter to fetch web page content using Playwright."""

    def __init__(
        self,
        *,
        use_persistent_context: bool = False,
        user_data_dir: str | None = None,
        browser_channel: str | None = None,
        headless: bool = True,
        browser_args: list[str] | None = None,
        manual_login: bool = False,
        wait_selector: str | None = None,
        wait_timeout_ms: int = 300000,
    ) -> None:
        """Initialize adapter with optional authenticated browsing settings."""
        self.use_persistent_context = use_persistent_context
        self.user_data_dir = user_data_dir
        self.browser_channel = browser_channel
        self.headless = headless
        self.browser_args = browser_args or []
        self.manual_login = manual_login
        self.wait_selector = wait_selector
        self.wait_timeout_ms = wait_timeout_ms

    async def fetch(self, url: str) -> str:
        """Fetch the HTML content of a web page and return it as a string."""
        async with async_playwright() as p:
            content = ""
            if self.use_persistent_context:
                # Persistent context (optionally using system Chrome via channel)
                print(
                    "Launching persistent browser context for authenticated access...",
                )
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir or "",
                    channel=self.browser_channel,
                    headless=self.headless,
                    args=self.browser_args,
                )
                page = await context.new_page()
                try:
                    print(f"Navigating to {url}...")
                    await page.goto(url, wait_until="domcontentloaded", timeout=120000)
                    # If a login form is present, allow the user time to sign in.
                    try:
                        login_elt = await page.query_selector(
                            (
                                "input[type='password'], "
                                "button:has-text('Sign in'), "
                                "button:has-text('Log in')"
                            ),
                        )
                        if login_elt is not None:
                            print(
                                "Login form detected. Please complete sign-in in the "
                                "opened browser window.",
                            )
                            print("Waiting up to 5 minutes...")
                            # Wait until login form disappears or the page transitions.
                            await page.wait_for_selector(
                                "input[type='password']",
                                state="detached",
                                timeout=300000,
                            )
                    except PlaywrightTimeoutError:
                        # Ignore wait timeouts; continue to attempt content retrieval.
                        pass

                    # Optional explicit manual pause for login flow
                    if self.manual_login and not self.headless:
                        try:
                            print(
                                "Manual login pause enabled. Switch to the browser window, "
                                "complete authentication, then return here and press Enter...",
                            )
                            input()
                        except EOFError:
                            # Non-interactive environment; ignore.
                            pass

                    # For Devin wiki, wait until on a wiki page if possible.
                    if "devin.ai" in url:
                        with suppress(PlaywrightTimeoutError):
                            await page.wait_for_url("**/wiki/**", timeout=180000)

                    # If provided, wait for a specific selector to ensure content is loaded.
                    if self.wait_selector:
                        with suppress(PlaywrightTimeoutError):
                            await page.wait_for_selector(
                                self.wait_selector,
                                timeout=self.wait_timeout_ms,
                            )

                    # Allow time for dynamic content/auth redirects
                    await page.wait_for_load_state("networkidle")
                    await page.wait_for_timeout(1500)
                    print("Retrieving page content...")
                    content = await page.content()
                    print("Content retrieved.")
                except Exception as e:
                    print(
                        "Error during Playwright navigation or content retrieval "
                        "(persistent context):",
                        e,
                    )
                    raise
                finally:
                    await context.close()
            else:
                # Ephemeral browser (public pages)
                browser = await p.chromium.launch(
                    headless=self.headless,
                    channel=self.browser_channel,
                    args=self.browser_args,
                )
                page = await browser.new_page()
                try:
                    print(f"Navigating to {url}...")
                    await page.goto(url, wait_until="networkidle", timeout=60000)
                    await page.wait_for_timeout(1000)
                    print("Retrieving page content...")
                    content = await page.content()
                    print("Content retrieved.")
                except Exception as e:
                    print(
                        f"Error during Playwright navigation or content retrieval: {e}",
                    )
                    raise
                finally:
                    await browser.close()

            return content
