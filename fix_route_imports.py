import os

def fix_imports(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                
              
                content = content.replace('from models.', 'from app.models.')
                
                
                content = content.replace('from config import', 'from app.config import')
                
               
                content = content.replace('from utils.', 'from app.utils.')
                
                
                content = content.replace('from services.', 'from app.services.')
                
                with open(filepath, 'w') as f:
                    f.write(content)

if __name__ == "__main__":
    fix_imports('app/routes')
