from selenium.webdriver.common.by import By
from app.functional_tests.base_functional_test import FunctionalTestCaseBase


class QuotaFunctmionalTestCase(FunctionalTestCaseBase):

    def test_quota(self):
        driver = self.driver
        self.login()
        self._test_show_project_list_and_click_project(driver)
        self._test_progress_bars_are_present(driver)

    def _test_progress_bars_are_present(self, driver):
        resource_types_count = len(driver.find_elements_by_xpath(PageElements.CONTENT_AREA_PATH))
        self.assertEqual(resource_types_count, 8)

    def _test_show_project_list_and_click_project(self, driver):
        self.wait_for(lambda: self.is_element_present(By.LINK_TEXT, "Resource Quota"))
        driver.find_element_by_link_text("Resource Quota").click()

        self.assertEqual("Resource Quota by Project", driver.find_element_by_css_selector(PageElements.MAIN_HEADING_CLASS).text)
        self.wait_for(lambda: self.is_element_present(By.LINK_TEXT, self.project_name))
        driver.find_element_by_link_text(self.project_name).click()

        self.wait_for(lambda: driver.find_element_by_xpath(PageElements.PROGRESS_BAR_PATH).is_displayed())
        self.assertEqual("%s Resource Quota" % self.project_name, driver.find_element_by_css_selector(PageElements.MAIN_HEADING_CLASS).text)


class PageElements():

    CONTENT_AREA_PATH = "//*[@class='progress progress-small']"
    PROGRESS_BAR_PATH = '//*[@class="progress progress-small"]'
    MAIN_HEADING_CLASS = "h2.ng-binding"
