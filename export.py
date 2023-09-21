#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import xmltodict


elect_data = xmltodict.parse(open("aec-mediafeed-results-standard-verbose-29581.xml", 'rb'))

# json_dict = json.dumps(elect_data, indent=4)

print(elect_data.MediaFeed.Results.Election.Referendum.Contests.Contest.Enrolment["@CloseOfRolls"])