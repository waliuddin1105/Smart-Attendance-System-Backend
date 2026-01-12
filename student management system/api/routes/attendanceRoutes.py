from flask import request
from flask_restx import Resource
from api.models.SMmodels import db, Employee, AttendanceLog, AttendanceLogType#for enum
from api.fields.attendanceFields import attendance_log_data
from api import attendance_log_ns
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

@attendance_log_ns.route('/add')
class addAttendnace(Resource):
    @jwt_required()
    @attendance_log_ns.doc("Add an attendance log")
    @attendance_log_ns.expect(attendance_log_data)
    def post(self):

        user_id = get_jwt_identity()
        data = request.json
        
        employee  = Employee.query.get(data['employee_id'])
        if not employee:
            return {"Error":f"Employee with id {data['employee_id']} does not exist"}, 400
        
        try:
            new_timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S")
        except ValueError as v:
            return {"Error":"Please enter timestamp in the format YYYY-MM-DD HH:MM:SS only!"}, 400
        
        new_type = data['type']
        new_type = new_type.lower()
        if new_type not in ['entry', 'exit']:
            return {"Error":"Type can only be entry or exit"}, 400
        
        new_attendance_log = AttendanceLog(employee_id = data['employee_id'], timestamp = new_timestamp, type = new_type)
        db.session.add(new_attendance_log)
        db.session.commit()

        return {"Success":"Attendnace log added successfully!",
                "user_id":user_id
                }, 200
    
@attendance_log_ns.route('/attendance-log/<int:id>')
class getAttendanceLog(Resource):
    @jwt_required()
    @attendance_log_ns.doc("Get an existing attendance log")
    def get(self, id):
        user_id = get_jwt_identity()
        attendance_log_to_get = AttendanceLog.query.get(id)

        if not attendance_log_to_get:
            return {"Error":f"Attendance log with id {id} does not exist!"}, 400
        
        return {
            "user_id":user_id,
            "id" : attendance_log_to_get.id,
            "employee_id" : attendance_log_to_get.employee_id,
            "timestamp" : attendance_log_to_get.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "type" : attendance_log_to_get.type.value #conert enum to string for json
        }, 200
    
@attendance_log_ns.route('/delete/<int:id>')
class deleteAttendanceLog(Resource):
    @jwt_required()
    @attendance_log_ns.doc("Delete an existing attendance log")
    def delete(self, id):
        user_id = get_jwt_identity()
        attendance_log_to_delete = AttendanceLog.query.get(id)

        if not attendance_log_to_delete:
            return {"Error":f"Attendance log with id {id} does not exist!"}, 400
        
        db.session.delete(attendance_log_to_delete)
        db.session.commit()

        return {"Success":f"Attendance log with id {id} deleted succesfully!",
                "user_id":user_id,
                }, 200
    
@attendance_log_ns.route('/edit/<int:id>')
class editAttendanceLog(Resource):
    @jwt_required()
    @attendance_log_ns.doc("Edit an existing attendnace log")
    @attendance_log_ns.expect(attendance_log_data)
    def put(self, id):
        user_id = get_jwt_identity()
        attendance_log_to_edit = AttendanceLog.query.get(id)

        if not attendance_log_to_edit:
            return {"Error":f"Attendance log with id {id} does not exist!"}, 400
        
        data = request.json
        new_employee_id = data.get("employee_id", attendance_log_to_edit.employee_id)
        employee = Employee.query.get(new_employee_id)
        if not employee:
            return {"Error":f"Employee with id {new_employee_id} does not exsit!"}, 400
        
        timestamps = data.get('timestamp')
        if timestamps:
            try:
                timestamps = datetime.strptime(timestamps, "%Y-%m-%d %H:%M:%S")
            except ValueError as v:
                return {"Error":"Please enter timestamp in the format YYYY-MM-DD HH:MM:SS only!"}, 400
            new_timestamp = timestamps
        else:
            new_timestamp = attendance_log_to_edit.timestamp

        new_type = data.get("type", attendance_log_to_edit.type.value)
        new_type = new_type.lower()
        if new_type not in ['entry', 'exit']:
            return {"Error":"Type can be entry or exit only!"}, 400
        
        attendance_log_to_edit.employee_id = new_employee_id
        attendance_log_to_edit.timestamp = new_timestamp
        attendance_log_to_edit.type = AttendanceLogType(new_type)   #Due to enum

        db.session.commit() 
        return {"Success":f"Attendance log with id {id} edited successfully!",
                "user_id":user_id,
                }, 200    

@attendance_log_ns.route('/display')
class displayAttendanceLogs(Resource):
    @jwt_required()
    @attendance_log_ns.doc("Display attendance logs")
    @attendance_log_ns.param('page', 'enter a page to display by, default is 1')
    @attendance_log_ns.param('per_page', 'enter how many entries per page, default is 3')
    @attendance_log_ns.param('type', 'Enter type  to filter type of attendance entry or exit')
    def get(self):
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type = int)
        per_page = request.args.get('per_page', 3, type = int)
        types = request.args.get('type')

        query = AttendanceLog.query
        
        if type:
            try:
                types = AttendanceLogType(types.lower())
                query = query.filter_by(type = types)
            except ValueError as v:
                return {"Error":"Type can be entry or exit only!"}, 400

        paginated_attendance_log = query.paginate(page = page, per_page = per_page, error_out = False)

        if not paginated_attendance_log.items:
            return {"Error":"No employees to show on this page"}, 400
        
        attendance_logs_list = [
            {
                "id" : attendance_log.id,
                "employee_id" : attendance_log.employee_id,
                "timestamp" : attendance_log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "type" :attendance_log.type.value
            }
            for attendance_log in paginated_attendance_log.items
        ]
        return {
                    "user_id":user_id,
                    "Attendance Logs":attendance_logs_list,
                    "page number" : page,
                    "per page" : per_page,
                    "total" : paginated_attendance_log.total,
                    "pages" : paginated_attendance_log.pages
                }, 200