Weather prediction module
Currently only obtaining samples from OpenWeatherMap

Two main scripts are in use:

cityMap.py can be used to extract a list of cities within a region from a json file containin all cities in OpenWeatherMap
getweather.py is the main script managing weather requests and data storage on a local mongo database.



Set up:

1. Clone the repo.
2. Create account in [https://openweathermap.org/](https://openweathermap.org/).
3. Generate API key in [https://home.openweathermap.org/api_keys](https://home.openweathermap.org/api_keys).
4. Copy API key and set it up as environment variable:

    `export OWM_API_KEY="your_API_key"`

5. (if you want, set this up in .bashrc, so the variable is set for the log in session)
6. Get telegram bot id and chat id, export them as well:
    
    `export BOT_CLIENT="bot_id"`
    `export BOT_CHATID="bot_chat_id"`

7. Download city list from [http://bulk.openweathermap.org/sample/](http://bulk.openweathermap.org/sample/)
8. Run CityMap.py giving the directory of the city list. This set up the cities where the samples will be taken.
9. Run getweather.py to get a sample on the defined cities.



