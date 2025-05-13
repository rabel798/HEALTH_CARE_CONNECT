from app import app, db
from models import Doctor, Assistant, Admin
from datetime import date

def init_db():
    with app.app_context():
        print("Creating database tables...")
        # Drop all tables first to start fresh
        db.drop_all()
        # Create all tables
        db.create_all()
        
        try:
            print("Creating default accounts...")
            # Create doctor account
            doctor = Doctor(
                username='drricha',
                email='drricha@eyeclinic.com',
                full_name='Dr. Richa Sharma',
                mobile_number='9876543210',
                qualifications='MBBS, MS, FPOS',
                specialization='Ophthalmology, Pediatric Eye Care'
            )
            doctor.set_password('admin123')
            db.session.add(doctor)
            print('Doctor account created')

            # Create assistant account
            assistant = Assistant(
                username='assistant',
                email='assistant@eyeclinic.com',
                full_name='Clinic Assistant',
                mobile_number='9876543211',
                position='Clinic Receptionist',
                joining_date=date.today()
            )
            assistant.set_password('assistant123')
            db.session.add(assistant)
            print('Assistant account created')

            # Create admin account
            admin = Admin(
                username='richa',
                email='admin@eyeclinic.com'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print('Admin account created')

            db.session.commit()
            print('All accounts created successfully!')
            
        except Exception as e:
            db.session.rollback()
            print(f'Error creating accounts: {str(e)}')

if __name__ == '__main__':
    init_db()
