#!/usr/bin/env python3
import os

import pika
from dotenv import load_dotenv

from world_pop import WorldPop
from nasa_epic import NasaEpic
from space_pop import SpacePop
from support.database import setup_db_connection

if __name__ == "__main__":
    load_dotenv()
    connection = setup_db_connection()
    SpacePop().save_space_pop(connection)
    WorldPop().save_space_pop(connection)
    new_date = NasaEpic().save_images(connection)
    if new_date is not None:
        print(f"Got new images, sending message for date: {new_date}")
        params = pika.URLParameters(os.environ.get('CLOUDAMQP_URL'))
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='aveey_new_images')
        channel.basic_publish(exchange='',
                              routing_key='aveey_new_images',
                              body=new_date)
        print("Message Sent")
        connection.close()
