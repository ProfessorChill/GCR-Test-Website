from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Quiz, QuizAnswers
from datetime import datetime
from config import Config


@app.route('/')
def index():
    return render_template('index.html', title='Tests Login Page')


@app.route('/reports/<int:user_id>/<int:quiz_id>')
@login_required
def route_user_quiz(user_id, quiz_id):
    if request.remote_addr != Config().ADMIN_IP:
        return render_template('404.html'), 404

    quiz_results = QuizAnswers.query.filter_by(
        user_id=user_id, quiz_id=quiz_id).first()
    quiz = Quiz.query.get(quiz_id)
    user = User.query.get(user_id)

    return render_template(
        'users_quiz_results.html',
        title='Users Quiz Results',
        quiz_results=quiz_results,
        quiz=quiz,
        user=user,
    )


@app.route('/reports/<int:user_id>')
@login_required
def route_user_data(user_id):
    if request.remote_addr != Config().ADMIN_IP:
        return render_template('404.html'), 404

    user = User.query.get(user_id)
    quizes = QuizAnswers.query.filter_by(user_id=user_id)

    quizes_formatted = []

    for quiz in quizes:
        quizes_formatted.append({
            'id': quiz.id,
            'quiz_id': quiz.quiz_id,
            'score': quiz.score,
            'complete': quiz.complete,
            'start_dt': quiz.start_dt,
            'complete_dt': quiz.complete_dt,
            'quiz': Quiz.query.get(quiz.quiz_id),
        })

    return render_template(
        'user_data.html',
        title='Users Data',
        quizes=quizes_formatted,
        user=user,
    )


@app.route('/users')
@login_required
def users():
    if request.remote_addr != Config().ADMIN_IP:
        return render_template('404.html'), 404

    users = User.query.order_by(User.first_name.asc()).all()
    return render_template('users.html', title='Users List', users=users)


@app.route('/test/<int:test_id>', methods=['GET', 'POST'])
@login_required
def test(test_id):
    qry = QuizAnswers.query.filter_by(
        user_id=current_user.id, quiz_id=test_id).first()

    quiz = Quiz.query.get(test_id)
    test = {
        'name': quiz.name,
        'questions': quiz.questions,
    }

    flash('1) You must acheive 100%<br/>\
            2) Recomplete answers that have been marked with an "X"<br/>\
            3) You can save progress at the bottom of the page<br/>\
            4) Press "Submit" at the bottom of the page when complete')

    if qry:
        if qry.answers:
            for ans in qry.answers:
                test['questions'][ans['id']]['selected'] = ans['answer']
        test['percent'] = qry.score
    else:
        new_qa = QuizAnswers(
            quiz_id=test_id,
            answers=None,
            score=None,
            complete=False,
            start_dt=datetime.now(),
            complete_dt=None,
            user_id=current_user.id,
        )
        db.session.add(new_qa)
        db.session.commit()

    for qu in test['questions']:
        lesson = qu.get('lesson')

        if lesson:
            qu['lesson'] = lesson.replace('\n', '<br/>')
        else:
            qu['lesson'] = ''

    if request.method == 'POST':
        correct = 0
        error = False
        answers = []

        for qu in test['questions']:
            ans = request.form.getlist('question{}'.format(qu['id']))

            if len(ans) == 0 and error is False:
                error = True
            elif len(ans) > 0:
                qu['selected'] = ans[0]
                answers.append({
                    'id': qu['id'],
                    'answer': ans[0],
                })
                if ans[0] == qu['correct_answer']:
                    correct += 1

        test['percent'] = correct / len(test['questions']) * 100

        if qry:
            qry.answers = answers
            qry.score = test['percent']
            qry.complete = not error
            qry.complete_dt = datetime.now()
            db.session.commit()
        else:
            # The quiz should never hit this branch, but in case of some
            # fluke error, the result will still be saved.
            qry = QuizAnswers(
                quiz_id=test_id,
                answers=answers,
                score=test['percent'],
                complete=not error,  # An error means there was an issue
                start_dt=datetime.now(),
                complete_dt=datetime.now(),
                user_id=current_user.id,
            )
            db.session.add(qry)
            db.session.commit()

    return render_template('test.html', title=quiz.name, test=test)


@app.route('/tests')
@login_required
def tests():
    tests_db = Quiz.query.all()
    tests = []
    for test in tests_db:
        tests.append({
            'name': test.name,
            'url': url_for('test', test_id=test.id),
        })

    return render_template('tests.html', title='Tests', tests=tests)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thank you for registering!')

        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
