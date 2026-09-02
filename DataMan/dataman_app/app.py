"""
Entry point for the DataMan Flask app.

All application code lives in the dataman/ package: dataman/__init__.py
has the app factory (create_app()), and dataman/routes/ has one
blueprint module per activity (Answer Checker, Memory Bank, Electro
Flash, Number Guesser, Wipe Out, Force Out, Missing Number). See that
package's docstring for the module layout.
"""

from dataman import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
