import os
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import app, db, login_manager
from models import User, Post, Comment, Category
from forms import RegisterForm, LoginForm, PostForm, CommentForm
from werkzeug.utils import secure_filename

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def home():
    posts = Post.query.filter(Post.user_id != current_user.id).order_by(Post.date_posted.desc()).all()
    return render_template('home.html', posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Bu username band!", "danger")
            return redirect(url_for('register'))
        if User.query.filter_by(email=form.email.data).first():
            flash("Bu email band!", "danger")
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(
            fullname=form.fullname.data,
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_pw
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Ro'yxatdan o'tdingiz!", "success")
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user:
            flash("Siz ro'yxatdan o'tmagansiz", "danger")
            return redirect(url_for('register'))

        if check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Muvaffaqiyatli kirdingiz!", "success")
            return redirect(url_for('home'))
        else:
            flash("Login yoki parol noto'g'ri!", "danger")
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Chiqdingiz!", "info")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    bloglar = Post.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', bloglar=bloglar)


@app.route('/blogs')
@login_required
def blogs():
    bloglar = Post.query.filter(Post.user_id != current_user.id).all()
    return render_template('blogs.html', bloglar=bloglar)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    categories = Category.query.all() 

    if request.method == 'POST' and form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        image = request.form.get('image')  
        selected_ids = request.form.getlist('categories')  
        new_post = Post(
            title=title,
            content=content,
            image=image,
            user_id=current_user.id
        )

        for cid in selected_ids:
            category = Category.query.get(int(cid))
            if category:
                new_post.categories.append(category)

        db.session.add(new_post)
        db.session.commit()
        flash("Post yuklandi", "succes")
        return redirect(url_for('profile'))
        

    return render_template('create.html', form=form, categories=categories)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)

    if post.user_id != current_user.id:
        flash("Faqat o'z postlaringizni tahrirlashingiz mumkin!", "danger")
        return redirect(url_for('home'))

    if request.method == "POST":
        post.title = request.form.get("title")
        post.content = request.form.get("content")
        selected_ids = list(map(int, request.form.getlist("categories")))
        post.categories = Category.query.filter(Category.id.in_(selected_ids)).all()
        db.session.commit()
        flash("Post yangilandi!", "success")
        return redirect(url_for('profile', id=post.id))

    selected_categories = [c.id for c in post.categories]
    return render_template(
        "edit.html",
        form=PostForm(obj=post),
        categories=Category.query.all(),
        selected_categories=selected_categories
    )


@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.user.id != current_user.id:
        flash("Faqat o'z postlaringizni o'chirishingiz mumkin!", "danger")
        return redirect(url_for('profile'))

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_detail(post_id):
    form = CommentForm()
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id, parent_id=None).all()

    if form.validate_on_submit():
        comment_text = form.text.data
        new_comment = Comment(
            text=comment_text,
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('post_detail', post_id=post.id))

    return render_template('single-blog.html', form=form, post=post, comments=comments)


# REPLY TO COMMENT
@app.route('/reply/<int:comment_id>', methods=['POST'])
@login_required
def reply_comment(comment_id):
    parent_comment = Comment.query.get_or_404(comment_id)
    reply_text = request.form['reply']
    reply = Comment(
        text=reply_text,
        user_id=current_user.id,
        post_id=parent_comment.post_id,
        parent_id=parent_comment.id
    )
    db.session.add(reply)
    db.session.commit()
    return redirect(url_for('post_detail', post_id=parent_comment.post_id))


@app.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    file = request.files.get('avatar')
    if file:
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(app.root_path, 'static/')
        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        current_user.avatar_url = url_for('static', filename=filename)
        db.session.commit()

        flash('Profil rasmi muvaffaqiyatli yangilandi!', 'success')
        return redirect(url_for('profile'))
    else:
        flash('Rasm yuklanmadi.', 'danger')

    return redirect(url_for('profile'))


# CATEGORY ROUTE (optional)
# @app.route('/category/<int:category_id>')
# @login_required
# def posts_by_category(category_id):
#     category = Category.query.get_or_404(category_id)
#     posts = Post.query.filter_by(category_id=category.id).all()
#     return render_template('category_posts.html', category=category, posts=posts)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
