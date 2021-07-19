import subprocess
import requests
import json
import pycountry_convert as pc
import random
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

import pathlib

vpn_log_path = pathlib.Path().absolute() / "Log" / "vpn.log"
file_handler = logging.FileHandler(vpn_log_path, 'w', 'utf-8')
# file_handler = logging.FileHandler(r'C:\Users\lucag\Documents\Thesis\datasets\project_gutenberg\goodreads\Log\vpn.log', 'w', 'utf-8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class NordVPNHelper():

    def __init__(self):
        self.servers_dict_by_cont = self.getServers()
        # self.pg = pg
        self.currIP = "47.153.29.66"
        pass

    def getContinentCodeFromCountryName(self, country):
        country_code = pc.country_name_to_country_alpha2(country, cn_name_format="default")
        return pc.country_alpha2_to_continent_code(country_code)

    # Append multiple value to a key in dictionary
    def add_values_in_dict(self, sample_dict, key, list_of_values):
        """Append multiple values to a key in the given dictionary"""
        if key not in sample_dict:
            sample_dict[key] = list()
        sample_dict[key].extend(list_of_values)
        return sample_dict

    def getServers(self):
        print("getting servers")
        servers = {}
        # URL = "https://api.nordvpn.com/server"
        # r = requests.get(url = URL)
        # data = r.json()
        with open('vpns.json') as f:
            data = json.load(f)
        for server in data:
            if server['load'] < 50:
                continent_name = self.getContinentCodeFromCountryName(server['country'])
                self.add_values_in_dict(servers, continent_name, [server['name']])
        return servers

    def chooseRandomServer(self, continentBased=True):
        return random.choice(self.servers_dict_by_cont.get('NA'))
        # country = self.mh.getCurrentCountry() # THIS MAY BE EMPTY FOR THE DUPLICATE COMPANIES FIXMEE
        # country = self.pg.getCurrentCountry()
        # logger.info("Current country is " + country)
        # continent_code = self.getContinentCodeFromCountryName(country)
        # if continent_code not in ['SA', 'AF', 'OC', 'AS', 'EU', 'NA']:
        #     return random.choice(self.servers_dict_by_cont.get('NA'))
        # else:
        #     return random.choice(self.servers_dict_by_cont.get(continent_code))

    def checkForIPChange(self):
        newIP = self.currIP
        ipify_attempts = 0
        URL = "https://checkip.amazonaws.com/"
        while newIP == self.currIP and ipify_attempts < 3:
            time.sleep(5)
            logger.info("Check if ip changed from " + str(self.currIP) + "; iteration " + str(ipify_attempts+1))
            try:
                r = requests.get(url = URL)
                if(r.status_code != 200):
                    logger.info(URL + " returned a status code of " + str(r.status_code))
                else:
                    newIP = r.text.strip()
                    logger.info("IP retrieved, IP is " + newIP)
            except requests.exceptions.RequestException as e:
                logger.info(URL + " exception raised")
            ipify_attempts += 1

        if ipify_attempts == 3 and newIP == self.currIP:
            logger.info("IP did not change from " + self.currIP)
            return False
                
        self.currIP = newIP
        logger.info("IP changed detected, IP is now " + str(self.currIP))
        return True

    def changeVPN(self, simple=True):
        if simple:
            self.changeVPNSimple()
        else:
            self.changeVPNComplex()

    def changeVPNSimple(self):
        server = self.chooseRandomServer()
        args = ['nordvpn', '-c', '-n', server]
        logger.info("Attempting VPN change (simple) to " + server)
        p = subprocess.Popen(args, cwd=r"C:\Program Files\NordVPN", shell=True)
        time.sleep(20)

    def changeVPNComplex(self):
        didIPChange = False
        while not didIPChange:
            server = self.chooseRandomServer()
            args = ['nordvpn', '-c', '-n', server]
            logger.info("Attempting VPN change (complex) to " + server)
            p = subprocess.Popen(args, cwd=r"C:\Program Files\NordVPN", shell=True)
            didIPChange = self.checkForIPChange()