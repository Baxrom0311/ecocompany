# ECO COMPANY backend

FastAPI + SQLAlchemy + PostgreSQL API: mahsulotlar, galereya, sertifikatlar, kontaktlar, sozlamalar, admin va DeepSeek/FastMCP chatbot.

## Lokal ishga tushirish

```sh
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env ichida DATABASE_URL va JWT_SECRET ni kiriting
alembic upgrade head
python scripts/seed.py
python scripts/create_admin.py --email admin@ecocompany.uz
uvicorn app.main:app --reload
```

Mijoz sayti `http://localhost:8080`, admin `http://localhost:8081`, API `http://localhost:8000/api/v1`. Lokal `.env` uchun `ALLOWED_ORIGINS=http://localhost:8080,http://localhost:8081` qo‘ying. Swagger kerak bo‘lsa `ENVIRONMENT=development` qo‘ying va `/docs` ni oching.

## Yangilash va deployment

Yangilangan paketlarni o‘rnating va **serverni qayta ishga tushirishdan oldin** `alembic upgrade head` bajaring. `003_user_token_version` mavjud adminlar uchun token revokatsiyasi maydonini qo‘shadi. Oldingi versiyadagi tokenlar yaroqsiz bo‘ladi; adminlar qayta login qiladi. Parol almashtirish va logout shu akkauntning barcha tokenlarini bekor qiladi.

ASGI server uchun:

```sh
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

HTTPS reverse proxy orqali yo‘naltiring. Passenger/cPanel ishlatilsa Python interpreter, application root va environment qiymatlarini cPanel ichida sozlang; startup fayl `passenger_wsgi.py`, callable `application`. Adapter ASGI lifespan ni ham ishga tushiradi, shuning uchun REST va HTTP MCP bir jarayonda ishlaydi. Lokal WSGI va MCP regression testlari bor; konkret hostingning timeout, process va proxy sozlamalarini o‘sha serverda tekshirish kerak.

`PUBLIC_BASE_URL` — API/media domeni (masalan, `https://api.example.com`). `SITE_URL` — mijoz sayti domeni (masalan, `https://www.example.com`); alohida domen ishlatilganda uni majburiy sozlang. `ALLOWED_ORIGINS` ga mijoz va admin domenlarini kiriting.

`media/` persistent storage bo‘lishi kerak. Yangi uploadlarda fayl mazmuni, kengaytmasi va hajmi tekshiriladi; rasmlar metadata olib tashlanib qayta kodlanadi. SVG va HTML yuklash qabul qilinmaydi. PDF/video uchun format signaturalari tekshiriladi; PDF attachment sifatida beriladi. Boshqa obyekt hali foydalanayotgan fayl o‘chirilmaydi.

Rate limit: umumiy 120/minut, login 5/minut, kontakt 5/soat, chat 20/soat; hisob har bir backend jarayoni xotirasida yuritiladi. Ko‘p worker/replica ishlatilsa umumiy limit uchun shared storage yoki reverse proxy limitini sozlang. Proxy ortida haqiqiy mijoz IP sini faqat ishonchli proxy orqali uzating.

## Chatbot va integratsiyalar

Saytdagi pastki o‘ng chat tugmasi `/api/v1/chat` ga murojaat qiladi. `DEEPSEEK_API_KEY` backend `.env` faylida beriladi; frontendga kalit yozilmaydi. `DEEPSEEK_BASE_URL` va `DEEPSEEK_MODEL` ham shu yerda sozlanadi. API kaliti bo‘lmasa foydalanuvchi chat sozlanmaganligi haqida javob oladi. AI prompt super-admin sozlamalarida boshqariladi. Public ma’lumotlar uchun HTTP MCP endpoint: `/api/v1/mcp/`.

SMTP 587 uchun standart sozlama: `SMTP_USE_TLS=false`, `SMTP_START_TLS=true`. Implicit TLS/465 ishlatilsa `SMTP_PORT=465`, `SMTP_USE_TLS=true`, `SMTP_START_TLS=false` qo‘ying. Telegram uchun bot tokeni va chat ID larini backend `.env` da kiriting. Instagram videolari admin panelida link bilan boshqariladi; token refresh cron kerak emas.

## Tekshiruv

```sh
python -m pytest tests -q
```

Testlar vaqtinchalik media, in-memory SQLite va test kalitlarini ishlatadi; developer bazasi va haqiqiy integratsiya kalitlari ishlatilmaydi. Regression testlar login limiti, token revokatsiyasi, upload, chat, MCP, WSGI adapter va yangi/mavjud bazadagi migratsiyalarni qamraydi. PostgreSQL/hosting integratsiyasini deploy muhitida alohida tekshiring.
