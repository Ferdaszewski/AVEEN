import requests


class WorldPop:
    def get_world_pop(self):
        print("Getting World Population")
        response = requests.get("https://www.census.gov/popclock/data/population.php/world")
        pop = response.json()["world"]['pop_midnight']
        print(f"World Population at midnight: {pop}")
        return pop

    def save_space_pop(self, db_connection):
        world_pop = self.get_world_pop()
        with db_connection as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO world_pop (pop) VALUES (%s)", (world_pop,))
