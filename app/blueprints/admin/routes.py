from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Property, Booking
from . import admin
from app.email import send_email

@admin.before_request
def require_admin():
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))

@admin.route('/admin/dashboard')
@login_required
def dashboard():
    total_users = User.query.count()
    total_properties = Property.query.count()
    total_bookings = Booking.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_properties = Property.query.order_by(Property.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_properties=total_properties,
                         total_bookings=total_bookings,
                         recent_users=recent_users,
                         recent_properties=recent_properties)

@admin.route('/admin/users')
@login_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=10)
    return render_template('admin/users.html', users=users)

@admin.route('/admin/properties')
@login_required
def manage_properties():
    page = request.args.get('page', 1, type=int)
    properties = Property.query.paginate(page=page, per_page=10)
    return render_template('admin/properties.html', properties=properties)

@admin.route('/admin/bookings')
@login_required
def manage_bookings():
    page = request.args.get('page', 1, type=int)
    bookings = Booking.query.paginate(page=page, per_page=10)
    return render_template('admin/bookings.html', bookings=bookings)

@admin.route('/admin/bookings/<int:booking_id>/update-status', methods=['POST'])
@login_required
def update_booking_status(booking_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    booking = Booking.query.get_or_404(booking_id)
    status = request.json.get('status')
    
    if status not in ['approved', 'rejected']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    
    booking.status = status
    db.session.commit()
    
    # Send email notification to the user
    subject = 'Booking Status Update'
    if status == 'approved':
        message = f'Your booking for {booking.property.title} has been approved.'
    else:
        message = f'Your booking for {booking.property.title} has been rejected.'
    
    send_email(
        subject=subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[booking.user.email],
        text_body=message,
        html_body=f'<p>{message}</p>'
    )
    
    return jsonify({
        'success': True,
        'message': f'Booking has been {status}'
    })


@admin.route('/admin/analytics')
@login_required
def analytics():
    # Get overall statistics
    total_properties = Property.query.count()
    total_users = User.query.count()
    total_bookings = Booking.query.count()
    total_payments = Payment.query.count()
    
    # Get monthly statistics
    current_month = datetime.utcnow().month
    monthly_properties = Property.query.filter(extract('month', Property.created_at) == current_month).count()
    monthly_users = User.query.filter(extract('month', User.created_at) == current_month).count()
    monthly_bookings = Booking.query.filter(extract('month', Booking.created_at) == current_month).count()
    monthly_revenue = db.session.query(func.sum(Payment.amount)).filter(
        extract('month', Payment.created_at) == current_month
    ).scalar() or 0
    
    return render_template('admin/analytics.html',
                         total_properties=total_properties,
                         total_users=total_users,
                         total_bookings=total_bookings,
                         total_payments=total_payments,
                         monthly_properties=monthly_properties,
                         monthly_users=monthly_users,
                         monthly_bookings=monthly_bookings,
                         monthly_revenue=monthly_revenue)

@admin.route('/admin/analytics/data')
@login_required
def analytics_data():
    data_type = request.args.get('type', 'properties')
    period = request.args.get('period', 'monthly')
    
    if period == 'monthly':
        labels = [calendar.month_name[i] for i in range(1, 13)]
        if data_type == 'properties':
            data = get_monthly_properties()
        elif data_type == 'bookings':
            data = get_monthly_bookings()
        elif data_type == 'revenue':
            data = get_monthly_revenue()
    
    return jsonify({
        'labels': labels,
        'data': data
    })