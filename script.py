from cloudAuto.paquetes.aws import Browser
from cloudAuto import Config
from cloudAuto.constants import ActionsInstance

config = Config()
browser = Browser()

browser.current_page

Browser.stop(browser)

browser = Browser()

us_west_oregon_url = config["aws"]["us_west_oregon_url"]
page_aws.goto(us_west_oregon_url)

instance_id = config["instance_id"]["server_double"]
status = browser.get_status_instance(page_aws, instance_id)
if status.is_off:
    browser.set_action_instance(page_aws, instance_id, ActionsInstance.Stop)

print()
