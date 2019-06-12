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
    # resp = {
    #     'headers': {
    #         "Access-Control-Allow-Origin": "*",
    #         "Content-Type": "text/plain"
    #     },
        
    #     'statusCode': 200,
    #     'body': event["queryStringParameters"]
        
    # }
    
    # return resp
    es = Elasticsearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

    index = event["queryStringParameters"]["t"]
    userId = event["queryStringParameters"]["user_id"]
    

    res = es.search(index=index, body = {"query": {"term":{"user":userId}}})
    
    results = []
    
    for hit in res["hits"]["hits"]:
        name = hit["_source"]["Name"]
        type_ = index
        preference = hit["_source"]["Preference"]
        result = {'name': name, 'type': type_, 'preference': preference}
        results.append(result)
    
    response1 = {
        "results": results
    }
    
    resp = {
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json"
        },
        
        'statusCode': 200,
        'body': json.dumps(response1)
        
    }
    
    return resp