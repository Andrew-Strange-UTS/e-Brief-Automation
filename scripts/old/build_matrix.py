import os
import urllib.parse
import requests
import json
import yaml

sn_url = os.environ["SN_URL"]
username = os.environ["SN_USERNAME"]
password = os.environ["SN_PASSWORD"]

lists_yaml = os.environ["LISTS_YAML"]
lists = yaml.safe_load(lists_yaml)

matrix = []

def fetch_task_numbers(desc):
    query = f"active=true^state=1^short_description={desc}"
    encoded_query = urllib.parse.quote(query)
    url = f"{sn_url}/api/now/table/sc_task?sysparm_query={encoded_query}&sysparm_fields=number"
    r = requests.get(url, auth=(username, password), headers={"Accept": "application/json"})
    r.raise_for_status()
    return [x["number"] for x in r.json().get("result", [])]

for l in lists:
    for mode in ["add", "remove"]:
        desc = l.get(f"{mode}_desc")
        url = l.get(f"{mode}_url")
        password_secret = l.get("password_secret")
        task_nums = fetch_task_numbers(desc)
        for task_num in task_nums:
            matrix.append({
                "list": l["name"],
                "mode": mode,
                "url": url,
                "password_secret": password_secret,
                "task_num": task_num
            })

print(json.dumps(matrix))
