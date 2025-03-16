import logging
from playwright.async_api import async_playwright
from .base import Base
from .request_interceptor import RequestInterceptor


class InterceptorActions(Base):
    async def modify_server_side_cookie(self, url,intercept_url_pattern, cookie):
        try:
            playwright, browser, page = await self.setup_playwright()
            interceptor = RequestInterceptor()
            cookie_name = cookie.get("name")
            cookie_value = cookie.get("value")
            await interceptor.modify_cookie(page, intercept_url_pattern, cookie_name, cookie_value, exact_match=True)

            # Navigate to the target site to trigger interception
            await page.goto(url)
            logging.info(f"{self.__class__.__name__}: Navigating to {url} to trigger interception.")

            cookie_value = self.driver.get_cookie(cookie_name)["value"]
            logging.info(f"{self.__class__.__name__}: {cookie_name} value after triggering interception: {cookie_value}")
            await interceptor.stop()
            # await playwright.stop()
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: An error occurred while modifying server-side cookie: {e}")

    async def setup_playwright(self):
        # Get debugger address
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
            raise ValueError("Could not find debugger address in browser capabilities")

        # Connect Playwright to the browser
        playwright = await async_playwright().start()
        browser = await playwright.chromium.connect_over_cdp(f"http://{debugger_address}")
        # Get first context and page
        contexts = browser.contexts
        if not contexts:
            await playwright.stop()
            raise ValueError("No browser contexts found")

        pages = contexts[0].pages
        if not pages:
            await playwright.stop()
            raise ValueError("No pages found in browser context")

        page = pages[0]
        logging.info(f"{self.__class__.__name__}: Successfully connected to page: {page.url}.")

        return playwright, browser, page
