import tweepy
import sys
import os, os.path
import _pickle
import re, string, unicodedata


#read twitter application credentials from file
with open('twitterCreds.txt','r') as f:
			myCreds = [line.strip() for line in f]

#choose application authentication to get the most requests possible
auth = tweepy.AppAuthHandler(myCreds[0],myCreds[1] )
 
api = tweepy.API(auth, wait_on_rate_limit=True,
				   wait_on_rate_limit_notify=True)
 
if (not api):
    print ("Can't Authenticate")
    sys.exit(-1)

#file that has list of geolocations
with open('locations.txt','r') as f:
	inputLocations = [line.strip() for line in f]
locations=[]

#split inputs into names and latitude/longitude
locations=[line.split("@")[0] for line in inputLocations]
geoLocations=[line.split("@")[1] for line in inputLocations]

tweets=[]
#if the program has been run before, load the existing values
max_id_fileName='maxId.txt'
if os.path.exists(max_id_fileName):
	print("\tReading existing id values from log")
	with open(max_id_fileName, 'rb') as f:
		inputData=_pickle.load(f)
		inputStrings=inputData.split("\t")
		sinceId=int(inputStrings[0])
		fileNumber=int(inputStrings[1])
else:
	print("\tmaking new id values")
	sinceId=None
	fileNumber=0

tweets_fileName='tweets.pkl'
if os.path.exists(tweets_fileName):
	print("\tAppending new tweets to existing list")
	with open(tweets_fileName, 'rb') as f:
		tweets=_pickle.load(f)




searchLocation=geoLocations[0]
#arbitrarily large, change to limit the amount of tweets to recieve
maxTweets=100000
#100 is the max possible tweets to return from get/search request
tweetsPerQry=100
max_id = -1
tweetCount=0

print("\tnew sinceID: {0}, new fileNumber {1}".format(sinceId,fileNumber))

print("Downloading max {0} tweets".format(maxTweets))

#f = open('tweets.txt','a+')


def saveInfo():
	with open('tweets.pkl', 'wb') as f:
		_pickle.dump(tweets,f)

	with open('maxId.txt','wb') as f:
		_pickle.dump(str(max_id)+"\t"+str(fileNumber),f)




while tweetCount < maxTweets:
	iterable = len(inputLocations)
	index=fileNumber % iterable
    
    #on every cycle of the loop, change the location
	geoLocation=geoLocations[index]
	location=locations[index]
	try:
		if (max_id <= 0):
			if (not sinceId):
				new_tweets = api.search(geocode=geoLocation, count=tweetsPerQry)
			else:
				new_tweets = api.search(geocode=geoLocation, count=tweetsPerQry,
				since_id=sinceId)
		else:
			if (not sinceId):
				new_tweets = api.search(geocode=geoLocation, count=tweetsPerQry,
				max_id=str(max_id - 1))
			else:
				new_tweets = api.search(geocode=geoLocation, count=tweetsPerQry,
				max_id=str(max_id - 1),
				since_id=sinceId)
		if not new_tweets:
			print("exiting")
			saveInfo()
			sys.exit(0)

		for tweet in new_tweets:
			#format outputs correctly
			temp = str(tweet.text)
			temp = re.sub(r"http\S+", "", temp)
			temp = "".join([x if ord(x) < 128 else '' for x in temp])
			temp = temp.replace("&amp;"," ")
			temp = " ".join(temp.split())
			temp1 = location+"¦"+temp
			temp1=''.join(x for x in temp1 if unicodedata.category(x)!= 'Po')
			temp = temp1

			#f.write(temp)
			tweets.append(temp)

			fileNumber += 1


		tweetCount += len(new_tweets)
		print("Downloaded {0} tweets".format(tweetCount))
		max_id = new_tweets[-1].id
	except tweepy.TweepError as e:
		# Just exit if any errors
		print("some error : " + str(e))
		break

saveInfo()

print ("Downloaded {0} tweets".format(tweetCount))