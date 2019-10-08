import os

a = "Erteilungen"
b = "von Anmeldungen"

for i in os.listdir("."):
    if ".csv" in i:
        with open(i) as f:
            data = f.read()
            
            if a not in data:
                print(i, "Wrong")
