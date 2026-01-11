from flask_restx import fields
from api import shifts_ns

shifts_data = shifts_ns.model(
    "Shifts Data",
    {
        "name" : fields.String(required = True, description = "Enter shift name i.e Morning, Evening etc"),
        "start_time" : fields.String(required = True, description = "Enter start time of the shift"),
        "end_time" : fields.String(required = True, description = "Enter end time of the shift")
    }
)