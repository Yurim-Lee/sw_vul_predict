import json

import requests

url = 'https://services.nvd.nist.gov/rest/json/cve/1.0/'
apiKey = "9e124ed3-052e-490a-83e4-e453999d7432"
# cve id로 검색
params = {'cveId': 'CVE-2021-42078', 'apiKey': apiKey}
res = requests.get(url, params=params)

url2 = "https://services.nvd.nist.gov/rest/json/cves/1.0/"
# cve 컬렉션 검색
params2 = {'apiKey': apiKey, 'keyword': 'reservation service'}
res2 = requests.get(url2, params=params2)

# print(res2.json())
a = res2.json()
print(json.dumps(a,indent=2))
