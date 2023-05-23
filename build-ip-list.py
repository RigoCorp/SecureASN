#!/usr/bin/env python3

import csv
import requests

with \
		open('secure-asn.tsv') as tsv_file, \
		open('ipv4-whitelist.txt', 'w') as ipv4_file, \
		open('ipv6-whitelist.txt', 'w') as ipv6_file:
	for system in csv.DictReader(tsv_file, dialect='excel-tab'):
		print(f"{system['asn']} - {system['name']}")

		# Fetch AS information from IPverse AS IP repo
		system_info = requests.get(f"https://raw.githubusercontent.com/ipverse/asn-ip/master/as/{system['asn']}/aggregated.json")
		system_info = system_info.json()

		for file, ipver in [(ipv4_file, 'ipv4'), (ipv6_file, 'ipv6')]:
			file.write(f"# AS {system['asn']} - {system['name']}\n")

			ip_list = '\n'.join(system_info['subnets'][ipver])
			if ip_list != '':
				file.write(ip_list)
			else:
				file.write('# (none)')

			file.write('\n\n')
