import logging
import sys

from openaq.common.db import add_measure_to_db
from openaq.ingestion.sqs import Response, get_measure, delete_message_from_sqs

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

log = logging.getLogger(__name__)


def main():
    while True:
        response: Response = get_measure()
        if response is not None:
            add_measure_to_db(measure=response.sql_measure)
            delete_message_from_sqs(response=response)
            log.info(f'Ingested measure for location {response.sql_measure.location}')
        else:
            log.info('No measure ingested for the last 10 seconds.')


if __name__ == '__main__':
    main()
