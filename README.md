# 📒 simpleNVMe

### 輕量級 NVMe 2.1 Controller Registers 解析工具

這是一個 **Python 編寫的 NVMe 工具**，用於讀取並解析  
**NVMe 2.1 Controller Registers**，可直接從 **[BAR] (Base Address Register)**  
映射的實體位址讀取 Controller 的暫存器內容，並逐欄位輸出解碼資訊。  
主要適合於 **Linux /dev/mem 環境**下的 NVMe 測試與除錯。

---

## 📝 功能特色

- 支援讀取 **NVMe 2.1 Controller Registers**  
- 逐欄位顯示解析內容，包含 **RO / RW / WO 欄位屬性**  
- 無需 NVMe 驅動程式，僅需 **/dev/mem 存取權限**  
- 適合快速除錯、比對硬體實際行為與 NVMe 規範  

---

## 🗂️ 專案結構

- `simpleNVMe.py`  
  - 主程式，提供暫存器解析功能
- `/dev/mem`  
  - Linux 下的實體記憶體裝置，用於存取 [BAR] 實體位址

---

## ⚙️ 運作流程

1.  由使用者指定 **[BAR] 的實體位址**  
2.  程式透過 `/dev/mem` 與 `mmap` 映射 [BAR] 區域  
3.  依照 NVMe 2.1 規範讀取暫存器 (CAP, VS, CC, CSTS …)  
4.  將暫存器值拆解為各欄位，輸出對應的名稱、屬性、數值  

---

## 🚀 使用方式

### 1. 顯示說明

```bash
python3 simpleNVMe.py -h
```

### 2. Dump NVMe Controller Registers

```bash
python3 simpleNVMe.py -s 0x[BAR]
```

輸出範例：

```
[0x00] [CAP] : 0x00411FF000000001
         -- [0:15] [RO] MQES : 0x1FF
         -- [16:16] [RO] CQR : 0x1
         -- [20:23] [RO] TO : 0x4
         -- [24:27] [RO] DSTRD : 0x1
         -- [28:31] [RO] NSSRS : 0x0
         ...

[0x08] [VS] : 0x00010201
         -- [0:15] [RO] TER : 0x201
         -- [16:23] [RO] MNR : 0x02
         -- [24:31] [RO] MJR : 0x01

[0x14] [CC] : 0x00046000
         -- [0:0] [RW] EN : 0x0
         -- [4:7] [RW] CSS : 0x1
         -- [11:14] [RW] MPS : 0x6
         ...
```

---

## 🔍 取得 NVMe [BAR] 位址

在使用 `simpleNVMe.py` 前，需要先知道 NVMe Controller 的 **[BAR] (Base Address Register)**。  
這裡提供兩種方法：  

### 1. 使用 `lspci -x` 直接讀取 offset 0x10  

[BAR0] 會出現在 **PCI Config Space offset 0x10** 的位置。  

範例：  

```bash
hyam@hyam-virtual-machine:~/simplePCI$ lspci -s [B:D:F] -x
[B:D:F] Non-Volatile memory controller: VMware Device 07f0
00: ad 15 f0 07 07 04 10 00 00 02 08 01 00 00 00 00
10: 04 c0 4f fd 00 00 00 00 01 40 00 00 00 00 00 00
20: 00 00 00 00 00 00 00 00 00 00 00 00 ad 15 f0 07
30: 00 00 00 00 40 00 00 00 00 00 00 00 0a 01 00 00
```

其中 offset **0x10** 的 4 bytes (`04 c0 4f fd`) 組合後得到：  

```
0xFD4FC004
```

這就是 **[BAR0] 的位址**。  

---

### 2. 使用 [simplePCI 專案](https://github.com/straytale/simplePCI) 輔助工具  

也可以透過 [simplePCI 專案](https://github.com/straytale/simplePCI) 直接解析出 [BAR] 資訊：  

```bash
python3 simplePCI.py -s [B:D:F] -v | grep -i BAR0
```

輸出範例：  

```
0x10   BAR0   0xFD4FC004
```

同樣可以直接取出 **[BAR0] 位址** 供 `simpleNVMe.py` 使用。  

---
