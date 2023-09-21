import json
import xmltodict
import boto3
import os

AWS_KEY = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET = os.environ['AWS_SECRET_ACCESS_KEY']

if 'AWS_SESSION_TOKEN' in os.environ:
	AWS_SESSION = os.environ['AWS_SESSION_TOKEN']

def eml_to_JSON(eml_file,local,timestamp, test):
	
	#convert xml to json
	
	if local:
		elect_data = xmltodict.parse(open(eml_file, 'rb'))
	else:
		elect_data = xmltodict.parse(eml_file)	
	  
	#parse house of reps
	national_json = {}
	states_list = []
	electorates_list = []
	results_json = {}
	summary_json = {}
	# swing_list = []
	# electorates_list = []

	
	# Get referendum results

	ref_results = elect_data['MediaFeed']['Results']['Election']['Referendum']['Contests']['Contest']

	# Enrolment
	# MediaFeed.Results.Election.Referendum.Contests.Contest.Enrolment["@CloseOfRolls"]
	national_json['enrolment'] = int(ref_results['Enrolment']['#text'])

	# Total votes counted
	# MediaFeed.Results.Election.Referendum.Contests.Contest.ProposalResults.Total.Votes["#text"]
	national_json['votesCounted'] = int(ref_results['ProposalResults']['Total']['Votes']["#text"])
	national_json['votesCountedPercent'] = float(ref_results['ProposalResults']['Total']['Votes']["@Percentage"])

	# Formal votes counted
	# MediaFeed.Results.Election.Referendum.Contests.Contest.ProposalResults.Formal
	national_json['votesFormal'] = int(ref_results['ProposalResults']['Formal']['Votes']["#text"])
	national_json['votesFormalPercent'] = int(ref_results['ProposalResults']['Formal']['Votes']["@Percentage"])

	# Informal votes
	national_json['votesInformal'] = int(ref_results['ProposalResults']['Informal']['Votes']["#text"])
	national_json['votesInformalPercent'] = int(ref_results['ProposalResults']['Informal']['Votes']["@Percentage"])

	# Yes and No votes
	# MediaFeed.Results.Election.Referendum.Contests.Contest.ProposalResults.Option
	for option in ref_results['ProposalResults']['Option']:
		if option['eml:ReferendumOptionIdentifier']['#text'] == "Yes":
			national_json['votesYes'] = int(option['Votes']['#text'])
			national_json['votesYesPercent'] = int(option['Votes']['@Percentage'])

		elif option['eml:ReferendumOptionIdentifier']['#text'] == "No":
			national_json['votesNo'] = int(option['Votes']['#text'])
			national_json['votesNoPercent'] = int(option['Votes']['@Percentage'])
		
	# Electorate level results
	# MediaFeed.Results.Election.Referendum.Contests.Contest.PollingDistricts.PollingDistrict

	for electorate in ref_results['PollingDistricts']['PollingDistrict']:
		electorates_json = {}
		electorates_json['id'] = int(electorate['PollingDistrictIdentifier']['@Id'])
		electorates_json['name'] = electorate['PollingDistrictIdentifier']['Name']
		electorates_json['state'] = electorate['PollingDistrictIdentifier']['StateIdentifier']['@Id']
		electorates_json['enrolment'] = int(electorate['Enrolment']['#text'])
		electorates_json['votesCounted'] = int(electorate['ProposalResults']['Total']['Votes']['#text'])
		electorates_json['votesCountedPercent'] = float(electorate['ProposalResults']['Total']['Votes']['@Percentage'])

		electorates_json['votesFormal'] = int(electorate['ProposalResults']['Formal']['Votes']['#text'])
		electorates_json['votesFormalPercent'] = float(electorate['ProposalResults']['Formal']['Votes']['@Percentage'])
		
		for option in electorate['ProposalResults']['Option']:

			if option['eml:ReferendumOptionIdentifier']['#text'] == "Yes":
				electorates_json['votesYes'] = int(option['Votes']['#text'])
				electorates_json['votesYesPercent'] = int(option['Votes']['@Percentage'])

			elif option['eml:ReferendumOptionIdentifier']['#text'] == "No":
				electorates_json['votesNo'] = int(option['Votes']['#text'])
				electorates_json['votesNoPercent'] = int(option['Votes']['@Percentage'])

		electorates_json['votesInformal'] = int(electorate['ProposalResults']['Informal']['Votes']['#text'])
		electorates_json['votesInformalPercent'] = float(electorate['ProposalResults']['Informal']['Votes']['@Percentage'])

		electorates_list.append(electorates_json)
	# MediaFeed.Results.Election.Referendum.Analysis.States.State
	for state in elect_data['MediaFeed']['Results']['Election']['Referendum']['Analysis']['States']['State']:
		state_json = {}
		state_json['name'] = state['StateIdentifier']['@Id']
		state_json['enrolment'] = int(state['Enrolment']['#text'])

		state_json['votesCounted'] = int(state['ProposalResults']['Total']['Votes']['#text'])
		state_json['votesCountedPercent'] = float(state['ProposalResults']['Total']['Votes']['@Percentage'])

		state_json['votesFormal'] = int(state['ProposalResults']['Formal']['Votes']['#text'])
		state_json['votesFormalPercent'] = float(state['ProposalResults']['Formal']['Votes']['@Percentage'])
		
		for option in state['ProposalResults']['Option']:

			if option['eml:ReferendumOptionIdentifier']['#text'] == "Yes":
				state_json['votesYes'] = int(option['Votes']['#text'])
				state_json['votesYesPercent'] = int(option['Votes']['@Percentage'])

			elif option['eml:ReferendumOptionIdentifier']['#text'] == "No":
				state_json['votesNo'] = int(option['Votes']['#text'])
				state_json['votesNoPercent'] = int(option['Votes']['@Percentage'])

		state_json['votesInformal'] = int(state['ProposalResults']['Informal']['Votes']['#text'])
		state_json['votesInformalPercent'] = float(state['ProposalResults']['Informal']['Votes']['@Percentage'])

		states_list.append(state_json)


	results_json['national'] = national_json
	results_json['states'] = states_list
	results_json['electorates'] = electorates_list

	summary_json['national'] = national_json
	summary_json['states'] = states_list

	newJson = json.dumps(results_json, indent=4)
	summaryJson = json.dumps(summary_json, indent=4)

	# Save the file locally

	# with open('{timestamp}.json'.format(timestamp=timestamp),'w') as fileOut:
	# 	print("saving results locally")
	# 	fileOut.write(newJson)		

	# with open('summaryResults.json','w') as fileOut:
	# 	print("saving results locally")
	# 	fileOut.write(summaryJson)		

	print("Connecting to S3")
	bucket = 'gdn-cdn'

	if 'AWS_SESSION_TOKEN' in os.environ:
		session = boto3.Session(
		aws_access_key_id=AWS_KEY,
		aws_secret_access_key=AWS_SECRET,
		aws_session_token = AWS_SESSION
		)
	else:
		session = boto3.Session(
		aws_access_key_id=AWS_KEY,
		aws_secret_access_key=AWS_SECRET,
		)
	
	s3 = session.resource('s3')	

	testStr = ''
	if test:
		testStr = '-test'

	key = "2023/09/aus-referendum/results-data/{timestamp}{testStr}.json".format(timestamp=timestamp, testStr=testStr)
	object = s3.Object(bucket, key)
	object.put(Body=newJson, CacheControl="max-age=60", ACL='public-read', ContentType="application/json")
	print("Done")


	key2 = "2023/09/aus-referendum/results-data/summaryResults{testStr}.json".format(testStr=testStr)	
	object = s3.Object(bucket, key2)
	object.put(Body=summaryJson, CacheControl="max-age=60", ACL='public-read', ContentType="application/json")
	print("Done")

	print("Done, JSON is uploaded")

# eml_to_JSON(eml_file,local,timestamp, test):
# eml_to_JSON('aec-mediafeed-results-standard-verbose-29581.xml',True,'20220518111214',False)