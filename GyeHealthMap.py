from flask import Flask, render_template
from MapGenerator import generateMap

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/healthmap/<string:institution>/')
def hello_world(institution):
    return 'Has accedido a la institucion', institution

if __name__ == '__main__':
    app.run(debug=True)
