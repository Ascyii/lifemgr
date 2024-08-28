from flask import Flask, jsonify, request, send_file, send_from_directory, abort
import calendar
from datetime import datetime
import os

app = Flask(__name__)

# In-memory storage for calendar notes
calendar_notes = {}

# Directory to save uploaded files
UPLOAD_FOLDER = 'data/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to generate a calendar with week numbers
def generate_calendar_with_weeks(year, month):
    cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
    days_in_month = cal.itermonthdays2(year, month)  # (day, weekday) tuples

    calendar_text = []
    for day, weekday in days_in_month:
        if day != 0:  # Only include actual days of the month
            week_num = datetime(year, month, day).isocalendar()[1]
            day_name = calendar.day_abbr[weekday]
            date_str = f'{year}-{month:02d}-{day:02d} w{week_num} {day_name}'
            if f'{year}-{month:02d}-{day:02d}' in calendar_notes:
                date_str += f'  {calendar_notes[f"{year}-{month:02d}-{day:02d}"]}'
            calendar_text.append(date_str)
    
    return "\n".join(calendar_text)

# API route to serve the index.html file
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# API route to get the calendar for a specific month and year
@app.route('/calendar', methods=['GET'])
def get_calendar():
    year = request.args.get('year', default=datetime.now().year, type=int)
    month = request.args.get('month', default=datetime.now().month, type=int)
    
    # Generate calendar with week numbers
    cal_text = generate_calendar_with_weeks(year, month)
    
    return jsonify({"calendar": cal_text})

# API route to add a note to a specific date
@app.route('/calendar/note', methods=['POST'])
def add_note():
    data = request.json
    year = data.get('year', datetime.now().year)
    month = data.get('month', datetime.now().month)
    day = data['day']
    note = data['note']
    
    date_key = f'{year}-{month:02d}-{day:02d}'
    calendar_notes[date_key] = note
    
    return jsonify({"message": "Note added successfully!"})

# API route to upload a calendar file
@app.route('/calendar/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        return jsonify({"message": "File uploaded and processed successfully!"})

# API route to download the current calendar
@app.route('/calendar/download', methods=['GET'])
def download_file():
    year = request.args.get('year', default=datetime.now().year, type=int)
    month = request.args.get('month', default=datetime.now().month, type=int)
    
    cal_text = generate_calendar_with_weeks(year, month)
    file_path = os.path.join(UPLOAD_FOLDER, f'calendar_{year}_{month}.txt')
    
    with open(file_path, 'w') as file:
        file.write(cal_text)
    
    return send_file(file_path, as_attachment=True)

# API route to list uploaded files
@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    files = [f for f in files if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    return jsonify({"files": files})

# API route to download a specific uploaded file
@app.route('/files/<filename>', methods=['GET'])
def download_uploaded_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        abort(404, description="File not found")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

