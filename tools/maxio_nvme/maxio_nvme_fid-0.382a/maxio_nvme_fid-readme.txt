Программа для получения некоторой информации о nvme ssd накопителях на контроллерах Maxio MAP1xxx.
Проверена работоспособность на MAP1002,MAP1202,MAP1602.
Не работает в rom mode, но ограниченно работает в gdp mode.
Не поддеривает заблокированные прошивки MAP1602.

Для работы необходимы определенные версии драйверов. Полная поддержка:
stornvme от Windows 10 (Standard NVM Express Controller)
intel nvme 3.2, 4.0
samsung 1.4,2.3,3.0
plextor 1.4
realtek 1.4
ofa nvme 1.2-1.5
phison 1.0e (требует отключения проверки цифровой подписи)
phison 1.2

Так же возможно подключение через usb-pcie/nvme мост JMS583 (проверено с fw.205, для более старых возможно потребуется обновление),
ASM2362/4 (для 2362 нужна прошивка 19xxxx) и RTL9210[B] (нужна прошивка 1.27 или выше).

Не поддерживаются (и не будут):
microsoft stornvme от w7,w8

При необходимости совместимый драйвер можно временно принудительно поставить (причем на дисковый контроллер, а не сам диск) других производителей, он возможны и несовместимости.

Запускать с параметром - номером диска, например:
maxio_nvme_fid 0
maxio_nvme_fid 1m - сохраняет только smart, включая расширенный, в maxio_nvme_fid_smart.txt, информацию о конфигурации не опрашивает
maxio_nvme_fid 1n - вывод серийного номера
maxio_nvme_fid 1y - для отключения "press any key" перед завершением

Если запустить без параметра - будет выведен список дисков и запрос.
---
Maxio NVME SSD id v0.1a by Ochkin Vadim
OS: 10.0 build 15063
 0: (Seagate BarraCuda 120 SSD ZA250CM10003
 1: JM583
 2: (OCZ-VERTEX4
Please select drive number:
---

Отчет выводится на экран и сохраняется в файл maxio_nvme_fid.txt, который перезаписывается.
Так же сохраняется файл maxio_nvme_fid_smart.txt, в котором сохраняется стандартный nvme smart и расширенный смарт.

Примеры отчетов:

MAP1002:
---
v0.2a
OS: 6.2 build 9200 
Drive   : 2(USB)
Bridge  : ASM
Model   : SPCC M.2 PCIe SSD                       
Fw      : SVN2789 
HMB     : 16384 - 16384 KB
Size    : 244198 MB [256.1 GB]
LBA Size: 512
AdminCmd: 0x00 0x01 0x02 0x04 0x05 0x06 0x08 0x09 0x0A 0x0C 0x10 0x11 0x80 0x84 0xC1 0xC2
I/O Cmd : 0x00 0x04 0x08 0x09
Firmware id string[1C0]: MKSSD_501003000027890000,Nov 28 2020,10:14:37,MAP1002,JQYOCDLC
Project id string[180] : r:/0_release/1_release_code/3_ymtc_all_capacity/5_svn2789
Controller             : MAP1002
NAND string            : CYAxxTE1B1xC3B
NAND MaxPE cycles      : 3000
NAND Freq              : 400
Ch0CE0: 0x9b,0xc3,0x48,0x25,0x10,0x0,0x0 - YMTC 3dv2-64L TLC 16k 256Gb/CE 256Gb/die 2Plane/die
Ch3CE0: 0x9b,0xc3,0x48,0x25,0x10,0x0,0x0 - YMTC 3dv2-64L TLC 16k 256Gb/CE 256Gb/die 2Plane/die
Ch6CE0: 0x9b,0xc3,0x48,0x25,0x10,0x0,0x0 - YMTC 3dv2-64L TLC 16k 256Gb/CE 256Gb/die 2Plane/die
Ch7CE0: 0x9b,0xc3,0x48,0x25,0x10,0x0,0x0 - YMTC 3dv2-64L TLC 16k 256Gb/CE 256Gb/die 2Plane/die
Ch0CE1: 0x9b,0xc3,0x48,0x25,0x10,0x0,0x0 - YMTC 3dv2-64L TLC 16k 256Gb/CE 256Gb/die 2Plane/die
Ch3CE1: 0x9b,0xc3,0x48,0x25,0x10,0x0,0x0 - YMTC 3dv2-64L TLC 16k 256Gb/CE 256Gb/die 2Plane/die
Ch6CE1: 0x9b,0xc3,0x48,0x25,0x10,0x0,0x0 - YMTC 3dv2-64L TLC 16k 256Gb/CE 256Gb/die 2Plane/die
Ch7CE1: 0x9b,0xc3,0x48,0x25,0x10,0x0,0x0 - YMTC 3dv2-64L TLC 16k 256Gb/CE 256Gb/die 2Plane/die
---
-------- NVME SMART --------
0 Critical Warning				: 0
1 Composite Temperature				: 26
2 Available Spare				: 100
3 Available Spare Threshold			: 1
4 Percentage Used				: 0
5 Data Units Read,MB				: 7566374
6 Data Units Written,MB				: 2398338
7 Host Read Commands				: 311269602
8 Host Write Commands				: 226866606
9 Controller Busy Time				: 978
10 Power Cycles					: 49
11 Power On Hours				: 187
12 Unsafe Shutdowns				: 31
13 Media and Data Integrity Errors		: 0
14 Number of Error Information Log Entries	: 681
15 Warning Composite Temperature Time		: 0
16 Critical Composite Temperature Time		: 0
17 Temperature Sensor 0				: 27
18 Temperature Sensor 1				: 27
19 Temperature Sensor 2				: 27
20 Temperature Sensor 3				: 27
21 Temperature Sensor 4				: 27
22 Temperature Sensor 5				: 27
23 Temperature Sensor 6				: 27
24 Temperature Sensor 7				: 27
25 Thermal Management Temp 1 Transition Count	: 0
26 Thermal Management Temp 2 Transition Count	: 0
27 Total Time For Thermal Management Temp 1	: 0
28 Total Time For Thermal Management Temp 2	: 0

-------- ATA-style ExtSMART --------
 id Description                      val            raw
009 Power-on Hours Count               0            187 (0000000000BB)
012 Power Cycle Count                  0             49 (000000000031)
167 SSD Protect Mode                   0              0 (000000000000)
168 PHY Error Count                    0          23130 (000000005A5A)
169 Bad Block Count                   98      88/    11 (00000058000B)
171 Program Fail Count                 0              0 (000000000000)
172 Erase Fail Count                   0              0 (000000000000)
173 Erase Count                        0   16/  27/  21 (0010001B0015)
175 Bad Cluster Table Count          100              0 (000000000000)
192 Unexpected Power Loss Count        0             31 (00000000001F)
194 Controller Temperature,C         100              4 (000000000115)
231 SSD Life Left                    100              0 (000000000000)
241 Total LBA written,MB               0        2398338 (0000004AF2B5)
242 Total LBA read,MB                  0        7566374 (000000EC72FD)
243 Nand Temperature,C                 0              4 (000000000115)

-------- ExtSMART --------
Write?		: 512
Read?		: 823
Unk1		: 0
Unk2		: 0
Unk3		: 0
AvePE		: 21
MaxPE		: 27
MinPE		: 16
AvePE SLC	: 1310
MaxPE SLC	: 1343
MinPE SLC	: 1116
Unk7		: 0
Bad Block Count?: 11
Bad Block Count?: 88
Unk10		: 0
SSD Life Left?	: 100
---