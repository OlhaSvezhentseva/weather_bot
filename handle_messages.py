from enum import Enum

class MessageStatus(Enum):
    INVALID_PLACE = 1
    INVALID_FORMAT = 2
    DATE_TOO_FAR = 3
    DATE_IN_THE_PAST = 4
    API_CONNECTION_ERROR = 5
    API_PARAMETERS_ERROR = 6
    GREETING = 7
    FINISHING_CHAT = 8


MESSAGES = {
    MessageStatus.INVALID_PLACE: "Sorry, I didn't get the place. "
    "Please, type your request again, don't forget to specify the place and the day.",
    MessageStatus.INVALID_FORMAT: "Sorry, I couldn't process your request. "
    "Could you reformulate it?",
     MessageStatus.DATE_TOO_FAR: "Sorry, the date seems to be more than 6 days away. "
    "Could you make a new request with the date that is within 6 days?",
     MessageStatus.DATE_IN_THE_PAST: "Sorry, the date seems to be in the past. "
    "Could you make a new request with the date that is either today or within the next 6 days?",
    MessageStatus.API_CONNECTION_ERROR: "Sorry, I am having difficulties with connection to the Weather API. "
    "Could you repeat your request?",
    MessageStatus.API_PARAMETERS_ERROR: "Sorry, I couldn't process your request. "
    "Could you reformulate it?",
     MessageStatus.GREETING: "Hello, I am your weather chat bot. "
    "Please, specify the location and the day, so that I can tell you the forecast. "
    "Remember that I can only give the forecast for up to 6 days in future. "
    "Whenever you feel like finishing our chat, type 'Bye'. "
    "What would you like to know?",
     MessageStatus.FINISHING_CHAT: "I hope I could help. Have a good day!",
}