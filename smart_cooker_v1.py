wistle=int(input("Enter number of wistles (max 10)"))
i=0
for i in range(11):
    if i>=wistle :
        print("Turn off the gas")
        break
    elif i<wistle :
        input("wistle")
        i=i+1
