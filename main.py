import os
import requests
import logging as log
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired


load_dotenv()
STATE_MAPPINGS = {
        "Alabama": 'AL', "Alaska": 'AK', "Arizona": 'AZ', 
        "Arkansas": 'AR', "California": 'CA', "Colorado": 'CO',
        "Connecticut": 'CT', "Delaware": 'DE', "Florida": 'FL',
        "Georgia": 'GA', "Hawaii": 'HI', "Idaho": 'ID',
        "Illinois": 'IL', "Indiana": 'IN', "Iowa": 'IO',
        "Kansas": 'KS', "Kentucky": 'KY', "Louisiana": 'LA',
        "Maine": 'ME', "Maryland": 'MD', "Massachusetts": 'MA',
        "Michigan": 'MI', "Minnesota": 'MN', "Mississippi": 'MS',
        "Missouri": 'MO', "Montana": 'MT', "Nebraska": 'NE',
        "Nevada": 'NV', "New Hampshire": 'NH', "New Jersey": 'NJ',
        "New Mexico": 'NM', "New York": 'NY', "North Carolina": 'NC',
        "North Dakota": 'ND', "Ohio": 'OH', "Oklahoma": 'OK',
        "Oregon": 'OR', "Pennsylvania": 'PA', "Rhode Island": 'RI',
        "South Carolina": 'SC', "South Dakota": 'SD', "Tennessee": 'TN',
        "Texas": 'TX', "Utah": 'UT', "Vermont": 'VT',
        "Virginia": 'VA', "Washington": 'WA', "West Virginia": 'WV',
        "Wisconsin": 'WI', "Wyoming": 'WY'
}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

class CampgroundSearchForm(FlaskForm):
    state = SelectField(label='state', choices=STATE_MAPPINGS.keys(), validators=[DataRequired()])
    submit = SubmitField('submit')

def get_campgrounds_list(state):
    state_abbrev = STATE_MAPPINGS[state]
    BASE_URL = "http://api.amp.active.com/camping/campgrounds"
    api_key = os.getenv("CAMPGROUND_API_KEY")

    resp = requests.get(f"{BASE_URL}?pstate={state_abbrev}&api_key={api_key}")
    xml = ET.fromstring(resp.text)

    campgrounds = []
    for table in xml.iter('resultset'):
        for child in table:
            campgrounds.append(child.attrib)

    return campgrounds


@app.route("/", methods=['GET', 'POST'])
def home():
    form = CampgroundSearchForm()
    if form.validate_on_submit():
        state = form.state.data
        return redirect(url_for('display_results', state=state))
    return render_template('home.html', form=form)


@app.get('/campground-results/<state>')
def display_results(state):
    try:
        campgrounds = get_campgrounds_list(state)
        return render_template('campgrounds.html', campgrounds=campgrounds)
    except Exception as e:
        print(e)
        log.error(e)
        return "Failed to retrieve the data you requested", 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
