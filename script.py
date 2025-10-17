

from labcontrol.lab_aws_http import LabAWSHttpApi
from labcontrol.lab_aws_browser import LabAWSBrowserAPI
from labcontrol.parser import load_netscape_cookies


cookies_path= r"C:\Users\Leo\Downloads\awsacademy.instructure.com_cookies.txt"
cookies= load_netscape_cookies(cookies_path)
api= LabAWSBrowserAPI(cookies)
detail= api.get_lab_details()

print(detail)

