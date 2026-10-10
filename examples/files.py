file1=open('file1.txt').readlines()
file2=open("file2.txt").readlines()
print(file1)
print(file2)
for line in file1:
    if line not in file2:
        print("only in file1: ", line)

for line in file2:
    if line not in file1:
        print("only in file2: ", line)

# open and read and write files
# with open('file1.txt', 'r') as file:
#     content = file.read()
#     print(content)

# with open('file1.txt', 'w') as file:
#     file.write('hello, world!')

# with open('file1.txt', 'a') as file:
#     file.write('hello, world!')
