password =input("Enter a password to test its security: ")

score = 0

if len(password) >= 8:
    score += 1

if any(char.isupper() for char in password):
    score += 1

if any(char.islower() for char in password):
    score += 1

if any(char.isdigit() for char in password):
    score += 1

if any(not char.isalnum() for char in password):
    score += 1

print() 

if score <= 2:
    print("Weak password. Please consider using a stronger password with a mix of uppercase, Lowercase, numbers and special characters for your own data security.")

elif score <= 4:
    print("Moderate password. Please consider adding more complexity to your password for better security.")

else:
    print("Strong password. Your password is secure. However, please be advised due to changing security that passwords must be sufficiently updgraded to meet security threats and data protection policies.")