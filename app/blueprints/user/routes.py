from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Booking, Property
from . import user

@user.route('/user/dashboard')
@login_required
def dashboard():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).limit(5).all()
    favorite_properties = current_user.favorite_properties[:5]
    return render_template('user/dashboard.html',
                         bookings=bookings,
                         favorite_properties=favorite_properties)

@user.route('/user/bookings')
@login_required
def my_bookings():
    page = request.args.get('page', 1, type=int)
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(
        Booking.created_at.desc()
    ).paginate(page=page, per_page=10)
    return render_template('user/bookings.html', bookings=bookings)

@user.route('/user/favorites')
@login_required
def my_favorites():
    page = request.args.get('page', 1, type=int)
    favorite_properties = Property.query.join(favorites).filter(
        favorites.c.user_id == current_user.id
    ).paginate(page=page, per_page=10)
    return render_template('user/favorites.html', properties=favorite_properties)

@user.route('/favorite/<int:property_id>', methods=['POST'])
@login_required
def toggle_favorite(property_id):
    property = Property.query.get_or_404(property_id)
    if property in current_user.favorites:
        current_user.favorites.remove(property)
        message = 'Property removed from favorites'
    else:
        current_user.favorites.append(property)
        message = 'Property added to favorites'
    db.session.commit()
    return jsonify({'success': True, 'message': message})

@user.route('/favorites')
@login_required
def favorites():
    page = request.args.get('page', 1, type=int)
    favorite_properties = current_user.favorites.paginate(page=page, per_page=12)
    return render_template('user/favorites.html', properties=favorite_properties)

@user.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html')