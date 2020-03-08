from app import app, db
from app.models import User, QuizAnswers, Quiz


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'QuizAnswers': QuizAnswers,
        'Quiz': Quiz,
    }
