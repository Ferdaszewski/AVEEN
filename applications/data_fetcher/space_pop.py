import requests


class SpacePop:
    @staticmethod
    def get_space_pop():
        print("Getting Space Population")
        response = requests.get("http://api.open-notify.org/astros.json")
        pop = response.json()["number"]
        print("Current Space Population is %s" % pop)
        return pop

    def save_space_pop(self, dbConnection):
        space_pop = self.get_space_pop()
        with dbConnection as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO space_pop (pop) VALUES (%s)", (space_pop,))
