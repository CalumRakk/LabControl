from labcontrol.credentials import get_settings
from labcontrol.parser import load_vocareum_params
from labcontrol.vocareum_http import VocareumApi

lab_cookies_path = r"C:\Users\Leo\Downloads\awsacademy.instructure.com_cookies.txt"
vocareum_params_path = r"C:\Users\Leo\Downloads\vocareum_params.json"
credentials = get_settings(".env/labcontrol.env")


params = load_vocareum_params(vocareum_params_path)
vocareum_api = VocareumApi(params)

response = vocareum_api.get_aws_status()
print(response)
