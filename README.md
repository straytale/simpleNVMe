# 📒 simpleNVMe

### 輕量級 NVMe 2.1 Controller Registers 解析工具

這是一個 **Python 編寫的 NVMe 工具**，用於讀取並解析  
**NVMe 2.1 Controller Registers**，可透過 **PCI BDF** 自動查詢對應的 **BAR 實體位址**，
再從 **/dev/mem** 直接映射 Controller 暫存器區域，逐欄位輸出解碼資訊。  
主要適合於 **Linux /dev/mem 環境**下的 NVMe 測試與除錯。

---

## 📝 功能特色

- 輸入 **BDF (Bus:Device.Function)**，自動解析 BAR 實體位址
- 支援讀取 **NVMe 2.1 Controller Registers**
- 逐欄位顯示解析內容，包含 **RO / RW / WO 欄位屬性**
- 無需 NVMe 驅動程式，僅需 **/dev/mem 存取權限**
- 適合快速除錯、比對硬體實際行為與 NVMe 規範  

---

## 🗂️ 專案結構

- `simpleNVMe.py`  
  - 主程式，提供暫存器解析功能
- `/dev/mem`  
  - Linux 下的實體記憶體裝置，用於存取 BAR 實體位址

---

## ⚙️ 運作流程

1. 使用者輸入 **PCI BDF (例如 04:00.0 或 0000:04:00.0)**  
2. 程式透過 `lspci -v -s [BDF]` 查詢對應 BAR 位址  
3. 程式以 `/dev/mem` 與 `mmap` 映射該 BAR 區域  
4. 依照 NVMe 2.1 規範讀取暫存器 (CAP, VS, CC, CSTS …)  
5. 將暫存器值拆解為各欄位，輸出對應的名稱、屬性、數值  

---

## 🚀 使用方式

### 1. 顯示說明

```bash
python3 simpleNVMe.py -h
```

### 2. Dump NVMe Controller Registers

```bash
python3 simpleNVMe.py -s [BDF]
```

範例：

```bash
python3 simpleNVMe.py -s 04:00.0
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

## 📌 待辦清單

1. 實現 **Controller Reset**：切換 `CC.EN` 並檢查 `CSTS.RDY` 狀態  
2. 實現 **NSSR (NVM Subsystem Reset)**：寫入 `NSSR` 並確認 `NSSRO`  
3. 實現 **Shutdown 流程**：設定 `CC.SHN`，監控 `CSTS.SHST`  
