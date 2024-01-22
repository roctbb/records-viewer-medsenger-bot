from blueprints import *

app.register_blueprint(actions_blueprint, url_prefix='/')
app.register_blueprint(medsenger_blueprint, url_prefix='/')
app.register_blueprint(api_blueprint, url_prefix='/api')


@app.route('/')
def index():
    return "Waiting for the thunder"


@app.route('/debug-sentry')
def trigger_error():
    try:
        division_by_zero = 1 / 0
    except Exception as e:
        log(e, True)
        abort(500)


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(HOST, PORT, debug=API_DEBUG)
