from flask import Flask, render_template
from MapGenerator import generateMap

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contacto')
def contact():
    return render_template('contacto.html')

@app.route('/healthmap/<string:institution>')
def hello_world(institution):
    mapping = {
        "hlb": "HOSPITAL LEON BECERRA",
        "all": "TODOS LOS HOSPITALES"
    }
    institution_name = mapping[institution]
    return render_template('healthmap.html',
                           institution=institution,
                           name=institution_name)

if __name__ == '__main__':
    app.run(debug=True)
