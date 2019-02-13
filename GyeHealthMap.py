from flask import Flask, render_template
from CONSTANTS import CONSTANTS
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')

app = Flask(__name__)
app.secret_key = 'shhhhhhhh'

@app.route('/')
def init():
    return render_template('init.html',
                           active="init")

@app.route('/institutions')
def institutions():
    c = CONSTANTS(APP_STATIC)
    return render_template('institutions.html',
                           active="institutions",
                           institutions=c.institutions)

@app.route('/contacto')
def contact():
    return render_template('contacto.html',
                           active="contact")

@app.route('/healthmap/<string:institution_id>')
def healthMap(institution_id):
    c = CONSTANTS(APP_STATIC, load_cie10=True)
    return render_template('healthmap.html',
                           active="institutions",
                           institution=c.findInstitution(institution_id),
                           capitulos=c.capitulos,
                           agrupacion=c.agrupaciones,
                           cie10=c.getCIE10forInstitution(institution_id))

if __name__ == '__main__':
    app.run(debug=False)
