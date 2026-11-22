from flask import Flask, render_template,request,jsonify
import requests

app=Flask(__name__)
app.secret_key='your_secret_key_here'
target_whistles = 0
current_attempts = 0
high_temp = False
new_whistle = False

@app.route("/")
def cooker():
    global current_attempts, target_whistles
    current_attempts = 0
    target_whistles = 0   

    return render_template("cooker.html")

@app.route("/whistle", methods=["post"])
def get_wistle():
   global target_whistles, current_attempts
   target_whistles = int(request.form.get("whistle", 0))
   current_attempts = 0
   
   return render_template("whistle.html",whistle=target_whistles,remaining=target_whistles)

@app.route("/api/count", methods=["POST"])
def esp32_count():
    global current_attempts, target_whistles, new_whistle

    if target_whistles > 0 and current_attempts < target_whistles:
        current_attempts += 1
        send_telegram(
          f"✅ Whistle Detected\n"
          f"Count: {current_attempts}/{target_whistles}\n"
          f"Remaining: {target_whistles-current_attempts}"
)
        new_whistle = True
        print(f"Whistle detected! Count: {current_attempts}/{target_whistles}")

    # Ensure target_whistles > 0 before setting is_complete to True
    is_done = (target_whistles > 0) and (current_attempts >= target_whistles)

    return jsonify({
        "attempts": current_attempts,
        "remaining": max(0, target_whistles - current_attempts),
        "is_complete": is_done
    }), 200

# --- NEW: Route hit by webpage JS to check live status ---
@app.route("/api/status", methods=["GET"])
def get_status():
    global current_attempts, target_whistles, high_temp
    remaining = max(0, target_whistles - current_attempts)
    is_complete = (target_whistles > 0) and (current_attempts >= target_whistles)
    
    return jsonify({
        "attempts": current_attempts,
        "target": target_whistles,
        "remaining": remaining,
        "is_complete": is_complete,
        "is_high_temp": high_temp,
        "new_whistle": new_whistle
    })

@app.route("/stop")
def stop_page():
    return render_template("stop.html")

@app.route('/temperature_alert')
def temperature_alert():
    global high_temp
    high_temp = True
    send_telegram(
        "🔥 HIGH TEMPERATURE ALERT!\nTemperature exceeded 122°C"
    )
    print("HIGH TEMP RECEIVED")
    return "OK"
    
@app.route('/alert')
def alert():
    return render_template('alert.html')

@app.route('/clear_alert')
def clear_alert():
    global high_temp
    high_temp = False
    return "OK"

@app.route("/reset", methods=["post"])
def reset():
   return render_template("cooker.html")


@app.route('/clear_whistle')
def clear_whistle():
    global new_whistle
    new_whistle = False
    return "OK"

# --- TELEGRAM NOTIFICATION FUNCTION ---

BOT_TOKEN = "TOKEN"
CHAT_ID = "ID"

def send_telegram(msg):

    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"

    requests.get(
        url,
        params={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )



if __name__=="__main__": app.run( host="0.0.0.0", port=5000, debug=True)