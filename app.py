import os, sys
from flask import Flask, render_template, request

from models.randomiser import Randomiser

UPLOAD_FOLDER = '/flask/server/image'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG"]

@app.route("/")
def render_default():
    return render_template("index.html")

@app.route('/api/randomiser', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'image' not in request.files:
            return 'there is no image in form !'

        if not os.path.isdir(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        file1 = request.files['image']
        path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        file1.save(path)
        xmin = int(request.form.get("xmin"))
        ymin = int(request.form.get("ymin"))
        xmax = int(request.form.get("xmax"))
        ymax = int(request.form.get("ymax"))
        
        randomiser = Randomiser(path, None, xmin, ymin, xmax, ymax)
        lst = randomiser.randomise()

        # lst = [[307, 176, 473, 294], [320, 427, 486, 545], [327, 885, 494, 1003]]
        data = {"size": len(lst), "bboxes": lst}

        return data


if __name__ == "__main__":

    app.run(host="127.0.0.1", port=8000, threaded=True, debug=True)
	
	