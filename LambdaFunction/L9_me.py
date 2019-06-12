from elasticsearch import Elasticsearch,RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import json
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

session = boto3.Session()
credentials = session.get_credentials()
access_key = credentials.access_key
secret_key = credentials.secret_key
region = 'us-east-1'

host = '<ELASTICSEARCH-DOMAIN>'
awsauth = AWS4Auth(access_key,secret_key, region, 'es',session_token=credentials.token)

def lambda_handler(event,context):

    queue_url = "<QUEUE-URL>"
    sqs = boto3.client('sqs')

    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    

    message = response['Messages'][0]
    logger.info(message)
    logger.info(type(message))
    receipt_handle = message['ReceiptHandle']
    
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    
    #print('Received and deleted message: %s' % message)

    Start = message["MessageAttributes"]["Start"]["StringValue"]
    End = message["MessageAttributes"]["End"]["StringValue"]
    Phone = message["MessageAttributes"]["Phone"]["StringValue"]
    userId = message["MessageAttributes"]["userId"]["StringValue"]
    
    logger.info(Start)
    
    es = Elasticsearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
    
    res = es.search(index="reminder", body={
    "query": { 
        "bool": {
            "must": [{
                "range": {
                    "Date": {
                        "gte": Start,
                        "lte": End
                    }
                }},
                {"term":{
                    "user" : userId
                }
            }]
        }
    }})


    logger.info(res)
    #print(res['hits']['hits'])
    
    count = 0
    sns_mes = "This is your schedule from "+ str(Start) + " to "+ str(End) + ": "
    for hit in res['hits']['hits']:
        count+=1
        sns_mes += (str(count) + ". " + str(hit["_source"]["Date"]) + " " + str(hit["_source"]["Time"]) + ": " + hit["_source"]["Events"])
        sns_mes += ", "
    sns_mes += "enjoy your day!"
    
    logger.info(sns_mes)
    
    sns_client = boto3.client('sns')
    
    sns_client.publish(
	    PhoneNumber="+1123456",
        Message=sns_mes)
    
    logger.info(response['Messages'])

    return sns_mes
