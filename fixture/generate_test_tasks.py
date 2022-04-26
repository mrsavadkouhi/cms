import json
import random

dataset = {
  "model": "centers.task",
  "pk": 1,
  "fields": {
    "name": "a",
    "description": "",
    "created_at": "2022-03-13T15:52:48.417Z",
    "employee": 4,
    "project": 1,
    "started_at": None,
    "to_be_finished": None,
    "payment": 0,
    "paid": 0,
    "created_financial_statement": False,
    "weight": 6,
    "progress": 0,
    "finished_at": None,
    "status": "verified",
    "attachments": []
  }
}

with open("test_tasks.json", "a+") as outfile:
  outfile.write('[')

status = ["to_do","inprogress","done","verified"]

for i in range(100):
  dataset["pk"] = i+1
  dataset["fields"]["name"] = str(i)
  dataset["fields"]["weight"] = (i%50)+1
  dataset["fields"]["status"] = "to_do"
  with open("test_tasks.json", "a+") as outfile:
      outfile.write(json.dumps(dataset))
      outfile.write(',')

for i in range(100):
  dataset["pk"] = i+101
  dataset["fields"]["name"] = str(i+101)
  dataset["fields"]["weight"] = (i%50)+1
  dataset["fields"]["status"] = "inprogress"
  dataset["fields"]["started_at"] = "2022-03-20T15:52:48.417Z"
  with open("test_tasks.json", "a+") as outfile:
      outfile.write(json.dumps(dataset))
      outfile.write(',')

for i in range(1000):
  dataset["pk"] = i+201
  dataset["fields"]["name"] = str(i+201)
  dataset["fields"]["weight"] = (i%50)+1
  dataset["fields"]["status"] = "done"
  dataset["fields"]["started_at"] = "2022-03-17T15:52:48.417Z"
  with open("test_tasks.json", "a+") as outfile:
      outfile.write(json.dumps(dataset))
      outfile.write(',')

for i in range(100):
  dataset["pk"] = i+301
  dataset["fields"]["name"] = str(i+301)
  dataset["fields"]["weight"] = (i%50)+1
  dataset["fields"]["status"] = "verified"
  dataset["fields"]["started_at"] = "2022-03-20T13:52:48.417Z"
  hours=['09','10','11','12','13','14','15','16','17','18']
  hour = random.choice(hours)
  days=[
    '01',
    '02',
    '03',
    '04',
    '05',
    '06',
    '07',
    '08',
    '09',
    '10',
    '11',
    '12',
    '13',
    '14',
    '15',
    '16',
    '17',
    '18',
    '19',
    '20',
    '21',
    '22',
    '23',
    '24',
    '25',
    '26',
    '27',
    '28',
    '29',
  ]
  day = random.choice(days)
  months=['01','02','03','04','05','06','07','08','09','10','11','12']
  month = random.choice(months)
  years=['0','1','2']
  year = random.choice(years)
  dataset["fields"]["finished_at"] = "202"+year+"-"+month+"-"+day+"T"+hour+":52:48.417Z"
  with open("test_tasks.json", "a+") as outfile:
      outfile.write(json.dumps(dataset))
      outfile.write(',')


dataset["pk"] = 401
dataset["fields"]["name"] = '401'
dataset["fields"]["weight"] = 50
dataset["fields"]["status"] = "verified"
dataset["fields"]["started_at"] = "2022-03-13T15:54:35.233Z"
dataset["fields"]["finished_at"] = "2022-03-13T15:54:35.233Z"
with open("test_tasks.json", "a+") as outfile:
    outfile.write(json.dumps(dataset))

with open("test_tasks.json", "a+") as outfile:
  outfile.write(json.dumps(dataset))
  outfile.write(']')