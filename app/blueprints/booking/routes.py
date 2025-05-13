from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Booking, Property
from datetime import datetime
from . import booking

@booking.route('/booking/<int:property_id>', methods=['GET', 'POST'])
@login_required
def schedule_viewing(property_id):
    property = Property.query.get_or_404(property_id)
    
    if request.method == 'POST':
        date_str = request.form.get('viewing_date')
        time_str = request.form.get('viewing_time')
        
        try:
            booking_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            booking = Booking(
                user_id=current_user.id,
                property_id=property_id,
                booking_date=booking_datetime,
                status='pending'
            )
            
            db.session.add(booking)
            db.session.commit()
            
            flash('Viewing request submitted successfully!', 'success')
            return redirect(url_for('property.view_property', property_id=property_id))
            
        except ValueError:
            flash('Invalid date or time format', 'danger')
    
    return render_template('booking/schedule.html', property=property)

@booking.route('/booking/check-availability', methods=['POST'])
@login_required
def check_availability():
    date = request.json.get('date')
    property_id = request.json.get('property_id')
    
    # Get all bookings for the selected date
    bookings = Booking.query.filter(
        Booking.property_id == property_id,
        Booking.booking_date.like(f"{date}%")
    ).all()
    
    # Get booked times
    booked_times = [b.booking_date.strftime("%H:%M") for b in bookings]
    
    return jsonify({'booked_times': booked_times})