
from flask import Flask, Response
import random
import time
import json

app = Flask(__name__)

# Define 50 fixed locations in Tamil Nadu, India
# Tamil Nadu coordinates are approximately between (8.1°N, 76.9°E) and (13.8°N, 80.3°E)
fixed_locations = [((12.8416),(80.1565)),((12.8438),(80.1549))]

def generate_random_data():
    while True:
        # Create a list of temperature data for all locations
        temperature_data = [
            {"lon": lon, "lat": lat
            , "temperature": random.uniform(80, 85)
            ,"uv":random.uniform(1,3)
            ,"humidity":random.uniform(65,75)
            ,"pressure":random.uniform(990,1050)
            ,"airQuality":random.uniform(0,10)}
            for lat, lon in fixed_locations
        ]
        # Convert the list to a JSON string
        data = json.dumps(temperature_data)
        # Yield the data as an SSE message
        yield f"data: {data}\n\n"
        time.sleep(1)  # Simulate a delay between updates

@app.route('/data')
def stream():
    return Response(generate_random_data(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
