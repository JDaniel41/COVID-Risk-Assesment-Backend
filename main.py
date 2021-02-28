import json
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource


app = Flask(__name__)

# Google Cloud SQL
PASSWORD = os.environ['DB_PASS']

# configuration
app.config["SECRET_KEY"] = "yoursecretkey"
app.config["SQLALCHEMY_DATABASE_URI"]= "mysql+pymysql://root:{}@/main?unix_socket=/cloudsql/cusehacks-306121:us-central1:cusehacks-db".format(PASSWORD)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True

print(app.config["SQLALCHEMY_DATABASE_URI"])
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)

## API Models
class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    county = db.Column(db.String(50))
    state = db.Column(db.String(50))

    def __repr__(self):
        return '<Post %s>' & self.name

class BusinessReview(db.Model):
    reviewId = db.Column(db.Integer, primary_key=True)
    businessId = db.Column(db.Integer, db.ForeignKey('business.id'))
    socialDistance = db.Column(db.Integer)
    busy = db.Column(db.Integer)
    pickupOptions = db.Column(db.Integer)
    reviewText = db.Column(db.String(1000))


## API Schemas
class BusinessSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "county", "state")
        model = Business

class BusinessReviewSchema(ma.Schema):
    class Meta:
        fields = ("reviewId", "businessId", "socialDistance", "busy", "pickupOptions", "reviewText")
        model = BusinessReview

business_schema = BusinessSchema()
businesses_schema = BusinessSchema(many=True)

business_review_schema = BusinessReviewSchema()
business_reviews_schema = BusinessReviewSchema(many=True)

## API Resources
class BusinessListResource(Resource):
    def get(self):
        businesses = Business.query.all()
        response = businesses_schema.dump(businesses)
        response = jsonify(response)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    def post(self):
        new_business = Business (
            name=request.args.get('name'),
            county=request.args.get('county'),
            state=request.args.get('state')
        )
        db.session.add(new_business)
        db.session.commit()

        response = business_schema.dump(new_business)
        response = jsonify(response)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return business_schema.dump(new_business)

class BusinessResource(Resource):
    def get(self, business_id):
        business = Business.query.get_or_404(business_id)
        response = business_schema.dump(business)
        response = jsonify(response)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

class BusinessReviewListResource(Resource):
    def get(self):
        businessReviews = BusinessReview.query.all()

        response = business_reviews_schema.dump(businessReviews)
        response = jsonify(response)
        response.headers.add("Access-Control-Allow-Origin", "*")

        return response

    def post(self):
        new_review = BusinessReview(
            businessId = request.args.get('businessId'),
            socialDistance = request.args.get('socialDistance'),
            busy = request.args.get('busy'),
            pickupOptions = request.args.get('pickupOptions'),
            reviewText = request.args.get('reviewText')
        )
        db.session.add(new_review)
        db.session.commit()

        response = business_review_schema.dump(new_review)
        response = jsonify(response)
        response.headers.add("Access-Control-Allow-Origin", "*")

        return response

class BusinessReviewsForBusinessResource(Resource):
    def get(self, business_id):
        reviews = BusinessReview.query.filter(BusinessReview.businessId == business_id)

        response = business_reviews_schema.dump(reviews)
        response = jsonify(response)
        response.headers.add("Access-Control-Allow-Origin", "*")

        return response

api.add_resource(BusinessListResource, '/business')
api.add_resource(BusinessResource, '/business/<int:business_id>')
api.add_resource(BusinessReviewListResource, '/businessReview')
api.add_resource(BusinessReviewsForBusinessResource, '/businessReview/<int:business_id>')

if __name__ == '__main__':
    app.run(debug=True)
