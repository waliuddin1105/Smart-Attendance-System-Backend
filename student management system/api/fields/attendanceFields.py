from api import attendance_log_ns
from flask_restx import fields

attendance_log_data = attendance_log_ns.model(
    "Attendance log data",
    {
        "employee_id" : fields.Integer(required = True, description = "Enter employee id"),
        "timestamp" : fields.String(required = True, description = "The time the employee entered or left"),
        "type" : fields.String(required = True, description = "Entry or exit")
    }
)