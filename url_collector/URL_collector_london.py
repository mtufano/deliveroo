import requests
from bs4 import BeautifulSoup
import os

london_list = {
'https://deliveroo.co.uk/restaurants/london/becontree-heath/?geohash=u10j711s4yd6&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/barnet/?geohash=gcpvgef53um1&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/bexley/?geohash=u10hes27k4d8&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/wembley-park/?geohash=gcpv3gd95vv7&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/bromley/?geohash=u10h2q1tf99g&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/belsize-park/?geohash=gcpvhr96nswy&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/croydon/?geohash=gcpumbfk6q0t&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/ealing/?geohash=gcpv11dqkyrr&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/enfield/?geohash=gcpvy5j0rq2z&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/new-charlton/?geohash=u10hbnp4sg7m&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/hackney/?geohash=gcpvnxpxmyxj&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/hammersmith/?geohash=gcpufz15s2m6&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/harringay/?geohash=gcpvmrz1n4yp&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/west-harrow/?geohash=gcpv2jyywcn5&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/gidea-park/?geohash=u10jkv6rjvum&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/hillingdon/?geohash=gcptjv9wjwkn&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/hounslow-central/?geohash=gcpsz80m8gpg&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/upper-street/?geohash=gcpvjwm45z2c&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/kensington/?geohash=gcpugx4ggs3m&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/kingston/?geohash=gcpu3pm492yn&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/lambeth/?geohash=gcpuvq45qjdm&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/lewisham/?geohash=gcpuzb4wvmzd&collection=restaurants&collection=all-restaurants',
"https://deliveroo.co.uk/restaurants/london/st-james's/?fulfillment_method=DELIVERY&geohash=gcpvj0e5712f&collection=restaurants&collection=all-restaurants",
'https://deliveroo.co.uk/restaurants/london/wimbledon/?geohash=gcpu7ny7xu9b&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/newham/?geohash=u10j0gctus7h&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/barkingside/?geohash=u10j3zkj2n2d&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/richmond/?fulfillment_method=DELIVERY&geohash=gcpuc04zcdeu&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/bermondsey-spa/?geohash=gcpuym07wmw8&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/sutton-and-west-sutton/?fulfillment_method=DELIVERY&geohash=gcpu5w4f02h5&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/mile-end-east/?geohash=gcpvp6fxk2dy&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/walthamstow/?geohash=gcpvrxrmtgjn&collection=restaurants&collection=all-restaurants',
'https://deliveroo.co.uk/restaurants/london/wandsworth/?geohash=gcpuexwq8zfr&collection=restaurants&collection=all-restaurants'
}


class URLCollector:

    def __init__(self, city_list):
        self.__list = city_list
        self.__dir = './data'
        self.__failed_links = []

    def create_directory(self):
        if not os.path.exists(self.__dir):
            os.makedirs(self.__dir)
        self.collect_urls()
        self.log_failed_links()

    def collect_urls(self):
        all_urls = []
        for link in self.__list:
            try:
                reqs = requests.get(link)
                soup = BeautifulSoup(reqs.text, 'html.parser')

                for a_tag in soup.find_all('a'):
                    href = a_tag.get('href')
                    if href and href.startswith('/menu/'):
                        modified_href = 'https://deliveroo.co.uk' + href
                        all_urls.append(modified_href)
            except Exception as e:
                print(f"Failed to process {link}: {e}")
                self.__failed_links.append(link)

        # Write all URLs to a single file
        with open(os.path.join(self.__dir, "london_rest_links_deliveroo.txt"), "w") as f:
            for url in all_urls:
                f.write(url + "\n")

    def log_failed_links(self):
        if self.__failed_links:
            with open(os.path.join(self.__dir, "failed_links.txt"), "w") as f:
                for link in self.__failed_links:
                    f.write(link + "\n")

# Usage
url_collector = URLCollector(london_list)
url_collector.create_directory()