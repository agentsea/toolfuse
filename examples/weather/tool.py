import os
from dotenv import load_dotenv
import requests
from toolfuse import Tool, action, observation

# Load the API key from the .env file
load_dotenv()
OPEN_AI_KEY = os.environ.get("OPEN_AI_KEY")


class WeatherLogger(Tool):
    def __init__(self):
        super().__init__()
        self.log_file = "weather.txt"

    @action
    def log(self, message: str):
        """Logs a message to the log file."""
        with open(self.log_file, "a") as file:
            file.write("***\n" + message + "\n")

    @observation
    def weather(self, location: str) -> str:
        """Checks the current weather from the internet using wttr.in."""
        weather_api_url = f"http://wttr.in/{location}?format=%l:+%C+%t"
        try:
            response = requests.get(weather_api_url)
            return response.text
        except requests.exceptions.HTTPError as err:
            return f"HTTP Error: {err}"
        except requests.exceptions.RequestException as e:
            return f"Error: Could not retrieve weather data. {e}"

    def close(self):
        """Close the WeatherLogger tool and release any resources."""
        # Since there are no resources to release in this simple example, pass is used.
        pass


if __name__ == "__main__":
    # Example usage
    tool = WeatherLogger()
    location = "Paris"
    weather_info = tool.weather(location)
    print(f"Weather in {location}: {weather_info}")
    tool.log(f"Weather in {location}: {weather_info}")
