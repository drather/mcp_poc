import json
from flask import Flask, jsonify, request
import datetime

app = Flask(__name__)

# DB 파일 경로 (app.py가 있는 was 폴더 기준)
DB_PATH = 'db/db.json'

def read_db():
    """DB 파일을 읽어 JSON 데이터를 반환합니다."""
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 파일이 없는 경우, 초기 구조를 반환합니다.
        return {"tasks": []}

def write_db(data):
    """JSON 데이터를 DB 파일에 기록합니다."""
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    return "MCP WAS Server is running!"

# [GET] 모든 할 일 목록을 조회하는 API
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    db = read_db()
    return jsonify(db.get('tasks', []))

# [GET] ID로 특정 할 일을 조회하는 API
@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    db = read_db()
    task = next((task for task in db.get('tasks', []) if task['id'] == task_id), None)
    if task:
        return jsonify(task)
    return jsonify({'error': 'Task not found'}), 404

# [POST] 새로운 할 일을 추가하는 API
@app.route('/api/tasks', methods=['POST'])
def create_task():
    if not request.json or 'content' not in request.json:
        return jsonify({'error': 'Content is required'}), 400

    db = read_db()
    tasks = db.get('tasks', [])
    
    # 새 task 객체 생성
    new_task = {
        'id': max([t['id'] for t in tasks]) + 1 if tasks else 1,
        'content': request.json['content'],
        'status': 'pending',
        'created_at': datetime.datetime.now().isoformat()
    }
    
    tasks.append(new_task)
    db['tasks'] = tasks
    write_db(db)
    
    return jsonify(new_task), 201

if __name__ == '__main__':
    # 외부에서 접근 가능하도록 host를 '0.0.0.0'으로 설정합니다.
    # 포트는 기존 파일과 동일하게 5000번을 사용합니다.
    app.run(host='0.0.0.0', port=5000, debug=True)