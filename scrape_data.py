import pandas as pd
import requests
import math
import sys
site = "https://mirai.badpackets.net"

#User agent from https://www.scrapehero.com/how-to-fake-and-rotate-user-agents-using-python-3/ :)
hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }

#Get number of pages on website
r = requests.get(site,headers=hdr)
text = r.text
records = int(text.split("Total Records: ")[1].split('<')[0])
pages = math.ceil(records/25)

print("Pages: {}".format(pages))
sys.stdout.flush()

rows = []
for page in range(1, pages+1):
    r = requests.get("{}/?page={}".format(site, page),headers=hdr)
    table = r.text.split("<tbody >")[1].split("</tbody>")[0]
    count = table.count("<tr")
    for row in range(25):
        try:
            row_data = table.split("<tr")[row+1].split("</tr>")[0]
            split = row_data.split("\n")
            ip = split[2].split(">")[2].split("<")[0]
            AS = split[4].split(">")[1].split("<")[0]
            country = split[6].split(">")[1].split("<")[0]
            ASN = split[8].split(">")[2].split("<")[0]
            time = split[10].split(">")[1].split("<")[0][0:-4]
            rows.append([ip, AS, country, ASN, time])
        except:
            print("page {} row {} failed".format(page, row))
    if (page % 10 == 0):
        print(page)
        sys.stdout.flush()
    
columns = ["IP_Address","Autonomous_System","Country","ASN","Date_First_Seen"]
df = pd.DataFrame(rows, columns=columns)
df.to_csv("mirai.csv", index=False)