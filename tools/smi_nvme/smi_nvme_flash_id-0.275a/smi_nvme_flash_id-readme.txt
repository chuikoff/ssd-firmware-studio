Утилита предназначена для получения информации о флеше в nvme ssd на контроллерах smi.
Проверена работоспособность на sm2263xt, sm2267xt, sm2268xt, sm2269xt, sm2260, sm2262, sm2262en, sm2263en, sm2264, sm2265, sm2267, sm2504, sm2508, sm8366.
Работает с дисками в rom mode.

Для работы необходимы определенные версии драйверов. Проверена работоспособность со следующими драйверами:
stornvme от Windows 10 (Standard NVM Express Controller)
intel nvme 3.2, 4.0, 4.4
smi nvme 1.4 - http://vlo.name:3000/tmph/smi_nvme_drv.rar
ограниченно работает с intel rst [17.x]

Не поддерживаются:
microsoft stornvme от w7,w8
samsung 1.4,2.3,3.0
plextor 1.4
realtek 1.4
ofa nvme 1.2-1.5

При необходимости совместимый драйвер можно временно принудительно поставить на диск(точнее дисковый контроллер) других производителей, он возможны и несовместимости.

Так же возможно подключение через usb-pcie/nvme мост JMS583 (проверено с fw.205, для более старых возможно потребуется обновление)
и ASM2362/4 (для 2362 нужна прошивка 19xxxx).

Запускать с параметром - номером диска, например:
smi_nvme_flash_id 0
smi_nvme_flash_id 1y - для отключения "press any key" перед завершением
smi_nvme_flash_id 1n - вывод серийного номера
smi_nvme_flash_id 1b - сохранение сырых данных (.bin)
smi_nvme_flash_id 1w - сохранение прошивки (для 2263xt)
параметры можно комбинировать, например 0ybw

Если запустить без параметра - будет выведен список дисков и запрос.
Номер вводится аналогично параметру командной строки, напрмер 0 или 0ybw
---
SMI NVME SSD flash id v0.223a by Ochkin Vadim
 0: KingDian S280 240GB
 1: OCZ-VERTEX4
 2: NVMe    NE-120
Please select drive number:
---

Отчет выводится на экран и сохраняется в файл smi_nvme_flash_id.txt, который перезаписывается.
В smi_nvme_flash_id_smart.txt сохраняется стандартный nvme smart.
В smi_nvme_flash_id_ec.txt сохраняется поблочный список счетчиков стирания (erase count).
В smi_nvme_flash_id_ec.txt сохраняется поблочный список дефектов.

Пример отчета:
---
v0.24a
OS: 10.0 build 15063 
Drive     : 3(NVME)
Scsi      : 1
Driver    : W10
Model     : LITEON CL1-8D256-HP                     
Fw        : L182    
HMB       : 32768 - 65536 KB (Enabled, 64 M)
Size      : 244198 MB [256.1 GB]
LBA Size  : 512
AdminCmd  : 0x00 0x01 0x02 0x04 0x05 0x06 0x08 0x09 0x0A 0x0C 0x10 0x11 0x14 0x80 0x81 0x82 0x84 0xC0 0xC1 0xC2 0xFC 0xFD 0xFE
I/O Cmd   : 0x00 0x01 0x02 0x04 0x05 0x08 0x09
Controller:  [SM2263XT] bufferless
Bank00: 0x98,0x3c,0x98,0xb3,0x76,0xe3,0x8,0x1e - Toshiba 96L BiCS4 TLC 16k 256Gb/CE 256Gb/die 2Plane/die
Bank01: 0x98,0x3c,0x98,0xb3,0x76,0xe3,0x8,0x1e - Toshiba 96L BiCS4 TLC 16k 256Gb/CE 256Gb/die 2Plane/die
Bank02: 0x98,0x3c,0x98,0xb3,0x76,0xe3,0x8,0x1e - Toshiba 96L BiCS4 TLC 16k 256Gb/CE 256Gb/die 2Plane/die
Bank03: 0x98,0x3c,0x98,0xb3,0x76,0xe3,0x8,0x1e - Toshiba 96L BiCS4 TLC 16k 256Gb/CE 256Gb/die 2Plane/die
Bank04: 0x98,0x3c,0x98,0xb3,0x76,0xe3,0x8,0x1e - Toshiba 96L BiCS4 TLC 16k 256Gb/CE 256Gb/die 2Plane/die
Bank05: 0x98,0x3c,0x98,0xb3,0x76,0xe3,0x8,0x1e - Toshiba 96L BiCS4 TLC 16k 256Gb/CE 256Gb/die 2Plane/die
Bank06: 0x98,0x3c,0x98,0xb3,0x76,0xe3,0x8,0x1e - Toshiba 96L BiCS4 TLC 16k 256Gb/CE 256Gb/die 2Plane/die
Bank07: 0x98,0x3c,0x98,0xb3,0x76,0xe3,0x8,0x1e - Toshiba 96L BiCS4 TLC 16k 256Gb/CE 256Gb/die 2Plane/die
Channel: 4
CE     : 2
Plane  : 2
Die/Ce : 1
Ch map : 0x0F
CE map : 0x03
Bit Per Cell  : (TLC)
Inter.        : 2
Pages/Block   : 1152(384)
First Fblock  :    1
Total Fblock  :  990
Total Hblock  : 5094
Fblock Per Ce :  990
Fblock Per Die:  990
Original Spare Block Count :    58
Vendor Marked Bad Block    :     0
Bad Block From Pretest     :     9

SM2263XT Telemetry data:
Re-allocated Sector Count (TLC/MLC)                      :              231
Total LBAs Written                                       :    4035431369051 [1924244GB]
Total LBAs Read                                          :      88502070294 [42201GB]
TLC Erase cycle average                                  :            20734
TLC Erase cycle Max                                      :            20904
TLC Erase cycle Min                                      :            20650
SLC Valid 4K count                                       :               32
TLC Valid 4K count                                       :        100991485
---
v0.24a
OS: 10.0 build 15063 
Drive     : 4(USB)
Bridge    : ASM
Model     : INTEL SSDPEKNW512G8H                    
Fw        : HPS0    
Size      : 488386 MB [512.1 GB]
LBA Size  : 512
AdminCmd  : 0x00 0x01 0x02 0x04 0x05 0x06 0x08 0x09 0x0A 0x0C 0x10 0x11 0x14 0x80 0x81 0x82 0x84 0xC0 0xC1 0xC2 0xD1 0xD2 0xE0 0xF3 0xF4
I/O Cmd   : 0x00 0x01 0x02 0x04 0x05 0x08 0x09
Controller: SM2263EN [SM2263AA] 
FW revision: SVN2406
ROM version: 2263ROM:SVN00350
Bank00: 0x89,0xd4,0xc,0x32,0xaa,0x0,0x0,0x0 - Intel 64L(N18A) QLC 1024Gb/CE 1024Gb/die
Bank01: 0x89,0xd4,0xc,0x32,0xaa,0x0,0x0,0x0 - Intel 64L(N18A) QLC 1024Gb/CE 1024Gb/die
Bank02: 0x89,0xd4,0xc,0x32,0xaa,0x0,0x0,0x0 - Intel 64L(N18A) QLC 1024Gb/CE 1024Gb/die
Bank03: 0x89,0xd4,0xc,0x32,0xaa,0x0,0x0,0x0 - Intel 64L(N18A) QLC 1024Gb/CE 1024Gb/die
--- Experimental ---
FlashID : 0x89,0xd4,0xc,0x32,0xaa,0x0,0x0,0x0 - Intel 64L(N18A) QLC 1024Gb/CE 1024Gb/die
Channel               : 4
Ch map                : 0x0F
CE map                : 0x01
Pages/Block           : 3072
First Fblock          : 2
Total Fblock          : 736
Bad Block From Pretest: 6
Start TLC/MLC Fblock  : 45
DRAM Info             : [0x0F 0x43]
DRAM Size,MB          : 256 (possible incorrect)
DRAM Bus,bit          : 16
DRAM Type             : DDR3
DRAM Vendor           : Hynix
UEFI OROM             : Disable

SM2262 Telemetry data:
VERSION                                                  :               19
Re-allocated Sector Count (TLC/MLC)                      :                0
Re-allocated Sector Count (SLC)                          :                0
Power-on Hours Count                                     :              772
Uncorrectable Error Count (XOR Fail) (TLC/MLC)           :                0
Uncorrectable Error Count (XOR Fail) (SLC)               :                0
ECCUnc (Soft LDPC fail) (TLC/MLC)                        :                0
Soft LDPC correction event count (TLC/MLC)               :                0
TLC read retry fail (TLC/MLC)                            :                0
SLC read retry fail (SLC)                                :                0
Temperature                                              :               27
RE-allocated Sector Events                               :           204298
Total LBAs Written                                       :       5754699435
Total LBAs Read                                          :      12706078804
PS3 Count                                                :                0
PS4 Count                                                :                1
L1.2 Count                                               :                0
TLC Available Spare Blocks (TLC/MLC)                     :               47
SLC Available Spare Blocks (SLC)                         :               27
WearRangeDelta (TLC/MLC)                                 :                8
WearRangeDelta (SLC)                                     :                0
High Temp                                                :               78
Low Temp                                                 :                0
Avg Temp                                                 :               39
Recent High                                              :                0
Recent Low                                               :                0
Auto Calibration FailCount                               :                0
SLC Nand Data Read (SLC)                                 :      63327370880
TLC Nand Data Read (TLC/MLC)                             :       2693779584
Valid block counts                                       :                0
SLC NAND Writes (SLC)                                    :      14446108160
TLC NAND writes (TLC/MLC)                                :       2241625856
TLC Wearing Leveling Count (TLC/MLC)                     :                9
SLC Wearing Leveling Count (SLC)                         :                0
TLC NAND writes due to Wearing Leveling (TLC/MLC)        :         14155776
SLC NAND writes due to Wearing Leveling (SLC)            :                0
Current TLC spare super block (TLC/MLC)                  :               50
Current SLC spare super block (SLC)                      :               25
SLC to TLC defrag count                                  :                0
TLC Defrag count                                         :                0
SLC Defrag count                                         :          9275392
Read back fail count                                     :                0
TLC Program Fail (TLC/MLC)                               :                0
SLC Program Fail (SLC)                                   :                0
TLC Erase Fail (TLC/MLC)                                 :                0
SLC Erase Fail (SLC)                                     :                0
TLC Erase cycle average                                  :               14
TLC Erase cycle Max                                      :              135
TLC Erase cycle Min                                      :                3
SLC Erase cycle average                                  :              141
SLC Erase cycle Max                                      :              183
SLC Erase cycle Min                                      :               99
PS0 to PS1                                               :                2
PS1 to PS0                                               :              336
PS1 to PS2                                               :                0
PS2 to PS1                                               :                0
PS2 to PS Shut Down Entry                                :                0
PS Shut Down to PS2 Exit                                 :                0
Idle Sleep Count                                         :          1906148
L1 event count                                           :          6127732
ECRC event count                                         :                0
LCRC event count                                         :                0
SLC to TLC program page cnt during Idle                  :          8304128
SLC to TLC program page cnt durning host activity        :        992037376
DRAM One Bit Error                                       :                0
SRAM One Bit Error                                       :                0
E2E detect count                                         :                0
PS3.5 count                                              :                2
Throttling light count(transit to PS1 from PS0 and PS2)  :                2
Throttling heavy count(transit to PS2 from PS1)          :                0
Throttling light duration (sec)                          :            12639
Throttling heavy duration (sec)                          :             1048
Retry count (retry trig)                                 :           291813
Soft Decode count (LDPC fail+pass)                       :                0
total manufacture bad count(unit : plane)                :               61
Worst manufacture bad count(unit : plane)                :                6
SLC Valid 4K count                                       :           244512
TLC Valid 4K count                                       :        124683518
SLC system block writes(sector)                          :        316502656
SLC writes due to read disturb(sector)                   :                0
TLC writes due to read disturb(sector)                   :                0
Max Open Block SSGS Count                                :                0
Max Closed Block SSGS Count                              :           696310
L2P table paging count                                   :         34742472
QLC open WL internal pre-read disabled                   :                0
SLC Max CW error count with RR pass                      :                0
TLC/QLC Max CW error count with RR pass                  :              162
Total Erase Pool Block Count                             :                0
DSLC blocks in link table                                :                0
Max DSLC Erase Cycle Count                               :               45
Avg DSLC Erase Cycle Count                               :               14
DSLC NAND write(sector)                                  :       3983109760
DSLC NAND read(sector)                                   :       6096597760
DSLC to DSLC Defrag count                                :          1609728
DSLC Program Fail                                        :                0
DSLC Erase Fail                                          :                0
DSLC Retired Blocks                                      :                0
DSLC Allocated Size                                      :                0
ReconditionQlcBlocks                                     :               15
MinDSLCEraseCount                                        :                2
MaxTotalEraseCount                                       :              144
MinTotalEraseCount                                       :                8
AvgTotalEraseCount                                       :               28
MaxOpenSsgsCount                                         :               33
MaxClosedSsgsCount                                       :              348
SlcDummyWrites                                           :         20923132
Qlc/Tlc DummyWrites                                      :       1309691655
DslcDummyWrites                                          :         17373368
ReconditionMaxEraseCount                                 :               45
DummyReads                                               :        729567984
CoreDumpCount                                            :               18
DataTrim                                                 :      14497971912
NAND Writes in TLC after POH threshold is triggered      :                0
Unknown                                                  :                0
Unknown                                                  :           166086
Unknown                                                  :            88671
Unknown                                                  :           112154
Max POH delta value (from all TLC super blocks)          :           338496
Min POH delta value (from all TLC super blocks)          :           330212
Ave POH delta value (from all TLC super blocks)          :           334334
Unknown                                                  :               18
Unknown                                                  :               76
Unknown                                                  :               11
Unknown                                                  :               43
Unknown                                                  :                0
TLC WAI with DSLC as TLC * 100                           :              499
TLC WAI with DSLC as SLC * 100                           :                0
WAI_SLC * 100                                            :                0
TLC Total Erase Count                                    :                0
SLC Total Erase Count                                    :                0
DSLC Total Erase Count                                   :                0
SectorPerBlock(TLC)                                      :                0
Map Block Pop count                                      :                0
GWPro Block Pop count                                    :                0
BGR Move Unit Count                                      :                0
---