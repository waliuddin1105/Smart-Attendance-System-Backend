from api import employee_ns
from flask_restx import fields

employee_data = employee_ns.model(
    "Add Employee Data",
    {
        "name" : fields.String(required = True, description = "Enter employee name"),
        "role" : fields.String(required = True, description = "Enter employee role"),
        "department" : fields.String(required = True, description = "Enter employee department")   
    } 
)
