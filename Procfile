web: PYTHONPATH=. gunicorn applications.web.app:app
worker: PYTHONPATH=. python ./applications/data_processor/data_processor.py
