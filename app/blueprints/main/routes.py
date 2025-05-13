from flask import render_template, request, jsonify
from app.models import Property
from . import main

@main.route('/')
@main.route('/index')
def index():
    featured_properties = Property.query.order_by(Property.views.desc()).limit(6).all()
    return render_template('main/index.html', featured_properties=featured_properties)

@main.route('/search')
def search():
    query = request.args.get('q', '')
    property_type = request.args.get('type', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    bedrooms = request.args.get('bedrooms', type=int)
    status = request.args.get('status', '')
    sort_by = request.args.get('sort', 'newest')
    
    # Base query
    properties = Property.query
    
    # Apply filters
    if query:
        properties = properties.filter(Property.title.ilike(f'%{query}%') | 
                                    Property.description.ilike(f'%{query}%') |
                                    Property.location.ilike(f'%{query}%'))
    
    if property_type:
        properties = properties.filter(Property.property_type == property_type)
    
    if min_price:
        properties = properties.filter(Property.price >= min_price)
    
    if max_price:
        properties = properties.filter(Property.price <= max_price)
    
    if bedrooms:
        properties = properties.filter(Property.bedrooms == bedrooms)
    
    if status:
        properties = properties.filter(Property.status == status)
    
    # Apply sorting
    if sort_by == 'price_low':
        properties = properties.order_by(Property.price.asc())
    elif sort_by == 'price_high':
        properties = properties.order_by(Property.price.desc())
    else:  # newest
        properties = properties.order_by(Property.created_at.desc())
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 12
    properties = properties.paginate(page=page, per_page=per_page)
    
    return render_template('main/search.html', properties=properties)