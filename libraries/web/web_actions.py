from libraries.web.web_action.alert_actions import AlertActions
from libraries.web.web_action.element_actions import ElementActions
from libraries.web.web_action.navigation_actions import NavigationActions
from libraries.web.web_action.cookie_actions import CookieActions
from libraries.web.web_action.window_actions import WindowActions
from libraries.web.web_action.javascript_actions import JavaScriptActions
from libraries.web.web_action.utils_actions import UtilsActions
from libraries.web.web_action.table_actions import TableActions
from libraries.web.web_action.verification_actions import VerificationActions
from libraries.web.web_action.wait_actions import WaitActions


class WebElementActions(
                        ElementActions,
                        VerificationActions,
                        WaitActions,
                        WindowActions,
                        JavaScriptActions,
                        TableActions,
                        NavigationActions,
                        CookieActions,
                        AlertActions,
                        UtilsActions):
    pass
