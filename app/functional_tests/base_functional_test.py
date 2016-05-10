import os
import unittest, time
from sys import platform as _platform
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
from selenium.webdriver import FirefoxProfile


class FunctionalTestCaseBase(unittest.TestCase):

    def setUp(self):
        if _platform != "darwin":
            self.display = Display(visible=0, size=(1280, 800))
            self.display.start()

        p = FirefoxProfile()
        p.set_preference("webdriver.log.file", "/tmp/firefox_console")

        self.driver = webdriver.Firefox(p)
        self.base_url = os.getenv('SELENIUM_BASE_URL')
        self.verificationErrors = []
        self.accept_next_alert = True
        self.driver.set_window_size(1280, 800)
        self.project_name = "DBaaS"

    def tearDown(self):
        self.driver.save_screenshot('selenium_fails/%s_screen.png' % os.path.basename(self.__class__.__name__))
        self.driver.quit()
        self.display.stop()
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
        self.driver.find_element_by_id("email").send_keys(os.getenv('SELENIUM_USER'))
        self.driver.find_element_by_id("password").clear()
        self.driver.find_element_by_id("password").send_keys(os.getenv('SELENIUM_PASSWORD'))
        self.driver.find_element_by_xpath("//*[@id=\"login-form\"]/button").click()

    def wait_for(self, func):
        for i in range(60):
            try:
                if func() : break
            except: pass
            time.sleep(1)
        else: self.fail("time out")