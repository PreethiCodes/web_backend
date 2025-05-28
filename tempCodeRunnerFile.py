# run.py
import os
from dotenv import load_dotenv
from core.main_app import MainApp

load_dotenv()

if __name__ == "__main__":
    main_app = MainApp()
    app = main_app.get_app()
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True)
