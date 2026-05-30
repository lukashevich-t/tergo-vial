## tergo-layout@tlukashevich.com
Расширения для Cinnamon desktop и Gnome desktop для отправки сообщений о смене раскладки в клавиатуру T-Ergo на основе прошивки QMK-vial  

### Установка
- при желании можно заново скомпилировать программу для общения с клавиатурой:
```bash
apt install libhidapi-dev gcc -y 
gcc send_hid.c -o send_hid -lhidapi-hidraw -s
```
- В файлах `cinnamon.yaml` и `gnome.yaml` в секции переменных указать "координаты" клавиатуры: vid (5954), pid(0003) и hid_raw_usage_page (FF60 по умолчанию для клавиатур на QMK)
- запустить установку для нужного десктопа:
```bash
ansible-playbook cinnamon.yaml -K
# или ansible-playbook gnome.yaml -K
```
- перезапустить рабочий стол (просто выйти и зайти не сработает):
```bash
systemctl restart display-manager # для gnome
systemctl restart lightdm # для cinnamon
```

### Полезные команды
#### Gnome
```bash
# отключить расширение:
gnome-extensions disable tergo-layout@tlukashevich.com
# Перезагрузить расширение. Всё равно не работает, и надо при изменениях перестартовать display-manager:
gnome-extensions reset tergo-layout@tlukashevich.com
# включить расширение
gnome-extensions enable tergo-layout@tlukashevich.com
# список включённых расширений
gsettings get org.gnome.shell enabled-extensions
# список всех расширений
gnome-extensions list
```

Наблюдать за логами:
```bash
journalctl -f -g 'tergo'
```
