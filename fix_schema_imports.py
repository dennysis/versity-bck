import os

def fix_imports(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                
                content = content.replace('from schemas.', 'from app.schemas.')
                
                with open(filepath, 'w') as f:
                    f.write(content)

if __name__ == "__main__":
    fix_imports('app/routes')
