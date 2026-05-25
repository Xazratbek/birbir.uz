# Frontend (API-integrated prototype)

Run quickly with static server:

```bash
cd frontend
python -m http.server 5173
```

Open: http://localhost:5173

If backend URL differs from `http://localhost:8000`, run in browser console:

```js
localStorage.setItem('api_base', 'http://YOUR_BACKEND_HOST');
location.reload();
```
