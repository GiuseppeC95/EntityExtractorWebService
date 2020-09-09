from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_fontawesome import FontAwesome
# from flask_pymongo import PyMongo
import json
from bson.json_util import dumps

import extractors.getEntitiesExample as Extractor

app = Flask(__name__)
fa =FontAwesome(app)
# mongo = PyMongo(app , uri="mongodb://localhost:27017/VIDEOLECTURES_DMS")


if __name__=="__main__":
    app.run(debug=True)

@app.route("/", methods=['POST','GET'])
def index(response=None):
    response=""

    if request.method=='GET' and request.args.get('searchText') is not None :
        print(request.args.get('searchText'))
        searchText = request.args.get('searchText')
        # searchText=request.form['searchText']

        # text = "This is the database course, which teaches you about database management system"
        try:
            # response_search= Extractor.getEntities(searchText)
            # response = mongo.db.entity.find({"_id":"http://www.wikidata.org/entity/Q8513"})
            # response = mongo.db.entity.find({ str("label@it"): "base di dati"})
            # return render_template("index.html", result=dumps(response))
            # return response_search

            with open('searchResult.json', encoding="utf-8") as json_file:
                searchResult = json.load(json_file)
                return render_template("index.html", result=searchResult)

        except:

            return 'There as an error'

    else:
        return render_template("index.html", result=None)




