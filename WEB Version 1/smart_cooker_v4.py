from flask import Flask, render_template,session,request

app=Flask(__name__)
app.secret_key='your_secret_key_here'

@app.route("/")
def cooker():
    if 'attempts' not in session :
      session['attempts']=0
    return render_template("cooker.html")

@app.route("/wistle", methods=["post"])
def get_wistle():
   session['wistle']=request.form.get("wistle")
   return render_template("wistle.html",wistle=session['wistle'])

@app.route("/count", methods=["post"])
def count():

  MAX=int(session.get('wistle'))
  
  session['attempts'] +=1

  if session['attempts'] >= MAX :
     return render_template("stop.html")

  if session['attempts'] < MAX :
     return render_template("wistle.html")

@app.route("/reset", methods=["post"])
def reset():
   session['attempts']=0
   return render_template("cooker.html")

if __name__=="__main__": app.run( host="0.0.0.0", port=5000, debug=True)