import os
import stripe
import logging
from flask import Blueprint, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from ..models import Tool, Purchase
from ..extensions import db

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

shop_bp = Blueprint('shop', __name__, url_prefix='/shop')

@shop_bp.route('/checkout/<int:tool_id>')
@login_required
def checkout(tool_id):
    tool = Tool.query.get_or_404(tool_id)
    
    # Check if user already purchased this tool
    existing_purchase = Purchase.query.filter_by(
        user_id=current_user.id,
        tool_id=tool.id
    ).first()
    
    if existing_purchase:
        flash('You have already purchased this tool!', 'info')
        return redirect(url_for('main.tool_detail', path=tool.slug))
    
    try:
        # Get the domain for redirect URLs
        domain = request.url_root.rstrip('/')
        
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': tool.name,
                        'description': f'Digital tool: {tool.name}'
                    },
                    'unit_amount': tool.price
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=f"{domain}{url_for('shop.success')}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{domain}{url_for('main.tool_detail', path=tool.slug)}",
            metadata={
                'tool_id': tool.id,
                'user_id': current_user.id
            }
        )
        
        if session and session.url:
            return redirect(session.url, code=303)
        else:
            flash('Unable to create checkout session', 'danger')
            return redirect(url_for('main.tool_detail', path=tool.slug))
        
    except Exception as e:
        logging.error(f"Stripe error: {str(e)}")
        flash('An error occurred while processing your payment. Please try again.', 'danger')
        return redirect(url_for('main.tool_detail', path=tool.slug))

@shop_bp.route('/success')
@login_required
def success():
    session_id = request.args.get('session_id')
    
    if session_id:
        try:
            # Retrieve the session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                # Get metadata
                tool_id = session.metadata.get('tool_id')
                user_id = session.metadata.get('user_id')
                
                if tool_id and user_id and int(user_id) == current_user.id:
                    # Check if purchase already recorded
                    existing_purchase = Purchase.query.filter_by(
                        stripe_session_id=session_id
                    ).first()
                    
                    if not existing_purchase:
                        # Record the purchase
                        purchase = Purchase()
                        purchase.user_id = current_user.id
                        purchase.tool_id = int(tool_id)
                        purchase.stripe_session_id = session_id
                        db.session.add(purchase)
                        db.session.commit()
                        
                        flash('Payment successful! You now have access to the tool.', 'success')
                    else:
                        flash('This purchase has already been recorded.', 'info')
                else:
                    flash('Invalid purchase session.', 'danger')
            else:
                flash('Payment was not completed successfully.', 'danger')
                
        except Exception as e:
            logging.error(f"Error processing successful payment: {str(e)}")
            flash('An error occurred while processing your purchase. Please contact support.', 'danger')
    else:
        flash('No payment session found.', 'danger')
    
    return redirect(url_for('main.dashboard'))

@shop_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhook events"""
    payload = request.data
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    if not endpoint_secret:
        return 'Webhook secret not configured', 400
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Get metadata
        tool_id = session['metadata'].get('tool_id')
        user_id = session['metadata'].get('user_id')
        
        if tool_id and user_id:
            # Check if purchase already recorded
            existing_purchase = Purchase.query.filter_by(
                stripe_session_id=session['id']
            ).first()
            
            if not existing_purchase:
                # Record the purchase
                purchase = Purchase()
                purchase.user_id = int(user_id)
                purchase.tool_id = int(tool_id)
                purchase.stripe_session_id = session['id']
                db.session.add(purchase)
                db.session.commit()
                logging.info(f"Recorded purchase via webhook: user {user_id}, tool {tool_id}")
    
    return 'Success', 200
