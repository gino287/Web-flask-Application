from app import db, create_app

app = create_app()

# 初始化資料庫（第一次運行時創建資料庫）
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)