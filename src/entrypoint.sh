#!/bin/sh

cd src

echo "----------- Run migrations -----------"
alembic upgrade head


echo "----------- Run app -----------"
uvicorn main:app --host 0.0.0.0 --port 8000 --use-colors --reload
