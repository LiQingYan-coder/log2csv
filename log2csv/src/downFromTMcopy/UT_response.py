import requests
from lxml import etree


def list_directory(url):
    response = requests.get(url)
    print(response.text)





if __name__ == "__main__":
    url = "file:///C:/Users/test/Desktop/logs/gaunghua4485/20240829115511_LTEDyn_B7_fail/mje/testData-beans-original/beans2/"
    list_directory(url)