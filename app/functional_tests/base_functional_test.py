import unittest, time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException


class FunctionalTestCaseBase(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://iaas-usage.dev.globoi.com"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.driver.maximize_window()
        self.project_name = "DBaaS"

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True

    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True

    def login(self):
        self.driver.get(self.base_url + "/logout")
        self.driver.find_element_by_id("email").clear()
        self.driver.find_element_by_id("email").send_keys("victor.eduardo@corp.globo.com")
        self.driver.find_element_by_id("password").clear()
        self.driver.find_element_by_id("password").send_keys("g)o!0(E2,'2=&{R")
        self.driver.find_element_by_xpath("//*[@id=\"login-form\"]/button").click()

    def wait_for(self, func):
        for i in range(60):
            try:
                if func() : break
            except: pass
            time.sleep(1)
        else: self.fail("time out")