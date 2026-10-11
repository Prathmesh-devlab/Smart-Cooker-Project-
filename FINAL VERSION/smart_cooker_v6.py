from flask import Flask, render_template,session,request

app=Flask(__name__)
app.secret_key='your_secret_key_here'

@app.route("/")
def cooker():
    if 'attempts' not in session :
      session['attempts']=0
    return render_template("cooker.html")

@app.route("/whistle", methods=["post"])
def get_wistle():
   session['whistle']=request.form.get("whistle")
   
   return render_template("whistle.html",whistle=session['whistle'],remaining=session['whistle'])

@app.route("/count", methods=["post"])
def count():

  MAX=int(session.get('whistle'))
  
  session['attempts'] +=1
  session['remaining']=MAX-session['attempts']

  if session['attempts'] >= MAX :
     return render_template("stop.html")

  if session['attempts'] < MAX :
     return render_template("whistle.html",remaining=session['remaining'])

@app.route("/reset", methods=["post"])
def reset():
   session['attempts']=0
   return render_template("cooker.html")

if __name__=="__main__": app.run( host="0.0.0.0", port=5000, debug=True)