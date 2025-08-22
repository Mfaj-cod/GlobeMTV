🌍 GlobeMTV

A modern streaming-inspired platform built with Flask, SQLite, and Bootstrap CSS, featuring subscription plans, checkout with Stripe integration, movie browsing, and more.

✨ Features

🎬 Movie & TV show listings with posters

🛒 Shopping cart & checkout flow

💳 Secure payments via Paypal

👤 User authentication (Register/Login)

📱 Responsive design with Bootstrap CSS

🔒 Environment variable support for sensitive keys (.env)

🖥️ Tech Stack

Backend: Flask (Python)

Frontend: HTML, CSS, Bootstrap, JavaScript

Database: SQLite

Payments: Paypal API

Deployment: Render

🚀 Getting Started
1️⃣ Clone the Repository
git clone https://github.com/Mfaj-cod/GlobeMTV.git
cd GlobeMTV

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Setup Environment Variables

Create a .env file in the root folder:

EMAIL=your_email
EMAIL_PASSWORD=your_email_app_password
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
FLASK_SECRET_KEY=your_flask_secret


⚠️ Do not commit .env (already excluded in .gitignore).

5️⃣ Run the App
flask run


Now visit 👉 http://127.0.0.1:5000

📂 Project Structure
GlobeMTV/
│── app.py                 # Main Flask app
│── data.py                # App data & constants
│── requirements.txt       # Python dependencies
│── Procfile               # For deployment on Render
│── site.db                # SQLite database
│── templates/             # HTML templates
│── static/                # CSS, JS, Images
└── .gitignore             # Ignoring secrets & venv

🔑 Deployment on Render

Push your repo to GitHub

Connect Render → New Web Service

Add Environment Variables in Render dashboard

Deploy 🎉

🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you’d like to change.
