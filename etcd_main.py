import time
import requests
import random
import etcd3


def check_service_resource(url):
    url = "http://" + url
    session = requests.Session()
    response = session.get(url, timeout=5)
    print(response.json()["ret"])
    if response.json()["ret"] == 0:
        return {"ret": 0, "url": url}
    else:
        print(response.json()["msg"])
        return {"ret": -1, "url": url}


def get_idle_service(c, service_name):
    url_dict = {"idle": [], "busy": []}
    r = c.get_prefix(service_name)
    for s in r:
        url = s[0].decode()
        r = check_service_resource(url)
        if (r["ret"] == 0):
            url_dict["idle"].append(r["url"])
        else:
            url_dict["busy"].append(r['url'])

    print(url_dict)
    leng = len(url_dict["idle"])
    if leng > 0:
        return url_dict["idle"][random.randint(0, leng-1)]
    else:
        print("resources are exhausted")
        return False


etcd_host = "172.16.81.1"
service_name = "/services"
c = etcd3.client(host=etcd_host, port=2379)

# node_url = get_idle_service(c, service_name)

while True:
    service_url = get_idle_service(c, service_name)
    if (service_url):
        print(service_url)
        session = requests.Session()
        try:
            response = session.get(service_url + "/?test=test", timeout=5)
            print(response.json()["ret"])
            if response.json()["ret"] == 0:
                print("task start")
            else:
                print(response.json()["msg"])
        except Exception as e:
            print(e)
            print("service", service_url, "is closed")
    time.sleep(5)
