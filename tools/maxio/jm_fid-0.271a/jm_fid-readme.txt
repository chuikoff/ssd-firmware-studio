ѕрограмма предназначена дл€ определени€ флеша у ssd накопителей на контроллерах jmicron/maxiotek/maxio
ƒолжны поддерживатьс€: jmf605/6/7/8, jmf612/16/18, jmf661/2/7/8, jmf670, mk8113/5, mas0902(cs1802a,mk8215,dm9343)
Ќе проверены mk8113/mas0901.
Ќе поддерживаетс€ mas1102.
Ќе поддерживаютс€ jmf601/2/3.
ѕоддерживаетс€ работа с диском в rom mode, но при этом отсутствует автоопределение и необходимо скопировать соответствующий контроллеру gdpXXXX.bin в gdp.bin.
ѕоддерживаетс€ так же работа с диском в loader mode.

ѕоддерживаетс€ работа при подключении по sata и некоторых usb (asm1051, jm20329, jms539, etc).
Ќе работает через ma6116, старые экземпл€ры(?) jm20330.
ќ— - windows xp sp2 и выше.

«апуск:
jm_fid <номердиска>[y][w]

y - отключение всех запросов к пользователю.
w - сохранение прошивки

ѕрограмма во врем€ работы переводит диск в различные режимы, при нахождении в которых данные недоступны.
“аким образом принципиально невозможна работа с системным диском, так же крайне нежелательна работа с диском содержащим какие-либо данные во избежание их повреждени€. ¬ этом случае на врем€ запуска у разделов надо отобрать буквы.
¬ случае сбоев в работе может потребоватьс€ сн€тие питани€ с диска дл€ его приведени€ в нормальный режим.

≈сли запустить без параметров - будет выведен список накопителей в системе и запрос номера.
---
JM/MK/MAS flash ID reader v0.2a by Ochkin Vadim
 0: PLEXTOR PX-128M5S
 1: WDC WD1001FALS-00J7B
Please select drive number:
---

ѕримеры отчета:
---
v0.2a
Drive: 13(USB)
Model: KINGSTON SV200S364G                     
Fw   : E120506a
Size : 61057 MB
Firmware id string[300]: JMSSD_200222_S,May  6 2012,14:31:42,662D,42LHHA
NAND string            : TC58NVG6D2HTA00
Controller             : JMF662

Read gdp662.bin GDP Size: 69120
Switch to rom mode.. Ok
Load GDP to drive.. Run GDP.. Ok

FID  : 0x98,0xde,0xa4,0x82,0x76,0x56,0xc - Toshiba 24nm MLC 8k 64Gb/CE 64Gb/die 2Plane/die
Ch   : 8
Bank : 1
CE   : 1

FID List:
Ch0CE0: 0x98,0xde,0xa4,0x82,0x76,0x56,0xc - Toshiba 24nm MLC 8k 64Gb/CE 64Gb/die 2Plane/die
Ch1CE0: 0x98,0xde,0xa4,0x82,0x76,0x56,0xc - Toshiba 24nm MLC 8k 64Gb/CE 64Gb/die 2Plane/die
Ch2CE0: 0x98,0xde,0xa4,0x82,0x76,0x56,0xc - Toshiba 24nm MLC 8k 64Gb/CE 64Gb/die 2Plane/die
Ch3CE0: 0x98,0xde,0xa4,0x82,0x76,0x56,0xc - Toshiba 24nm MLC 8k 64Gb/CE 64Gb/die 2Plane/die
Ch4CE0: 0x98,0xde,0xa4,0x82,0x76,0x56,0xc - Toshiba 24nm MLC 8k 64Gb/CE 64Gb/die 2Plane/die
Ch5CE0: 0x98,0xde,0xa4,0x82,0x76,0x56,0xc - Toshiba 24nm MLC 8k 64Gb/CE 64Gb/die 2Plane/die
Ch6CE0: 0x98,0xde,0xa4,0x82,0x76,0x56,0xc - Toshiba 24nm MLC 8k 64Gb/CE 64Gb/die 2Plane/die
Ch7CE0: 0x98,0xde,0xa4,0x82,0x76,0x56,0xc - Toshiba 24nm MLC 8k 64Gb/CE 64Gb/die 2Plane/die

Read PP..

Switch to fw mode.. Ok
---

Firmware id string/Project id string - строчки из образа прошивки
NAND string - строка, формируема€ mptool при прошивке диска из flash.ini

jm_fid.txt - файл, в который дописываетс€ текстовый отчет (дублирует выводимое на экран)
jm_fid_ppg.txt - декодированный nand parameter page
id.bin - ata паспорт диска
jm_ec.bin - поблочные счетчики стираний блоков (форматы у разных контроллеров могут различатс€, где-то по 2 байта на элемент, где-то по 4)
jm_fw.bin - образ прошивки (насколько корректный - вопрос)
jm_id.bin - начало образа с Firmware id string/Project id string
jm_nand.bin - отсюда беретс€ NAND string
jm_pp.bin - nand parameter page
smart.bin - smart диска

--------------------
get flash id from jmicron-based ssd

posible support jmf605/6/7/8, jmf612/16/18, jmf661/2/7/8, jmf670, mk8113/5, mas0902(mk8215,cs1802)
don't support jmf601/2/3

possible work with usb2sata bridge with sat support (asm1051, jm20329, jms539, etc)

don't work with ssd connections via some older sample of pata2sata: jm20330, usb2sata: ma6116