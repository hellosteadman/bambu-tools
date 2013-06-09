from bambu.international.models import Country
from pygeoip import GeoIP, MEMORY_CACHE
from os import path
import threading, socket

def ip_to_country(ip_address):
	db = GeoIP(
		path.abspath(
			path.join(
				path.dirname(__file__),
				'fixtures',
				'geoip.dat'
			)
		),
		MEMORY_CACHE
	)
	
	return Country.objects.get(
		code = db.country_code_by_addr(ip_address)
	)

def domain_to_country(domain):
	ip_address = socket.gethostbyname(domain)
	return ip_to_country(ip_address)