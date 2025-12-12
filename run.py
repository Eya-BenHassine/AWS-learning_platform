import os
from app import create_app, db
from app.models import User, Course, Module, Enrollment, UserProgress
from app.routes import init_sample_data
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Course': Course,
        'Module': Module,
        'Enrollment': Enrollment,
        'UserProgress': UserProgress
    }

# Initialize database with sample data
with app.app_context():
    db.create_all()
    init_sample_data()
    
    # Create an admin user if none exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        from app import bcrypt
        admin_user = User(
            username='admin',
            email='admin@awslearning.com',
            password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created: admin / admin123")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)