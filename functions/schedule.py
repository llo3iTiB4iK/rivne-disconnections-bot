import datetime

from functions.parser import Parser
from config import DISCONNECTIONS_URL, NUM_TURNS


class Schedule:

    def __init__(self):
        self.turns_list = [(turn // 2 + 1) * 10 + turn % 2 + 1 for turn in range(NUM_TURNS)]
        self.disconnections_by_turns = {}
        self.last_updated = ""
        self.previous_data = {}

    def fill(self, disconnections_table_content, last_update_text):
        start_index = 3 + 2 * NUM_TURNS + NUM_TURNS // 2
        dates = disconnections_table_content[start_index::NUM_TURNS + 1]

        def split(string, size):
            return [string[i:i + size] for i in range(0, len(string), size)]

        for i, turn in enumerate(self.turns_list):
            disconnection_hours = disconnections_table_content[start_index + i + 1::NUM_TURNS + 1]
            self.disconnections_by_turns[turn] = {
                date: split(hours, 13) for date, hours in zip(dates, disconnection_hours)
                if datetime.datetime.strptime(date, "%d.%m.%Y").date() >= datetime.date.today()
            }

        self.last_updated = last_update_text

    def need_updates(self):
        time_now = datetime.datetime.now()
        return not self.disconnections_by_turns or (time_now - self.get_last_updated_dt()).total_seconds() / 60 >= 30

    def update(self):
        self.previous_data = self.disconnections_by_turns.copy()
        parser = Parser(DISCONNECTIONS_URL)
        self.fill(parser.read_table(), parser.find_by_pattern(r"Оновлено: \d{2}\.\d{2}\.\d{4} \d{2}:\d{2}"))

    def get_last_updated_dt(self):
        return datetime.datetime.strptime(" ".join(self.last_updated.split()[1:]), "%d.%m.%Y %H:%M")

    def get_schedule_by_turn(self, turn):
        return self.disconnections_by_turns[turn]

    def get_changed_turns(self):
        if self.disconnections_by_turns and self.previous_data:
            return [turn for turn in self.disconnections_by_turns
                    if self.disconnections_by_turns[turn] != self.previous_data[turn]]
        return []

    def get_disconnections_start_times(self):
        return {
            turn: [
                datetime.datetime.strptime(f"{date} {disconnection.split(' - ')[0]}", "%d.%m.%Y %H:%M")
                for date, hours in disconnections.items()
                for disconnection in hours if disconnection != 'Очікується'
            ]
            for turn, disconnections in self.disconnections_by_turns.items()
        }


schedule = Schedule()