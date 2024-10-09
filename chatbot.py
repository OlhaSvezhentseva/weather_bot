import re
import os
import requests
import datetime
from handle_messages import MessageStatus, MESSAGES


from groq import Groq


os.environ["GROQ_API_KEY"] = "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"

CLIENT = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

CURR_DATE = datetime.date.today()
CURR_WEEKDAY = CURR_DATE.strftime("%A")


with open("model_message_template.txt", "r") as file:
    template = file.read()

MODEL_PROMPT = template.format(CURR_DATE=CURR_DATE, CURR_WEEKDAY=CURR_WEEKDAY)


class Bot:
    def __init__(self):
        self.place = None
        self.coordinates = None
        self.date = None

    def _validate_model_response(self, response):
        # Regular expression pattern for "DATE: YYYY.MM.DD, LAT: <latitude>, LON: <longitude>, PLACE: <place>."
        pattern = r"^DATE: (\d{4})\-(\d{2})\-(\d{2}), LAT: (-?\d+(\.\d+)?), LON: (-?\d+(\.\d+)?), PLACE:\s*([\w\s\-\.,'’]+)\.?$"

        # Match the pattern against the response
        match = re.match(pattern, response)
        # print(response)

        if match:
            year = match.group(1)
            month = match.group(2)
            day = match.group(3)
            latitude = match.group(4)
            longitude = match.group(6)
            place = match.group(8)
            if place == "NULL":
                return False, MessageStatus.INVALID_PLACE

            weather_date = datetime.datetime.strptime(
                f"{year}-{month}-{day}", "%Y-%m-%d"
            ).date()
            if (weather_date - CURR_DATE).days > 6:
                return False, MessageStatus.DATE_TOO_FAR
            elif (weather_date - CURR_DATE).days < 0:
                return False, MessageStatus.DATE_IN_THE_PAST

            self.date = f"{year}-{month}-{day}"
            self.place = place
            self.coordinates = [latitude, longitude]
            return True, "Valid format"
        else:
            return False, MessageStatus.INVALID_FORMAT

    def ask_model(self, query):
        chat_completion = CLIENT.chat.completions.create(
            messages=[{"role": "user", "content": MODEL_PROMPT + query}],
            model="mixtral-8x7b-32768",
            # model="llama3-70b-8192", problems with days of week
            # model="llama3-8b-8192", problems with days of week
            # model="gemma2-9b-it",
        )

        response = chat_completion.choices[0].message.content
        status, info = self._validate_model_response(response)

        return status, info

    def get_temperature(self):
        weather_response = requests.get(
            f"http://my.meteoblue.com/packages/basic-day?lat={self.coordinates[0]}&lon={self.coordinates[1]}&apikey=wjfERQS1i2cv5p4k&expire=1924948800"
        )

        if weather_response.status_code != 200:
            return MessageStatus.API_CONNECTION_ERROR
        else:
            weather_response = weather_response.json()
            if "data_day" not in weather_response:
                return MessageStatus.API_PARAMETERS_ERROR

            for i in range(len(weather_response["data_day"]["time"])):
                if weather_response["data_day"]["time"][i] == self.date:
                    return {
                        "place": self.place,
                        "date": self.date,
                        "temperatures": [
                            round(weather_response["data_day"]["temperature_max"][i]),
                            round(weather_response["data_day"]["temperature_min"][i]),
                            round(weather_response["data_day"]["temperature_mean"][i]),
                        ],
                    }


class Chat:
    def __init__(self, bot):
        self.bot = bot

    def run_chat(self):
        self.generate_message(MessageStatus.GREETING)
        while True:
            query = input().strip()
            if "bye" in query.lower():
                self.generate_message(MessageStatus.FINISHING_CHAT)
                return
            status_success, info = self.bot.ask_model(query)
            if status_success:
                temperatures = self.bot.get_temperature()
                self.generate_message(temperatures, temperature_report=True)

            else:
                self.generate_message(info)

    def generate_message(self, message_data, temperature_report=False):
        if temperature_report:
            if (
                "temperatures" in message_data
                and len(message_data["temperatures"]) == 3
            ):
                print("\nHere you are!\n")
                for name, temp in zip(
                    ["Max", "Min", "Average"], message_data["temperatures"]
                ):
                    print(
                        f"{name} temperature in {message_data['place']} on {message_data['date']} is {temp}°C.\n"
                    )
                print(
                    "Feel free to ask me again about the weather. If you want to stop our chat, type 'Bye'.\n"
                )
                print("---------------------------------------------------------------------")

        else:
            print(f"\n{MESSAGES[message_data]}\n")


weather_bot = Bot()
chat = Chat(weather_bot)
chat.run_chat()
