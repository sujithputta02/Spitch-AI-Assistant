import mysql.connector
from config import DATABASE_PATH

def setup_database():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Sujith@20$',
        database='spitch_ai'
    )
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sys_command (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            path VARCHAR(1024) NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS web_command (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            url VARCHAR(1024) NOT NULL
        )
    ''')
    
    # Add some basic system commands
    system_commands = [
        ('notepad', 'C:\\Windows\\System32\\notepad.exe'),
        ('calculator', 'C:\\Windows\\System32\\calc.exe'),
        ('paint', 'C:\\Windows\\System32\\mspaint.exe'),
        ('wordpad', 'C:\\Program Files\\Windows NT\\Accessories\\wordpad.exe'),
        ('explorer', 'C:\\Windows\\explorer.exe'),
        ('control panel', 'C:\\Windows\\System32\\control.exe'),
        ('task manager', 'C:\\Windows\\System32\\taskmgr.exe'),
        ('cmd', 'C:\\Windows\\System32\\cmd.exe'),
        ('powershell', 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe')
    ]
    
    # Add some basic web commands
    web_commands = [
        ('google', 'https://www.google.com'),
        ('youtube', 'https://www.youtube.com'),
        ('facebook', 'https://www.facebook.com'),
        ('twitter', 'https://twitter.com'),
        ('linkedin', 'https://www.linkedin.com'),
        ('github', 'https://github.com'),
        ('stack overflow', 'https://stackoverflow.com'),
        ('wikipedia', 'https://www.wikipedia.org'),
        ('amazon', 'https://www.amazon.com'),
        ('netflix', 'https://www.netflix.com')
    ]
    
    # Insert system commands
    for name, path in system_commands:
        cursor.execute('INSERT IGNORE INTO sys_command (name, path) VALUES (%s, %s)', (name, path))
    
    # Insert web commands
    for name, url in web_commands:
        cursor.execute('INSERT IGNORE INTO web_command (name, url) VALUES (%s, %s)', (name, url))
    
    conn.commit()
    conn.close()
    print("Database setup completed successfully!")

if __name__ == "__main__":
    setup_database() 