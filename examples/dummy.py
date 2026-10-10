file1=["1,a,200", "2,b,300", "3,c,400"]
file2=["2,a,200", "2,b,300", "3,c,400"]

for i in file1:
    id1=i.split(",")[0]
    found=False
    for j in file2:
        id2=j.split(",")[0]

        if id1==id2:
            found=True
            print("Id matched: ", id2)
            if i==j:
                print("item matched", i)
            else:
                print("Id matched but item didnt match")
        else:
            print("not matched")
    if not found:
        print("missing in file2")
for j in file2:
    id2=j.split(",")[0]
    if not any(id2==i.split(",")[0] for i in file1):
        print("missing in file 1")