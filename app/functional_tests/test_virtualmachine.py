import unittest, time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from app.functional_tests.base_functional_test import FunctionalTestCaseBase


class VirtualMachineFunctionalTestCase(FunctionalTestCaseBase):

    def test_virtual_machine(self):
        self.login()
        self._test_show_project_list_and_click_project(self.driver)
        self._test_add_and_remove_filter(self.driver)
        self._test_search(self.driver)
        self._test_pagination(self.driver)
        self._test_clipboard_button(self.driver)

    def _test_show_project_list_and_click_project(self, driver):
        self.wait_for(lambda: self.is_element_present(By.LINK_TEXT, self.project_name))
        driver.find_element_by_link_text(self.project_name).click()
        self.wait_for(lambda: driver.find_element_by_xpath(PageElements.PAGE_CONTENT_PATH).is_displayed())
        self.assertEqual("%s Instances" % self.project_name, driver.find_element_by_css_selector(PageElements.MAIN_HEADING_CLASS).text)

    def _test_add_and_remove_filter(self, driver):
        all_instances_count = driver.find_element_by_id(PageElements.TABLE_INFO_ID).text
        driver.find_element_by_xpath(PageElements.OFFERING_FILTER_PATH).click()
        self.wait_for(lambda: driver.find_element_by_css_selector(PageElements.SUCCESS_NOTIFICATION_CLASS).is_displayed())
        self.assertEqual("Filtering instances by Compute Offering.", driver.find_element_by_css_selector(PageElements.SUCCESS_NOTIFICATION_CLASS).text)
        filtered_instances_count = driver.find_element_by_id(PageElements.TABLE_INFO_ID).text
        self.assertNotEqual(all_instances_count, filtered_instances_count)

        time.sleep(5)  # wait for previous success messages to be cleared out
        driver.find_element_by_xpath(PageElements.CLEAR_FILTER_BUTTON_PATH).click()
        self.wait_for(lambda: driver.find_element_by_css_selector(PageElements.SUCCESS_NOTIFICATION_CLASS).is_displayed())
        self.assertEqual("Removing filters", driver.find_element_by_css_selector(PageElements.SUCCESS_NOTIFICATION_CLASS).text)

        driver.find_element_by_xpath(PageElements.OFFERING_FILTER_PATH).click()
        driver.find_element_by_xpath(PageElements.OFFERING_FILTER_PATH).click()
        self.wait_for(lambda: driver.find_element_by_css_selector(PageElements.SUCCESS_NOTIFICATION_CLASS).is_displayed())
        self.assertEqual("Compute Offering filter removed.", driver.find_element_by_css_selector(PageElements.SUCCESS_NOTIFICATION_CLASS).text)

    def _test_search(self, driver):
        driver.find_element_by_css_selector(PageElements.SEARCH_FIELD_CLASS).clear()
        driver.find_element_by_css_selector(PageElements.SEARCH_FIELD_CLASS).send_keys("SELENIUM TEST")
        driver.find_element_by_css_selector(PageElements.SEARCH_FIELD_CLASS).send_keys(Keys.ENTER)
        searched_instances = driver.find_element_by_id(PageElements.TABLE_INFO_ID).text

        self.assertTrue('Showing 0 to 0 of 0 entries' in searched_instances)

        driver.find_element_by_css_selector(PageElements.SEARCH_FIELD_CLASS).clear()
        driver.find_element_by_css_selector(PageElements.SEARCH_FIELD_CLASS).send_keys(Keys.ENTER)

    def _test_pagination(self, driver):
        driver.find_element_by_link_text("2").click()
        searched_instances = driver.find_element_by_id(PageElements.TABLE_INFO_ID).text
        self.assertTrue('Showing 11 to 20' in searched_instances)

    def _test_clipboard_button(self, driver):
        time.sleep(5)
        driver.find_element_by_xpath(PageElements.COPY_CLIPBOARD_BUTTON_PATH).click()
        self.assertEqual("Copy to clipboard",driver.find_element_by_css_selector(PageElements.CLIPBOARD_COPY_BOX_CLASS).text)


class PageElements():

    PAGE_CONTENT_PATH = '//*[@id="page-wrapper"]/div[2]/div/div[2]/div[2]'
    OFFERING_FILTER_PATH = '//*[@id="page-wrapper"]/div[2]/div/div[2]/div[2]/div[1]/div[1]/div/div[2]/table/tbody/tr[1]/td[1]/a'
    COPY_CLIPBOARD_BUTTON_PATH = "//div[@id='DataTables_Table_2_wrapper']/div/div/a/span"
    CLEAR_FILTER_BUTTON_PATH = '//*[@id="page-wrapper"]/div[2]/div/div[2]/div[2]/div[3]/div/div/div[1]/div/a[1]'
    TABLE_INFO_ID = "DataTables_Table_2_info"
    MAIN_HEADING_CLASS = "h2.ng-binding"
    SUCCESS_NOTIFICATION_CLASS = "div.toast.toast-success"
    SEARCH_FIELD_CLASS = "input.form-control.input-sm"
    CLIPBOARD_COPY_BOX_CLASS = "#datatables_buttons_info > h2"

