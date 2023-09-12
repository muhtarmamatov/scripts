import requests
import json


workspace = "muktarbek_mamatov"
repo_slug = "productcatalog"
pull_request_id = 4
api_token = "ATCTT3xFfGN0t-0hSSEyU4RpyrnPk7GHdD2WBJL7cNFcM5EcLWpp_yoPspmNkg-Byo7tRNPHdxA-rxdqMWfKbGG2WusERZ2Sgtr0p_mpdEHw0PBUF0GShDxc0OvsjG7tNQm46PAjMxIk78GwrGwXA2ycZRiO7wXelzFqPP70qrdSJ_rPAEVnIAc=D3F6AB0B"

url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}"

headers = {
  "Accept": "application/json",
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_token}"
}

payload = json.dumps( {
    "reviewers": [
        {
            "uuid": "{65505616-11ce-4695-aeb2-1d410333529d}"
        },
        {
            "uuid": "{b55e6f61-a17e-4aa2-a1e5-2ec5a01f9df8}" 
        }
    ]
})


response = requests.request(
   "PUT",
   url,
   data=payload,
   headers=headers
)

if response.status_code == 200:
    print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
    print("Successfully added reviewers")
else:
    print("Failed to update reviewers ",response.status_code, response.text)
