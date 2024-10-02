# app/routes.py

from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import login_required, login_user, logout_user, current_user
from .models import Employee, Admin, Attendance, LeaveRequest, Notification
from . import db, login_manager
from datetime import datetime, date, time
from sqlalchemy import and_

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    if session.get('user_type') == 'employee':
        return Employee.query.get(int(user_id))
    else:
        return Admin.query.get(int(user_id))

@main.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Employee.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            session['user_type'] = 'employee'
            return redirect(url_for('main.employee_dashboard'))

        user = Admin.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            session['user_type'] = 'admin'
            return redirect(url_for('main.admin_dashboard'))

        flash('Invalid credentials')
        return render_template('login.html')
    return render_template('login.html')

@main.route('/employee_dashboard')
@login_required
def employee_dashboard():
    if session.get('user_type') != 'employee':
        return redirect(url_for('main.login'))
    return render_template('employee_dashboard.html')

@main.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))
    return render_template('admin_dashboard.html')

@main.route('/check_in', methods=['GET', 'POST'])
@login_required
def check_in():
    if session.get('user_type') != 'employee':
        return redirect(url_for('main.login'))

    current_time = datetime.now()
    check_in_deadline = datetime.combine(date.today(), time(10, 15))

    # Check if the employee has already checked in today
    existing_attendance = Attendance.query.filter_by(
        employee_id=current_user.id,
        date=current_time.date()
    ).first()

    if existing_attendance and existing_attendance.check_in_time:
        flash('You have already checked in today.')
        return redirect(url_for('main.employee_dashboard'))

    if current_time.time() < time(7, 0):
        flash('You cannot check in before 7:00 AM.')
        return redirect(url_for('main.employee_dashboard'))

    if current_time > check_in_deadline:
        if request.method == 'POST':
            # Request for late check-in
            existing_attendance = Attendance(
                employee_id=current_user.id,
                date=current_time.date(),
                late_check_in_requested=True
            )
            db.session.add(existing_attendance)
            db.session.commit()
            flash('Late check-in request submitted for approval.')
            return redirect(url_for('main.employee_dashboard'))
        else:
            return render_template('late_check_in_request.html')

    # Normal check-in
    attendance = Attendance(
        employee_id=current_user.id,
        date=current_time.date(),
        check_in_time=current_time
    )
    db.session.add(attendance)
    db.session.commit()
    return render_template('check_in.html', check_in_time=current_time)

@main.route('/check_out')
@login_required
def check_out():
    if session.get('user_type') != 'employee':
        return redirect(url_for('main.login'))

    current_time = datetime.now()

    # Retrieve today's attendance record
    attendance = Attendance.query.filter_by(
        employee_id=current_user.id,
        date=current_time.date()
    ).first()

    if not attendance or not attendance.check_in_time:
        flash('You need to check in before checking out.')
        return redirect(url_for('main.employee_dashboard'))

    if attendance.check_out_time:
        flash('You have already checked out today.')
        return redirect(url_for('main.employee_dashboard'))

    attendance.check_out_time = current_time
    db.session.commit()
    return render_template('check_out.html', check_out_time=current_time)

@main.route('/leave_request', methods=['GET', 'POST'])
@login_required
def leave_request():
    if session.get('user_type') != 'employee':
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        reason = request.form['reason']

        leave = LeaveRequest(
            employee_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )
        db.session.add(leave)
        db.session.commit()

        flash('Leave request submitted.')
        return redirect(url_for('main.employee_dashboard'))

    return render_template('leave_request.html')

@main.route('/notifications')
@login_required
def notifications():
    if session.get('user_type') != 'employee':
        return redirect(url_for('main.login'))

    notifications = Notification.query.filter_by(employee_id=current_user.id).order_by(Notification.date.desc()).all()
    return render_template('notifications.html', notifications=notifications)

@main.route('/attendance_records')
@login_required
def attendance_records():
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))

    # Filter by custom date range if provided
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    attendances = Attendance.query
    if start_date and end_date:
        attendances = attendances.filter(
            and_(
                Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
                Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date()
            )
        )
    attendances = attendances.order_by(Attendance.date.desc()).all()
    return render_template('attendance_records.html', attendances=attendances)

@main.route('/manage_late_check_ins')
@login_required
def manage_late_check_ins():
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))

    late_requests = Attendance.query.filter_by(
        late_check_in_requested=True,
        late_check_in_approved=False
    ).order_by(Attendance.date.desc()).all()
    return render_template('manage_late_check_ins.html', late_requests=late_requests)

@main.route('/approve_late_check_in/<int:attendance_id>')
@login_required
def approve_late_check_in(attendance_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))

    attendance = Attendance.query.get(attendance_id)
    if attendance:
        attendance.late_check_in_approved = True
        attendance.check_in_time = datetime.now()
        attendance.late_check_in_requested = False

        # Send notification to employee
        notification = Notification(
            employee_id=attendance.employee_id,
            message='Your late check-in request has been approved.',
            date=datetime.now()
        )
        db.session.add(notification)
        db.session.commit()

        flash('Late check-in approved.')
    return redirect(url_for('main.manage_late_check_ins'))

@main.route('/reject_late_check_in/<int:attendance_id>')
@login_required
def reject_late_check_in(attendance_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))

    attendance = Attendance.query.get(attendance_id)
    if attendance:
        # Send notification to employee
        notification = Notification(
            employee_id=attendance.employee_id,
            message='Your late check-in request has been rejected.',
            date=datetime.now()
        )
        db.session.add(notification)
        db.session.delete(attendance)
        db.session.commit()

        flash('Late check-in rejected.')
    return redirect(url_for('main.manage_late_check_ins'))

@main.route('/manage_leave_requests')
@login_required
def manage_leave_requests():
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))

    leave_requests = LeaveRequest.query.order_by(LeaveRequest.start_date.desc()).all()
    return render_template('manage_leave_requests.html', leave_requests=leave_requests)

@main.route('/approve_leave/<int:leave_id>')
@login_required
def approve_leave(leave_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))

    leave = LeaveRequest.query.get(leave_id)
    if leave:
        leave.status = 'Approved'

        # Send notification to employee
        notification = Notification(
            employee_id=leave.employee_id,
            message='Your leave request has been approved.',
            date=datetime.now()
        )
        db.session.add(notification)
        db.session.commit()

        flash('Leave request approved.')
    return redirect(url_for('main.manage_leave_requests'))

@main.route('/reject_leave/<int:leave_id>')
@login_required
def reject_leave(leave_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))

    leave = LeaveRequest.query.get(leave_id)
    if leave:
        leave.status = 'Rejected'

        # Send notification to employee
        notification = Notification(
            employee_id=leave.employee_id,
            message='Your leave request has been rejected.',
            date=datetime.now()
        )
        db.session.add(notification)
        db.session.commit()

        flash('Leave request rejected.')
    return redirect(url_for('main.manage_leave_requests'))

@main.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_type', None)
    return redirect(url_for('main.login'))
