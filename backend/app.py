from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from database import db
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, origins="*", supports_credentials=True)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
db.init_app(app)

from routes.auth import auth_bp
from routes.projects import projects_bp
from routes.tasks import tasks_bp
from routes.users import users_bp
from routes.dashboard import dashboard_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(projects_bp, url_prefix='/api/projects')
app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

with app.app_context():
    db.create_all()

@app.route('/api/health')
def health():
    return {'status': 'ok', 'message': 'TaskFlow API running'}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    from flask import render_template
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
