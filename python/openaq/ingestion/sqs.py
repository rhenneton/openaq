import json
import boto3

from dataclasses import dataclass
from typing import Dict

from openaq.common import environment
from openaq.common import db

sqs_client = boto3.client('sqs')


@dataclass
class Response:
    sqs_message: Dict
    sql_measure: db.Measure


def get_measure() -> Response:
    """
    Retrieves a message from the SQS Client and returns it alongside the Measure in SQLAlchemy format.

    :param sqs_client: The sqs client from which we poll the new measure
    :return: A response containing the polled SQS message and the SQL Measure
    """
    response = sqs_client.receive_message(QueueUrl=environment.sqs_url, WaitTimeSeconds=10)
    if 'Messages' in response:
        for element in response['Messages']:
            if 'Body' in element:
                body = json.loads(response['Messages'][0]['Body'])
                if 'Message' in body:
                    message = json.loads(body['Message'])
                    sql_measure = db.Measure(id=element['MessageId'],
                                             date_utc=message.get('date')['utc'],
                                             value=message.get('value'),
                                             unit=message.get('unit'),
                                             location=message.get('location'),
                                             city=message.get('city'),
                                             latitude=message.get('coordinates', dict()).get('latitude'),
                                             longitude=message.get('coordinates', dict()).get('longitude'),
                                             country=message.get('country'))
                    return Response(sqs_message=element,
                                    sql_measure=sql_measure)
    return None


def delete_message_from_sqs(response: Response):
    """
    Delete an SQS message from the SQS queue after being processed

    :param Response: The response containing the SQS message
    """
    handle: str = response.sqs_message['ReceiptHandle']
    sqs_client.delete_message(QueueUrl=environment.sqs_url, ReceiptHandle=handle)
