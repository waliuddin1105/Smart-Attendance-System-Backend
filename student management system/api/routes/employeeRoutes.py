from api import employee_ns, db
from flask import request
from flask_restx import Resource
from api.models.SMmodels import Employee
from api.fields.employeeFields import employee_data
from flask_jwt_extended import jwt_required, get_jwt_identity

@employee_ns.route('/add')
class AddEmployee(Resource):
    @jwt_required()
    @employee_ns.doc("Adding a new employee")
    @employee_ns.expect(employee_data)

    def post(self):
        user_id = get_jwt_identity()
        data = request.json
        new_employee = Employee(name = data["name"], role = data["role"], department = data["department"])
        db.session.add(new_employee)
        db.session.commit()

        return {"Success" : "Employee added successfully",
                "user_id" : user_id
                }, 200
    
@employee_ns.route('/get/<int:id>')
class getEmployeeData(Resource):
    @jwt_required()
    @employee_ns.doc("Getting employee data")
    def get(self,id):
        user_id = get_jwt_identity()
        employee_to_get = Employee.query.get(id)
        if not employee_to_get:
            return {"Error":f"Employee with ID:{id} does not exist!"}, 400
        
        employee_list = [
            {
                "name": employee_to_get.name,
                "role": employee_to_get.role,
                "department": employee_to_get.department
            }
        ]

        return {"user_id" : user_id,
                f"Employee with id:{id}":employee_list}
    
@employee_ns.route('/delete/<int:id>')
class deleteEmployee(Resource):
    @jwt_required()
    @employee_ns.doc("Delete an employee")
    def delete(self, id):
        user_id = get_jwt_identity()
        employee_to_delete = Employee.query.get(id)

        if not employee_to_delete:
            return {"Error":f"Employee with id:{id} does not exist!"}, 400
        
        db.session.delete(employee_to_delete)
        db.session.commit()

        return{"Success":f"Employee with id {id} Deleted successfully",
               "user_id" : user_id
               }, 200
    
@employee_ns.route('/edit/<int:id>')
class EditEmployee(Resource):
    @jwt_required()
    @employee_ns.doc("Editing an employee")
    @employee_ns.expect(employee_data)
    def put(self, id):
        user_id = get_jwt_identity()
        employee_to_edit = Employee.query.get(id)
        if not employee_to_edit:
            return {"Error":f"Employee with id:{id} does not exist!"}, 400
        
        data = request.json

        new_name = data.get("name", employee_to_edit.name)
        new_role = data.get("role", employee_to_edit.role)
        new_department = data.get("department", employee_to_edit.department)

        employee_to_edit.name = new_name
        employee_to_edit.role = new_role
        employee_to_edit.department = new_department    
        db.session.commit()
        return {"Success": f"Employee with id {id} edited!",
                "user_id" : user_id
                }, 200

@employee_ns.route('/display')
class displayEmployees(Resource):
    @jwt_required()
    @employee_ns.doc("Displaying employees")
    @employee_ns.param('page', 'enter a page to display by, default is 1')
    @employee_ns.param('per_page', 'enter how many entries per page, default is 3')
    @employee_ns.param('department', 'Enter department to filter employees')
    @employee_ns.param('role', 'Enter role to filter employees')
    def get(self):
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type = int)
        per_page = request.args.get('per_page', 3, type = int)
        department = request.args.get('department')
        role = request.args.get('role')

        query = Employee.query
        if department:
            query = query.filter_by(department = department)
        if role:    
            query = query.filter_by(role = role)

        paginated_employees = query.paginate(page = page, per_page = per_page, error_out = False)

        if not paginated_employees.items:
            return {"Error":"No employees to show on this page"}, 400
        
        employees_list = [
            {
                "name" : employee.name,
                "role" : employee.role,
                "department" : employee.department
            }
            for employee in paginated_employees.items
        ]

        return {
            "user_id" : user_id,
            "employees" : employees_list,
            "page number" : page,
            "per page" : per_page,
            "total" : paginated_employees.total,
            "pages" :paginated_employees.pages
        }, 200