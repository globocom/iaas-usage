from selenium.webdriver.common.by import By
from app.functional_tests.base_functional_test import FunctionalTestCaseBase


class CapacityFunctionalTestCase(FunctionalTestCaseBase):

    def test_resource(self):
        driver = self.driver
        self.login()
        self._test_menu_link_present(driver)
        self._test_page_heading_present(driver)
        self._test_capacity_bars_present(driver)

    def _test_menu_link_present(self, driver):
        self.wait_for(lambda: self.is_element_present(By.LINK_TEXT, "Cloud Capacity"))
        driver.find_element_by_link_text("Cloud Capacity").click()

    def _test_page_heading_present(self, driver):
        self.wait_for(lambda: self.is_element_present(By.XPATH, PageElements.CAPACITY_CONTEXT_PATH))
        self.assertEqual("Cloud Capacity by Zone", driver.find_element_by_css_selector(PageElements.MAIN_HEADING_CLASS).text)

    def _test_capacity_bars_present(self, driver):
        self.wait_for(lambda: self.is_element_present(By.XPATH, PageElements.PROGRESS_BAR_PATH))
        resource_type_count = len(driver.find_elements_by_xpath(PageElements.ZONE_PROGRESS_BARS_PATH))
        self.assertEqual(resource_type_count, 4)

class PageElements():

    CAPACITY_CONTEXT_PATH = '//div[@ng-controller="CapacityCtrl as capacityCtrl"]'
    PROGRESS_BAR_PATH = '//div[@class="progress-bar"]'
    ZONE_PROGRESS_BARS_PATH = '(//div[@class="ibox-content"])[1]/div'
    MAIN_HEADING_CLASS = "h2.ng-binding"

