import pickle

# Create binary file
f = open("student.dat", "wb")

n = int(input("Enter number of students: "))

for i in range(n):
    roll = int(input("Enter roll no: "))
    name = input("Enter name: ")
    marks = float(input("Enter marks: "))

    student = [roll, name, marks]
    pickle.dump(student, f)

f.close()

# Update marks
roll_no = int(input("\nEnter roll no to update marks: "))
new_marks = float(input("Enter new marks: "))

f = open("student.dat", "rb")
students = []

try:
    while True:
        student = pickle.load(f)

        if student[0] == roll_no:
            student[2] = new_marks

        students.append(student)

except EOFError:
    f.close()

# Rewrite file with updated data
f = open("student.dat", "wb")

for student in students:
    pickle.dump(student, f)

f.close()

print("Marks updated successfully.")