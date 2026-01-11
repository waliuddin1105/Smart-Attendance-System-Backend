from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_restx import Namespace, Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from celery_config import make_celery

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:14Nov%402005@localhost:5432/studentManagement_db"
app.config['JWT_SECRET_KEY'] = '3475db22d42f64964f4'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

authorizations = {
    'bearer authorizations':
    {
        'type' : 'apiKey',
        'in' : 'header',
        'name' : 'Authorization',
        'description' : '*Bearer* <type your bearer token here>'
    }
}
api = Api(
    app,
    version='1.0',
    title="Smart Attendance management",
    description="Api for smart attendance management",
    authorizations=authorizations,
    security= 'bearer authorizations' #this makes sure that we dont need to authorize for every route every time
)
jwt = JWTManager(app)

employee_ns = Namespace('Employee', description = 'Data about the employee')
api.add_namespace(employee_ns, path = '/employee')

shifts_ns = Namespace('Shifts', description= "Data about the shifts")
api.add_namespace(shifts_ns, '/shifts')

shift_management_ns = Namespace("Shift Assignment", description = "Assignment of shifts to employees")
api.add_namespace(shift_management_ns, '/shift-management')

attendance_log_ns = Namespace('Attendance Log', description = "Maintain and keep record of attendance logs")
api.add_namespace(attendance_log_ns,'/attendance-log')

user_ns = Namespace('User', description = 'Users using the api')
api.add_namespace(user_ns, '/user')

celery = make_celery(app)

auth_ns = Namespace('Authorization', description = 'user authorization')
api.add_namespace(auth_ns, '/auth')
import api.routes.employeeRoutes
import api.routes.shiftsRoutes
import api.routes.shiftManagementRoutes
import api.routes.attendanceRoutes
import api.routes.userRoutes
import api.models.SMmodels