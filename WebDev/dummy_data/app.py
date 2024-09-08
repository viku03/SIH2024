from flask import Flask, Response
import random
import time
import json

app = Flask(__name__)

# Define 50 fixed locations in Tamil Nadu, India
# Tamil Nadu coordinates are approximately between (8.1°N, 76.9°E) and (13.8°N, 80.3°E)
fixed_locations = [(random.uniform(8.1, 13.8), random.uniform(76.9, 80.3)) for _ in range(50)]

def generate_random_data():
    while True:
        # Create a list of temperature data for all locations
        temperature_data = [
            {"lon": lon, "lat": lat
            , "temperature": random.uniform(40, 70)
            ,"uv":random.uniform(4,9)
            ,"humidity":random.uniform(50,85)
            ,"pressure":random.uniform(950,1020)
            ,"airQuality":random.uniform(50,150)}
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
