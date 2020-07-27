from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_fontawesome import FontAwesome
from flask_pymongo import PyMongo
from bson.json_util import dumps

import extractors.getEntitiesExample as Extractor

app = Flask(__name__)
fa =FontAwesome(app)
mongo = PyMongo(app , uri="mongodb://localhost:27017/VIDEOLECTURES_DMS")


if __name__=="__main__":
    app.run(debug=True)

@app.route("/", methods=['POST','GET'])
def index(response=None):
    response=""

    if request.method=='POST':
        searchText=request.form['searchText']

        # text = "This is the database course, which teaches you about database management system"
        try:
            # response=Extractor.getEntities(searchText)
            response = mongo.db.entity.find({"_id":"http://www.wikidata.org/entity/P10"})

            return render_template("index.html", result=dumps(response))

        except:

            return 'There as an error'

    else:

        return render_template("index.html")




