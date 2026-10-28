import re

from flask import Flask, request, Response, jsonify;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity;
from configuration import Configuration;
from models import database, User, UserRole;
from email.utils import parseaddr;
from sqlalchemy import and_;

application = Flask(__name__);
application.config.from_object(Configuration);

EMAIL_REGEX = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';

@application.route("/register", methods=["POST"])
def register( ):
    forename = request.json.get("forename", "");
    surname = request.json.get("surname", "");
    email = request.json.get("email", "");
    password = request.json.get("password", "");

    forename_empty = len(forename) == 0;
    surname_empty = len(surname) == 0;
    email_empty = len( email ) == 0;
    password_empty = len( password ) == 0;


    if (forename_empty):
        return jsonify(message = "Field forename is missing."), 400;
    if (surname_empty):
        return jsonify(message = "Field surname is missing."), 400;
    if(email_empty):
        return jsonify(message = "Field email is missing."), 400;
    if (password_empty):
        return jsonify(message = "Field password is missing."), 400;

    if not re.match(EMAIL_REGEX, email):
        return jsonify(message="Invalid email."), 400

    if(len( password ) < 8):
        return jsonify(message = "Invalid password."), 400;

    email_exists = User.query.filter(User.email == email).first();
    if email_exists:
        return jsonify(message = "Email already exists."), 400;

    user = User(forename = forename, surname = surname, email = email, password = password);
    database.session.add(user);
    database.session.commit();

    user_role = UserRole(userId = user.id, roleId = 2);
    database.session.add(user_role);
    database.session.commit();

    return Response(status=200);

jwt = JWTManager(application);

@application.route("/login", methods = ["POST"])
def login( ):
    email = request.json.get("email", "");
    password = request.json.get("password", "");

    email_empty = len(email) == 0;
    password_empty = len(password) == 0;

    if (email_empty):
        return jsonify(message = "Field email is missing."), 400;
    if (password_empty):
        return jsonify(message = "Field password is missing."), 400;

    if not re.match(EMAIL_REGEX, email):
        return jsonify(message="Invalid email."), 400;

    user = User.query.filter(and_(User.email == email, User.password == password)).first();
    if (not user):
        return jsonify(message = "Invalid credentials."), 400;

    additional_claims = {
        "forename": user.forename,
        "surname": user.surname,
        "roles": [ str(role) for role in user.roles ]
    };

    access_token = create_access_token(identity = user.email, additional_claims = additional_claims);

    return jsonify(accessToken = access_token), 200;

@application.route("/delete", methods = ["POST"])
@jwt_required()
def delete( ):
    email = get_jwt_identity();

    user = User.query.filter(User.email == email).first();

    if (not user):
        return jsonify(message = "Unknown user."), 400;

    UserRole.query.filter(UserRole.userId == user.id).delete();

    database.session.delete(user);
    database.session.commit();

    return Response(status=200);

if (__name__ == "__main__"):
    database.init_app(application);
    application.run(debug=True, host = "0.0.0.0", port = 5000);