from flask import render_template
from flask import Flask
import oyaml as yaml

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/')
def index():
    website_data = yaml.load(open('_config.yaml'),
                             Loader=yaml.FullLoader)

    return render_template('index.html', data=website_data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
