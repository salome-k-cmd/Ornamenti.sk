from flask import render_template, redirect, flash
from forms import RegisterForm
from forms import ProductForm, CommentForm, LoginForm, ContactForm, AskForm
import os
from ext import app, db
from models import Product, Comment, User, Wishlist, ContactMessage, CommentLike
from flask_login import login_user, logout_user, login_required, current_user
from flask import session, url_for, jsonify
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def get_cart_items():
    return session.get('cart', [])

@app.context_processor
def inject_cart_items():
    return {'cart_items': len(get_cart_items())}

profiles = []

products = [
    {"name":"Flowers from Normandy", "artist":"Fantin-Latour", "price":"500", "image":"https://images.unsplash.com/photo-1700213399559-706d428e1178?q=80&w=785&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", "id": 0},
    {"name":"A heavy sea at Moeraki", "artist":"George Butler", "price":"700", "image":"https://images.unsplash.com/photo-1694158127206-c4103b2965a7?q=80&w=1222&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", "id": 1},
    {"name":" Õunapuu", "price":"300", "artist":"Bruni, L", "image":"https://images.unsplash.com/photo-1741116879891-c7523c450460?q=80&w=713&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", "id": 2},
    {"name":"Still Life with Cantaloupe", "artist":"William Mason Brown", "price":"125", "image":"https://images.unsplash.com/photo-1763073064895-a71c40af5ddf?q=80&w=1239&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", "id": 3},
    {"name":"An Owl", "price":"135", "artist":"Moses Haughton the Elder", "image":"https://images.unsplash.com/photo-1650214562914-9db1ae262752?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", "id": 4},
    # {"name":"Viva la Vida, Watermelons", "artist":"Frida Kahlo", "price":"300", "image":"https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQD2a2_CLQ88nG6IeGQAISi7U2pZndUADniDwOC41N2NWCXNjLgUjQceynurMt7", "id": 4},
    {"name":"Viva la Vida, Watermelons", "price":"300", "artist":"Moses Haughton the Elder", "image":"/static/images/viva-la-vida-watermelons.jpg", "id": 6},
    
]
role= "Admin"
def populate_initial_products():
    for p in products:
        exists = Product.query.filter_by(name=p["name"]).first()
        if not exists:
            new_product = Product(
                name=p["name"],
                artist=p["artist"],
                price=float(p["price"]),
                img=p["image"]
            )
            db.session.add(new_product)
    db.session.commit()  
with app.app_context():
    populate_initial_products()


with app.app_context():
    populate_initial_products()


@app.route("/")
def home():
    # cart_items = len(get_cart_items())
    return render_template("main.html")     
        #  cart_items=cart_items

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # user = {
        #     "username" : form.username.data,
        #     "password": form.password.data,
        #     "repeat_password": form.repeat_password.data,
        #     "gender": form.gender.data,
        #     "birthday": form.birthday.data,
        #     "country": form.country.data
        # }
        
        # image = form.profile_img.data
        # img_location = os.path.join(app.root_path, "static", "images", image.filename)
        # image.save(img_location)
        # user['profile_img'] = image.filename
        # profiles.append(user)
    # print(profiles)
    # print(form.errors) 
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("That username is already taken. Please choose another.", category="warning")
            return redirect("/register")
        
        new_user = User(username=form.username.data, password=form.password.data)

        db.session.add(new_user)
        db.session.commit()

        flash("User Registered Succesfully", category="success")
        return redirect("/login")

    return render_template("register.html", form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)

            flash("Logged in successfully.", category="success")
            return redirect("/")
        else:
            flash("Invalid username or password. Please try again.", category="warning")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    session.pop('chat_history', None)
    flash("Logged out succesfully.", category="info")
    return redirect("/")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        new_message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(new_message)
        db.session.commit()
        flash("Message sent successfully! We'll get back to you soon.", category="success")
        return redirect("/contact")
    
    return render_template("contact.html", form=form)

@app.route("/admin/messages")
@login_required
def view_messages():
    if current_user.role != 'Admin':
        flash("Access denied.", category="danger")
        return redirect("/")
    
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("admin_messages.html", messages=messages)

@app.route("/products")
def products_page():
    all_db_products = Product.query.all()
    # all_db_products = Product.query.filter(Product.price > 10, Product.name == "Product 1")
    # cart_items = len(get_cart_items())
    return render_template("products.html", products=all_db_products, role=role) 
# cart_items=cart_items

@app.route("/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    form = ProductForm()
    
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            artist=form.artist.data,
            price=form.price.data,
          )
        if form.product_img.data:
            image = form.product_img.data
            filename = image.filename
            image_path = os.path.join(app.root_path, "static", "images", filename)
            image.save(image_path)
            new_product.img = "/static/images/" + filename
        else:
             new_product.img = "https://via.placeholder.com/300"
        
        db.session.add(new_product)
        db.session.commit()
        
        flash("Product added succesfully", category="success")
        return redirect("/products") 
    print(products)
    return render_template("add_product.html", form=form)


@app.route ("/detailed/<int:product_id>", methods=["GET", "POST"])
def detailed(product_id):
    product = Product.query.get_or_404(product_id)
    form = CommentForm()
    in_wishlist = False
    if current_user.is_authenticated:
        in_wishlist = Wishlist.query.filter_by(
            user_id=current_user.id, 
            product_id=product_id
        ).first() is not None
    if form.validate_on_submit():
        new_comment = Comment(
            text=form.text.data,
            product_id=product.id,
            user_id=current_user.id
        )
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment posted!", "success")
        return redirect(f"/detailed/{product_id}")
    comments = Comment.query.filter(Comment.product_id == product_id).all()
    user_liked_comments = []
    if current_user.is_authenticated:
        user_liked_comments = [like.comment_id for like in CommentLike.query.filter_by(user_id=current_user.id).all()]
    return render_template("detailed.html", product=product, comments=comments, form=form, in_wishlist=in_wishlist, user_liked_comments=user_liked_comments)



@app.route("/delete_product/<int:product_id>")
def delete_product(product_id):
    product = Product.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted succesfully", category="danger")
    return redirect("/products")
    
# CRUD Create Read Update Delete 

@app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    product = Product.query.get(product_id)
    form = ProductForm(name=product.name, price=product.price)
    if form.validate_on_submit():
        product.name = form.name.data
        product.artist = form.artist.data
        product.price = form.price.data
        if form.product_img.data:
            image = form.product_img.data
            filename = image.filename
            image_path = os.path.join(app.root_path, "static", "images", filename)
            image.save(image_path)
            product.img = "/static/images/" + filename 

        db.session.commit() 
        flash("Product updated succesfully", category="success")
        return redirect("/products")
    
    return render_template("edit_product.html", form=form, product=product)

@app.route("/cart")
@login_required
def cart():
    cart_product_ids = get_cart_items()
    length = len(cart_product_ids)
    
    if cart_product_ids:
        products = Product.query.filter(Product.id.in_(cart_product_ids)).all()
    else:
        products = []
    total = sum(product.price for product in products)
    
    return render_template('cart.html', products=products, cart_items=length, total=total)

@app.route('/add_to_cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    cart = session.get('cart', [])
    cart.append(item_id)
    session['cart'] = cart
    flash("Added to cart!", category="success")
    return redirect("/products")

@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    cart = session.get('cart', [])
    if item_id in cart:
        cart.remove(item_id)
        session['cart'] = cart
        flash("Removed from cart!", category="info")
    return redirect("/cart")

@app.route('/clear_cart')
@login_required
def clear_cart():
    session['cart'] = []
    flash("Cart cleared!", category="info")
    return redirect("/cart")


@app.route("/profiles/<int:profile_id>")
def profile(profile_id):
    return render_template("profile.html", user=profiles[profile_id])
    # if profile_id == 1
    # return f"id of this profile is {profile_id}, belongs to youtube"
    # else:
    # return f"id of this profile is {profile_id}, belongs to google"


@app.route("/wishlist")
@login_required
def wishlist():
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template("wishlist.html", wishlist_items=wishlist_items)


@app.route("/add_to_wishlist/<int:product_id>")
@login_required
def add_to_wishlist(product_id):
    existing = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if existing:
        flash("This artwork is already in your wishlist!", category="info")
    else:
        new_wishlist_item = Wishlist(user_id=current_user.id, product_id=product_id)
        db.session.add(new_wishlist_item)
        db.session.commit()
        flash("Added to wishlist!", category="success")
    
    return redirect(f"/detailed/{product_id}")


@app.route("/remove_from_wishlist/<int:product_id>")
@login_required
def remove_from_wishlist(product_id):
    wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
        flash("Removed from wishlist!", category="info")
    
    return redirect(f"/detailed/{product_id}")


@app.route("/delete_comment/<int:comment_id>")
@login_required
def delete_comment(comment_id):

    comment = Comment.query.get_or_404(comment_id)
    product_id = comment.product_id
    
    if current_user.role == 'Admin' or comment.user_id == current_user.id:
        db.session.delete(comment)
        db.session.commit()
    
    return redirect(f"/detailed/{product_id}")


@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.user_id != current_user.id:
        return redirect(f"/detailed/{comment.product_id}")
    
    form = CommentForm(text=comment.text)
    
    if form.validate_on_submit():
        comment.text = form.text.data
        db.session.commit()
        return redirect(f"/detailed/{comment.product_id}")
    
    return render_template("edit_comment.html", form=form, comment=comment)




@app.route('/ask', methods=['GET', 'POST'])
def ai_page():
    form = AskForm()
    
    if 'chat_history' not in session:
        session['chat_history'] = []

    if form.validate_on_submit():
        question = form.question.data
        
        session['chat_history'].append({"role": "user", "content": question})

        all_products = Product.query.all()
        products_info = "\n".join([
            f"- {p.name} by {p.artist}: ₾{p.price}" 
            for p in all_products
        ])

        system_content = f"""You are the Ornamenti.ge Website Assistant. You help users with our Georgian art marketplace.

CURRENT ARTWORKS IN CATALOG:
{products_info}

INSTRUCTIONS:
- Be brief and direct (2-3 sentences max)
- Don't use poetic or flowery language
- When asked about prices, provide the EXACT price from the list above
- When asked about artists, mention the artist name from the list
- When asked about availability, say "Visit our Catalog page to view all available artworks"
- If asked about something not in our catalog, say "We don't currently have that, but check our Catalog page for our full collection"
- For purchases: "Add items to your cart and proceed to checkout"
- For general questions: Keep it simple and helpful

Be accurate with prices and artist names!"""

        messages_to_send = [
            {
                "role": "system",
                "content": system_content
            }
        ] + session['chat_history']

        try:
            client = get_groq_client()
            if not client:
                raise Exception("API key not configured")
                
            chat_completion = client.chat.completions.create(
                messages=messages_to_send,
                model="llama-3.3-70b-versatile",
                max_tokens=200,
                temperature=0.5
            )
            answer = chat_completion.choices[0].message.content
            session['chat_history'].append({"role": "assistant", "content": answer})
            session.modified = True
            
        except Exception as e:
            print(f"ERROR: {e}")
            answer = "I'm currently studying our latest collection. Please check back in a moment or browse the catalog!"
            session['chat_history'].append({"role": "assistant", "content": answer})
            session.modified = True
        
        return redirect('/ask')

    return render_template('ask_ai.html', form=form, chat_history=session['chat_history'])



@app.route('/clear-chat')
def clear_chat():
    session.pop('chat_history', None)
    return redirect(url_for('ai_page'))


@app.route("/like_comment/<int:comment_id>")
@login_required
def like_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    existing_like = CommentLike.query.filter_by(
        comment_id=comment_id, 
        user_id=current_user.id
    ).first()
    
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        new_like = CommentLike(comment_id=comment_id, user_id=current_user.id)
        db.session.add(new_like)
        db.session.commit()
        liked = True
    
    like_count = CommentLike.query.filter_by(comment_id=comment_id).count()
  


    return jsonify({'liked': liked, 'like_count': like_count})

