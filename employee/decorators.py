from functools import wraps

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt


def role_check ( role ):
    def decorator ( function ):
        @jwt_required ( )
        @wraps ( function )
        def wrapper ( *args, **kwargs ):
            # verify_jwt_in_request ( )
            claims = get_jwt ( )
            if ( role in claims["roles"] ):
                return function ( *args, **kwargs )
            else:
                return jsonify({"msg": "Missing Authorization Header"}), 401

        return wrapper

    return decorator