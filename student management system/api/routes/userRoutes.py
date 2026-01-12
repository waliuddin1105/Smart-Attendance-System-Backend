from flask import request
from flask_restx import Resource
from api import user_ns, db, auth_ns
from api.fields.userFields import UserSchema, user_data
from api.fields.loginFields import login_data, UserLoginSchema
from api.models.SMmodels import User
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token

@user_ns.route('/register')
class RegisterUser(Resource):
    @user_ns.doc('Registering a user')
    @user_ns.expect(user_data)
    def post(self):
        data = request.json

        try:
            validated_data = UserSchema().load(data)
        except ValidationError as e:
            return {"Error":e.messages}, 400
        
        if User.query.filter_by(username = validated_data['username']).first():
            return {"error": "Username already exists, choose another one."}, 409
        
        new_user = User(username = validated_data['username'])
        new_user.set_password(validated_data['password'])   #assigns password to self.password

        db.session.add(new_user)
        db.session.commit()
        return {"Success":"User registered succesfully!"}, 200

@auth_ns.route('/login')
class userLogin(Resource):
    @auth_ns.doc('Login existing user')
    @auth_ns.expect(login_data)
    def post(self):
        data = request.json
        
        try:
            validated_data = UserLoginSchema().load(data)
        except ValidationError as e:
            return {"Error":e.messages}, 401
        
        attempted_user = User.query.filter_by(username = validated_data['username']).first()
        
        if not attempted_user or not attempted_user.check_password(validated_data['password']):
            return {"Error": "Incorrect username or password"}, 401
        
        access_token = create_access_token(identity = str((attempted_user.id)))

        return {
            "Success":"Login sucessful",
            "access_token": access_token
        }, 200