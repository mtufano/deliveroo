import requests
from bs4 import BeautifulSoup
import os

london_dict = {
    "Barking and Dagenham": "https://deliveroo.co.uk/restaurants/london/becontree-heath/?geohash=u10j711s4yd6&collection=restaurants&collection=all-restaurants&collection=all-restaurants",
    "Barnet": "https://deliveroo.co.uk/restaurants/london/barnet/?geohash=gcpvgef53um1&collection=restaurants&collection=all-restaurants",
    "Bexley": "https://deliveroo.co.uk/restaurants/london/bexley/?geohash=u10hes27k4d8&collection=restaurants&collection=all-restaurants",
    "Brent": "https://deliveroo.co.uk/restaurants/london/wembley-park/?geohash=gcpv3gd95vv7&collection=restaurants&collection=all-restaurants",
    "Bromley": "https://deliveroo.co.uk/restaurants/london/bromley/?geohash=u10h2q1tf99g&collection=restaurants&collection=all-restaurants",
    "Camden": "https://deliveroo.co.uk/restaurants/london/belsize-park/?geohash=gcpvhr96nswy&collection=restaurants&collection=all-restaurants",
    "Croydon": "https://deliveroo.co.uk/restaurants/london/croydon/?geohash=gcpumbfk6q0t&collection=restaurants&collection=all-restaurants",
    "Ealing": "https://deliveroo.co.uk/restaurants/london/ealing/?geohash=gcpv11dqkyrr&collection=restaurants&collection=all-restaurants",
    "Enfield": "https://deliveroo.co.uk/restaurants/london/enfield/?geohash=gcpvy5j0rq2z&collection=restaurants&collection=all-restaurants",
    "Greenwich": "https://deliveroo.co.uk/restaurants/london/new-charlton/?geohash=u10hbnp4sg7m&collection=restaurants&collection=all-restaurants",
    "Hackney": "https://deliveroo.co.uk/restaurants/london/hackney/?geohash=gcpvnxpxmyxj&collection=restaurants&collection=all-restaurants",
    "Hammersmith and Fulham": "https://deliveroo.co.uk/restaurants/london/hammersmith/?geohash=gcpufz15s2m6&collection=restaurants&collection=all-restaurants",
    "Haringey": "https://deliveroo.co.uk/restaurants/london/harringay/?geohash=gcpvmrz1n4yp&collection=restaurants&collection=all-restaurants",
    "Harrow": "https://deliveroo.co.uk/restaurants/london/west-harrow/?geohash=gcpv2jyywcn5&collection=restaurants&collection=all-restaurants",
    "Havering": "https://deliveroo.co.uk/restaurants/london/gidea-park/?geohash=u10jkv6rjvum&collection=restaurants&collection=all-restaurants",
    "Hillingdon": "https://deliveroo.co.uk/restaurants/london/hillingdon/?geohash=gcptjv9wjwkn&collection=restaurants&collection=all-restaurants",
    "Hounslow": "https://deliveroo.co.uk/restaurants/london/hounslow-central/?geohash=gcpsz80m8gpg&collection=restaurants&collection=all-restaurants",
    "Islington": "https://deliveroo.co.uk/restaurants/london/upper-street/?geohash=gcpvjwm45z2c&collection=restaurants&collection=all-restaurants",
    "Kensington and Chelsea": "https://deliveroo.co.uk/restaurants/london/kensington/?geohash=gcpugx4ggs3m&collection=restaurants&collection=all-restaurants",
    "Kingston upon Thames": "https://deliveroo.co.uk/restaurants/london/kingston/?geohash=gcpu3pm492yn&collection=restaurants&collection=all-restaurants",
    "Lambeth": "https://deliveroo.co.uk/restaurants/london/lambeth/?geohash=gcpuvq45qjdm&collection=restaurants&collection=all-restaurants",
    "Lewisham": "https://deliveroo.co.uk/restaurants/london/lewisham/?geohash=gcpuzb4wvmzd&collection=restaurants&collection=all-restaurants",
    "London region": "https://deliveroo.co.uk/restaurants/london/st-james's/?fulfillment_method=DELIVERY&geohash=gcpvj0e5712f&collection=restaurants&collection=all-restaurants",
    "Merton": "https://deliveroo.co.uk/restaurants/london/wimbledon/?geohash=gcpu7ny7xu9b&collection=restaurants&collection=all-restaurants",
    "Newham": "https://deliveroo.co.uk/restaurants/london/newham/?geohash=u10j0gctus7h&collection=restaurants&collection=all-restaurants",
    "Redbridge": "https://deliveroo.co.uk/restaurants/london/barkingside/?geohash=u10j3zkj2n2d&collection=restaurants&collection=all-restaurants",
    "Richmond upon Thames": "https://deliveroo.co.uk/restaurants/london/richmond/?fulfillment_method=DELIVERY&geohash=gcpuc04zcdeu&collection=restaurants&collection=all-restaurants",
    "Southwark": "https://deliveroo.co.uk/restaurants/london/bermondsey-spa/?geohash=gcpuym07wmw8&collection=restaurants&collection=all-restaurants",
    "Sutton": "https://deliveroo.co.uk/restaurants/london/sutton-and-west-sutton/?fulfillment_method=DELIVERY&geohash=gcpu5w4f02h5&collection=restaurants&collection=all-restaurants",
    "Tower Hamlets": "https://deliveroo.co.uk/restaurants/london/mile-end-east/?geohash=gcpvp6fxk2dy&collection=restaurants&collection=all-restaurants",
    "Waltham Forest": "https://deliveroo.co.uk/restaurants/london/walthamstow/?geohash=gcpvrxrmtgjn&collection=restaurants&collection=all-restaurants",
    "Wandsworth": "https://deliveroo.co.uk/restaurants/london/wandsworth/?geohash=gcpuexwq8zfr&collection=restaurants&collection=all-restaurants",
    "Westminster": "https://deliveroo.co.uk/restaurants/london/victoria/?geohash=gcpuuyv4wuvf&collection=restaurants&collection=all-restaurants"
}

class URLCollector:

    def __init__(self, city_dict):
        self.__dict = city_dict
        self.__dir = './data'

    def create_directory(self):
        for city, link in self.__dict.items():
            # Create a directory for the city if it doesn't exist
            self.__dir = self.__dir + f"/{city}"
            if not os.path.exists(self.__dir):
                os.makedirs(self.__dir)
            self.collect_urls()

    def collect_urls(self):
        for city, link in self.__dict.items():
            reqs = requests.get(link)
            soup = BeautifulSoup(reqs.text, 'html.parser')

            urls = []
            for a_tag in soup.find_all('a'):
                href = a_tag.get('href')
                if href and href.startswith('/menu/'):
                    modified_href = 'https://deliveroo.co.uk' + href + ','
                    urls.append(modified_href)

            # Write the URLs to urls.txt in the directory
            with open(os.path.join(self.__dir + f"/{city}_urls.txt"), "w") as f:
                for url in urls:
                    f.write(url + "\n")


# Create the directory for each city
url_c = URLCollector(london_dict)
url_c.create_directory()

# Collect and write the URLs for each city
#my_dict.collect_urls()