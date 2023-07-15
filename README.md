# Donation System API

The Donation System API is a backend application developed using Django that provides RESTful services for a donation system. It allows users to make donations easily and securely. The API handles user authentication, donation processing, payment history management, and provides a monthly payment dashboard for data visualization.

## Features

- User authentication using phone numbers and OTP-based verification.
- Donation processing through an online payment gateway.
- Payment history management for users.
- Monthly payment dashboard for data visualization.

## Requirements

- Python 3.9 or higher
- Django 3.2 or higher
- Django REST Framework 3.12 or higher
- Other dependencies mentioned in the requirements.txt file.

## Installation

1. Clone the repository:

```
git clone https://github.com/patelabhi1607/donating_system
```

2. Create a virtual environment:

```
python3 -m venv venv
```

3. Activate the virtual environment:

```
source venv/bin/activate
```

4. Install the dependencies:

```
pip install -r requirements.txt
```

5. Set up the database:

```
python manage.py migrate
```

6. Start the development server:

```
python manage.py runserver
```

7. Access the API at [http://localhost:8000/api/](http://localhost:8000/api/)

## Configuration

1. Payment Gateway Integration: Implement the payment gateway integration logic in `donation_app/views.py` in the `process_donation` method of the `DonationViewSet`. Replace the dummy response with the actual payment gateway integration code.

2. OTP Verification: Implement the OTP verification logic in `donation_app/views.py` in the `login` method of the `UserViewSet`. Replace the dummy response with the actual OTP verification code using your preferred OTP library or service.
