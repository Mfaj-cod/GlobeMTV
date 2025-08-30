import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, g
)
from functools import wraps
from datetime import datetime
import os
import smtplib
import uuid
from data import PRODUCTS, PLANS, CHANNEL_GROUPS, POSTS, MOVIES, COUPONS, msg
import os
import paypalrestsdk
# from coinbase_commerce.client import Client as CbClient

paypalrestsdk.configure({
    "mode": os.getenv("PAYPAL_MODE", "sandbox"),  # sandbox or live
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
})


print("Testing PayPal connection...")
if paypalrestsdk.Api({
    "mode": "sandbox",
    "client_id": "YOUR_SANDBOX_CLIENT_ID",
    "client_secret": "YOUR_SANDBOX_CLIENT_SECRET"
}):
    print("✅ Connected successfully!")
else:
    print("❌ Failed, check credentials")


# cb = CbClient(api_key=os.getenv("COINBASE_COMMERCE_API_KEY"))
CHECKOUT_CURRENCY = os.getenv("CHECKOUT_CURRENCY", "USD").upper()


# app
app = Flask(__name__)
app.secret_key = os.getenv("KEY")


# Use /data/site.db on Render (persistent disk), fall back to local file in dev
DATABASE = os.getenv("DATABASE_PATH", os.path.join(os.path.abspath(os.path.dirname(__file__)), "site.db"))


# DB Setup
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # rows act like dicts
    return g.db


# before each request
@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# Initializing the database
def init_db():
    print(f"🔧 Using database at: {DATABASE}")
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin INTEGER DEFAULT 0,
            plan TEXT DEFAULT 'Free',
            free_trial INTEGER DEFAULT 0
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            features TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER,
            plan_id INTEGER,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (plan_id) REFERENCES plans(id)
        );
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            badge TEXT,
            desc1 TEXT,
            desc2 TEXT,
            desc3 TEXT,
            rating TEXT,
            shipping TEXT
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS product_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            image_path TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            comment TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL,
          total_amount REAL NOT NULL,
          currency TEXT NOT NULL,
          status TEXT NOT NULL,                  -- 'pending'|'paid'|'canceled'|'failed'
          gateway TEXT,                          -- 'stripe'|'paypal'|'razorpay'|'coinbase'
          gateway_ref TEXT,                      -- e.g., session id / order id
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          order_id INTEGER NOT NULL,
          product_id INTEGER NOT NULL,
          name TEXT NOT NULL,
          unit_price REAL NOT NULL,
          quantity INTEGER NOT NULL,
          FOREIGN KEY (order_id) REFERENCES orders(id)
        );
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS coupons (
          code TEXT NOT NULL,
          discount INT NOT NULL,
          description TEXT NOT NULL
        );
    """)

    # Admin
    db.execute("UPDATE users SET is_admin = 1 WHERE email = ?", ("globemtv@gmail.com",))

    for c in COUPONS:
        exists = db.execute("SELECT 1 FROM coupons WHERE code=?", (c["code"],)).fetchone()
        if not exists:
            db.execute("""
                INSERT INTO coupons (code, discount, description) VALUES (?, ?, ?)
            """, (c["code"], c["discount"], c["description"]))

    for p in PLANS:
        exists = db.execute("SELECT 1 FROM plans WHERE name=?", (p["title"],)).fetchone()
        if not exists:
            db.execute("""
                INSERT INTO plans (name, price, features) VALUES (?, ?, ?)
            """, (p["title"], p["price"], ",".join(p["features"])))

    
    # Insert products
    for p in PRODUCTS:
        exists = db.execute("SELECT 1 FROM products WHERE id=?", (p["id"],)).fetchone()
        if not exists:
            db.execute("""
                INSERT INTO products (id, name, price, badge, desc1, desc2, desc3, rating, shipping)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p["id"],
                p["name"],
                p["price"],
                p.get("badge"),
                p.get("desc1") or p.get("desc") or "",
                p.get("desc2") or "",
                p.get("desc3") or "",
                p.get("rating") or "",
                p.get("shipping") or ""
            ))

        # images: accept list or single string
        imgs = p.get("image") or p.get("images") or []
        if isinstance(imgs, str):
            imgs = [imgs]
        for img in imgs:
            exists_img = db.execute(
                "SELECT 1 FROM product_images WHERE product_id=? AND image_path=?",
                (p["id"], img)
            ).fetchone()
            if not exists_img:
                db.execute(
                    "INSERT INTO product_images (product_id, image_path) VALUES (?, ?)",
                    (p["id"], img)
                )
    db.commit()


# Global Template Vars
@app.context_processor
def inject_globals():
    return {"year": datetime.utcnow().year}


#defining login required function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    
    return decorated_function



def get_cart_items_for_user(user_id):
    db = get_db()
    return db.execute("""
        SELECT p.id AS product_id, p.name, p.price, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id=?
    """, (user_id,)).fetchall()

def create_order_snapshot(user_id, currency, gateway):
    db = get_db()
    items = get_cart_items_for_user(user_id)
    if not items:
        return None, None

    total = sum(i["price"] * i["quantity"] for i in items)
    cur = db.execute(
        "INSERT INTO orders (user_id, total_amount, currency, status, gateway) VALUES (?, ?, ?, ?, ?)",
        (user_id, total, currency, "pending", gateway)
    )
    order_id = cur.lastrowid

    for it in items:
        db.execute("""INSERT INTO order_items (order_id, product_id, name, unit_price, quantity)
                      VALUES (?, ?, ?, ?, ?)""",
                   (order_id, it["product_id"], it["name"], it["price"], it["quantity"]))
    db.commit()
    return order_id, items




# Routes
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html", products=PRODUCTS, plans=PLANS, channels=CHANNEL_GROUPS, movies=MOVIES)


@app.route("/products")
def products():
    return render_template("products.html", products=PRODUCTS)


@app.route("/products/<int:pid>")
def product_detail(pid):
    product = next((p for p in PRODUCTS if p["id"] == pid), None)

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("products"))
    
    return render_template("product_detail.html", product=product)


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/blog")
def blog():
    return render_template("blog.html", posts=POSTS)


#contact
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        if "user_id" not in session:
            flash("Please log in to contact us.", "warning")
            return redirect(url_for("login"))

        name = session.get("username", "")
        email = session.get("email", "").strip().lower()
        message = request.form.get("message", "").strip()

        if not message:
            flash("Please fill out all fields.", "error")
        else:
            # send the message via email:
            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                    connection.starttls()
                    connection.login(os.getenv("COMPANY_EMAIL"), os.getenv("EMAIL_PASSWORD"))

                    connection.sendmail(
                        from_addr=os.getenv("COMPANY_EMAIL"),
                        to_addrs=os.getenv("COMPANY_EMAIL"),
                        msg=f"Subject: Contact Form Submission\n\nName: {name}\nEmail: {email}\nMessage: {message}"
                    )

            except Exception as e:
                flash(f"Failed to send message: {e}", "error")
            else:
                flash("Thanks! We received your message and will reply within 24 to 48 working hours.", "success")
            return redirect(url_for("contact"))
        
    return render_template("contact.html")




# Register
@app.route("/register", methods=["GET", "POST"]) 
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        domain = email.split('@')[-1]
        if domain not in ['gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com']:
            flash("Please use a valid email address.", "error")
            return redirect(url_for("register"))
        
        if password.isdigit() or password.isalpha() or len(password) < 6:
            flash("Password must contain both letters and numbers and be at least 6 characters long.", "error")
            return redirect(url_for("register"))

        # optional pre-checking
        db = get_db()
        exists = db.execute(
            "SELECT 1 FROM users WHERE username=? OR email=?", 
            (username, email)
        ).fetchone()

        if exists:
            flash("Username or email already exists.", "error")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)
        # is_admin with default 0 and plan with default Free
        db.execute(
            "INSERT INTO users (username, email, password, plan, is_admin) VALUES (?, ?, ?, ?, ?)",
            (username, email, hashed_pw, "Free", 0)
        )
        db.commit()

        try:
                with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                    connection.starttls()
                    connection.login(os.getenv("COMPANY_EMAIL"), os.getenv("EMAIL_PASSWORD"))
                    connection.sendmail(
                        from_addr=os.getenv("COMPANY_EMAIL"),
                        to_addrs=email,
                        msg=msg
                    )
        except Exception as e:
            flash(f"Failed to send info email: {e}", "error")

        flash("Registration successful. Please login.", "success")

        return redirect(url_for("login"))

    return render_template("register.html")



# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Please enter email and password.", "error")

            return redirect(url_for("login"))

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        # IMP: comparing using check_password_hash
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful!", "success")

            return redirect(url_for("home"))
        else:
            flash("Invalid credentials!", "error")

            return redirect(url_for("login"))

    return render_template("login.html")



@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "error")

    return redirect(url_for("home"))


@app.route("/account")
def account():
    if "user_id" not in session:
        flash("Please log in to view your account.", "error")
        return redirect(url_for("login"))

    db = get_db()
    user_id = session["user_id"]

    # fetch user
    user = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()

    # fetch orders
    orders = db.execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()

    # fetch items for each order (if you have order_items table)
    order_items = {}
    for order in orders:
        items = db.execute(
            "SELECT * FROM order_items WHERE order_id=?",
            (order["id"],)
        ).fetchall()
        order_items[order["id"]] = items

    return render_template("account.html", user=user, orders=orders, order_items=order_items,  user_id=user_id)


# Admin page
@app.route("/admin")
def admin():
    if not g.user or g.user["is_admin"] == 0:
        return redirect(url_for("login"))

    db = get_db()
    users = db.execute("SELECT username, email, plan FROM users").fetchall()

    return render_template("admin.html", users=users)


# Trial
@app.route("/free-trial")
def free_trial():
    if "user_id" not in session:
        flash("Please log in to access the free trial.", "error")
        return redirect(url_for("login"))
    
    elif "user_id" in session and session.get("free_trial") == 1: #checking if free trial is already used
        flash("You have already used your free trial.\nOnly 1x trial access per customer allowed.", "error")
        return redirect(url_for("home"))
    
    else:
        return render_template("free_trial.html")



# Activation request
@app.route("/activate-trial", methods=["POST"])
def activate_trial():
    if "user_id" not in session:
        flash("Please log in to activate free trial.", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    db = get_db()
    user = db.execute("SELECT username, email FROM users WHERE id = ?", (user_id,)).fetchone()

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("login"))

    user_name = user["username"]
    user_email = user["email"]

    #send email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(os.getenv("COMPANY_EMAIL"), os.getenv("EMAIL_PASSWORD"))

            connection.sendmail(
                from_addr=os.getenv("COMPANY_EMAIL"),
                to_addrs=os.getenv("COMPANY_EMAIL"),
                msg=f"Subject: Free Trial Activation request.\n\n"
                    f"From: {user_name}\n"
                    f"User Email: {user_email}\n"
                    f"Message: User has requested the activation of the 24h free trial."
            )
        flash("✅ Free Trial Activation request has been submitted. We'll contact you in the next 24 to 48 hours.", "success")
    except Exception as e:
        flash(f"⚠️ Failed to send activation email: {e}", "error")

    db.execute("UPDATE users SET free_trial = 1 WHERE id = ?", (user_id,)) #update user's free trial status
    db.commit()
    session["free_trial"] = 1  # Update session variable

    return redirect(url_for("home"))



# Add to Cart
@app.route("/add_to_cart/<int:product_id>")
@login_required
def add_to_cart(product_id):
    user_id = session["user_id"]

    # Checking if product is already in cart
    db = get_db()
    existing = db.execute("SELECT * FROM cart WHERE user_id=? AND product_id=?", (user_id, product_id)).fetchone()

    if existing:
        db.execute("UPDATE cart SET quantity = quantity + 1 WHERE user_id=? AND product_id=?", (user_id, product_id))
    else:
        db.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)", (user_id, product_id, 1))

    db.commit()
    flash("Added to cart!", "success")

    return redirect(url_for("products"))




@app.route("/add_plan_to_cart/<int:plan_id>")
@login_required
def add_plan_to_cart(plan_id):
    user_id = session["user_id"]
    db = get_db()

    # Check if already in cart
    existing = db.execute(
        "SELECT id, quantity FROM cart WHERE user_id=? AND plan_id=?",
        (user_id, plan_id)
    ).fetchone()

    if existing:
        db.execute("UPDATE cart SET quantity=? WHERE id=?", (existing["quantity"] + 1, existing["id"]))
    else:
        db.execute("INSERT INTO cart (user_id, plan_id, quantity) VALUES (?, ?, ?)", (user_id, plan_id, 1))

    db.commit()
    return redirect(url_for("cart"))



@app.route("/remove_from_cart/<int:cart_id>")
@login_required
def remove_from_cart(cart_id):
    user_id = session["user_id"]
    db = get_db()

    # Ensure the cart item belongs to this user
    db.execute("DELETE FROM cart WHERE id=? AND user_id=?", (cart_id, user_id))
    db.commit()

    return redirect(url_for("cart"))



@app.route('/update_quantity/<int:cart_id>/<string:action>')
@login_required
def update_quantity(cart_id, action):
    user_id = session["user_id"]
    db = get_db()

    if action == "increase":
        db.execute("UPDATE cart SET quantity = quantity + 1 WHERE id = ? AND user_id = ?", (cart_id, user_id))
    elif action == "decrease":
        db.execute("UPDATE cart SET quantity = quantity - 1 WHERE id = ? AND user_id = ?", (cart_id, user_id))
    db.commit()

    return redirect(url_for("cart"))



# View Cart
@app.route("/cart")
@login_required
def cart():
    user_id = session["user_id"]
    db = get_db()

    product_items = db.execute("""
        SELECT cart.id, cart.quantity, products.name, products.price
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id=? AND cart.product_id IS NOT NULL
    """, (user_id,)).fetchall()

    plan_items = db.execute("""
        SELECT cart.id, cart.quantity, plans.name, plans.price
        FROM cart
        JOIN plans ON cart.plan_id = plans.id
        WHERE cart.user_id=? AND cart.plan_id IS NOT NULL
    """, (user_id,)).fetchall()

    items = product_items + plan_items
    total = sum(item["price"] * item["quantity"] for item in items)

    return render_template("cart.html", items=items, total=total)





# Buy the product that's in the cart
@app.route("/buy", methods=["POST"])
@login_required
def buy():
    return redirect(url_for("checkout"))


@app.route("/checkout")
@login_required
def checkout():
    user_id = session["user_id"]
    db = get_db()

    # Products in cart
    product_items = db.execute("""
        SELECT cart.id, cart.quantity, products.name, products.price
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id=? AND cart.product_id IS NOT NULL
    """, (user_id,)).fetchall()

    # Plans in cart
    plan_items = db.execute("""
        SELECT cart.id, cart.quantity, plans.name, plans.price
        FROM cart
        JOIN plans ON cart.plan_id = plans.id
        WHERE cart.user_id=? AND cart.plan_id IS NOT NULL
    """, (user_id,)).fetchall()

    # Merge both
    items = product_items + plan_items

    # Calculate total
    total = sum(item["price"] * item["quantity"] for item in items)

    return render_template("checkout.html", items=items, total=total)


@app.route("/process_payment", methods=["POST"])
@login_required
def process_payment():
    user_id = session["user_id"]
    db = get_db()

    # Fetch products in cart
    product_items = db.execute("""
        SELECT cart.id, cart.quantity, products.name, products.price
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id=? AND cart.product_id IS NOT NULL
    """, (user_id,)).fetchall()

    # Fetch plans in cart
    plan_items = db.execute("""
        SELECT cart.id, cart.quantity, plans.name, plans.price
        FROM cart
        JOIN plans ON cart.plan_id = plans.id
        WHERE cart.user_id=? AND cart.plan_id IS NOT NULL
    """, (user_id,)).fetchall()

    # Merge both
    items = product_items + plan_items

    # If empty cart
    if not items:
        flash("Your cart is empty.", "error")
        return redirect(url_for("cart"))

    # Calculate total before discount
    total = sum(item["price"] * item["quantity"] for item in items)

    # Handle coupon code
    coupon_code = request.form.get("coupon_code", "").strip()
    discount = 0
    applied_coupon = None

    if coupon_code:
        coupon = db.execute("SELECT * FROM coupons WHERE code=?", (coupon_code,)).fetchone()
        if coupon:
            discount = coupon["discount"]
            applied_coupon = coupon_code
            total = max(total - discount, 0)
            # flash(f"Coupon '{coupon_code}' applied! -${discount:.2f}", "success")
        else:
            flash("Invalid coupon code.", "error")

    # Save order snapshot in session
    session["pending_order"] = {
        "user_id": user_id,
        "items": [dict(it) for it in items],
        "total": total,
        "coupon_code": applied_coupon,
        "discount": discount,
    }

    # Payment method selected
    method = request.form.get("method")

    if method == "PayPal":
        # Build PayPal items list
        items_list = []
        for it in items:
            items_list.append({
                "name": it["name"],
                "sku": str(it["id"]) if "id" in it.keys() else "",
                "price": f"{it['price']:.2f}",
                "currency": CHECKOUT_CURRENCY,
                "quantity": int(it["quantity"])
            })

        # Add discount line if coupon applied
        if discount > 0:
            items_list.append({
                "name": f"Coupon {applied_coupon}",
                "sku": "DISCOUNT",
                "price": f"-{discount:.2f}",
                "currency": CHECKOUT_CURRENCY,
                "quantity": 1
            })

        # PayPal payment object
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": url_for("paypal_execute", _external=True),
                "cancel_url": url_for("payment_cancel", _external=True),
            },
            "transactions": [{
                "item_list": {"items": items_list},
                "amount": {
                    "total": f"{total:.2f}",   # discounted total
                    "currency": CHECKOUT_CURRENCY
                },
                "description": "GlobeMTV Order"
            }]
        })

        if payment.create():
            session["pending_order"]["gateway_ref"] = payment.id
            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(str(link.href))

        # Log PayPal errors for debugging
        print("PayPal error:", payment.error)
        flash("PayPal error. Please try again or use another method.", "error")
        return redirect(url_for("checkout"))

    # If no valid method
    flash("Please select a valid payment method.", "error")
    return redirect(url_for("checkout"))


    # # Crypto (Coinbase Commerce example)
    # if method == "Crypto":
    #     charge = cb.charge.create(
    #         name="GlobeMTV Order",
    #         description="Purchase",
    #         local_price={"amount": f"{total:.2f}", "currency": CHECKOUT_CURRENCY},
    #         pricing_type="fixed_price",
    #         metadata={"user_id": str(session.get("user_id"))},
    #         redirect_url=url_for("payment_success", _external=True),
    #         cancel_url=url_for("payment_cancel", _external=True),
    #     )

    #     session["pending_order"]["gateway_ref"] = charge.id
    #     return redirect(charge.hosted_url)

    # flash("Unknown payment method.", "error")
    # return redirect(url_for("checkout"))






@app.route("/checkout/paypal/execute")
def paypal_execute():
    order_id = request.args.get("order_id")
    payment_id = request.args.get("paymentId")
    payer_id = request.args.get("PayerID")

    if not order_id or not payment_id or not payer_id:
        flash("Missing payment information.", "error")
        return redirect(url_for("cart"))

    try:
        payment = paypalrestsdk.Payment.find(payment_id)
    except Exception as e:
        flash(f"PayPal lookup failed: {e}", "error")
        return redirect(url_for("payment_cancel", order_id=order_id))

    if payment.execute({"payer_id": payer_id}):
        db = get_db()
        order = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()

        if not order:
            flash("Order not found.", "error")
            return redirect(url_for("cart"))

        # mark paid & save PayPal ref
        db.execute("UPDATE orders SET status='paid', gateway_ref=? WHERE id=?", (payment_id, order_id))
        db.execute("DELETE FROM cart WHERE user_id=?", (order["user_id"],))
        db.commit()

        return redirect(url_for("payment_success", order_id=order_id))
    else:
        db = get_db()
        db.execute("UPDATE orders SET status='canceled' WHERE id=?", (order_id,))
        db.commit()
        flash("PayPal payment execution failed.", "error")
        return redirect(url_for("payment_cancel", order_id=order_id))




# from coinbase_commerce.webhook import Webhook, SignatureVerificationError

# @app.route("/webhooks/coinbase", methods=["POST"])
# def coinbase_webhook():
#     secret = os.getenv("COINBASE_COMMERCE_WEBHOOK_SECRET")
#     sig = request.headers.get("X-CC-Webhook-Signature", "")
#     payload = request.data
#     try:
#         event = Webhook.construct_event(payload, sig, secret)
#     except WebhookInvalidSignature:
#         return ("Invalid signature", 400)

#     if event["type"] in ("charge:confirmed", "charge:resolved"):
#         meta = (event["data"] or {}).get("metadata") or {}
#         order_id = meta.get("order_id")
#         if order_id:
#             db = get_db()
#             row = db.execute("SELECT user_id, status FROM orders WHERE id=?", (order_id,)).fetchone()
#             if row and row["status"] != "paid":
#                 db.execute("UPDATE orders SET status='paid' WHERE id=?", (order_id,))
#                 db.execute("DELETE FROM cart WHERE user_id=?", (row["user_id"],))
#                 db.commit()
#     return ("", 200)




@app.route("/payment-success")
def payment_success():
    order_id = request.args.get("order_id")
    db = get_db()
    order = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()

    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("cart"))

    user = db.execute("SELECT * FROM users WHERE id=?", (order["user_id"],)).fetchone()
    items = db.execute("""
        SELECT p.*, oi.quantity
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    """, (order_id,)).fetchall()

    # PayPal verification
    if order["gateway"] == "paypal":
        payment = paypalrestsdk.Payment.find(order["gateway_ref"])
        if payment and payment.state == "approved":
            db.execute("UPDATE orders SET status='paid' WHERE id=?", (order_id,))
            db.commit()

            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                    connection.starttls()
                    connection.login(os.getenv("COMPANY_EMAIL"), os.getenv("EMAIL_PASSWORD"))
                    connection.sendmail(
                        from_addr=os.getenv("COMPANY_EMAIL"),
                        to_addrs=os.getenv("COMPANY_EMAIL"),   # send to company email
                        msg=f"Subject: RECIEVED AN ORDER\n\n"
                            f"Payment: Successful\n"
                            f"Items:\n"
                            f"{''.join([f' - {item['name']} (x{item['quantity']})\n' for item in items])}"
                            f"Total: {order['total']}\n\n"
                            f"from: {user['username']}\n"
                            f"user_email: {user['email']}\n"
                            f"order_id: {order_id}\n\n"
                    )
            
            except Exception as e:
                flash(f"Failed to send info email to company: {e}", "error")



            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                    connection.starttls()
                    connection.login(os.getenv("COMPANY_EMAIL"), os.getenv("EMAIL_PASSWORD"))
                    connection.sendmail(
                        from_addr=os.getenv("COMPANY_EMAIL"),
                        to_addrs=user["email"],   # send to user
                        msg=f"Subject: Payment Successful\n\n"
                            f"We have received your order and are processing it.\n\n"
                            f"Thank you for your purchase!\n\n"
                            f"Items:\n"
                            f"{''.join([f' - {item["name"]} (x{item["quantity"]})\n' for item in items])}"
                            f"Total: {order['total']}\n\n"
                            f"order_id: {order_id}\n\n"
                            f"If you have any questions, contact us at {os.getenv('COMPANY_EMAIL')}"
                    )
            
            except Exception as e:
                flash(f"Failed to send info email to user: {e}", "error")

            return render_template("success.html", order_id=order_id, user=user)
        else:
            flash("Payment verification failed.", "error")
            return redirect(url_for("payment_cancel", order_id=order_id))

    # # Coinbase verification
    # elif order["gateway"] == "coinbase":
    #     charge = cb.charge.retrieve(order["gateway_ref"])
    #     if charge and charge["status"] == "COMPLETED":   # check
    #         db.execute("UPDATE orders SET status='paid' WHERE id=?", (order_id,))
    #         db.commit()
    #     else:
    #         flash("Crypto payment not completed yet.", "warning")
    #         return redirect(url_for("payment_cancel", order_id=order_id))

    # return render_template("success.html", order=order, user=user)   # pass full objects




@app.route("/payment-cancel")
def payment_cancel():
    order_id = request.args.get("order_id")
    db = get_db()
    order = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()

    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("cart"))

    user = db.execute("SELECT * FROM users WHERE id=?", (order["user_id"],)).fetchone()

    db.execute("UPDATE orders SET status='canceled' WHERE id=?", (order_id,))
    db.commit()

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(os.getenv("COMPANY_EMAIL"), os.getenv("EMAIL_PASSWORD"))
            connection.sendmail(
                from_addr=os.getenv("COMPANY_EMAIL"),
                to_addrs=user["email"],
                msg=f"Subject: Payment Failed\n\n"
                    f"Hi {user['username']},\n\n"
                    f"Your order #{order_id} was canceled. No charges were made."
            )
    except Exception as e:
        flash(f"Failed to send info email: {e}", "error")

    return render_template("cancel.html", order=order, user=user)   # sending objects





@app.route("/delete_account", methods=["GET", "POST"])
def delete_account():
    if "user_id" not in session:
        flash("You must be logged in to delete your account.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        if not request.form.get("password"):
            flash("Password is required.", "error")
            return redirect(url_for("delete_account"))

        password = request.form.get("password")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()

        if user and check_password_hash(user["password"], password):  
            # Delete account if password matches
            db.execute("DELETE FROM users WHERE id = ?", (session["user_id"],))
            db.commit()

            session.pop("user_id", None)
            flash("Your account has been deleted.", "success")
            return redirect(url_for("home"))
        else:
            flash("Incorrect password. Please try again.", "error")
            db.close()

    return render_template("index.html")



@app.route("/reviews", methods=["GET", "POST"])
def reviews():
    if request.method == "POST":
        name = request.form.get("name")
        comment = request.form.get("comment")
        rating = request.form.get("rating")

        # Saving review in DB
        db = get_db()
        db.execute("""
            INSERT INTO reviews (name, comment, rating)
            VALUES (?, ?, ?)
        """, (name, comment, rating))
        db.commit()

        return redirect(url_for("reviews"))

    # Fetch reviews from the database
    db = get_db()
    reviews = db.execute("SELECT * FROM reviews").fetchall()

    return render_template("reviews.html", reviews=reviews)

@app.before_request
def initialize_database():
    init_db()


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
