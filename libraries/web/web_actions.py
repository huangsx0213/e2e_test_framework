from libraries.web.web_action.alert_actions import AlertActions
from libraries.web.web_action.basic_actions import BasicActions
from libraries.web.web_action.browser_actions import BrowserActions
from libraries.web.web_action.cookie_actions import CookieActions
from libraries.web.web_action.frame_window_actions import FrameWindowActions
from libraries.web.web_action.javascript_actions import JavaScriptActions
from libraries.web.web_action.screenshot_actions import ScreenshotActions
from libraries.web.web_action.table_actions import TableActions
from libraries.web.web_action.verification_actions import VerificationActions
from libraries.web.web_action.wait_actions import WaitActions


class WebElementActions(
                        BasicActions,
                        VerificationActions,
                        WaitActions,
                        FrameWindowActions,
                        JavaScriptActions,
                        TableActions,
                        BrowserActions,
                        CookieActions,
                        AlertActions,
                        ScreenshotActions):
    pass
