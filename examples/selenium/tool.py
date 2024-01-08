from agent_tools import Tool, action, observation
from selenium import webdriver


class SeleniumBrowser(Tool):
    """Selenium browser as a tool"""

    def __init__(self, headless: bool = True) -> None:
        super().__init__()
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

    @action
    def open_url(self, url: str) -> None:
        """Open a URL in the browser

        Args:
            url (str): URL to open
        """
        self.driver.get(url)
        self.take_screenshot()

    @action
    def click_element(self, selector: str, selector_type: str = "css_selector") -> None:
        """Click an element identified by a CSS selector

        Args:
            selector (str): CSS selector
            selector_type (str, optional): Selector type. Defaults to "css_selector".
        """
        element = self.driver.find_element(selector_type, selector)
        element.click()
        self.take_screenshot()

    @observation
    def get_html(self) -> str:
        """Get the entire HTML of the current page.

        Returns:
            str: Page HTML
        """
        return self.driver.page_source

    def close(self) -> None:
        self.driver.quit()
