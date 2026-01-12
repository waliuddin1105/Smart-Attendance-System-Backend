from flask import request, jsonify
from flask_restx import Resource
from api import db, shift_management_ns
from api.models.SMmodels import ShiftAssignment, Employee, Shifts
from api.fields.shiftManagementFields import shift_management_data
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

@shift_management_ns.route('/add')
class addShiftManagement(Resource):
    @jwt_required()
    @shift_management_ns.doc('Assign a new shift to an employee')
    @shift_management_ns.expect(shift_management_data)
    def post(self):
        user_id = get_jwt_identity()
        data  = request.json
        employee = Employee.query.get(data['employee_id'])
        shifts = Shifts.query.get(data['shift_id'])

        if not employee:
            return{"Error": f"Employee with id {data['employee_id']} does not exist!"}, 400
        
        if not shifts:
            return{"Error":f"Shift with id {data['shift_id']} does not exist!"}, 400
        
        try:
            new_date = datetime.strptime(data['date'], "%Y-%m-%d") 
        except ValueError as v:
            return {"Error":"Please enter date in the format %Y-%m-%d only!"}, 400

        new_shift_assigned = ShiftAssignment(employee_id = data['employee_id'], date = new_date , shift_id = data['shift_id'])
        db.session.add(new_shift_assigned)
        db.session.commit()

        return {"Success":"Shift assigned succesfully",
                "user_id" : user_id
                }, 200
    
@shift_management_ns.route('/assigned-shift/<int:id>')
class getAssignedShift(Resource):
    @jwt_required()
    @shift_management_ns.doc('Get details of an existing assigned shift')
    def get(self, id):
        user_id = get_jwt_identity()
        assigned_shift_to_get = ShiftAssignment.query.get(id)

        if not assigned_shift_to_get:
            return {"Error":f"An assigned shift with id {id} does not exist!"}, 400
        
        return {
            "user_id" : user_id,
            "id" : assigned_shift_to_get.id,
            "employee_id" : assigned_shift_to_get.employee_id,
            "date" : assigned_shift_to_get.date.strftime("%Y-%m-%d").date(),
            "shift_id" : assigned_shift_to_get.shift_id
        }, 200
    
@shift_management_ns.route('/delete/<int:id>')
class deleteAssignedShift(Resource):
    @jwt_required()
    @shift_management_ns.doc('Delete an existing assigned shift')
    def delete(self, id):
        user_id = get_jwt_identity()
        assigned_shift_to_delete = ShiftAssignment.query.get(id)

        if not assigned_shift_to_delete:
            return {"Error":f"An assigned shift with id {id} does not exist!"}, 400
        
        db.session.delete(assigned_shift_to_delete)
        db.session.commit()
        return {"Success": f"Assigned shift with id {id} deleted successfully!",
                "user_id" : user_id,
                }, 200
    
    
@shift_management_ns.route('/edit/<int:id>')
class editAssignedShift(Resource):
    @jwt_required()
    @shift_management_ns.doc('Edit an existing assigned shift')
    @shift_management_ns.expect(shift_management_data)
    def put(self, id):
        user_id = get_jwt_identity()
        assigned_shift_to_edit = ShiftAssignment.query.get(id)

        if not assigned_shift_to_edit:
            return {"Error":f"An assigned shift with id {id} does not exist!"}, 400

        data = request.json
        
        new_employee_id = data.get("employee_id", assigned_shift_to_edit.employee_id)
        employee = Employee.query.get(new_employee_id)
        if not employee:
            return {"Error":f"Employee with id {data['employee_id']} does not exist!"}
           #this is used if user does not want to edit the employee id
        
        new_date = data.get("date")
        if new_date:
            try:
                dates = datetime.strptime(data['date'], "%Y-%m-%d").date()
            except ValueError as v:
                return{"Error":"Please enter date in the format %Y-%m-%d only!"}, 400
            new_date = dates
        else:
            new_date = assigned_shift_to_edit.date

        new_shift_id = data.get("shift_id", assigned_shift_to_edit.shift_id)
        shift = Shifts.query.get(new_shift_id)
        if not shift:
            return {"Error":f"Shift  with id {data['shift_id']} does not exist!"}, 400
        
        assigned_shift_to_edit.employee_id = new_employee_id
        assigned_shift_to_edit.date = new_date
        assigned_shift_to_edit.shift_id = new_shift_id

        db.session.commit()

        return {"Success":f"Assigned shift with id {id} updated succesfully!",
                "user_id" : user_id,
                }, 200
    
@shift_management_ns.route('/display')
class displayAssignedShifts(Resource):
    @jwt_required()
    @shift_management_ns.doc("Display all assigned shifts")
    @shift_management_ns.param('page', 'enter a page to display by, default is 1')
    @shift_management_ns.param('per_page', 'enter how many entries per page, default is 3')
    @shift_management_ns.param('shift_id', 'Enter shift id to filter shift assigned to employees by shift id')
    def get(self):
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type = int)
        per_page = request.args.get('per_page', 3, type = int)
        shift_id = request.args.get('shift_id')

        query = ShiftAssignment.query
        if shift_id:
            query = query.filter_by(shift_id = shift_id)
        paginated_assigned_shifts = query.paginate(page = page, per_page = per_page, error_out = False)

        if not paginated_assigned_shifts.items:
            return {"Error":"No assigned shifts to show on this page"}, 400
        
        assigned_shifts_list = [
            {
                "id" : shift.id,
                "employee_id" : shift.employee_id,
                "date" : shift.date.strftime("%Y-%m-%d"),
                "shift_id" : shift.shift_id
            }
            for shift in paginated_assigned_shifts.items
        ]

        return {
                    "user_id": user_id,
                    "Assigned Shifts": assigned_shifts_list,
                    "page number" : page,
                    "per page" : per_page,
                    "total" : paginated_assigned_shifts.total,
                    "pages" : paginated_assigned_shifts.pages
                }, 200
