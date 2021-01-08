from const import DEBUG
from web import create_app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=DEBUG)
