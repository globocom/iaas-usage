from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from app.functional_tests.base_functional_test import FunctionalTestCaseBase


class UsageFunctionalTestCase(FunctionalTestCaseBase):

    def test_usage(self):
        driver = self.driver
        self.login()
        self._test_open_usage_report(driver)
        self._test_search(driver)
        self._test_pagination(driver)
        self._test_clipboard_button(driver)
        self._test_calendar_controls_are_present(driver)

    def _test_open_usage_report(self, driver):
        self.wait_for(lambda: self.is_element_present(By.LINK_TEXT, "Resource Usage"))
        driver.find_element_by_link_text("Resource Usage").click()
        self.wait_for(lambda: driver.find_element_by_xpath("//*[@id=\"DataTables_Table_2_wrapper\"]").is_displayed())
        self.assertEqual("Resource Usage", driver.find_element_by_css_selector(PageElements.MAIN_HEADING_CLASS).text)

    def _test_search(self, driver):
        self.assertTrue(self.is_element_present(By.CSS_SELECTOR, "#reportrange > span"))
        self.wait_for(lambda: driver.find_element_by_xpath("//*[@id=\"DataTables_Table_2\"]").is_displayed())
        driver.find_element_by_css_selector(PageElements.SEARCH_FIELD_CLASS).clear()
        driver.find_element_by_css_selector(PageElements.SEARCH_FIELD_CLASS).send_keys("SELENIUM TEST")
        driver.find_element_by_css_selector(PageElements.SEARCH_FIELD_CLASS).send_keys(Keys.ENTER)
        searched_records = driver.find_element_by_id("DataTables_Table_2_info").text
        self.assertTrue('Showing 0 to 0 of 0 entries' in searched_records)
        driver.find_element_by_css_selector(PageElements.SEARCH_FIELD_CLASS).clear()
        driver.find_element_by_css_selector(PageElements.SEARCH_FIELD_CLASS).send_keys("")
        driver.find_element_by_css_selector(PageElements.SEARCH_FIELD_CLASS).send_keys(Keys.ENTER)

    def _test_pagination(self, driver):
        driver.find_element_by_link_text("2").click()
        searched_records = driver.find_element_by_id("DataTables_Table_2_info").text
        self.assertTrue('Showing 11 to 20' in searched_records)

    def _test_clipboard_button(self, driver):
        driver.find_element_by_xpath("//div[@id='DataTables_Table_2_wrapper']/div/div/a/span").click()
        self.assertEqual("Copy to clipboard", driver.find_element_by_css_selector("#datatables_buttons_info > h2").text)

    def _test_calendar_controls_are_present(self, driver):
        driver.find_element_by_css_selector("i.fa.fa-calendar").click()
        self.assertTrue(driver.find_element_by_xpath("//*[@class=\"calendar first right\"]").is_displayed())
        self.assertTrue(driver.find_element_by_xpath("//*[@class=\"calendar second left\"]").is_displayed())

class PageElements():

    SEARCH_FIELD_CLASS = "input.form-control.input-sm"
    MAIN_HEADING_CLASS = "h2.ng-binding"