# Aqua-Verify


## 🚀 Pour tester
```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass #seulement s'il y a des problèmes avec les scripts
```

1. **Lancer le backend** :
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

2. **Lancer le frontend** (nouveau terminal) :
```bash
cd frontend
npm install
npm run dev
```

3. **Ouvrir** : http://localhost:5173