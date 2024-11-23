from flask import Blueprint, render_template, redirect, url_for, flash, request
from .models import Article, User,Comment,Rating,Like
from .forms import ArticleForm, RegistrationForm,LoginForm,CommentForm,RatingForm
from . import db, bcrypt
from flask_login import login_user, logout_user, current_user,login_required


main = Blueprint('main', __name__)

# 首頁路由 (保持不變)
@main.route('/')
@login_required
def home():
    articles = Article.query.all()
    return render_template('home.html', title="Home Page", articles=articles)

# 文章詳細頁路由
@main.route('/article/<int:article_id>', methods=['GET', 'POST'])
def article_detail(article_id):
    article = Article.query.get_or_404(article_id)
    article.views += 1
    db.session.commit()
    
    comments = Comment.query.filter_by(article_id=article.id).all()
    ratings = Rating.query.filter_by(article_id=article.id).all()

    comment_form = CommentForm()
    rating_form = RatingForm()
    is_liked = any(like.user_id == current_user.id for like in article.likes) if current_user.is_authenticated else False
    
    if comment_form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(content=comment_form.content.data, user_id=current_user.id, article_id=article.id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added!', 'success')
        return redirect(url_for('main.article_detail', article_id=article.id))

    if rating_form.validate_on_submit() and current_user.is_authenticated:
        rating = Rating(score=rating_form.score.data, user_id=current_user.id, article_id=article.id)
        db.session.add(rating)
        db.session.commit()
        flash('Rating added!', 'success')
        return redirect(url_for('main.article_detail', article_id=article.id))

    avg_rating = db.session.query(db.func.avg(Rating.score)).filter_by(article_id=article.id).scalar()

    return render_template('article_detail.html', article=article, comments=comments,is_liked = is_liked, comment_form=comment_form, rating_form=rating_form, avg_rating=avg_rating)


# 刪除文章的路由
@main.route('/article/<int:article_id>/delete', methods=['POST'])
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this article.', 'danger')
        return redirect(url_for('main.home'))
    
    db.session.delete(article)
    db.session.commit()
    flash('Article has been deleted!', 'success')
    return redirect(url_for('main.home'))


# 編輯文章的路由
@main.route('/article/<int:article_id>/edit', methods=['GET', 'POST'])
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to edit this article.', 'danger')
        return redirect(url_for('main.home'))

    form = ArticleForm()
    if request.method == 'GET':
        form.title.data = article.title
        form.author.data = article.author
        form.content.data = article.content
        form.image_url.data = article.image_url
        form.category.data = article.category
    elif request.method == 'POST':
        print("POST request received")  

        if form.validate_on_submit():
            print("Form validated and submitted")  
            article.title = form.title.data
            article.author = form.author.data
            article.content = form.content.data
            article.image_url = form.image_url.data
            article.category = form.category.data
            db.session.commit()
            flash('Article has been updated!', 'success')
            return redirect(url_for('main.article_detail', article_id=article.id))
        else:
            print("Form validation failed")  
            print(form.errors)

    return render_template('edit_article.html', title='Edit Article', form=form, article=article)

#新增文章
@main.route('/new', methods=['GET', 'POST'])
def new_article():
    if not current_user.is_authenticated:
        flash('You need to log in to create an article.', 'danger')
        return redirect(url_for('main.login'))
    
    form = ArticleForm()
    if form.validate_on_submit():
        new_article = Article(
            title=form.title.data,
            author=form.author.data,
            content=form.content.data,
            image_url=form.image_url.data,
            category=form.category.data,
            user_id=current_user.id  # 將當前使用者設置為文章的擁有者
        )
        db.session.add(new_article)
        db.session.commit()
        flash('Article has been created!', 'success')
        return redirect(url_for('main.home'))
    
    return render_template('new_article.html', title='New Article', form=form)

#註冊帳號
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('main.login'))  # 成功註冊後重定向到登入頁面
    
    return render_template('register.html', title='Register', form=form)

#登入功能
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html', title='Login', form=form)

#登出功能
@main.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

#按讚功能
@main.route('/article/<int:article_id>/like', methods=['POST'])
@login_required
def like_article(article_id):
    article = Article.query.get_or_404(article_id)
    like = Like.query.filter_by(user_id=current_user.id, article_id=article.id).first()

    if like:
        # 取消讚
        db.session.delete(like)
        db.session.commit()
        flash('You unliked the article.', 'info')
    else:
        # 按讚
        new_like = Like(user_id=current_user.id, article_id=article.id)
        db.session.add(new_like)
        db.session.commit()
        flash('You liked the article!', 'success')

    return redirect(url_for('main.article_detail', article_id=article.id))

#分類
@main.route('/category/<string:category>')
def category(category):
    articles = Article.query.filter_by(category=category).all()
    return render_template('home.html', title=category.capitalize(), articles=articles)

#刪除評論
@main.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this comment.', 'danger')
        return redirect(url_for('main.article_detail', article_id=comment.article_id))
    
    db.session.delete(comment)
    db.session.commit()
    flash('Comment has been deleted.', 'success')
    return redirect(url_for('main.article_detail', article_id=comment.article_id))