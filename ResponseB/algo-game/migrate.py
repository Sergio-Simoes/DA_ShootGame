"""
Migration script to help set up the refactored game from the original files.
"""

import os
import shutil
import sys


def migrate_project(source_dir):
    """
    Migrate files from the original project structure.
    
    Args:
        source_dir: Path to the original algo-game directory
    """
    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' not found!")
        return False
        
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create teams directory if it doesn't exist
    teams_dir = os.path.join(current_dir, "teams")
    if not os.path.exists(teams_dir):
        os.makedirs(teams_dir)
        print(f"Created teams directory: {teams_dir}")
        
    # Copy team scripts
    source_teams = os.path.join(source_dir, "teams")
    if os.path.exists(source_teams):
        for file in os.listdir(source_teams):
            if file.endswith(".py"):
                src = os.path.join(source_teams, file)
                dst = os.path.join(teams_dir, file)
                shutil.copy2(src, dst)
                print(f"Copied team script: {file}")
                
    # Copy image assets
    for asset in ["cannon.png", "ball.png"]:
        src = os.path.join(source_dir, asset)
        if os.path.exists(src):
            dst = os.path.join(current_dir, asset)
            shutil.copy2(src, dst)
            print(f"Copied asset: {asset}")
        else:
            print(f"Warning: Asset '{asset}' not found in source directory")
            
    print("\nMigration complete!")
    print("\nTo run the game: python game.py")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        source_path = sys.argv[1]
    else:
        # Try to find the original directory in the inputs
        possible_path = "/tmp/inputs/Original/algo-game"
        if os.path.exists(possible_path):
            source_path = possible_path
        else:
            print("Usage: python migrate.py <path_to_original_algo-game_directory>")
            sys.exit(1)
            
    migrate_project(source_path)
