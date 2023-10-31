import pickle
#creat a list

names = ["ba","asd","bsd"]

print(names)

pickle.dump(names, open("names.dat", "wb"))

names.remove("ba")

names = pickle.load(open("names.dat","rb"))
print(names)