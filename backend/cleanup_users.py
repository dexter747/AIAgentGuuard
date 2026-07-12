import os
#!/usr/bin/env python3
"""
Clean up all users from database for testing
"""
import subprocess

def cleanup_via_sql():
    """Cleanup using direct SQL via psql"""
    
    # Get DB URL from .env
    db_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/agentguard_db")
    
    sql_commands = "DELETE FROM users; DELETE FROM organizations;"
    
    try:
        result = subprocess.run(
            ['psql', db_url, '-c', sql_commands],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Database cleaned successfully!")
            print(result.stdout)
        else:
            print(f"❌ Error: {result.stderr}")
    except FileNotFoundError:
        print("❌ psql command not found. Install PostgreSQL client tools.")
        print("\nAlternative: Use this SQL in your database client:")
        print(sql_commands)

if __name__ == "__main__":
    print("Cleaning up database...")
    cleanup_via_sql()


