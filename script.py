

from labcontrol.lab_aws_http import LabAWSHttpApi
from labcontrol.parser import load_netscape_cookies


cookies_path= r"C:\Users\Leo\Downloads\awsacademy.instructure.com_cookies.txt"
cookies= load_netscape_cookies(cookies_path)
api= LabAWSHttpApi()
if api.is_valid_cookie(cookies):
    print("Cookie is valid")

