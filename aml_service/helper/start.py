import os, json, sys
from azcli import az_login, az_account_set


# print('current dir is ' +os.curdir)
with open("aml_config/config.json") as f:
    config = json.load(f)

with open("aml_config/security_config.json") as f:
    security_config = json.load(f)

subscription_id = config["subscription_id"]
sp_user = security_config["sp_user"]
sp_password = security_config["sp_password"]
sp_tenant_id = security_config["sp_tenant_id"]



out, err = az_login(sp_user, sp_password, sp_tenant_id)
out, err = az_account_set(subscription_id)