from app import app
# Ignoring unused import errors since its needed for import of callbacks
import attribute_editor  # noqa: F401
import canvas  # noqa: F401
import sidebar  # noqa: F401

if __name__ == "__main__":
    app.run_server(debug=False)
