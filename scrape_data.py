import pandas as pd
import requests
import math
import sys
from multiprocessing import Pool
from itertools import chain
import random
from time import sleep
site = "https://mirai.badpackets.net"

#User agent from https://www.scrapehero.com/how-to-fake-and-rotate-user-agents-using-python-3/ :)
user_agent_list = [
   #Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
]

hdr = {'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36'
        }
        
def parse(page):
    sleep(1)
    rows = []
    try:
        user_agent = random.choice(user_agent_list)
        headers = {'User-Agent': user_agent}
        r = requests.get("{}/?page={}".format(site, page),headers=headers)
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
            except Exception as e:
                print("page {} row {} failed {}".format(page, row, e))
        print("page {} done".format(page))
        sys.stdout.flush()
    except Exception as e:
        print("page {} failed {}".format(page, e))
    return rows
            

if __name__ == '__main__':
    #Get number of pages on website
    r = requests.get(site,headers=hdr)
    text = r.text
    records = int(text.split("Total Records: ")[1].split('<')[0])
    pages = math.ceil(records/25)
    
    print("Pages: {}".format(pages))
    sys.stdout.flush()

    rows = []
    with Pool(5) as p:
        records = p.map(parse, range(1000, 2000+1))
        
    print("Done pool")
    sys.stdout.flush()
    columns = ["IP_Address","Autonomous_System","Country","ASN","Date_First_Seen"]
    df = pd.DataFrame(list(chain(*records)), columns=columns)
    df.to_csv("mirai.csv", index=False)