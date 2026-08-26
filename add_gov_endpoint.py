import re

with open('6_builder_app.py', 'r', encoding='utf-8') as f:
    text = f.read()

endpoint_code = '''
@app.route('/governance_stats', methods=['GET'])
def governance_stats():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(__file__), 'workspace', 'governance.db')
    if not os.path.exists(db_path):
        return jsonify({"total_sessions": 0, "total_actions": 0, "uncensored_sessions": 0})
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM sessions WHERE is_uncensored = 1")
        uncensored_sessions = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM actions")
        total_actions = c.fetchone()[0]
        
        c.execute("SELECT model, COUNT(*) FROM sessions GROUP BY model")
        models = dict(c.fetchall())
        
        conn.close()
        return jsonify({
            "total_sessions": total_sessions,
            "total_actions": total_actions,
            "uncensored_sessions": uncensored_sessions,
            "models_used": models
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/build', methods=['POST'])
'''

text = text.replace("@app.route('/build', methods=['POST'])", endpoint_code.strip())
with open('6_builder_app.py', 'w', encoding='utf-8') as f:
    f.write(text)
