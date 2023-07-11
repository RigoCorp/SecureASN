#!/usr/bin/env python3

from collections import namedtuple
from csv import DictReader
from io import StringIO
import requests
import sys

# Step 1 - read list of secure AS from the .txt file
AS = namedtuple('AS', ['name', 'asns'])
wanted_as = dict()
with open('secure-as.txt') as as_file:
	for system in DictReader(as_file, delimiter=';', skipinitialspace=True):
		wanted_as[system['company']] = AS(system['name'], [])

# Step 2 - find all numbers for each company
as_list = requests.get('https://raw.githubusercontent.com/ipverse/asn-info/master/as.csv').text
for entry in DictReader(StringIO(as_list)):
	match = wanted_as.get(entry['description'])
	if match is not None:
		match.asns.append(int(entry['asn']))

# Fetch IPs for each one
with \
		open('ipv4-whitelist.txt', 'w') as ipv4_file, \
		open('ipv6-whitelist.txt', 'w') as ipv6_file:
	for system in wanted_as.values():
		print(system.name)
		for file in [ipv4_file, ipv6_file]:
			file.write(f'#\n')
			file.write(f'# {system.name}\n')
			file.write(f'#\n')

		for asn in system.asns:
			print(f' - {asn}')

			# Fetch AS information from IPverse AS IP repo
			system_info = requests.get(f"https://raw.githubusercontent.com/ipverse/asn-ip/master/as/{asn}/aggregated.json")
			if system_info.status_code == 200:
				system_info = system_info.json()

				for file, ipver in [(ipv4_file, 'ipv4'), (ipv6_file, 'ipv6')]:
					file.write(f"# ASN {asn}\n")

					ip_list = '\n'.join(system_info['subnets'][ipver])
					if ip_list != '':
						file.write(ip_list)
					else:
						file.write('# (none)')

					file.write('\n\n')
			elif system_info.status_code != 404:
				system_info.raise_for_status()
