# ChujAI Database 🤖

AI-powered Database with Note-taking and RAG (Retrieval Augmented Generation) capabilities

## ฟีเจอร์ 🌟

- ✍️ จดบันทึกพร้อม tags
- 🔍 ค้นหาข้อมูลด้วย semantic search
- 🤖 ถาม-ตอบกับ AI โดยใช้ข้อมูลจาก notes
- 🎯 RAG (Retrieval Augmented Generation) ช่วยให้ AI ตอบคำถามได้แม่นยำขึ้น

## การติดตั้ง 🛠️

1. Clone repository:
```bash
git clone https://github.com/yourusername/ChujaiDatabase.git
cd ChujaiDatabase
```

2. สร้าง virtual environment และติดตั้ง dependencies:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/MacOS
source venv/bin/activate

pip install -r requirements.txt
```

3. ตั้งค่า environment variables ใน .env file:
```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///./chujai.db
APP_NAME=ChujAI Database
DEBUG=True
```

4. รัน server:
```bash
uvicorn app.main:app --reload
```

## การใช้งาน API 🚀

### 1. สร้าง Note ใหม่
```bash
curl -X POST "http://localhost:8000/api/notes/" \
     -H "Content-Type: application/json" \
     -d '{"title": "My First Note", "content": "This is a test note", "tags": ["test", "first"]}'
```

### 2. ดึงรายการ Notes
```bash
# ดึงทั้งหมด
curl "http://localhost:8000/api/notes/"

# กรองด้วย tag
curl "http://localhost:8000/api/notes/?tag=test"
```

### 3. ค้นหา Notes ที่เกี่ยวข้อง
```bash
curl -X POST "http://localhost:8000/api/notes/search/" \
     -H "Content-Type: application/json" \
     -d '{"query": "your search query"}'
```

### 4. ถามคำถามกับ AI
```bash
curl -X POST "http://localhost:8000/api/notes/ask/" \
     -H "Content-Type: application/json" \
     -d '{"question": "your question here"}'
```

## API Documentation 📚

เมื่อรัน server แล้ว สามารถเข้าดู API documentation ได้ที่:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## โครงสร้างโปรเจ็ค 📁

```
ChujaiDatabase/
├── app/
│   ├── api/            # API endpoints
│   ├── models/         # Database models
│   ├── services/       # Business logic
│   └── main.py         # FastAPI application
├── requirements.txt    # Dependencies
└── .env               # Environment variables
```

## การพัฒนาต่อ 🔧

1. เพิ่ม authentication
2. เพิ่มการ export/import notes
3. เพิ่ม real-time collaboration
4. เพิ่มการ backup อัตโนมัติ
5. อื่นๆ ตามความต้องการ

## License 📄

MIT License - ดูรายละเอียดเพิ่มเติมได้ที่ [LICENSE](LICENSE)
