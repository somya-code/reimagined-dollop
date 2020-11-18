import json
from flair.models import SequenceTagger
from flair.data import Sentence
import flair
#flair.datasets.WASSA_FEAR(data_folder="/datadrive/floatbot-ai")
flair.cache_root = "/datadrive"
tagger = SequenceTagger.load("ner-ontonotes-fast")
import requests

class FindFoodPlace(object):
	def find(text):
		try:
			results=[]
			zomato_city_id=""
			zomato_entity_id=[]
			zomato_entity_type=[]
			supported_cuisine_city=[]
			cuisine_id=[]
			s= Sentence(text)
			dictn={}
			tagger.predict(s)
			label_value = s.to_dict(tag_type='ner') #get the place and cuisine type
			print(label_value)
			for i in label_value["entities"]:
				#if float(re.sub("[()]","",str(i["labels"][0]).split(" ")[1])) > 0.3: - this is to put the confidence filter
				k=str(i["labels"][0]).split(" ")[0]
				if k in dictn:
					dictn[k]=dictn[k]+" "+i["text"]
				elif k == "NORP":
					dictn[k]=i["text"]
				elif k == "GPE" or "LOC":
					dictn["place"] = i["text"]
				else:
					pass

			if "place" in dictn:

				headers = {
					'Accept': 'application/json',
					'user-key': 'cc5476714733aabca6f77b93892855bb',
				}

				params = (
					('q', dictn["place"]),
				)

				response = requests.get('https://developers.zomato.com/api/v2.1/cities', headers=headers, params=params)

				# Decode UTF-8 bytes to Unicode, and convert single quotes 
				# to double quotes to make it valid JSON
				
				if response.status_code == 200:
					my_json = response.content.decode('utf8').replace("'", '"')

					
					data = json.loads(my_json)
					
					zomato_city_id = str(data["location_suggestions"][0]["id"])
					

				#the below request is to find the supported cuisines in the place
				params = (
					('city_id', str(zomato_city_id)),
				)
				response = requests.get('https://developers.zomato.com/api/v2.1/cuisines', headers=headers, params=params)
				
				
				if response.status_code == 200:
					my_json = response.content.decode('utf8').replace("'", '"')

					
					data = json.loads(my_json)
					

					supported_cuisine_city = [(i["cuisine"]["cuisine_id"],i["cuisine"]["cuisine_name"]) for i in data["cuisines"]]

				params = (('query',  dictn["place"]),)

				#to get the entity id & type based on place
				response = requests.get('https://developers.zomato.com/api/v2.1/locations', headers=headers, params=params)
				
				
				
				d = response.content.decode('utf8').replace("'", '"')
					
				data1 = json.loads(d)
				

				zomato_entity_id = str(data1["location_suggestions"][0]["entity_id"])
				zomato_entity_type = data1["location_suggestions"][0]["entity_type"]
				

				if "NORP" in dictn:
					
						cuisine_id = [str(i) for i,j in supported_cuisine_city if j in dictn["NORP"]]
						
						params = (('entity_id', zomato_entity_id),('entity_type', zomato_entity_type),('cuisines', cuisine_id),('count', '5'),)
						#to get the list of  top 5 restaurants
						response = requests.get('https://developers.zomato.com/api/v2.1/search', headers=headers, params=params)
						
						d = response.content.decode('utf8').replace("'", '"')
						
						
						data_new= json.loads(d)
						
						results = [(r["restaurant"]["name"],r["restaurant"]["location"]["address"]) for r in data_new["restaurants"]]
				else:
					return "Please enter the cuisine type Also"
			else:
				return "Please enter the location for which you are looking for restaurants"
			
			
			s=""
			for i,j in results:
				
				s = s+ "Name____"+i+"_____\n"+"____Address_____"+j+"\n\n\n____"
			
			return s
		except Exception as e:
			print(e)
			return "Please try after some time"