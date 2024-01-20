from flask import Flask, render_template, request
from chesscog.recognition.recognition import TimedChessRecognizer
from werkzeug.utils import secure_filename
import os
import cv2
from pathlib import Path

app = Flask(__name__)
print("Current working directory:", os.getcwd())

print("Effective UID:", os.geteuid())
print("Real UID:", os.getuid())


UPLOAD_FOLDER = '/Users/yagmursahin/Downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def recognize_chess():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('error.html', error='No file part')

        file = request.files['file']

        # Check if a file is selected
        if file.filename == '':
            return render_template('error.html', error='No selected file')

        # Check if the file type is allowed
        if file and allowed_file(file.filename):
            # Save the file to the upload folder
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Read the image using OpenCV
            img = cv2.imread(file_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Perform chess recognition

            occupancy_classifier_path = 'models/occupancy_classifier'
            print(os.listdir(occupancy_classifier_path))

# Add this line to print the full path of the classifier folder
            print(f"Full path: {Path(occupancy_classifier_path).resolve()}")

# Add this line to print the full path of the model files
            print(f"Model files: {list(Path(occupancy_classifier_path).resolve().glob('*.pt'))}")

            #recognizer = TimedChessRecognizer(classifiers_folder=Path(occupancy_classifier_path))
            recognizer = TimedChessRecognizer(classifiers_folder=Path("models"))


                              
            board, _, times = recognizer.predict(img)

            # Example response
            recognized_board = {
                'fen': board.fen(),
                'positions': {square: str(board.piece_at(square)) for square in board.piece_map()}
            }

            # Add times to the response
            recognized_board['times'] = times

            return render_template('result.html', recognized_board=recognized_board)

        return render_template('error.html', error='Invalid file type')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
