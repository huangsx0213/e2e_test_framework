import re

class RequestInterceptor:
    def __init__(self):
        self.page = None
        self.active = False
        self.routes = []

    async def modify_cookie(self, page, url_pattern, cookie_name, new_cookie_value, exact_match=False):
        """
        Intercept requests and modify the specified cookie in the response header.
        """
        if self.active:
            print("Interception is already active. Please stop the current interception before starting a new one.")
            return False

        self.page = page
        self.active = True
        url_pattern_lower = url_pattern.lower()
        pattern = None if exact_match else re.compile(url_pattern_lower)

        async def handler(route):
            request_url = route.request.url.lower()
            match = (request_url == url_pattern_lower) if exact_match else (pattern.search(request_url) is not None)
            if match:
                print(f"Intercepted request: {request_url}")
                response = await route.fetch()
                body = await response.body()
                status = response.status
                headers = response.headers.copy()
                modified = False

                if "set-cookie" in headers:
                    cookies = headers["set-cookie"].split(", ")
                    new_cookies = []
                    for group in cookies:
                        parts = group.split("; ")
                        new_parts = []
                        for cookie in parts:
                            if cookie.startswith(f"{cookie_name}="):
                                new_parts.append(f"{cookie_name}={new_cookie_value}")
                                modified = True
                                print(f"Modified cookie: {cookie_name}={new_cookie_value}")
                            else:
                                new_parts.append(cookie)
                        new_cookies.append("; ".join(new_parts))
                    headers["set-cookie"] = ", ".join(new_cookies)

                if not modified:
                    print(f"Target cookie '{cookie_name}' not found.")
                await route.fulfill(status=status, headers=headers, body=body)
            else:
                await route.continue_()

        handler_info = {"pattern": "**", "handler": handler}
        self.routes.append(handler_info)
        await self.page.route("**", handler)
        print(f"Cookie interception started using {'exact' if exact_match else 'regex'} match for pattern: {url_pattern}")
        return True

    async def modify_body(self, page, url_pattern, new_body, exact_match=False):
        """
        Intercept requests and replace the response body with a new body.

        Parameters:
        - page: Playwright page object.
        - url_pattern: URL pattern to match.
        - new_body: The new response body (bytes) to set.
        - exact_match: If True, perform an exact URL match; otherwise use regex matching.
        """
        if self.active:
            print("Interception is already active. Please stop the current interception before starting a new one.")
            return False

        self.page = page
        self.active = True
        url_pattern_lower = url_pattern.lower()
        pattern = None if exact_match else re.compile(url_pattern_lower)

        async def handler(route):
            request_url = route.request.url.lower()
            match = (request_url == url_pattern_lower) if exact_match else (pattern.search(request_url) is not None)
            if match:
                print(f"Intercepted request for body modification: {request_url}")
                response = await route.fetch()
                status = response.status
                headers = response.headers.copy()
                print("Response body replaced.")
                await route.fulfill(status=status, headers=headers, body=new_body)
            else:
                await route.continue_()

        handler_info = {"pattern": "**", "handler": handler}
        self.routes.append(handler_info)
        await self.page.route("**", handler)
        print(f"Body interception started using {'exact' if exact_match else 'regex'} match for pattern: {url_pattern}")
        return True

    async def modify_header(self, page, url_pattern, header_mods, exact_match=False):
        """
        Intercept requests and modify the response headers.

        Parameters:
        - page: Playwright page object.
        - url_pattern: URL pattern to match.
        - header_mods: Dictionary of headers to modify or add.
        - exact_match: If True, perform an exact URL match; otherwise use regex matching.
        """
        if self.active:
            print("Interception is already active. Please stop the current interception before starting a new one.")
            return False

        self.page = page
        self.active = True
        url_pattern_lower = url_pattern.lower()
        pattern = None if exact_match else re.compile(url_pattern_lower)

        async def handler(route):
            request_url = route.request.url.lower()
            match = (request_url == url_pattern_lower) if exact_match else (pattern.search(request_url) is not None)
            if match:
                print(f"Intercepted request for header modification: {request_url}")
                response = await route.fetch()
                body = await response.body()
                status = response.status
                headers = response.headers.copy()
                for key, value in header_mods.items():
                    headers[key] = value
                    print(f"Modified header: {key} => {value}")
                await route.fulfill(status=status, headers=headers, body=body)
            else:
                await route.continue_()

        handler_info = {"pattern": "**", "handler": handler}
        self.routes.append(handler_info)
        await self.page.route("**", handler)
        print(f"Header interception started using {'exact' if exact_match else 'regex'} match for pattern: {url_pattern}")
        return True

    async def stop(self):
        """
        Stop all active interceptions.
        """
        try:
            if not self.active or not self.page:
                print("No active interception to stop.")
                return False

            for r in self.routes:
                await self.page.unroute(r["pattern"], r["handler"])
            self.routes = []
            self.active = False

            print("All interceptions stopped.")
            return True
        except Exception as e:
            print(f"Error stopping interception: {e}")
            return False
