def add(x , y):
    return x+y

def subtract(x, y):
    return x -y

def multiply(x, y):
    return x * y

def devide(x, y):
    
    if y == 0:
        return f"{x} can not be devide by 0!"
    return x/y

def calculator():
    print("Simple calculator")
    print("Operations:")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Devide")
    print("5. Exit calculator")
    
    while True:
        choice = input("Enter operation number (1/2/3/4/5): ")
        if choice == "5":
            print("Calculator exiting. Goodbye...............")
            break
        
        if choice  not in ['1','2','3','4','5']:
            print("Invalid choice please try again")
            continue
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
        
        if choice == '1':
           result = add(num1,num2)
           
        elif choice == '2':
            result = subtract(num1-num2)
        elif choice == '3':
            result = multiply(num1,num2)
        else:
            result = devide(num1,num2)
        
        print("Result: ",result)
        print()

if __name__ == "__main__":
    calculator()
        