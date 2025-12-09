from flask import Flask, render_template, request, redirect, session
from instagrapi import Client
import threading
import time
import random
import uuid

app = Flask(__name__)
app.secret_key = "sujal_spam_king_007_2025"

users_data = {}

# Random Group Names (tere dost jaisa)
GROUP_NAMES = [
    "KING BHEEKMANG",
    "SMOKER/NITISH TMKB CHUD RNDIKE",
    "SPAMERABBU PRO MAX",
    "RAMU KAKA LADKE TMKC",
    "SUJAL BAAP KA RAJ",
    "BHEEKMANG ON TOP",
    "CHUD GAYA INSTA",
    "NITISH RANDIKE",
    "KING KUNAL EBUU",
    "DEVIL NOOR SHER"
]

def add_log(user_id, msg, color="lime"):
    if user_id not in users_data:
        users_data[user_id] = {"logs": []}
    timestamp = time.strftime('%H:%M:%S')
    users_data[user_id]["logs"].append({"time": timestamp, "msg": msg, "color": color})
    if len(users_data[user_id]["logs"]) > 500:
        users_data[user_id]["logs"] = users_data[user_id]["logs"][-500:]

def change_group_name(client, thread_id):
    try:
        new_name = random.choice(GROUP_NAMES)
        # Real like change
        client.group_chat_title_change(thread_id, new_name)
        return new_name
    except:
        return None

def spam_worker(user_id, client, thread_ids, messages, delay, change_name):
    while users_data[user_id]["running"]:
        try:
            thread_id = random.choice(thread_ids)
            msg = random.choice(messages)
            client.direct_send(msg, thread_ids=[thread_id])
            users_data[user_id]["total_sent"] += 1
            add_log(user_id, f"Sent to GC {thread_id} from {client.username}: {msg[:50]}...", "lime")

            if change_name and random.random() < 0.3:  # 30% chance
                new_name = change_group_name(client, thread_id)
                if new_name:
                    add_log(user_id, f"GC {thread_id} name changed to {new_name}", "yellow")

            time.sleep(delay * random.uniform(0.9, 1.2))
        except Exception as e:
            add_log(user_id, f"Error: {str(e)}", "red")
            time.sleep(20)

@app.route('/', methods=['GET', 'POST'])
def index():
    user_id = session.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id
        users_data[user_id] = {
            "running": False,
            "total_sent": 0,
            "logs": [],
            "clients": []
        }

    data = users_data[user_id]

    if request.method == 'POST':
        data["running"] = False
        time.sleep(2)
        data["logs"] = []
        add_log(user_id, "New spam session started", "cyan")

        usernames = [u.strip() for u in request.form['usernames'].split(',') if u.strip()]
        passwords = [p.strip() for p in request.form['passwords'].split(',') if p.strip()]
        thread_ids = [int(t.strip()) for t in request.form['thread_ids'].split(',') if t.strip()][:10]  # Max 10 GC

        messages = [m.strip() for m in request.form['messages'].split('\n') if m.strip()]
        delay = float(request.form['delay'])
        change_name = 'change_name' in request.form

        data["total_sent"] = 0
        data["running"] = True
        data["clients"] = []

        for i in range(len(usernames)):
            cl = Client()
            try:
                cl.login(usernames[i], passwords[i])
                add_log(user_id, f"Account {usernames[i]} logged in", "lime")
                data["clients"].append(cl)
                t = threading.Thread(target=spam_worker, args=(user_id, cl, thread_ids, messages, delay, change_name), daemon=True)
                t.start()
            except Exception as e:
                add_log(user_id, f"Account {usernames[i]} failed: {str(e)}", "red")

        add_log(user_id, f"SPAM STARTED - {len(thread_ids)} GC | {len(usernames)} IDs | Delay {delay}s", "lime")

    return render_template('index.html',
        total_sent=data.get("total_sent", 0),
        logs=data.get("logs", [])
    )

@app.route('/stop')
def stop():
    user_id = session.get('user_id')
    if user_id and user_id in users_data:
        users_data[user_id]["running"] = False
        add_log(user_id, "SPAM STOPPED", "red")
    return redirect('/')

@app.route('/clear')
def clear():
    user_id = session.get('user_id')
    if user_id and user_id in users_data:
        users_data[user_id]["logs"] = []
    return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
