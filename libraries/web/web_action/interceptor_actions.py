import asyncio
import logging
from playwright.async_api import async_playwright
from .base import Base
from .request_interceptor import RequestInterceptor


class InterceptorActions(Base):
    async def modify_server_side_cookies(self, cookies):
        """
        Modify multiple server-side cookies at once.

        Args:
            url (str): The domain URL for the cookies
            cookies (list): List of cookie dictionaries to set
        """
        try:
            playwright, browser, page, client = await self.setup_playwright()

            cookie_name = cookies.get("name")
            cookie_value = cookies.get("value")

            # Additional cookies parameters with defaults
            domain = cookies.get("domain", '')
            path = cookies.get("path", "/")
            secure = cookies.get("secure", True)
            httpOnly = cookies.get("httpOnly", True)
            sameSite = cookies.get("sameSite", "None")

            await client.send("Network.setCookie", {
                "name": cookie_name,
                "value": cookie_value,
                "domain": domain,
                "path": path,
                "secure": secure,
                "httpOnly": httpOnly,
                "sameSite": sameSite
            })

            await asyncio.sleep(1)
            await playwright.stop()
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: An error occurred while modifying server-side cookies: {e}")

    async def setup_playwright(self):
        """Connect Playwright to browser and return essential objects."""
        capabilities = self.driver.capabilities
        debugger_address = None

        # Try to find debugger address in different browser capabilities
        if 'goog:chromeOptions' in capabilities:
            debugger_address = capabilities['goog:chromeOptions']['debuggerAddress']
        elif 'ms:edgeOptions' in capabilities:
            debugger_address = capabilities['ms:edgeOptions']['debuggerAddress']
        else:
            for key in capabilities:
                if isinstance(capabilities[key], dict) and 'debuggerAddress' in capabilities[key]:
                    debugger_address = capabilities[key]['debuggerAddress']
                    break

        if not debugger_address:
            raise ValueError("Could not find browser debugger address")

        try:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.connect_over_cdp(f"http://{debugger_address}")

            # Directly get the first context and page
            context = browser.contexts[0]
            page = context.pages[0]
            client = await context.new_cdp_session(page)

            logging.info(f"{self.__class__.__name__}: Connected to page: {page.url}")
            return playwright, browser, page, client

        except Exception as e:
            if 'playwright' in locals():
                await playwright.stop()
            logging.error(f"{self.__class__.__name__}: Failed to set up Playwright: {e}")
            raise
