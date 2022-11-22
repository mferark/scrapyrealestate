from flask import Flask, render_template, request
import json

app = Flask(__name__, template_folder='templates')  # still relative to module


@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html")

@app.route('/data', methods=['POST', 'GET'])
def result():
    dict_form = request.form.to_dict()
    # si el algun moment veiem que el diccionari no esta buit, guardem la info en un json
    if dict_form != {}:
        with open("./data/config.json", "w") as outfile:
            json.dump(dict_form, outfile)
        return render_template("info.html")

    return

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
