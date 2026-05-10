# Назначение
Макрос FreeCAD для нанесения гравировки на кейкапы [KLP-Lame](https://github.com/braindefender/KLP-Lame-Keycaps)  
Испытывался на кейкапах "Choc stem - choc size" в FreeCAD v1.1.1  

# Установка
проще всего создать симлинки:
```bash
cd $HOME/.local/share/FreeCAD/v1-1/Macro
ln -s /path_to_repo/freecad-keycaps-engrave/keycap_engrave.FCMacro
ln -s /path_to_repo/freecad-keycaps-engrave/keycap_engrave_libs
```

Но можно и просто скопировать файл `keycap_engrave.FCMacro` и папку `keycap_engrave_libs` в `$HOME/.local/share/FreeCAD/v1-1/Macro/`  

# Разработка
Для настройки удобств при разработке макросов для FreeCAD в VS Code + Pylance придётся сделать кучу шагов:
- Freecad поставляется в формате AppImage, а это по сути образ squashfs. Настроим, чтобы он всегда монтировался:
```bash
sudo mkdir /mnt/freecad
# Узнаем, с какого смещения в файле Appimage начинается собственно образ:
OFFSET=`/opt/AppImages/FreeCAD_1.1.1-Linux-x86_64-py311.AppImage --appimage-offset`
echo "/opt/AppImages/FreeCAD_1.1.1-Linux-x86_64-py311.AppImage /mnt/freecad   squashfs        loop,offset=$OFFSET      0 0" | sudo tee -a /etc/fstab
```

- установить freecad-stubs:
	a. из гитхаба:
	```bash
	mkdir -p /home/tim/work/freecad && cd $_
	git clone https://github.com/ostr00000/freecad-stubs.git
	```
	b. в виртуальное окружение
	```bash
	mkdir -p /home/tim/work/freecad && cd $_
	python3 -m venv freecad-venv
	source freecad-venv/bin/activate
	pip3 install freecad-stubs
	```
- в проекте создать файл `.vscode/settings.json`:
```json
{
	"files.associations": {
	    "*.FCMacro": "python" // чтобы VSCode считал файлы *.FCMacro кодом на Python
	},
    "python.analysis.extraPaths": [
      "./libs", // просто наша либа в рамках проекта
      "/mnt/freecad/usr/bin", // пути к папкам с so-файлами Freecad
      "/mnt/freecad/usr/lib"
    ],
	"python.analysis.stubPath": "/home/tim/work/freecad/freecad-stubs/freecad_stubs", // путь к стабам (биндингам)
	"python.analysis.typeCheckingMode": "standard",
}
```

# Проблемы
Иногда случаются проблемы при нанесении гравировки. Помогает открыть проблемный кейкап в FreeCAD и поднять выдавленный 3Д-текст на 1 мкм по оси Z.
