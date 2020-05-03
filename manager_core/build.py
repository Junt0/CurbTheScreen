import os

# Create dir to store output of build
os.mkdir("build")

# Create dir for database files for PyInstaller to add

os.chdir("build")



os.system("pyinstaller __main__.spec")
