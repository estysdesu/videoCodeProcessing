dir=`pwd`
.PHONY: clean build

build:
	pyisntaller ${dir}/spec/LTVideo_osx.spec || pyinstaller --specpath="spec" --onefile --add-data="${dir}/resources:resources" --icon="${dir}resources/images/clapperboard.ico" --clean --name="LTVideo" ${dir}/main.py

clean:
	rm -rf {__pycache__,venv,.vscode,dist,build}