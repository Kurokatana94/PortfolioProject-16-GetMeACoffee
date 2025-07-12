from flask import Flask, render_template, jsonify, request, redirect
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
import datetime as dt
import stripe
import os
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
Bootstrap5(app)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
app.config['STRIPE_PUBLISHABLE_KEY'] = os.environ.get('STRIPE_PUBLISHABLE_KEY')

MAIN_DOMAIN = "http://127.0.0.1:5000"

@app.route('/')
def index():
    return render_template("index.html", year=dt.datetime.now().year, stripe_pk=app.config['STRIPE_PUBLISHABLE_KEY'])

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.get_json()
    amount = data.get("amount", 0)

    if amount < 50:  # Stripe minimum in GBP
        return jsonify({"error": "Minimum donation is £0.50"}), 400
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'unit_amount': amount,
                    'product_data': {
                        'name': 'Gift me a coffee ☕',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=MAIN_DOMAIN + '/checkout-successful',
            cancel_url=MAIN_DOMAIN + '/',
        )
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/checkout-successful")
def checkout_successful():
    return render_template("checkout-successful.html")

if __name__ == "__main__":
    app.run(debug=True)