from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Property, Booking
from . import agent

@agent.before_request
def require_agent():
    if not current_user.is_authenticated or current_user.role != 'agent':
        flash('Access denied. Agent privileges required.', 'danger')
        return redirect(url_for('main.index'))

@agent.route('/agent/dashboard')
@login_required
def dashboard():
    total_properties = Property.query.filter_by(owner_id=current_user.id).count()
    total_bookings = Booking.query.join(Property).filter(Property.owner_id == current_user.id).count()
    recent_properties = Property.query.filter_by(owner_id=current_user.id).order_by(Property.created_at.desc()).limit(5).all()
    recent_bookings = Booking.query.join(Property).filter(Property.owner_id == current_user.id).order_by(Booking.created_at.desc()).limit(5).all()
    
    return render_template('agent/dashboard.html',
                         total_properties=total_properties,
                         total_bookings=total_bookings,
                         recent_properties=recent_properties,
                         recent_bookings=recent_bookings)

@agent.route('/agent/properties')
@login_required
def manage_properties():
    page = request.args.get('page', 1, type=int)
    properties = Property.query.filter_by(owner_id=current_user.id).paginate(page=page, per_page=10)
    return render_template('agent/properties.html', properties=properties)

@agent.route('/agent/bookings')
@login_required
def manage_bookings():
    page = request.args.get('page', 1, type=int)
    bookings = Booking.query.join(Property).filter(Property.owner_id == current_user.id).paginate(page=page, per_page=10)
    return render_template('agent/bookings.html', bookings=bookings)