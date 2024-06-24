#!/usr/bin/env python3
from nasa_epic import NasaEpic
from space_pop import SpacePop
from support.database import setup_db_connection

if __name__ == "__main__":
    connection = setup_db_connection()
    SpacePop().save_space_pop(connection)
    NasaEpic().save_images(connection)
