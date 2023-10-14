import requests
import simplejson as json
import time
import os
import boto3

GDN_KEY = os.environ['GDN_KEY']
AWS_KEY = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET = os.environ['AWS_SECRET_ACCESS_KEY']

if 'AWS_SESSION_TOKEN' in os.environ:
	AWS_SESSION = os.environ['AWS_SESSION_TOKEN']

# Example request
# https://content.guardianapis.com/sport/2022/oct/07/cricket-jos-buttler-primed-for-england-comeback-while-phil-salt-stays-focused?api-key=test

def getLatest(article_key):
	requestUrl = f"https://content.guardianapis.com/{article_key}?api-key={GDN_KEY}&show-blocks=body:latest:10"
	print(requestUrl)
	newJson = []
	r = requests.get(requestUrl)
	results = r.json()
	
	if results['response']['status'] == "ok":
		blocks = results['response']['content']['blocks']['requestedBodyBlocks']["body:latest:10"]
		for block in blocks:
			labelText = block['bodyTextSummary']
			if len(labelText) > 50:
				labelText = block['bodyTextSummary'][:50] + "..."
			
			block_id = block['id']
			url = f"https://www.theguardian.com/{article_key}?page=with:block-{block_id}#block-{block_id}"
			print(labelText)
			# print(url)
			newJson.append({"label":labelText, "url":url})

	# with open('output.json','w') as fileOut:
	# 	print("saving results locally")
	# 	fileOut.write(json.dumps(newJson, indent=4))

	newJsonOutput = json.dumps(newJson, indent=4)
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


	key = "2023/09/aus-referendum/results-data/ticker.json"
	object = s3.Object(bucket, key)
	object.put(Body=newJsonOutput, CacheControl="max-age=60", ACL='public-read', ContentType="application/json")
	print("Ticker updated")

# test = "/australia-news/live/2023/oct/14/voice-referendum-2023-live-updates-australia-latest-news-yes-no-vote-winner-results-australian-indigenous-voice-to-parliament-polls"
# getLatest(test)