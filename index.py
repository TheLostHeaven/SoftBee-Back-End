from app import app_create
# from src.utils.rolecreate import create_roles, create_admin_user

app = app_create()

if __name__ == '__main__':
    app = app_create()
    app.run(debug=True)