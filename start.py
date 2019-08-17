import os, json, sys


# print('current dir is ' +os.curdir)
with open("aml_config/config.json") as f:
    config = json.load(f)


subscription_id = config["subscription_id"]
sp_user = config["sp_user"]
sp_password = config["sp_password"]
sp_tenant_id = config["sp_tenant_id"]

