

import subprocess
import sys
import os

def run_script(script_path, description):
    """Run a Python script and handle errors"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run([sys.executable, script_path], check=True)
        print(f"\n✅ {description} - COMPLETE")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - FAILED")
        print(f"Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🏪 STORE SUPPLY CHAIN - COMPLETE SETUP")
    print("="*60)
    
    # Check if synthetic_data directory exists
    if not os.path.exists('synthetic_data'):
        os.makedirs('synthetic_data')
    
    # Step 1: Generate Data
    if not run_script('scripts/01_generate_data.py', 'STEP 1: Generate Synthetic Data'):
        print("\n❌ Setup failed at data generation")
        return
    
    input("\n✅ Data generation complete! Press ENTER to continue to PostgreSQL setup...")
    
    # Step 2: Setup PostgreSQL
    if not run_script('scripts/02_setup_postgresql.py', 'STEP 2: Setup PostgreSQL'):
        print("\n❌ Setup failed at PostgreSQL setup")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your password in config/db_config.py")
        print("3. Verify PostgreSQL is accessible on localhost:5432")
        return
    
    input("\n✅ PostgreSQL setup complete! Press ENTER to continue to MongoDB setup...")
    
    # Step 3: Setup MongoDB
    if not run_script('scripts/03_setup_mongodb.py', 'STEP 3: Setup MongoDB'):
        print("\n❌ Setup failed at MongoDB setup")
        print("\nTroubleshooting:")
        print("1. Make sure MongoDB is running")
        print("2. Check if MongoDB is accessible on localhost:27017")
        return
    
    input("\n✅ MongoDB setup complete! Press ENTER to verify setup...")
    
    # Step 4: Verify Setup
    run_script('scripts/04_verify_setup.py', 'STEP 4: Verify All Databases')
    
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. To start the real-time simulator:")
    print("   python scripts/05_realtime_simulator.py")
    print("\n2. To create the Neo4j Knowledge Graph:")
    print("   (We'll create this script next)")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()