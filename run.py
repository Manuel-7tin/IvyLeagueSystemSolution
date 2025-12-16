from app import create_app
import tracemalloc
tracemalloc.start()

app = create_app()

if __name__ == "__main__":
    # app.run(host="0.0.0.0", debug=True, port=5001)
    app.run(host="0.0.0.0", port=5001)  # production
#ngrok http --url=maximum-pegasus-luckily.ngrok-free.app 5001
#SELECT setval('signees_id_seq', (SELECT MAX(id) FROM signees)+1);


#Remember to add the profile endpoint

#--- I will need this when i am splitting the routes
# # in app/__init__.py
# from app.auth import bp as auth_bp
# from app.routes import bp as routes_bp
# app.register_blueprint(auth.bp) #app/auth.py
# app.register_blueprint(routes.bp) #app/routes.py

# #ROute
# bp = Blueprint('routes', __name__)
#
# @bp.route('/dashboard')
# @login_required
# def dashboard():
#
# #APP
# bp = Blueprint('auth', __name__, url_prefix='/auth')  # <--- added url_prefix
#
#
# @bp.route('/login', methods=['POST'])
# def login():
# # login logic here