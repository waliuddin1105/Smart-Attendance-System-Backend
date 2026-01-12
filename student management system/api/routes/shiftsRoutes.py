from flask import request
from sms import db, shifts_ns
from flask_restx import Resource
from sms.schemas.shiftFields import shifts_data
from sms.models.SMmodels import Shifts
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

@shifts_ns.route('/add')
class addShift(Resource):
    @jwt_required()
    @shifts_ns.doc('Add a shift')
    @shifts_ns.expect(shifts_data)
    def post(self):
        user_id = get_jwt_identity()
        data = request.json
        
        try:    #converting string of time into time
            start = datetime.strptime(data['start_time'], "%H:%M").time()    #.time() only cuts the time part and excludes the date , strp parses string to datetime method of %H%M
            end = datetime.strptime(data["end_time"], "%H:%M").time()

        except ValueError as v:
            return {"Error":v}, 400
        
        new_shift = Shifts(name = data['name'], start_time = start, end_time = end)
        db.session.add(new_shift)
        db.session.commit()

        return {"Sucess":"Shift added successfully!",
                "user_id" : user_id
                }, 200
    
@shifts_ns.route('/get-shift/<int:id>')
class getShift(Resource):
    @jwt_required()
    @shifts_ns.doc('Get data of a particular shift')
    def get(self, id):
        user_id = get_jwt_identity()
        shift_to_get = Shifts.query.get(id)
        if not shift_to_get:
            return {"Error":f"Shift with id {id} does not exist"}, 400
        
        shifts = [
            {
                "name" : shift_to_get.name,
                "start_time" : shift_to_get.start_time.strftime("%H:%M"),
                "end_time" :   shift_to_get.end_time.strftime("%H:%M")
            }
        ]
        
        return{f"Shift with id {id}": shifts,
               "user_id" : user_id
               }, 200
    
@shifts_ns.route('/delete/<int:id>')
class deleteShift(Resource):
    @jwt_required()
    @shifts_ns.doc('Delete a shift')
    def delete(seld, id):
        user_id = get_jwt_identity()
        shift_to_delete = Shifts.query.get(id)
        if not shift_to_delete:
            return {"Error" :f"Shift with id {id} does not exist"}, 400
        
        db.session.delete(shift_to_delete)
        db.session.commit()
        return {"Success" : f"Shift with id {id} deleted succesfully!",
                "user_id" : user_id
                }, 200
    
@shifts_ns.route('/edit/<int:id>')
class editShift(Resource):
    @jwt_required()
    @shifts_ns.doc("Edit a shift")
    @shifts_ns.expect(shifts_data)
    def put(self, id):
        user_id = get_jwt_identity()
        shift_to_update = Shifts.query.get(id)
        if not shift_to_update:
            return {"Error":f"Shift with id {id} does not exist"}, 400
        
        data = request.json
        new_name = data.get("name", shift_to_update.name)
        start = datetime.strptime(data["start_time"], "%H:%M").time()
        end = datetime.strptime(data["end_time"], "%H:%M").time()
        new_start = data.get("start_time", start)
        new_end = data.get("end_time", end)

        shift_to_update.name = new_name
        shift_to_update.start_time = new_start
        shift_to_update.end_time = new_end

        db.session.commit()
        return {"Success":f"Shift with id {id} edited succesfully!",
                "user_id" : user_id}, 200
    
@shifts_ns.route('/display')
class dsiplayShifts(Resource):
    @jwt_required()
    @shifts_ns.doc("Display shifts")
    @shifts_ns.param('page', 'enter a page to display by, default is 1')
    @shifts_ns.param('per_page', 'enter how many entries per page, default is 3')
    @shifts_ns.param('name', 'Enter shift name to filter shifts by morning, evening or noon')
    def get(self):
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type = int)
        per_page = request.args.get('per_page', 3, type = int)
        name = request.args.get('name')

        query = Shifts.query
        if name:
            query = query.filter_by(name = name)

        paginated_shifts = query.paginate(page=page, per_page=per_page, error_out=False)

        if not paginated_shifts.items:
            return {"Error":"Nothing to display on this page"}, 400
        
        shifts_list = [
            {
                "name" : shift.name,
                "start_time" : shift.start_time.strftime("%H:%M"),
                "end_time" : shift.end_time.strftime("%H:%M")
            }
            for shift in paginated_shifts.items
        ]
        

        return {
                    "user_id" : user_id,
                    "Shifts" : shifts_list,
                    "page" : page,
                    "per_page" : per_page,
                    "pages" : paginated_shifts.pages,
                    "total" : paginated_shifts.total
            }, 200