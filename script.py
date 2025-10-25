
from labcontrol.config import get_settings
from labcontrol.utils import get_params_with_config
from labcontrol.vocareum_http import VocareumApi

config = get_settings(".env/labcontrol.env")
params= get_params_with_config(config)
vocareum_api = VocareumApi(params)

result = vocareum_api.get_aws_status()

print(result)
