from flask import Flask, request, jsonify, render_template_string
from markupsafe import escape

app = Flask(__name__)


BOOKS = [
    {
        "id": 1, 
        "title": "Lập trình Python Căn Bản", 
        "author": "Nguyễn Văn A", 
        "year": 2022, 
        "category": "Lập trình", 
        "available": True
    },
    {
        "id": 2, 
        "title": "Cấu trúc dữ liệu và Giải thuật", 
        "author": "Trần Thị B", 
        "year": 2021, 
        "category": "Lập trình", 
        "available": False
    },
    {
        "id": 3, 
        "title": "Lịch sử Thế giới Cổ đại", 
        "author": "John Doe", 
        "year": 2019, 
        "category": "Lịch sử", 
        "available": True
    },
    {
        "id": 4, 
        "title": "Đại số Tuyến tính Ứng dụng", 
        "author": "Lê Văn C", 
        "year": 2020, 
        "category": "Toán học", 
        "available": True
    },
]


BASE_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{{ title }} - LibraryMS</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; color: #333; }
        nav { background: #2c3e50; padding: 12px 20px; margin-bottom: 20px; border-radius: 5px; }
        nav a { color: white; margin-right: 20px; text-decoration: none; font-weight: bold; }
        nav a:hover { text-decoration: underline; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background-color: #f4f4f4; }
        .filter-bar { background: #f8f9fa; padding: 12px; border-radius: 5px; margin-bottom: 15px; border: 1px solid #e9ecef; }
        .filter-bar a { margin-right: 12px; text-decoration: none; color: #007bff; }
        .filter-bar a.active { font-weight: bold; color: #dc3545; text-decoration: underline; }
        .badge-success { color: green; font-weight: bold; }
        .badge-danger { color: red; font-weight: bold; }
        .card { border: 1px solid #ddd; padding: 20px; border-radius: 5px; background: #fafafa; }
    </style>
</head>
<body>
    <nav>
        <a href="{{ url_for('index') }}">Trang chủ</a>
        <a href="{{ url_for('books') }}">Danh sách sách</a>
    </nav>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    total_books = len(BOOKS)
    available_books = sum(1 for b in BOOKS if b["available"])
    
    html = BASE_HTML.replace("{% block content %}{% endblock %}", """
        <h1>Trang chủ - LibraryMS v0.1</h1>
        <div class="card">
            <p><strong>Tổng số đầu sách:</strong> {{ total_books }}</p>
            <p><strong>Số sách sẵn sàng cho mượn:</strong> {{ available_books }}</p>
        </div>
    """)
    return render_template_string(html, title="Trang chủ", total_books=total_books, available_books=available_books)



@app.route("/books")
def books():
    category = request.args.get("category", "").strip()
    
    
    categories = sorted(list(set(b["category"] for b in BOOKS)))
    
    
    if category:
        filtered_books = [b for b in BOOKS if b["category"].lower() == category.lower()]
    else:
        filtered_books = BOOKS
        
    html = BASE_HTML.replace("{% block content %}{% endblock %}", """
        <h1>Danh sách sách</h1>
        <div class="filter-bar">
            <strong>Thể loại:</strong>
            <a href="{{ url_for('books') }}" class="{% if not selected_cat %}active{% endif %}">Tất cả</a>
            {% for cat in categories %}
                <a href="{{ url_for('books', category=cat) }}" 
                   class="{% if selected_cat == cat %}active{% endif %}">
                   {{ cat | e }}
                </a>
            {% endfor %}
        </div>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Tên sách</th>
                    <th>Tác giả</th>
                    <th>Thể loại</th>
                    <th>Năm xuất bản</th>
                    <th>Trạng thái</th>
                </tr>
            </thead>
            <tbody>
                {% for book in books_list %}
                <tr>
                    <td>{{ book.id }}</td>
                    <td><a href="{{ url_for('book_detail', book_id=book.id) }}">{{ book.title | e }}</a></td>
                    <td>{{ book.author | e }}</td>
                    <td>{{ book.category | e }}</td>
                    <td>{{ book.year }}</td>
                    <td>
                        {% if book.available %}
                            <span class="badge-success">Sẵn sàng</span>
                        {% else %}
                            <span class="badge-danger">Đã mượn</span>
                        {% endif %}
                    </td>
                </tr>
                {% else %}
                <tr><td colspan="6">Không tìm thấy sách nào thuộc thể loại này.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    """)
    return render_template_string(
        html, 
        title="Danh sách sách", 
        books_list=filtered_books, 
        categories=categories, 
        selected_cat=category
    )



@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    
    if not book:
        
        error_msg = f"Không có sách với ID = {escape(book_id)}"
        html = BASE_HTML.replace("{% block content %}{% endblock %}", f"""
            <h1>Lỗi 404</h1>
            <div class="card" style="border-color: #dc3545;">
                <p style="color: #dc3545; font-size: 18px;"><strong>{error_msg}</strong></p>
                <p><a href="{{{{ url_for('books') }}}}"> Quay lại danh sách sách</a></p>
            </div>
        """)
        return render_template_string(html, title="Không tìm thấy sách"), 404

    html = BASE_HTML.replace("{% block content %}{% endblock %}", """
        <h1>Chi tiết sách</h1>
        <div class="card">
            <h2>{{ book.title | e }}</h2>
            <p><strong>Mã sách (ID):</strong> {{ book.id }}</p>
            <p><strong>Tác giả:</strong> {{ book.author | e }}</p>
            <p><strong>Thể loại:</strong> {{ book.category | e }}</p>
            <p><strong>Năm xuất bản:</strong> {{ book.year }}</p>
            <p><strong>Trạng thái:</strong> 
                {% if book.available %}
                    <span class="badge-success">Sẵn sàng cho mượn</span>
                {% else %}
                    <span class="badge-danger">Đã mượn</span>
                {% endif %}
            </p>
            <p><a href="{{ url_for('books') }}"> Quay lại danh sách</a></p>
        </div>
    """)
    return render_template_string(html, title=book["title"], book=book)



@app.route("/api/books")
def api_books():
    return jsonify(BOOKS)

@app.route("/api/books/<int:book_id>")
def api_book_detail(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": f"Không có sách với ID = {book_id}"}), 404
    return jsonify(book)



@app.errorhandler(404)
def page_not_found(e):
    html = BASE_HTML.replace("{% block content %}{% endblock %}", """
        <h1>Lỗi 404 - Trang không tồn tại</h1>
        <div class="card">
            <p>Đường dẫn bạn truy cập không tồn tại trên hệ thống.</p>
            <p><a href="{{ url_for('index') }}">Quay lại trang chủ</a></p>
        </div>
    """)
    return render_template_string(html, title="404 Not Found"), 404


if __name__ == "__main__":
    app.run(debug=True)