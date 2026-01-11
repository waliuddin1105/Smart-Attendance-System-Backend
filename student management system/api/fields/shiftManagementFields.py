from sms import shift_management_ns
from flask_restx import fields

shift_management_data = shift_management_ns.model(
    'Shift Management data',
    {
        "employee_id" : fields.Integer(required = True, description = "Enter employee id with whose shift it is assigned to"),
        "date" : fields.String(required = True, description = "Enter the date (e.g. YYYY-MM-DD)"),
        "shift_id" : fields.Integer(required = True, description = "ID of the shift being assigned")
    }  
)