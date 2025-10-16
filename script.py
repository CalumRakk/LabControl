from datetime import datetime, timedelta
import re
from typing_extensions import cast
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from labcontrol.api.browser.actions_lab_aws import get_course_id, get_lab_item_id, get_lab_item_id, set_cookies_on_driver, switch_to_iframe
from labcontrol.api.lab_aws_browser import LabAWSBrowserAPI
from labcontrol.api.lab_aws_http import LabAWSHttpApi, logger
from labcontrol.api.browser.driver import DriverManager
from labcontrol.api.parser import load_netscape_cookies
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from lxml import html
from datetime import timedelta
import requests


cookies_path= r"C:\Users\Leo\Downloads\awsacademy.instructure.com_cookies.txt"
cookies= load_netscape_cookies(cookies_path)
api= LabAWSHttpApi()
if api.is_valid_cookie(cookies):
    print("Cookie is valid")

