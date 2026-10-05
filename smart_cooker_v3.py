x=1
while x>0 :
    try :
      wistle=int(input("Enter number of wistles (max 10)"))
      i=0
      for i in range(11) :
        if i>=wistle :
          print("Turn off the gas")
          x=x-1
          break
        elif i<wistle :
          a=input("wistle")
          if a.strip().lower()=="stop":
             x=x-1
             break
          else :
             i=i+1
    except ValueError :
       print("Please enter proper value")