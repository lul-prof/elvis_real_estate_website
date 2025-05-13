from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Payment, Property
from . import payment
import stripe

stripe.api_key = 'your_stripe_secret_key'

@payment.route('/payment/process', methods=['POST'])
@login_required
def process_payment():
    try:
        data = request.json
        amount = data.get('amount')
        property_id = data.get('property_id')
        payment_type = data.get('payment_type')  # booking_fee, premium_listing, etc.

        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency='usd',
            metadata={
                'property_id': property_id,
                'user_id': current_user.id,
                'payment_type': payment_type
            }
        )

        return jsonify({
            'clientSecret': intent.client_secret
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@payment.route('/payment/confirm', methods=['POST'])
@login_required
def confirm_payment():
    try:
        payment_intent_id = request.json.get('payment_intent_id')
        
        # Verify payment intent
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status == 'succeeded':
            # Create payment record
            payment = Payment(
                user_id=current_user.id,
                property_id=intent.metadata.property_id,
                amount=intent.amount / 100,  # Convert from cents
                payment_type=intent.metadata.payment_type,
                status='completed',
                transaction_id=payment_intent_id
            )
            db.session.add(payment)
            db.session.commit()
            
            return jsonify({'success': True})
            
        return jsonify({'error': 'Payment not completed'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 400