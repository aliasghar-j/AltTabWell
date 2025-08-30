from app import app, db
from models import User, WellnessRecord, StepRecord, NutritionRecord, Department

def init_database():
    with app.app_context():
        # Drop all tables to ensure a clean slate
        db.drop_all()
        print("Existing tables dropped.")

        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Add some sample data for testing
        if Department.query.count() == 0:
            print("Adding sample departments...")
            departments = ['IT', 'Marketing', 'Finance', 'Human Resources']
            for dept_name in departments:
                department = Department(name=dept_name)
                db.session.add(department)
            db.session.commit()
            print("Sample departments added!")

        if User.query.count() == 0:
            print("Adding sample users...")
            
            # Get departments to assign to users
            it_dept = Department.query.filter_by(name='IT').first()
            marketing_dept = Department.query.filter_by(name='Marketing').first()
            finance_dept = Department.query.filter_by(name='Finance').first()

            sample_users = [
                User(
                    email='john.doe@example.com',
                    name='John Doe',
                    department_id=it_dept.id,
                    google_id='sample_google_id_1'
                ),
                User(
                    email='jane.smith@example.com',
                    name='Jane Smith',
                    department_id=marketing_dept.id,
                    google_id='sample_google_id_2'
                ),
                User(
                    email='mike.johnson@example.com',
                    name='Mike Johnson',
                    department_id=finance_dept.id,
                    google_id='sample_google_id_3'
                )
            ]
            
            for user in sample_users:
                db.session.add(user)
            
            db.session.commit()
            print("Sample users added!")
            
            # Add sample step records
            from datetime import datetime, timedelta
            import random
            
            users = User.query.all()
            for user in users:
                for i in range(7):  # Last 7 days
                    date = datetime.utcnow().date() - timedelta(days=i)
                    steps = random.randint(5000, 15000)
                    
                    step_record = StepRecord(
                        user_id=user.id,
                        date=date,
                        steps=steps
                    )
                    db.session.add(step_record)
            
            db.session.commit()
            print("Sample step records added!")

if __name__ == '__main__':
    init_database()
