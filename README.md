# Smart SQL Agent

## Backend

```bash
cd backend

pip install -r requirements.txt

cp .env.example .env

uvicorn app.main:app --reload
```

## Frontend

```bash
cd frontend

npm install

npm run dev
```