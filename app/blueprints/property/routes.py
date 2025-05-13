from flask import render_template, url_for, flash, redirect, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Property, PropertyImage, PropertyReview
from . import property
from .forms import PropertyForm, ContactAgentForm, ViewingForm
import os
from app.recommendation import PropertyRecommender
from werkzeug.utils import secure_filename

recommender = PropertyRecommender()

@property.route('/property/new', methods=['GET', 'POST'])
@login_required
def new_property():
    if current_user.role not in ['admin', 'agent']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    form = PropertyForm()
    if form.validate_on_submit():
        property = Property(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            property_type=form.property_type.data,
            status=form.status.data,
            location=form.location.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            bedrooms=form.bedrooms.data,
            bathrooms=form.bathrooms.data,
            area=form.area.data,
            owner=current_user
        )
        db.session.add(property)
        db.session.commit()
        
        # Handle image uploads
        for image in form.images.data:
            if image:
                filename = save_property_image(image)
                property_image = PropertyImage(filename=filename, property=property)
                db.session.add(property_image)
                images_saved = True
        if images_saved:
            db.session.commit()
            flash('Property and images have been created!', 'success')
        else:
            flash('Property created but there was an issue with image uploads.', 'warning')
            
        flash('Property has been created!', 'success')
        return redirect(url_for('property.view_property', property_id=property.id))
    
    return render_template('property/new_property.html', title='New Property', form=form)

'''
@property.route('/property/<int:property_id>')
def view_property(property_id):
    property = Property.query.get_or_404(property_id)
    
    # Increment view count
    property.views += 1
    
    # Add to user's viewed properties if logged in
    if current_user.is_authenticated:
        if property not in current_user.viewed_properties:
            current_user.viewed_properties.append(property)
        db.session.commit()
    
    # Get similar properties
    similar_properties = recommender.get_similar_properties(property_id)
    
    return render_template('property/property_detail.html',
                         property=property,
                         similar_properties=similar_properties)

    '''

@property.route('/property/<int:property_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    property = Property.query.get_or_404(property_id)
    if property.owner != current_user and current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    form = PropertyForm()
    if form.validate_on_submit():
        property.title = form.title.data
        property.description = form.description.data
        property.price = form.price.data
        property.property_type = form.property_type.data
        property.status = form.status.data
        property.location = form.location.data
        property.latitude = form.latitude.data
        property.longitude = form.longitude.data
        property.bedrooms = form.bedrooms.data
        property.bathrooms = form.bathrooms.data
        property.area = form.area.data
        
        # Handle new image uploads
        for image in form.images.data:
            if image:
                filename = save_property_image(image)
                property_image = PropertyImage(filename=filename, property=property)
                db.session.add(property_image)
        
        db.session.commit()
        flash('Property has been updated!', 'success')
        return redirect(url_for('property.view_property', property_id=property.id))
    
    elif request.method == 'GET':
        form.title.data = property.title
        form.description.data = property.description
        form.price.data = property.price
        form.property_type.data = property.property_type
        form.status.data = property.status
        form.location.data = property.location
        form.latitude.data = property.latitude
        form.longitude.data = property.longitude
        form.bedrooms.data = property.bedrooms
        form.bathrooms.data = property.bathrooms
        form.area.data = property.area
    
    return render_template('property/edit_property.html', title='Edit Property', form=form, property=property)

def save_property_image(image):
    # Generate unique filename
    try:
        filename = secure_filename(image.filename)
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        return filename
    except Exception as e:
        flash(f'Error saving image: {str(e)}', 'danger')
        return None



@property.route('/property/<int:property_id>')
def view_property(property_id):
    property = Property.query.get_or_404(property_id)
    
    # Increment view count
    property.views += 1

    
    # Add to user's viewed properties if logged in
    if current_user.is_authenticated:
        if property not in current_user.viewed_properties:
            current_user.viewed_properties.append(property)
        db.session.commit()

    contact_form = ContactAgentForm()
    viewing_form = ViewingForm()
    
    # Get similar properties
    similar_properties = recommender.get_similar_properties(property_id)
    
    return render_template('property/property_detail.html',
                         property=property,
                         similar_properties=similar_properties,form=contact_form,
                         viewing_form=viewing_form)

@property.route('/recommendations')
@login_required
def recommendations():
    recommended_properties = recommender.get_personalized_recommendations(current_user.id)
    return render_template('property/recommendations.html',
                         properties=recommended_properties)

@property.route('/property/<int:property_id>/contact', methods=['POST'])
@login_required
def contact_agent(property_id):
    property = Property.query.get_or_404(property_id)
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')
    
    # Here you can add logic to send email to the agent
    # For example, using your existing email functionality
    
    flash('Your message has been sent to the agent!', 'success')
    return redirect(url_for('property.view_property', property_id=property_id))

@property.route('/property/<int:property_id>/review', methods=['POST'])
@login_required
def add_review(property_id):
    property = Property.query.get_or_404(property_id)
    rating = request.form.get('rating', type=int)
    content = request.form.get('content')
    
    if not rating or not content:
        flash('Both rating and review content are required.', 'danger')
        return redirect(url_for('property.view_property', property_id=property_id))
    
    review = PropertyReview(
        user_id=current_user.id,
        property_id=property_id,
        rating=rating,
        content=content
    )
    
    db.session.add(review)
    db.session.commit()
    
    flash('Your review has been added!', 'success')
    return redirect(url_for('property.view_property', property_id=property_id))

