from flask import Flask, request, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "\x82\xdc\x15\xc6\x179m\xbf}SxM7}\xb0o\xa2\x87\xfd\t;3\xf6\xc4"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employee_leave.sqlite'
db = SQLAlchemy(app)
app.app_context().push()

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    leave_balance = db.Column(db.Integer, default=26)  

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    start_date = db.Column(db.String(50), nullable=False)
    end_date = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(10), default='درحال بررسی')  

    employee = db.relationship('Employee', backref=db.backref('leave_request', lazy=True))

db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/members')
def members_view():
    members = Employee.query.all()
    return render_template('members.html', members=members)

@app.route('/leave-list')
def leaves_list_view():
    leaves = LeaveRequest.query.all()
    return render_template('leaves_list.html', leaves=leaves)

@app.route('/create-member')
def create_member_view():
    return render_template('create_member.html')

@app.route('/create-member', methods=['POST'])
def create_member():
    data = request.form
    emp = Employee(name=data.get('name'))
    db.session.add(emp)
    db.session.commit()

    flash('کارمند جدید با موفقیت ثبت شد !')
    return redirect(url_for('members_view'))

@app.route('/create-leave')
def request_leave_view():
    members = Employee.query.all()
    return render_template('create_leave.html', members=members)
    

@app.route('/request_leave', methods=['POST'])
def request_leave():
    data = request.form
    employee_id = data.get('employee_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    employee = Employee.query.get(employee_id)
    if not employee:
        flash('کارمند پیدا نشد!')
        return redirect(url_for('request_leave_view'))

    leave_duration = (int(end_date.replace('-','')) - int(start_date.replace('-',''))) + 1

    if leave_duration > employee.leave_balance:
        flash('!تعداد درخواست مرخصی بیش از حد مجاز می باشد')
        return redirect(url_for('request_leave_view'))
    
    leave_request = LeaveRequest(employee_id=employee_id, start_date=start_date, end_date=end_date)
    db.session.add(leave_request)

    db.session.commit()

    flash('درخواست مرخصی با موفقیت ثبت شد!')
    return redirect(url_for('leaves_list_view'))

@app.route('/approve_leave/<int:request_id>')
def approve_leave(request_id):
    leave_request = LeaveRequest.query.get(request_id)
    if not leave_request:
        flash('درخواست مرخصی پیدا نشد!')
        return redirect(url_for('leaves_list_view'))
    
    start_date = leave_request.start_date 
    end_date = leave_request.end_date
    leave_duration = (int(end_date.replace('-','')) - int(start_date.replace('-',''))) + 1

    if leave_duration > leave_request.employee.leave_balance:
        flash('تعداد درخواست مرخصی بیش ار حد مجاز است!')
        return redirect(url_for('request_leave_view'))

    leave_request.employee.leave_balance = leave_request.employee.leave_balance - leave_duration

    leave_request.status = 'قبول درخواست'
    db.session.commit()

    flash('با مرخصی موافقت شد!')
    return redirect(url_for('leaves_list_view'))

@app.route('/deny_leave/<int:request_id>')
def deny_leave(request_id):
    leave_request = LeaveRequest.query.get(request_id)
    if not leave_request:
        flash('درخواست مرخصی پیدا نشد!')
        return redirect(url_for('leaves_list_view'))

    leave_request.status = 'رد درخواست'
    db.session.commit()

    flash('با مرخصی موافقت نشد!')
    return redirect(url_for('leaves_list_view'))

if __name__ == '__main__':
    app.run(debug=True)
