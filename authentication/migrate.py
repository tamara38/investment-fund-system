from flask import Flask
from sqlalchemy_utils import database_exists, create_database

from models import Role, User, UserRole;
from configuration import Configuration;

from models import database;

from flask_migrate import Migrate, init, upgrade, migrate;

application = Flask ( __name__ );
application.config.from_object ( Configuration );

migrate_obj = Migrate ( application, database );

if (not database_exists( application.config["SQLALCHEMY_DATABASE_URI"] ) ):
	create_database( application.config["SQLALCHEMY_DATABASE_URI"] );

database.init_app( application );

with application.app_context() as context:
	init();
	migrate (message = "Production migration");
	upgrade();

	director_role = Role( name = "director");
	employee_role = Role( name = "employee");

	database.session.add( director_role);
	database.session.add( employee_role);
	database.session.commit();

	director = User(
		forename = "Scrooge",
		surname = "McDuck",
		email = "onlymoney@gmail.com",
		password = "evenmoremoney"
	);

	database.session.add( director);
	database.session.commit();

	user_role = UserRole( userId = director.id, roleId = director_role.id);

	database.session.add(user_role);
	database.session.commit();
