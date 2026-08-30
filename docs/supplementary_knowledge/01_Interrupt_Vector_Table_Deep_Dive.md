# INTERRUPT VECTOR TABLE - TU JUNIOR+ DEN SENIOR EMBEDDED ENGINEER

> **Tac gia:** Senior Embedded Systems Engineer / Firmware Architect  
> **Cap do:** Junior+ -> Senior Embedded  
> **Huong tiep can:** Engineering thuc te: WHY -> WHAT -> HOW -> HARDWARE -> CODE -> MEMORY -> DEBUG -> PRODUCTION  
> **Nền tang:** ARM Cortex-M + Bare-metal + FreeRTOS

---

## MUC LUC

1. [Chuong 1: Mental Model - Cai nhin toan canh](#ch1)
2. [Chuong 2: Vector Table o cap Memory](#ch2)
3. [Chuong 3: ARM Cortex-M Deep Dive](#ch3)
4. [Chuong 4: Code thuc te - Startup + Linker + ISR](#ch4)
5. [Chuong 5: Interrupt Flow o cap CPU](#ch5)
6. [Chuong 6: Interrupt Priority va Preemption](#ch6)
7. [Chuong 7: Interrupt + RTOS (FreeRTOS)](#ch7)
8. [Chuong 8: Bootloader + Multi-Image](#ch8)
9. [Chuong 9: Debugging Vector Table - 5 Case Thuc Te](#ch9)
10. [Chuong 10: Debug voi GDB](#ch10)
11. [Chuong 11: 15+ Misconceptions cua Junior](#ch11)
12. [Chuong 12: So sanh Kien truc CPU](#ch12)
13. [Chuong 13: Phan tich Startup Code thuc te](#ch13)
14. [Chuong 14: Thiet ke ISR chuan Senior](#ch14)
15. [Chuong 15: Performance va Real-Time](#ch15)
16. [Chuong 16: 10 Bai Tap Tang Dan Do Kho](#ch16)
17. [Chuong 17: Senior Mindset](#ch17)
18. [Chuong 18: Master Debug Checklist](#ch18)

---

<a name="ch1"></a>
## CHUONG 1: MENTAL MODEL - CAI NHIN TOAN CANH

### 1.1 Interrupt la gi o cap do Hardware?

**WHY - Tai sao Interrupt ton tai?**

CPU la may tinh tuan tu - no chi lam duoc mot viec tai mot thoi diem. Nhung the gioi ben ngoai (peripherals, sensors, mang) xay ra bat dong bo (asynchronously). Van de:

- UART nhan byte moi 87 microseconds (115200 baud)
- CPU dang tinh toan phuc tap mat 1ms
- Neu CPU lien tuc kiem tra UART (polling), 99% thoi gian CPU lua dao ("busy-waiting")
- Toi te hon: cac su kien co the bi miss neu CPU dang lam viec khac

**Giai phap: Interrupt Mechanism**

```
+------------------+        +------------------+        +------------------+
|   PERIPHERAL     |        |    INTERRUPT      |        |      CPU         |
|                  |        |   CONTROLLER      |        |                  |
|  UART RX buffer  |------->|     (NVIC)        |------->|  Dang xu ly      |
|  Timer overflow  |  IRQ   |                   |  nIRQ  |  main code       |
|  ADC done        |        |  - Priority Mgmt  |        |                  |
|  GPIO edge       |        |  - Enable/Disable |        |  Nhan tin hieu   |
+------------------+        +------------------+        |  DUNG LAI        |
                                                         |  Jump vao ISR    |
                                                         +------------------+
```

**Hardware thuc su lam gi khi co IRQ?**

1. Peripheral hoan thanh mot tac vu (vi du: UART nhan xong 1 byte)
2. Peripheral SET bit IRQ len duong day tin hieu vat ly (mot wire)
3. Interrupt Controller (NVIC tren Cortex-M) nhan tin hieu nay
4. NVIC kiem tra: interrupt co bi mask khong? Priority co du cao khong?
5. NVIC gui tin hieu den CPU core
6. CPU hoan thanh lenh dang thuc hien (most cases), sau do dung lai
7. CPU tu dong luu trang thai hien tai (registers) xuong stack
8. CPU doc Vector Table de biet ISR nam o dau
9. CPU nhay den ISR
10. ISR thuc hien, xu ly su kien
11. ISR ket thuc (BX LR / EXC_RETURN)
12. CPU khoi phuc trang thai cu
13. Main code tiep tuc tu dung cho

---

### 1.2 Phan biet Interrupt, Exception, Trap, Fault, Reset

Day la diem Junior thuong nham lan nhat. Cac khai niem nay KHONG giong nhau.

```
+------------------+---------------------------------------------------+------------------+
| Thuat ngu        | Mo ta                                             | Vi du            |
+------------------+---------------------------------------------------+------------------+
| Interrupt        | Asynchronous: den tu hardware ben ngoai CPU       | UART RX, Timer   |
|                  | CPU dang lam viec, bi "ngat" tu ben ngoai         | ADC, GPIO        |
+------------------+---------------------------------------------------+------------------+
| Exception        | Tong hop: bat ky su kien nao khien CPU doi mode   | Bao gom ca       |
|                  | Cortex-M goi tat ca la "exception"                | interrupt        |
+------------------+---------------------------------------------------+------------------+
| Trap             | Synchronous: phat sinh boi lenh CPU thuc hien    | SVC instruction  |
|                  | CPU tu tao ra - co the du doan truoc              | BKPT             |
+------------------+---------------------------------------------------+------------------+
| Fault            | CPU gap loi trong qua trinh thuc hien lenh       | Chia cho 0       |
|                  | Hardware phat hien vi pham                        | Bad memory       |
+------------------+---------------------------------------------------+------------------+
| Reset            | CPU bat dau lai tu dau                            | Power-on reset   |
|                  | Trang thai CPU duoc khoi tao lai hoan toan        | Watchdog reset   |
+------------------+---------------------------------------------------+------------------+
| Software Interrupt| Interrupt gia lap bang phan mem                  | NVIC->STIR       |
|                  | CPU tu kich hoat interrupt                        | SVC #0           |
+------------------+---------------------------------------------------+------------------+
```

**Cortex-M goi tat ca la "Exception":**

```
Exception Number |  Ten                    | Loai
-----------------|-------------------------|---------
1                | Reset                   | Reset
2                | NMI                     | Interrupt (Non-maskable)
3                | HardFault               | Fault
4                | MemManage               | Fault
5                | BusFault                | Fault
6                | UsageFault              | Fault
7-10             | Reserved                | -
11               | SVCall (SVC)            | Trap/Software
12               | DebugMonitor            | Debug
13               | Reserved                | -
14               | PendSV                  | Software Interrupt
15               | SysTick                 | Interrupt (Timer)
16+              | IRQ0, IRQ1, ... IRQn    | Hardware Interrupt
```

---

### 1.3 Flow Toan Bo: Tu Peripheral den ISR den Return

```
+==========================================+
|  FLOW CHINH XAC KHI INTERRUPT XAY RA   |
+==========================================+

1. PERIPHERAL TRIGGER
   UART nhan xong 1 byte
   Timer dem den 0 (underflow)
   ADC conversion complete
        |
        v
2. IRQ SIGNAL (Hardware Wire)
   Peripheral SET bit IRQ
   Day la tin hieu dien ap thay doi
        |
        v
3. INTERRUPT CONTROLLER (NVIC)
   Kiem tra: interrupt co enable khong?
   Kiem tra: priority co du cao hon current?
   Neu co -> gui nIRQ (active low) den CPU
        |
        v
4. CPU CHAP NHAN INTERRUPT
   CPU hoan thanh lenh HIEN TAI (khong dung giua chung)
   CPU kiem tra dieu kien: PRIMASK/BASEPRI/FAULTMASK
        |
        v
5. CONTEXT SAVE (Hardware Automatic - Cortex-M)
   CPU tu dong PUSH xuong stack:
   xPSR (Program Status Register)
   PC   (Program Counter - dia chi se quay lai)
   LR   (Link Register)
   R12
   R3, R2, R1, R0
   Tong: 8 registers = 32 bytes tren stack
        |
        v
6. EXCEPTION NUMBER XAC DINH
   NVIC cung cap exception number cho CPU
   Vi du: IRQ0 = exception number 16
        |
        v
7. VECTOR TABLE LOOKUP
   CPU lay Vector Table Base Address tu VTOR
   CPU tinh: dia chi = VTOR + (exception_number * 4)
   CPU DOC 4 bytes tai dia chi do -> lay ISR address
        |
        v
8. CPU NHAY DEN ISR
   PC = ISR address
   LR = EXC_RETURN (gia tri dac biet, khong phai dia chi binh thuong)
        |
        v
9. ISR THUC HIEN
   Code cua lap trinh vien chay
   Xu ly su kien, clear flag
   KHONG nen lam viec nang
        |
        v
10. EXCEPTION RETURN
    ISR thuc hien BX LR (hoac tuong duong)
    CPU phat hien LR = EXC_RETURN (bit[31:28] = 0xF)
    CPU bat dau qua trinh khoi phuc
        |
        v
11. CONTEXT RESTORE (Hardware Automatic)
    CPU POP tu stack:
    R0, R1, R2, R3, R12, LR, PC, xPSR
    SP (Stack Pointer) tu dong tang len
        |
        v
12. MAIN CODE TIEP TUC
    PC = dia chi lenh tiep theo sau khi bi ngat
    Moi thu nhu chua co gi xay ra
```

---

### 1.4 Kiem tra Tu Duy - Chuong 1

**Cau 1:** Timer interrupt xay ra dung luc CPU dang thuc hien lenh `MUL R0, R1, R2` chua hoan thanh. CPU se lam gi? Dung hay sai khi noi "CPU se dung ngay lenh do"?

**Cau 2:** Co phai moi interrupt xay ra deu se vao ISR ngay lap tuc khong? Neu khong, hay liet ke it nhat 3 ly do khien interrupt bi tri hoan.

**Cau 3:** Junior noi "toi da enable interrupt trong NVIC roi nen interrupt se hoat dong". Hay chi ra nhung gi co the van sai.

---

<a name="ch2"></a>
## CHUONG 2: VECTOR TABLE O CAP MEMORY

### 2.1 Vector Table la gi chinh xac?

**KHONG phai:** Mot danh sach ten function.  
**KHONG phai:** Phan cua NVIC hardware.  
**DUNG:** Mot mang (array) cac **dia chi 32-bit** nam trong **bo nho** (Flash), moi phan tu la dia chi cua mot ISR.

```c
// Day la vector table - don gian chi la mot mang dia chi
const uint32_t vector_table[] = {
    (uint32_t)&__StackTop,       // [0] Initial Stack Pointer
    (uint32_t)Reset_Handler,     // [1] Reset
    (uint32_t)NMI_Handler,       // [2] NMI
    (uint32_t)HardFault_Handler, // [3] HardFault
    // ...
    (uint32_t)TIM2_IRQHandler,   // [32+16] = [48] IRQ32
};
// CPU DOC MANG NAY TRUC TIEP TU FLASH - KHONG QUA NVIC
```

### 2.2 Vector Table Nam o Dau trong Memory?

```
MEMORY MAP - STM32F4 (Vi du dien hinh)
+-------------------------+  <- 0xFFFFFFFF
|                         |
|   Peripheral Registers  |
|   (APB1, APB2, AHB1...) |
|                         |
+-------------------------+  <- 0x40000000
|                         |
|   SRAM (128KB)          |
|   .data, .bss, stack    |
|   heap                  |
|                         |
+-------------------------+  <- 0x20000000
|                         |
|   FLASH (512KB)         |
|                         |
|  0x08000000:            |
|  +-------------------+  |
|  | Vector Table      |  |  <- CPU DOC DAU TIEN KHI BOOT
|  | [0] Stack Pointer |  |  <- 4 bytes: gia tri dau cua MSP
|  | [1] Reset_Handler |  |  <- 4 bytes: dia chi ham Reset_Handler
|  | [2] NMI_Handler   |  |  <- 4 bytes: dia chi ham NMI_Handler
|  | [3] HardFault     |  |  <- 4 bytes
|  | ...               |  |
|  | [n] IRQn_Handler  |  |
|  +-------------------+  |
|  .text (code)           |
|  .rodata (const data)   |
|  .data (init values)    |
|                         |
+-------------------------+  <- 0x08000000
```

**Tai sao Vector Table phai o DAU Flash?**

Khi CPU Cortex-M boot, no KHONG biet chuong trinh cua ban o dau. No chi biet mot dieu:  
> "Sau khi Reset, toi se tim Stack Pointer tai dia chi 0x00000000, va tim Reset_Handler tai 0x00000004"

Dieu nay la CUNG VA KHONG THE THAY DOI o hardware level. VTOR (Vector Table Offset Register) ban dau = 0x00000000.

Tren STM32, 0x00000000 duoc ALIAS (remap) den 0x08000000 (dau Flash) thong qua BOOT pins hoac address remapping.

### 2.3 Moi Entry Trong Vector Table Chua Gi?

```
Vector Table Entry (4 bytes = 32-bit):

Bit 31                                    Bit 1  Bit 0
+------------------------------------------+------+---+
|      ISR Function Address [31:1]         |  0   | T |
+------------------------------------------+------+---+
                                                    |
                                            T=1: Thumb mode
                                            (Cortex-M chi chay Thumb)
```

**Quan trong:** Entry [0] la NGOAI LE - no la gia tri nap vao MSP (Main Stack Pointer), KHONG phai dia chi ISR.

```
Entry [0]: Initial Stack Pointer Value
           = 0x20020000 (cuoi RAM 128KB: 0x20000000 + 0x20000)
           CPU se nap gia tri nay vao SP truoc khi chay bat cu lenh nao

Entry [1..n]: ISR Address | 0x1 (Thumb bit)
              Vi du: Reset_Handler tai 0x08000101
              = 0x08000100 | 0x1 = 0x08000101
              CPU jump den 0x08000100 (bit 0 chi la Thumb flag)
```

### 2.4 Relocate Vector Table - VTOR

Cortex-M3/M4/M7 co thanh ghi **VTOR** (Vector Table Offset Register) tai dia chi `0xE000ED08`.

```c
// Cach relocate vector table (vi du trong bootloader -> app)
#define VTOR_ADDRESS  0xE000ED08
#define APP_BASE      0x08008000  // App bat dau o day

// Ghi dia chi moi vao VTOR
*((volatile uint32_t*)VTOR_ADDRESS) = APP_BASE;
// Tu bay gio, CPU se tim vector table tai 0x08008000
```

**Rang buoc khi relocate:**
- Address phai align theo so luong entries * 4, lam tron len power of 2
- Vi du: 256 interrupts = 256 * 4 = 1024 bytes -> align 1024 bytes
- STM32 thong thuong: align 0x200 (512 bytes)

### 2.5 Kiem tra Tu Duy - Chuong 2

**Cau 1:** CPU doc entry [0] cua vector table de lam gi? Co phai de biet dia chi ISR dau tien khong?

**Cau 2:** Neu ban co 256 external interrupts, vector table cua ban co kich thuoc bao nhieu bytes? Align requirement la gi?

**Cau 3:** Mot bootloader chay dung. Sau do no jump vao application. Application khong nhan duoc bat ky interrupt nao du IRQ da enable. Nguyen nhan kha nang nhat la gi?

---

<a name="ch3"></a>
## CHUONG 3: ARM CORTEX-M DEEP DIVE

### 3.1 Toan Bo Exception List Cortex-M4

```
Exception  | IRQ# | Ten              | Priority     | Mo ta
-----------|------|------------------|--------------|--------------------------------
1          | -    | Reset            | -3 (cao nhat)| Power-on, watchdog, pin reset
2          | -    | NMI              | -2           | Non-Maskable Interrupt
3          | -    | HardFault        | -1           | Loi nghiem trong
4          | -    | MemManage        | configurable | Vi pham MPU
5          | -    | BusFault         | configurable | Loi bus (invalid address)
6          | -    | UsageFault       | configurable | Lenh bat hop le, chia cho 0
7-10       | -    | Reserved         | -            | -
11         | -    | SVCall           | configurable | SVC instruction (RTOS API)
12         | -    | DebugMonitor     | configurable | Debug breakpoint
13         | -    | Reserved         | -            | -
14         | -    | PendSV           | configurable | Pendable SVC (context switch)
15         | -    | SysTick          | configurable | System tick timer (RTOS tick)
16         | 0    | IRQ0             | configurable | External interrupt 0
17         | 1    | IRQ1             | configurable | External interrupt 1
...        | ...  | ...              | ...          | ...
255        | 239  | IRQ239           | configurable | External interrupt 239
```

### 3.2 Mot So Exception Quan Trong Can Hieu Sau

**RESET (Exception #1)**
```
- Priority: -3 (cao nhat tuyet doi, khong the thay doi)
- Xay ra khi: Power-on, NRST pin, WWDG/IWDG reset, software reset
- CPU lam gi: Nap MSP tu [0], nap PC tu [1], bat dau thuc hien
- KHONG the bi preempt boi bat cu thu gi
```

**NMI - Non-Maskable Interrupt (Exception #2)**
```
- Priority: -2
- KHONG the bi mask boi PRIMASK hay BASEPRI
- Chi dung cho cac tinh huong khoc liet: Clock failure, power fail
- Neu NMI handler bi loi -> vao HardFault
```

**HardFault (Exception #3)**
```
- Priority: -1
- "Noi nuong chiu" cua moi loi khac
- Xay ra khi: Fault khac ko the xu ly, fault trong fault handler
- Debug HardFault = ky nang quan trong cua Senior
- Registers can doc: SCB->HFSR, SCB->CFSR, SCB->BFAR, SCB->MMFAR
```

**SVCall - SVC (Exception #11)**
```
- Kich hoat boi lenh SVC #imm8
- RTOS dung de: Task goi OS API tu unprivileged mode
- Vi du FreeRTOS: xTaskCreate() -> SVC -> scheduler chay trong privileged mode
```

**PendSV (Exception #14)**
```
- "Context Switch Engine" cua RTOS
- Luon co priority thap nhat
- FreeRTOS SysTick ISR set PendSV pending -> PendSV chay sau tat ca ISR -> context switch
- Tai sao can PendSV? Vi khong the context switch trong giua ISR khac
```

**SysTick (Exception #15)**
```
- Timer 24-bit tich hop trong CPU (khong phai peripheral rieng)
- FreeRTOS dung lam RTOS tick (mac dinh 1ms = 1000Hz)
- Nap vao: configTICK_RATE_HZ trong FreeRTOSConfig.h
```

### 3.3 NVIC vs Vector Table - Junior Thuong Nham

**Day la diem quan trong nhat chuong nay.**

```
+=====================================================+
|  NVIC (Nested Vectored Interrupt Controller)       |
|  - La HARDWARE BLOCK nam trong CPU                 |
|  - Chuc nang:                                      |
|    * Nhan IRQ tu peripherals                       |
|    * Quan ly priority                              |
|    * Enable/Disable tung IRQ                       |
|    * Mask interrupt (PRIMASK, BASEPRI)             |
|    * Theo doi trang thai: Pending, Active          |
|    * Tinh toan IRQ nao duoc phep phuc vu           |
|    * Gui tin hieu den CPU core khi can             |
|  - Registers: NVIC->ISER, NVIC->ICER,             |
|               NVIC->ISPR, NVIC->ICPR,             |
|               NVIC->IPR                            |
+=====================================================+
         |
         | NVIC chi gui "exception number" cho CPU
         | NVIC KHONG biet ISR o dau
         v
+=====================================================+
|  VECTOR TABLE (trong Flash/RAM)                    |
|  - La SOFTWARE DATA STRUCTURE (mang dia chi)       |
|  - Chuc nang:                                      |
|    * Chua dia chi ISR cho moi exception            |
|    * CPU doc truc tiep tu bo nho                   |
|    * Duoc tao boi linker tu source code            |
|  - CPU dung VTOR + exception_number*4 de tim       |
+=====================================================+
         |
         | CPU doc dia chi ISR tu vector table
         v
+=====================================================+
|  CPU CORE                                          |
|  - Nhan exception number tu NVIC                   |
|  - Tinh dia chi: VTOR + (exc_num * 4)              |
|  - Doc 32-bit tai dia chi do = ISR address         |
|  - Jump den ISR address                            |
+=====================================================+
```

**Luu y quan trong:**
- NVIC: Hardware, quan ly PRIORITY va ENABLE
- Vector Table: Software (data trong Flash), chua ADDRESS
- Chung la 2 thu hoan toan khac nhau
- Enable NVIC ma khong co vector table dung = HardFault
- Vector table dung ma khong enable NVIC = interrupt khong chay

### 3.4 Kiem tra Tu Duy - Chuong 3

**Cau 1:** Neu NVIC->ISER da set (IRQ enable) nhung Vector Table entry cho IRQ do la 0x00000000, chuyen gi xay ra khi interrupt kich hoat?

**Cau 2:** PendSV luon co priority thap nhat. Tai sao? Neu dat PendSV priority cao hon SysTick thi hau qua la gi?

**Cau 3:** SVC va PendSV deu la "software interrupt". Khac nhau gi? Tai sao FreeRTOS can ca hai?

---

<a name="ch4"></a>
## CHUONG 4: CODE THUC TE - STARTUP + LINKER + ISR

### 4.1 Khai Bao Vector Table Trong C

```c
/* startup_stm32f4xx.c */

/* Kieu du lieu cho ISR */
typedef void (*ISR_Handler)(void);

/* Khai bao cac ISR (weak - co the override) */
void Reset_Handler(void);
void NMI_Handler(void)          __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void)    __attribute__((weak, alias("Default_Handler")));
void MemManage_Handler(void)    __attribute__((weak, alias("Default_Handler")));
void BusFault_Handler(void)     __attribute__((weak, alias("Default_Handler")));
void UsageFault_Handler(void)   __attribute__((weak, alias("Default_Handler")));
void SVC_Handler(void)          __attribute__((weak, alias("Default_Handler")));
void DebugMon_Handler(void)     __attribute__((weak, alias("Default_Handler")));
void PendSV_Handler(void)       __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void)      __attribute__((weak, alias("Default_Handler")));
void TIM2_IRQHandler(void)      __attribute__((weak, alias("Default_Handler")));
/* ... them cac IRQ khac */

/* Default handler - vong lap vo han neu ISR chua duoc implement */
void Default_Handler(void) {
    while (1);
    /* Senior: them log truoc khi loop de debug */
}

/* Linker symbol - dia chi cuoi RAM (stack bau dau tu day) */
extern uint32_t __StackTop;

/*
 * VECTOR TABLE
 * - __attribute__((section(".isr_vector"))): dat vao section rieng
 * - __attribute__((used)): bao compiler KHONG xoa du linker khong thay reference
 * - const: nam trong Flash (khong phai RAM)
 */
__attribute__((section(".isr_vector")))
__attribute__((used))
const ISR_Handler vector_table[] = {
    /* [0]  Stack Pointer initial value */
    (ISR_Handler)&__StackTop,

    /* [1]  Reset */
    Reset_Handler,

    /* [2]  NMI */
    NMI_Handler,

    /* [3]  HardFault */
    HardFault_Handler,

    /* [4]  MemManage */
    MemManage_Handler,

    /* [5]  BusFault */
    BusFault_Handler,

    /* [6]  UsageFault */
    UsageFault_Handler,

    /* [7-10] Reserved */
    0, 0, 0, 0,

    /* [11] SVCall */
    SVC_Handler,

    /* [12] DebugMon */
    DebugMon_Handler,

    /* [13] Reserved */
    0,

    /* [14] PendSV */
    PendSV_Handler,

    /* [15] SysTick */
    SysTick_Handler,

    /* [16] IRQ0 = WWDG */
    WWDG_IRQHandler,

    /* [17] IRQ1 = PVD */
    PVD_IRQHandler,

    /* [18] IRQ2 = TAMP_STAMP */
    TAMP_STAMP_IRQHandler,

    /* ... tiep tuc cho toan bo IRQ cua MCU */

    /* [46] IRQ30 = TIM2 */
    TIM2_IRQHandler,
};
```

### 4.2 Weak Symbol - Ky Thuat Quan Trong

```c
/*
 * WEAK SYMBOL MECHANISM
 *
 * void TIM2_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
 *
 * Nghia la:
 * 1. TIM2_IRQHandler la "weak" definition
 * 2. No la alias cua Default_Handler
 * 3. Neu user code KHONG dinh nghia TIM2_IRQHandler:
 *    -> Linker dung alias nay -> TIM2 interrupt vao Default_Handler (while(1))
 * 4. Neu user code CO dinh nghia TIM2_IRQHandler:
 *    -> Linker dung dinh nghia cua user -> override weak symbol
 *
 * Ket qua: Compile thanh cong du user chua implement moi ISR
 * Neu interrupt xay ra ma khong implement ISR -> vao Default_Handler
 */

/* User code trong main.c hoac tim2.c */
void TIM2_IRQHandler(void) {
    /* Ghi de weak symbol */
    if (TIM2->SR & TIM_SR_UIF) {
        TIM2->SR &= ~TIM_SR_UIF;  /* Clear interrupt flag */
        /* Xu ly logic */
        timer2_tick_count++;
    }
}
```

### 4.3 Linker Script Chi Tiet

```ld
/* stm32f407vg.ld */

/* MEMORY REGIONS: Dinh nghia vung bo nho vat ly */
MEMORY
{
    /* Flash: doc/thuc thi, bat dau 0x08000000, 1MB */
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 1024K

    /* SRAM: doc/ghi/thuc thi, bat dau 0x20000000, 128KB */
    SRAM  (rwx) : ORIGIN = 0x20000000, LENGTH = 128K

    /* CCM RAM: chi CPU co the truy cap, nhanh hon */
    CCMRAM (rw) : ORIGIN = 0x10000000, LENGTH = 64K
}

/* ENTRY POINT: Noi lenh dau tien duoc thuc hien */
ENTRY(Reset_Handler)

/* LINKER SYMBOLS: Gia tri duoc dung trong C code */
_stack_size = 0x400;  /* 1KB stack */

SECTIONS
{
    /* ==== SECTION 1: VECTOR TABLE ==== */
    .isr_vector :
    {
        . = ALIGN(4);
        KEEP(*(.isr_vector))  /* KEEP: khong xoa du code chua reference truc tiep */
        . = ALIGN(4);
    } > FLASH

    /* ==== SECTION 2: CODE ==== */
    .text :
    {
        . = ALIGN(4);
        *(.text)          /* Code chinh */
        *(.text*)         /* Code tu tat ca object files */
        *(.glue_7)        /* ARM/Thumb interworking */
        *(.glue_7t)
        *(.eh_frame)
        KEEP(*(.init))
        KEEP(*(.fini))
        . = ALIGN(4);
        _etext = .;       /* Symbol: ket thuc phan code */
    } > FLASH

    /* ==== SECTION 3: CONST DATA ==== */
    .rodata :
    {
        . = ALIGN(4);
        *(.rodata)
        *(.rodata*)
        . = ALIGN(4);
    } > FLASH

    /* ==== SECTION 4: DATA (initialized) ==== */
    /* Gia tri khoi tao nam trong Flash, duoc copy sang RAM khi boot */
    _sidata = LOADADDR(.data);  /* Dia chi trong Flash */

    .data :
    {
        . = ALIGN(4);
        _sdata = .;        /* Symbol: bat dau .data trong RAM */
        *(.data)
        *(.data*)
        . = ALIGN(4);
        _edata = .;        /* Symbol: ket thuc .data trong RAM */
    } > SRAM AT> FLASH     /* Chay trong SRAM, luu trong Flash */

    /* ==== SECTION 5: BSS (zero-initialized) ==== */
    .bss :
    {
        . = ALIGN(4);
        _sbss = .;
        __bss_start__ = _sbss;
        *(.bss)
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
        __bss_end__ = _ebss;
    } > SRAM

    /* ==== SECTION 6: STACK ==== */
    ._user_heap_stack :
    {
        . = ALIGN(8);
        PROVIDE(end = .);
        . = . + _stack_size;
        . = ALIGN(8);
    } > SRAM

    /* __StackTop: CPU dung lam gia tri khoi tao MSP */
    __StackTop = ORIGIN(SRAM) + LENGTH(SRAM);
}
```

### 4.4 Startup Code (Reset_Handler)

```c
/* startup_stm32f4xx.c - Reset_Handler */
void Reset_Handler(void) {

    /* 1. Copy .data tu Flash sang RAM */
    uint32_t *src = &_sidata;  /* Nguon: Flash */
    uint32_t *dst = &_sdata;   /* Dich: RAM */
    while (dst < &_edata) {
        *dst++ = *src++;
    }

    /* 2. Zero-fill .bss */
    dst = &_sbss;
    while (dst < &_ebss) {
        *dst++ = 0;
    }

    /* 3. Goi system init (clock setup, etc.) */
    SystemInit();

    /* 4. Goi main() */
    main();

    /* 5. Neu main() thoat (khong nen) */
    while (1);
}
```

### 4.5 Full Flow: Tu Source Code Den ISR

```
SOURCE CODE (.c, .h)
        |
        | GCC compile
        v
OBJECT FILES (.o)
  startup.o     <- chua vector_table[]
  main.o        <- chua main(), TIM2_IRQHandler()
  tim.o         <- chua TIM2 config code
        |
        | LD linker (dung linker script .ld)
        v
ELF FILE (axf/elf)
  - Chua tat ca sections
  - Symbol table
  - Debug info
  - .isr_vector tai 0x08000000
        |
        | objcopy -O binary
        v
BINARY FILE (.bin)
  Bytes thuan tuy, khong co header
  Byte dau = LSB cua __StackTop
  Byte 4-7 = dia chi Reset_Handler
        |
        | Flash programmer
        v
FLASH MEMORY
  0x08000000: [Stack Top value]
  0x08000004: [Reset_Handler addr]
  0x08000008: [NMI_Handler addr]
  ...
        |
        | Power-on Reset
        v
CPU BOOT
  1. Doc 0x08000000 -> nap vao MSP
  2. Doc 0x08000004 -> nap vao PC
  3. Jump den Reset_Handler
  4. Reset_Handler copy .data, zero .bss
  5. Goi main()
        |
        | TIM2 interrupt xay ra
        v
CPU -> NVIC -> VECTOR TABLE LOOKUP
  Tinh: 0x08000000 + (46 * 4) = 0x080000B8
  Doc 4 bytes: = dia chi TIM2_IRQHandler
        |
        v
ISR THUC HIEN
```

### 4.6 Cach Kich Hoat Interrupt Day Du

```c
void setup_TIM2_interrupt(void) {

    /* BUOC 1: Enable clock cho peripheral */
    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;

    /* BUOC 2: Cau hinh peripheral */
    TIM2->PSC = 8400 - 1;    /* Prescaler: 84MHz / 8400 = 10kHz */
    TIM2->ARR = 10000 - 1;   /* Auto-reload: 10kHz / 10000 = 1Hz */
    TIM2->CNT = 0;

    /* BUOC 3: Enable interrupt tai peripheral */
    TIM2->DIER |= TIM_DIER_UIE;   /* Update Interrupt Enable */

    /* BUOC 4: Enable IRQ trong NVIC */
    NVIC_EnableIRQ(TIM2_IRQn);    /* = IRQ28 tren STM32F4 */

    /* BUOC 5: Set priority (tuy chon, truoc khi enable) */
    NVIC_SetPriority(TIM2_IRQn, 5);  /* Priority 5, thap hon 0 */

    /* BUOC 6: Enable peripheral */
    TIM2->CR1 |= TIM_CR1_CEN;

    /* BUOC 7: Global interrupt enable */
    /* Thong thuong da enable tu dau, neu khong: */
    __enable_irq();   /* Xoa bit PRIMASK */
}
```

### 4.7 Kiem tra Tu Duy - Chuong 4

**Cau 1:** Tai sao can `KEEP(*(.isr_vector))` trong linker script? Neu bo KEEP thi chuyen gi xay ra khi build voi optimization `-O2`?

**Cau 2:** `__attribute__((weak))` hoat dong o buoc nao: compiler hay linker? Neu ca startup.c va user code deu dinh nghia TIM2_IRQHandler (khong co weak), linker se bao loi gi?

**Cau 3:** Reset_Handler copy .data tu Flash sang RAM. Neu buoc nay bi bo qua (gia su Reset_Handler bi viet sai), bien global co gia tri khoi tao nhu `int x = 5;` se co gia tri gi?

---

<a name="ch5"></a>
## CHUONG 5: INTERRUPT FLOW O CAP CPU

### 5.1 Context Save - CPU Lam Gi Truoc Khi Vao ISR?

Day la ky nang phan biet Junior va Senior: hieu chinh xac CPU luu gi, o dau, theo thu tu nao.

**Cortex-M Auto-stacking (Hardware Automatic):**

```
TRUOC INTERRUPT:           SAU CONTEXT SAVE:
Stack (RAM):               Stack (RAM):
                           +----------------+  <- SP truoc (cao hon)
                           |    xPSR        |  [SP+28]
                           |    PC          |  [SP+24] <- return address
                           |    LR          |  [SP+20]
                           |    R12         |  [SP+16]
                           |    R3          |  [SP+12]
                           |    R2          |  [SP+8]
                           |    R1          |  [SP+4]
                           |    R0          |  [SP+0]
                           +----------------+  <- SP moi (thap hon 32 bytes)
```

**Tai sao chi luu R0-R3, R12, LR, PC, xPSR?**

Day la AAPCS (ARM Architecture Procedure Call Standard):
- R0-R3, R12: Caller-saved registers (function duoc phep thay doi)
- R4-R11: Callee-saved registers (function phai bao ton)
- ISR la "function" -> no tu giu R4-R11 neu can dung
- Hardware chi luu phan ma caller khong bao ton

```
R0-R3:   Tham so function / gia tri tra ve
R4-R11:  Local variables (ISR phai push/pop neu dung)
R12:     Scratch register (Intra-procedure-call)
LR:      Link Register (EXC_RETURN trong exception context)
PC:      Program Counter (dia chi lenh tiep theo de return ve)
xPSR:    Program Status Register (flags, exception number, Thumb bit)
SP:      Stack Pointer (tu dong thay doi, khong push)
```

### 5.2 EXC_RETURN - Gia Tri Bao Than

Khi CPU vao ISR, LR KHONG chua dia chi return nhu truong hop function call binh thuong. LR chua gia tri dac biet goi la **EXC_RETURN**:

```
EXC_RETURN gia tri (Cortex-M4):

0xFFFFFFF1: Return to Handler mode, MSP, 8 regs stacked
0xFFFFFFF9: Return to Thread mode, MSP, 8 regs stacked
0xFFFFFFFD: Return to Thread mode, PSP, 8 regs stacked
0xFFFFFFE1: Return to Handler mode, MSP, 26 regs (FPU)
0xFFFFFFE9: Return to Thread mode, MSP, 26 regs (FPU)
0xFFFFFFED: Return to Thread mode, PSP, 26 regs (FPU)

Bit [3] = 1: Use MSP for unstacking
Bit [3] = 0: Use PSP for unstacking
Bit [2] = 1: Return to Thread mode
Bit [2] = 0: Return to Handler mode (nested interrupt)
```

**Tai sao CPU biet day la exception return?**

Khi ISR thuc hien `BX LR`:
- CPU kiem tra bit[31:28] cua gia tri
- Neu = 0xF (1111 1111 1111 1111 1111 1111 1111 XXXX) -> Day la EXC_RETURN
- CPU biet can thuc hien exception return, khong phai jump binh thuong

### 5.3 Mo Phong Timer Interrupt Step-by-Step

```
TIME 0:   TIM2 counter dem den gia tri ARR (underflow/overflow)
          TIM2->SR bit UIF = 1 (Update Interrupt Flag)
          TIM2 assert TIM2_IRQn line (dien ap thay doi)

TIME 1:   NVIC nhan IRQ line active
          NVIC kiem tra NVIC->ISER[0] bit 28 (TIM2) = 1? -> Yes
          NVIC kiem tra NVIC->IPR[7] byte 0 (priority TIM2) = 5
          NVIC kiem tra BASEPRI: co mask khong? -> No
          NVIC kiem tra co IRQ uu tien cao hon dang active? -> No
          NVIC gui nIRQ signal den CPU core

TIME 2:   CPU dang thuc hien lenh ADD R1, R2, R3
          CPU hoan thanh lenh nay (KHONG dung giua chung)
          CPU kiem tra nIRQ signal: active

TIME 3:   CPU bat dau exception entry sequence:
          - Push {R0-R3, R12, LR, PC, xPSR} xuong MSP (hoac PSP)
          - SP giam 32 bytes
          - CPU doc exception number tu NVIC: 28+16 = 44
          - LR = EXC_RETURN (0xFFFFFFF9 neu Thread mode, MSP)

TIME 4:   CPU doc VTOR: 0x08000000
          CPU tinh: 0x08000000 + (44 * 4) = 0x080000B0
          CPU doc 4 bytes tai 0x080000B0: gia tri = 0x08001234 | 0x1
          PC = 0x08001235 (Thumb bit set)

TIME 5:   CPU bat dau thuc hien TIM2_IRQHandler tai 0x08001234
          NVIC danh dau TIM2 la "Active" (khong chi "Pending" nua)

          void TIM2_IRQHandler(void) {
              if (TIM2->SR & TIM_SR_UIF) {
                  TIM2->SR &= ~TIM_SR_UIF;  /* QUAN TRONG: phai clear flag */
                  timer_tick++;
              }
          }

TIME 6:   ISR ket thuc, thuc hien BX LR (EXC_RETURN = 0xFFFFFFF9)
          CPU phat hien EXC_RETURN
          CPU bat dau exception return:
          - Pop {R0-R3, R12, LR, PC, xPSR} tu MSP
          - SP tang 32 bytes
          - PC = gia tri vua pop = dia chi lenh tiep theo truoc khi bi ngat
          - xPSR duoc khoi phuc

TIME 7:   CPU tiep tuc thuc hien main code tu dung cho
          Moi thu nhu chua co gi xay ra
```

### 5.4 Kiem tra Tu Duy - Chuong 5

**Cau 1:** Neu ISR KHONG clear flag cua peripheral (vi du TIM2->SR bit UIF), chuyen gi xay ra sau khi ISR return?

**Cau 2:** Stack pointer thay doi bao nhieu bytes khi vao ISR? Neu stack da gan day (chi con 20 bytes), chuyen gi xay ra?

**Cau 3:** EXC_RETURN = 0xFFFFFFFD co nghia la gi? Khi nao CPU su dung PSP thay vi MSP de unstack?

---

<a name="ch6"></a>
## CHUONG 6: INTERRUPT PRIORITY VA PREEMPTION

### 6.1 Priority Trong Cortex-M

```
Priority Number:  0 = HIGHEST, 255 = LOWEST
(Nguoc voi common sense - Junior thuong nham)

Cortex-M4 co 4-bit priority (16 muc): 0, 16, 32, 48, 64, 80, 96, 112,
                                       128, 144, 160, 176, 192, 208, 224, 240

Priority Grouping (SCB->AIRCR PRIGROUP field):
  Group 0: [7:4] = preempt, [3:0] = subpriority (16 preempt, 1 sub)
  Group 4: [7:5] = preempt, [4:0] = subpriority (8 preempt, 1 sub)
  Group 7: No preemption bits, all sub-priority

Preemption: ISR co priority cao hon CO THE ngat ISR dang chay
Sub-priority: Quyet dinh thu tu khi nhieu IRQ co cung preemption priority dang pending
```

### 6.2 States Cua Mot Interrupt

```
DISABLED <---> ENABLED
                  |
                  v
              [Event xay ra]
                  |
                  v
             PENDING <------+
             (cho phuc vu)  |
                  |         |
                  v         |
              ACTIVE        | (neu ISR KHONG clear flag)
           (dang chay)  ----+
                  |
                  v
               DONE
               (ISR return)
```

### 6.3 Preemption Timeline

```
Kich ban: IRQ1 priority=3, IRQ2 priority=1 (HIGHER priority)

Timeline:

Main    |===A====|          |============C============|
        |        |          |
IRQ1    |        |==B1===|  |==B2=|     |====B3======|
        |        |       |  |     |     |
IRQ2    |        |       |==|==D==|=|   |
        |        |       |        |
         t0     t1      t2  t3   t4  t5

t0: Main dang chay (A)
t1: IRQ1 xay ra, priority=3. CPU context save -> vao ISR1 (B1)
t2: IRQ2 xay ra, priority=1 (cao hon 3). CPU preempt ISR1!
    Context save them lan nua (stack lau lau hon)
    CPU vao ISR2 (D)
t3: ISR2 done, CPU exception return -> khoi phuc ISR1 (B2)
t4: ISR1 done, CPU exception return -> khoi phuc Main (C)

Stack luc t2 (tu tren xuong duoi):
  [ISR1 frame: R0-R3,R12,LR,PC,xPSR]
  [Main frame: R0-R3,R12,LR,PC,xPSR]
  [... rest of stack ...]
```

### 6.4 Tail-Chaining - Optimization Cua Cortex-M

```
Kich ban: IRQ1 va IRQ2 ca hai pending, IRQ1 priority cao hon

KHONG co Tail-Chaining (naive):
  ISR1: | context save | ISR1 execute | context restore |
  ISR2:                                                  | context save | ISR2 | restore |
  Overhead: 2x context save/restore = 64 bytes * 2 = 16 cycles * 2

VOI Tail-Chaining:
  ISR1: | context save | ISR1 execute | --- NO RESTORE --- |
  ISR2:                               | vector fetch | ISR2 | context restore |
  Overhead: 1x save + 1x restore + 1x vector fetch
  Tiet kiem ~12 cycles (khong restore roi save lai)

CPU tu dong phat hien: sau khi ISR1 xong, con IRQ pending?
  -> YES: khong restore, thuc hien tail-chain
  -> NO: restore context, ve main
```

### 6.5 Late Arrival

```
Kich ban: IRQ1 (priority=5) dang trong qua trinh context save,
          IRQ2 (priority=2) xay ra

KHONG co Late Arrival:
  | IRQ1 context save | IRQ1 execute | IRQ1 return | IRQ2 context save | IRQ2 |

VOI Late Arrival (Cortex-M):
  | context save | IRQ2 fetch vector | IRQ2 execute | IRQ2 return |
                                                                    | IRQ1 fetch vector | IRQ1 |
  CPU dang context save -> IRQ cao priority den -> switch sang fetch vector cua IRQ moi
  Context save cu van dung duoc (vi stack frame la chung)
```

### 6.6 BASEPRI, PRIMASK, FAULTMASK

```c
/* PRIMASK: Mask tat ca interrupts ngoai NMI va HardFault */
__set_PRIMASK(1);   /* Disable tat ca maskable interrupts */
/* Critical section code */
__set_PRIMASK(0);   /* Enable lai */

/* BASEPRI: Chi mask interrupt priority <= gia tri nay */
__set_BASEPRI(5 << 4);  /* Mask tat ca priority >= 5 (gia tri lon = priority thap) */
/* Chi cho phep priority 0,1,2,3,4 preempt */
__set_BASEPRI(0);        /* Disable masking */

/* FAULTMASK: Mask ca HardFault (ngoai NMI) */
__set_FAULTMASK(1);  /* Rat nguy hiem, chi dung trong fault handler */

/* FreeRTOS su dung configMAX_SYSCALL_INTERRUPT_PRIORITY
   = gia tri BASEPRI de protect RTOS critical sections
   IRQ co priority < configMAX_SYSCALL = KHONG the goi FreeRTOS API */
```

### 6.7 Kiem tra Tu Duy - Chuong 6

**Cau 1:** IRQ1 priority = 5, IRQ2 priority = 3. Ca hai dang pending cung luc. CPU se phuc vu cai nao truoc? Sau khi xong cai do, co tail-chain khong?

**Cau 2:** FreeRTOS co configMAX_SYSCALL_INTERRUPT_PRIORITY = 5. ISR co priority = 3 goi xQueueSendFromISR(). Chuyen gi xay ra?

**Cau 3:** Nested interrupt co the xay ra bao nhieu cap? Gioi han la gi?

---

<a name="ch7"></a>
## CHUONG 7: INTERRUPT + RTOS (FREERTOS)

### 7.1 Tai Sao Khong The Goi xSemaphoreGive() Trong ISR?

```c
/* HAM KHONG DUNG CHO ISR */
BaseType_t xSemaphoreGive(SemaphoreHandle_t xSemaphore);

/* Ham nay ben trong goi: */
void xQueueGenericSend(...) {
    /* ... */
    taskENTER_CRITICAL();      /* Disable interrupts! */
    /* ... them vao queue ... */
    taskEXIT_CRITICAL();       /* Enable interrupts */

    /* Neu co task dang cho, goi scheduler */
    if (xHigherPriorityTaskWoken) {
        portYIELD();            /* Trigger PendSV */
    }
}
```

**Van de 1: Critical Section trong ISR**

`taskENTER_CRITICAL()` disable interrupt bang cach set BASEPRI. Nhung chung ta DANG trong ISR roi - nghia la interrupt da bi disable de vao day. Goi tiep tuc disable co the gay ra deadlock hoac nested critical section sai.

**Van de 2: Scheduler goi sai luc**

`portYIELD()` set PendSV pending. Nhung ISR hien tai CHUA ket thuc! PendSV se chay NGAY khi ISR return -> context switch xay ra truoc khi CPU khoi phuc dung trang thai.

```c
/* HAM DUNG CHO ISR */
BaseType_t xSemaphoreGiveFromISR(
    SemaphoreHandle_t xSemaphore,
    BaseType_t *pxHigherPriorityTaskWoken  /* OUTPUT */
);

/* Ben trong: */
void xQueueGenericSendFromISR(...) {
    /* Khong dung taskENTER_CRITICAL() */
    /* Thay the: UBaseType_t uxSavedInterruptStatus = portSET_INTERRUPT_MASK_FROM_ISR() */
    /* -> Dung cach phu hop voi ISR context */

    /* Them vao queue */
    /* ... */

    /* KHONG goi scheduler truc tiep */
    /* Thay the: set flag de ISR caller quyet dinh */
    *pxHigherPriorityTaskWoken = pdTRUE;

    /* portCLEAR_INTERRUPT_MASK_FROM_ISR(uxSavedInterruptStatus) */
}
```

### 7.2 Dung Pattern Chuan Cho ISR Voi FreeRTOS

```c
/* ISR chuan voi FreeRTOS */
void UART1_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;

    /* Doc du lieu tu peripheral */
    uint8_t data = USART1->DR;

    /* Gui vao queue - ham "FromISR" */
    xQueueSendFromISR(uart_rx_queue, &data, &xHigherPriorityTaskWoken);

    /* Neu task co priority cao hon da san sang:
       Request context switch NGAY SAU KHI ISR return */
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    /* portYIELD_FROM_ISR:
       Neu xHigherPriorityTaskWoken = pdTRUE: set PendSV pending
       PendSV chay ngay sau khi ISR return
       -> Context switch ngay lap tuc
    */
}
```

### 7.3 SysTick, PendSV, SVC - Ba Truc Cot Cua FreeRTOS

```
+=========================================================+
|  FREERTOS INTERRUPT MECHANISM                           |
+=========================================================+
|                                                         |
|  SysTick (Priority: cao - vi du 0xE0 = 224)            |
|  -> Goi moi configTICK_RATE_HZ (1ms)                   |
|  -> Dem tick count                                      |
|  -> Phat hien task timeout/delay                        |
|  -> Neu can context switch: set PendSV PENDING          |
|                                                         |
|  PendSV (Priority: THAP NHAT - 0xFF = 255)             |
|  -> Chi chay khi khong con ISR nao khac dang active     |
|  -> Thuc hien actual context switch                     |
|  -> Luu thanh ghi R4-R11 cua task hien tai             |
|  -> Nap thanh ghi R4-R11 cua task moi                  |
|                                                         |
|  SVC (Priority: configurable)                           |
|  -> Task goi OS API tu unprivileged mode                |
|  -> Bat dau scheduler lan dau (vTaskStartScheduler)     |
|                                                         |
+=========================================================+

FLOW CHINH XAC:

1ms Hardware SysTick
       |
       v
SysTick_Handler (FreeRTOS)
  xTaskIncrementTick()
  Phat hien TaskB het delay -> ReadyList
  portYIELD_FROM_ISR(pdTRUE)
    -> NVIC_INT_CTRL = PENDSVSET
       |
       v
PendSV pending (nhung chua chay vi SysTick chua return)
       |
       v
SysTick_Handler return (BX LR = EXC_RETURN)
       |
       v
PendSV_Handler bat dau (vi no la pending va khong con ISR nao khac)
  PUSH {R4-R11} xuong PSP cua TaskA (luu context)
  TaskA->pxTopOfStack = PSP
  TaskA -> NotReady list (neu het quantum)

  TaskB = highest priority ready task
  PSP = TaskB->pxTopOfStack
  POP {R4-R11} tu PSP cua TaskB (nap context)
  BX LR (EXC_RETURN)
       |
       v
CPU return to Thread mode voi PSP cua TaskB
TaskB tiep tuc chay tu dung cho
```

### 7.4 Kiem tra Tu Duy - Chuong 7

**Cau 1:** Tai sao PendSV phai co priority thap nhat trong he thong? Dieu gi xay ra neu PendSV co priority cao hon UART ISR?

**Cau 2:** FreeRTOS portENTER_CRITICAL() dung BASEPRI, khong dung PRIMASK. Tai sao? Su khac biet trong thuc te la gi?

**Cau 3:** vTaskDelay(100) ben trong hoat dong nhu the nao lien quan den SysTick va scheduler?

---

<a name="ch8"></a>
## CHUONG 8: BOOTLOADER + MULTI-IMAGE

### 8.1 Flash Layout Voi Bootloader

```
FLASH MEMORY (Vi du STM32F4, 1MB):

0x08000000 +---------------------------+
           |    BOOTLOADER             |
           |    Vector Table BL        |  <- CPU doc day khi power-on
           |    BL Code                |
           |    BL Data (rodata)       |
0x08008000 +---------------------------+
           |    APPLICATION            |
           |    Vector Table APP       |  <- App co vector table RIENG
           |    App Code               |
           |    App Data               |
0x08100000 +---------------------------+
           |    (Unused / OTA buffer)  |
0x08200000 +---------------------------+  <- End of Flash
```

### 8.2 Bootloader Jump Vao Application - Dung Cach

```c
/* Bootloader code */

/* Dinh nghia dia chi app */
#define APP_START_ADDRESS   0x08008000
#define APP_STACK_POINTER   (*((volatile uint32_t*)APP_START_ADDRESS))
#define APP_RESET_HANDLER   (*((volatile uint32_t*)(APP_START_ADDRESS + 4)))

typedef void (*AppResetHandler_t)(void);

void bootloader_jump_to_app(void) {

    /* BUOC 1: Tat tat ca peripheral va interrupt */
    /* QUAN TRONG: Neu khong tat, app se inherit trang thai tu BL */
    HAL_DeInit();
    /* Hoac thu cong: */
    RCC->AHB1ENR = 0;
    RCC->APB1ENR = 0;
    RCC->APB2ENR = 0;

    /* BUOC 2: Disable tat ca NVIC IRQ */
    for (int i = 0; i < 8; i++) {
        NVIC->ICER[i] = 0xFFFFFFFF;  /* Disable all */
        NVIC->ICPR[i] = 0xFFFFFFFF;  /* Clear pending */
    }

    /* BUOC 3: Disable SysTick */
    SysTick->CTRL = 0;

    /* BUOC 4: Disable global interrupts */
    __disable_irq();

    /* BUOC 5: Validate app (kiem tra magic number hoac CRC) */
    /* Stack pointer phai nam trong RAM range */
    if ((APP_STACK_POINTER & 0xFF000000) != 0x20000000) {
        /* App khong hop le */
        Error_Handler();
    }

    /* BUOC 6: Set MSP toi gia tri Stack Pointer cua app */
    __set_MSP(APP_STACK_POINTER);

    /* BUOC 7: RELOCATE VECTOR TABLE cua app */
    SCB->VTOR = APP_START_ADDRESS;

    /* BUOC 8: Enable interrupt tro lai (app se tu config) */
    __enable_irq();

    /* BUOC 9: Jump den Reset_Handler cua app */
    AppResetHandler_t app_reset = (AppResetHandler_t)APP_RESET_HANDLER;
    app_reset();

    /* Khong bao gio den day */
    while(1);
}
```

### 8.3 Tai Sao Chi Jump Reset_Handler Chua Du?

```
Junior thuong nghĩ: "Toi chi can jump den Reset_Handler cua app la xong"

Sai vi:
1. VTOR van tro den vector table cua bootloader
   -> App interrupt -> CPU tim ISR cua BOOTLOADER -> sai!
   -> App se gap HardFault ngay khi co interrupt dau tien

2. MSP van tro den stack cua bootloader
   -> App Reset_Handler se copy .data, zero .bss, sau do goi main()
   -> main() chay tren stack cua BL -> stack overflow neu BL stack nho

3. Peripheral state cua BL con do
   -> App khong biet peripheral da duoc cau hinh gi
   -> Co the gay conflict

DUNG CACH (thu tu quan trong):
1. Tat peripheral + NVIC + SysTick
2. Set MSP = app->stack_pointer
3. Set VTOR = app_start_address
4. Jump den app->reset_handler
```

### 8.4 Loi Thuong Gap Khi Bootloader Jump App

```
LOI 1: HardFault ngay khi app enable interrupt lan dau
  Nguyen nhan: VTOR chua duoc set -> CPU tim ISR sai address
  Debug: Kiem tra SCB->VTOR = 0x08008000 (khong phai 0x08000000)

LOI 2: App chay duoc nhung crash sau vai giay
  Nguyen nhan: Stack MSP chua duoc update -> stack overlap BL data
  Debug: Xem SP register, so sanh voi _stack_size trong linker

LOI 3: App khong chay duoc gi ca
  Nguyen nhan: NVIC interrupts tu BL van con active/pending
  Debug: Tat tat ca NVIC truoc khi jump

LOI 4: App chay nhung FreeRTOS crash
  Nguyen nhan: SysTick cua BL van dang chay -> xung dot voi SysTick cua app
  Debug: Disable SysTick (SysTick->CTRL = 0) truoc khi jump

LOI 5: OTA update xong nhung app moi khong nhan duoc flash moi nhat
  Nguyen nhan: Flash cache chua duoc invalidate
  Debug: FLASH->ACR cache flush
```

### 8.5 Kiem tra Tu Duy - Chuong 8

**Cau 1:** Bootloader dat tai 0x08000000, App tai 0x08008000. App da chay duoc. Nhung khi Timer interrupt xay ra, CPU vao HardFault. Nguyen nhan chinh xac la gi va cach fix?

**Cau 2:** Tai sao can disable global interrupt truoc khi jump, nhung sau khi set VTOR lai can enable lai?

**Cau 3:** App linker script co can thay doi so voi project thong thuong (khong co bootloader) khong?

---

<a name="ch9"></a>
## CHUONG 9: DEBUGGING VECTOR TABLE - 5 CASE THUC TE

### Case 1: Interrupt Khong Bao Gio Vao ISR

**Checklist debug 9 buoc (theo thu tu):**

```
BUOC 1: Kiem tra Peripheral Clock
  - RCC->APB1ENR / APB2ENR / AHB1ENR co bit clock cua peripheral duoc set?
  - Neu clock chua enable: peripheral KHONG hoat dong, KHONG the tao IRQ
  Fix: RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;

BUOC 2: Kiem tra Peripheral Interrupt Flag
  - Co su kien xay ra chua? (TIM2->SR & TIM_SR_UIF)?
  - Neu flag = 0: peripheral chua tao ra event
  Fix: Kiem tra cau hinh peripheral (ARR, PSC, etc.)

BUOC 3: Kiem tra Peripheral Interrupt Enable
  - TIM2->DIER & TIM_DIER_UIE = 1?
  - Neu = 0: peripheral co event nhung KHONG gui IRQ signal
  Fix: TIM2->DIER |= TIM_DIER_UIE;

BUOC 4: Kiem tra NVIC Enable
  - NVIC->ISER[0] bit 28 (TIM2) = 1?
  - Neu = 0: NVIC nhan duoc IRQ nhung bo qua
  Fix: NVIC_EnableIRQ(TIM2_IRQn);

BUOC 5: Kiem tra Priority va Masking
  - NVIC->IPR priority < BASEPRI?
  - PRIMASK = 1?
  - FAULTMASK = 1?
  - Neu BASEPRI = 0x50 (80) va priority = 96: bi mask!
  Fix: __set_BASEPRI(0); hoac tang priority cua IRQ

BUOC 6: Kiem tra Global Interrupt Enable
  - __get_PRIMASK() = 0? (0 = interrupts enabled)
  - Neu PRIMASK = 1: tat ca maskable interrupts bi disable
  Fix: __enable_irq();

BUOC 7: Kiem tra Vector Table o Dung Dia Chi
  - SCB->VTOR = 0x08000000 (hoac gia tri mong doi)?
  - Su dung GDB: x/4xw 0x08000000
  - Gia tri tai [28] = dia chi TIM2_IRQHandler?
  Fix: Kiem tra linker script, them VTOR setup

BUOC 8: Kiem tra ISR Symbol Co Trong Binary
  - arm-none-eabi-nm firmware.elf | grep TIM2_IRQHandler
  - Co ket qua khong? Dia chi co hop le khong?
  Fix: Kiem tra ten function, extern "C" trong C++

BUOC 9: Kiem tra Linker Placement
  - arm-none-eabi-objdump -h firmware.elf | grep isr_vector
  - Section .isr_vector co o dia chi 0x08000000?
  - arm-none-eabi-readelf -s firmware.elf | grep vector_table
  Fix: Kiem tra linker script, them KEEP()
```

### Case 2: CPU Nhay Vao Default_Handler

**Nguyen nhan va cach phan biet:**

```c
/* Default_Handler duoc vao khi:
 * 1. ISR CHUA duoc implement (weak alias)
 * 2. ISR NAME SAI (typo)
 * 3. Vector table co NULL pointer
 */

/* Cach phat hien: Them debug info vao Default_Handler */
void Default_Handler(void) {
    /* Doc exception number dang active */
    volatile uint32_t exc_number = __get_IPSR() & 0xFF;
    /* exc_number: 1=Reset, 2=NMI, 3=HardFault, ..., 16+=IRQ0+ */

    /* Tinh ten IRQ */
    volatile int irq_number = (int)exc_number - 16;

    /* Dung debugger tai day de doc exc_number */
    __BKPT(0);  /* Breakpoint */
    while (1);
}

/* Sau khi biet exc_number:
 * - Lookup IRQ table de biet ten IRQ
 * - Kiem tra co implement ISR cho IRQ do chua
 * - Kiem tra ten co dung chinh xac khong
 */
```

**Typo example:**
```c
/* SAI: Ten function sai */
void Tim2_IRQHandler(void) { /* 'T' thay vi 'TIM' */
    /* Code nay KHONG bao gio duoc goi */
    /* Weak alias van tro den Default_Handler */
}

/* DUNG: */
void TIM2_IRQHandler(void) {
    /* ... */
}
```

### Case 3: CPU Vao HardFault Ngay Sau Khi Interrupt Xay Ra

**Cac nguyen nhan co the xay ra:**

```
NGUYEN NHAN A: Invalid ISR Address trong Vector Table
  Trieu chung: HardFault NGAY khi fetch ISR address
  Debug: Kiem tra SCB->HFSR bit VECTTBL = 1
         SCB->HFSR |= 0x00000002 -> VECTTBL fault
  Cach fix: Kiem tra vector table co dia chi hop le

NGUYEN NHAN B: Stack Corruption Truoc Do
  Trieu chung: HardFault khi CPU co push stack (exception entry)
  Debug: Kiểm tra SP: phai aligned 8 bytes, phai trong RAM range
         CFSR->STKERR = 1 -> stacking error
  Cach fix: Tang stack size, tim stack overflow

NGUYEN NHAN C: Sai ISR Address (Thumb bit missing)
  Trieu chung: CPU nhay den dia chi chan (even) tren Cortex-M -> FAULT
  Debug: Kiem tra gia tri trong vector table co Thumb bit set?
         Gia tri phai la ODD (ket thuc bang 1)
  Cach fix: Linker script va compiler tu xu ly, nhung kiem tra neu assembly

NGUYEN NHAN D: Wrong Vector Table (sau Bootloader Jump)
  Trieu chung: VTOR van tro den BL vector table
  Debug: SCB->VTOR = 0x08000000 khi le ra phai la 0x08008000
  Cach fix: Them SCB->VTOR = APP_START; trong bootloader

NGUYEN NHAN E: MPU Violation
  Trieu chung: ISR co gang truy cap vung nho bi cam
  Debug: SCB->CFSR IACCVIOL hoac DACCVIOL
  Cach fix: Cau hinh lai MPU regions
```

**Debug HardFault chuan:**
```c
/* Them vao HardFault_Handler de doc thong tin */
void HardFault_Handler(void) {
    __asm volatile (
        "TST LR, #4\n"          /* Kiem tra EXC_RETURN bit 2 */
        "ITE EQ\n"
        "MRSEQ R0, MSP\n"       /* Neu = 0: dung MSP */
        "MRSNE R0, PSP\n"       /* Neu = 1: dung PSP */
        "B hard_fault_handler_c\n"
    );
}

void hard_fault_handler_c(uint32_t *sp) {
    /* Doc stacked registers */
    volatile uint32_t stacked_r0  = sp[0];
    volatile uint32_t stacked_r1  = sp[1];
    volatile uint32_t stacked_r2  = sp[2];
    volatile uint32_t stacked_r3  = sp[3];
    volatile uint32_t stacked_r12 = sp[4];
    volatile uint32_t stacked_lr  = sp[5];
    volatile uint32_t stacked_pc  = sp[6];  /* PC tai thoi diem fault */
    volatile uint32_t stacked_psr = sp[7];

    /* Doc fault status registers */
    volatile uint32_t cfsr  = SCB->CFSR;   /* Combined Fault Status */
    volatile uint32_t hfsr  = SCB->HFSR;   /* HardFault Status */
    volatile uint32_t dfsr  = SCB->DFSR;   /* Debug Fault Status */
    volatile uint32_t bfar  = SCB->BFAR;   /* Bus Fault Address */
    volatile uint32_t mmar  = SCB->MMFAR;  /* MemManage Fault Address */

    __BKPT(0);
    while(1);
}
```

### Case 4: Firmware Bi Loi Sau Khi Bat -O2 Optimization

**Phan tich nguyen nhan:**

```c
/* NGUYEN NHAN 1: Thieu volatile cho bien chia se voi ISR */
uint32_t counter = 0;  /* THIEU volatile */

void TIM2_IRQHandler(void) {
    counter++;
}

void main_task(void) {
    while (counter < 100) {  /* Compiler co the optimize thanh while(true) */
        /* Compiler nghi: counter khong thay doi trong loop nay */
        /* Nen: no co the cache gia tri counter trong register */
    }
}

/* FIX: */
volatile uint32_t counter = 0;  /* Phai co volatile */

/* NGUYEN NHAN 2: ISR bi inline hoac bi xoa */
/* Neu ISR khong duoc reference ngoai vector table:
   compiler co the xoa, hoac optimizer thay doi cau truc */

/* FIX: Them __attribute__((noinline)) hoac __attribute__((used)) */

/* NGUYEN NHAN 3: Memory ordering (khong co barrier) */
uint8_t data_ready = 0;
uint32_t data_value = 0;

void ISR(void) {
    data_value = read_sensor();
    data_ready = 1;           /* CPU co the reorder truoc data_value! */
}

void main_loop(void) {
    if (data_ready) {
        use(data_value);      /* data_value co the chua duoc ghi */
    }
}

/* FIX: Them memory barrier */
void ISR(void) {
    data_value = read_sensor();
    __DMB();                  /* Data Memory Barrier */
    data_ready = 1;
}

/* NGUYEN NHAN 4: Interrupt flag khong clear truoc khi exit */
/* Voi -O2 code chay nhanh hon -> interrupt re-enter ngay lap tuc */
/* Lich su tich luy khi code chay cham an di loi */
```

### Case 5: Bootloader OK Nhung App Khong Nhan Interrupt

**Debug step-by-step:**

```
BUOC 1: Xac nhan VTOR
  GDB: x/xw 0xE000ED08
  Ket qua mong doi: 0x08008000 (app start)
  Neu thay 0x08000000: VTOR chua duoc update -> Fix: SCB->VTOR = 0x08008000

BUOC 2: Xac nhan Vector Table App
  GDB: x/32xw 0x08008000
  Entry [0]: gia tri Stack Pointer (phai trong RAM: 0x20000000-0x20020000)
  Entry [1]: Reset_Handler address (phai trong Flash app)
  Entry [TIM2]: TIM2_IRQHandler address

BUOC 3: Kiem tra NVIC State
  NVIC->ICER co bi set boi BL ma chua duoc clear?
  GDB: x/8xw 0xE000E180  (NVIC ICER registers)
  Phai = 0 (tat ca 0) sau khi BL reset NVIC

BUOC 4: Kiem tra SysTick
  SysTick->CTRL: bit 0 (ENABLE) = 0?
  Neu BL dung SysTick va khong tat truoc khi jump -> xung dot

BUOC 5: Kiem tra App Linker Script
  App phai co ORIGIN = 0x08008000 (khong phai 0x08000000)
  arm-none-eabi-objdump -h app.elf | grep isr_vector
  -> Address phai la 0x08008000
```

---

<a name="ch10"></a>
## CHUONG 10: DEBUG VOI GDB

### 10.1 Cac Lenh GDB Thiet Yeu

```gdb
# Ket noi den target (OpenOCD)
target remote localhost:3333

# Doc toan bo Vector Table (64 entries dau)
x/64xw 0x08000000

# Doc VTOR - Biet vector table dang o dau
x/xw 0xE000ED08

# Doc SCB registers quan trong
x/xw 0xE000ED04    # ICSR - Interrupt Control and State Register
x/xw 0xE000ED28    # CFSR - Configurable Fault Status Register
x/xw 0xE000ED2C    # HFSR - HardFault Status Register
x/xw 0xE000ED34    # BFAR - Bus Fault Address Register
x/xw 0xE000ED38    # MMFAR - MemManage Fault Address Register

# Xem tat ca registers hien tai
info registers

# Xem Stack Pointer
info registers sp
# Hoac:
print $sp

# Xem Program Counter
info registers pc
print $pc

# Kiem tra CPU o Thread hay Handler mode
# IPSR (lo 8 bits cua xPSR) != 0 -> Handler mode
x/xw 0xE000EF00    # Khong chinh xac, dung:
info registers xpsr
# IPSR = xPSR & 0xFF, neu != 0 -> dang trong exception

# Xem bo nho tai dia chi cu the
x/16xb 0x20000000  # 16 bytes tu 0x20000000 (hex bytes)
x/4xw  0x20000000  # 4 words tu 0x20000000
x/s    0x20000000  # Doc string

# Xem source code tai dia chi
list *0x08001234

# Find function address
info functions TIM2
```

### 10.2 Phan Tich CFSR - Giai Ma Loi

```
CFSR (Configurable Fault Status Register) = 0xE000ED28

Bit layout:
  [31:26] Reserved
  [25]    DIVBYZERO  - UsageFault: chia cho 0
  [24]    UNALIGNED  - UsageFault: truy cap khong align
  [19]    NOCP       - UsageFault: lenh coprocessor khong co
  [18]    INVPC      - UsageFault: PC khong hop le (EXC_RETURN loi)
  [17]    INVSTATE   - UsageFault: EPSR.T = 0 (khong phai Thumb)
  [16]    UNDEFINSTR - UsageFault: lenh khong dinh nghia
  [15]    BFARVALID  - BusFault: BFAR chua dia chi hop le
  [13]    LSPERR     - BusFault: loi khi lazy float save
  [12]    STKERR     - BusFault: loi khi stacking (exception entry)
  [11]    UNSTKERR   - BusFault: loi khi unstacking (exception return)
  [10]    IMPRECISERR- BusFault: loi async (khong biet dia chi)
  [9]     PRECISERR  - BusFault: loi precise (BFAR hop le)
  [8]     IBUSERR    - BusFault: loi fetch lenh
  [7]     MMARVALID  - MemManage: MMFAR chua dia chi hop le
  [5]     MLSPERR    - MemManage: loi khi lazy float save
  [4]     MSTKERR    - MemManage: loi khi stacking
  [3]     MUNSTKERR  - MemManage: loi khi unstacking
  [1]     DACCVIOL   - MemManage: vi pham truy cap data
  [0]     IACCVIOL   - MemManage: vi pham fetch lenh

HFSR (HardFault Status Register) = 0xE000ED2C
  [31]    DEBUGEVT   - Debug event
  [30]    FORCED     - Forced HardFault (fault bi escalate)
  [1]     VECTTBL    - Fault khi doc Vector Table
```

### 10.3 Debug Workflow Khi Co HardFault

```
BUOC 1: Dung tai HardFault_Handler (breakpoint hoac while(1))

BUOC 2: Doc stacked PC (dia chi lenh gay fault)
  info registers -> lay SP
  x/8xw $sp -> [6] la stacked PC
  Hoac: print ((uint32_t*)$sp)[6]

BUOC 3: Tim source code tai stacked PC
  list *0x<stacked_pc>
  info symbol 0x<stacked_pc>

BUOC 4: Doc CFSR de biet loai fault
  x/xw 0xE000ED28

BUOC 5: Neu PRECISERR set -> BFAR co dia chi sai
  x/xw 0xE000ED34   # BFAR

BUOC 6: Neu STKERR set -> stack overflow/corruption
  Kiem tra: x/xw $sp - xem co trong RAM khong
  So sanh voi __StackTop - __stack_size

BUOC 7: Neu FORCED set -> fault khac escalate thanh HardFault
  Kiem tra CFSR[15:8] (BusFault), CFSR[7:0] (MemManage), CFSR[31:16] (UsageFault)
```

---

<a name="ch11"></a>
## CHUONG 11: 15+ MISCONCEPTIONS CUA JUNIOR

### Misconception 1
```
MISCONCEPTION: "Vector table chinh la NVIC"

THUC TE:
- NVIC: Hardware block, quan ly enable/disable/priority/pending/active
- Vector Table: Mang dia chi ISR trong Flash/RAM, doc boi CPU
- CPU doc vector table truc tiep, NVIC chi cung cap exception number

TAI SAO NHAM: Ca hai deu lien quan den interrupt -> de nham
HU QUA: Cau hinh sai thu tu, debug sai huong
```

### Misconception 2
```
MISCONCEPTION: "ISR chi la function binh thuong, chi can khai bao va implement"

THUC TE:
- ISR phai duoc DAT vao Vector Table dung vi tri
- Ten phai KHOP CHINH XAC voi khai bao weak alias
- ISR chay o Handler mode (privilege) khac Thread mode
- ISR khong duoc tra ve gia tri, khong co tham so
- ISR KHONG the goi nhieu FreeRTOS API binh thuong
- ISR nhat thiet phai clear interrupt flag cua peripheral

TAI SAO NHAM: Cau truc giong function binh thuong
HU QUA: Interrupt khong hoat dong hoac HardFault
```

### Misconception 3
```
MISCONCEPTION: "Interrupt luon chay ngay lap tuc khi event xay ra"

THUC TE:
- Interrupt co the bi mask (PRIMASK, BASEPRI, FAULTMASK)
- Interrupt co priority thap co the bi tri hoan boi IRQ priority cao dang chay
- CPU hoan thanh lenh hien tai truoc khi chap nhan interrupt
- Trong FreeRTOS critical section: interrupt bi mask hoan toan

TAI SAO NHAM: Khai niem "real-time" lam nguoi ta nghĩ "tuc thi"
HU QUA: Thiet ke sai timing, bo sot su kien, latency bug
```

### Misconception 4
```
MISCONCEPTION: "Enable NVIC la du de interrupt hoat dong"

THUC TE:
Phai du 6 dieu kien:
1. Peripheral clock enable
2. Peripheral interrupt flag
3. Peripheral interrupt enable (DIER, CR1, etc.)
4. NVIC enable (NVIC->ISER)
5. Global interrupt enable (PRIMASK = 0)
6. Vector table entry dung

TAI SAO NHAM: NVIC la "interrupt controller" nen tuong rang no la thu can enable duy nhat
HU QUA: Debug hang gio ma khong tim ra nguyen nhan
```

### Misconception 5
```
MISCONCEPTION: "Vector table luon phai o dia chi 0x00000000"

THUC TE:
- Sau Reset: CPU doc tu 0x00000000 (co the la alias)
- VTOR co the thay doi: Vector table co the relocate
- Cortex-M0: KHONG co VTOR, vector table luon o 0x00000000
- Cortex-M3/M4/M7: VTOR co the tro den Flash, RAM, hoac bat ky dau
- Bootloader relocate vector table cua app la use case pho bien

TAI SAO NHAM: Tai lieu nhap mon thuong noi "0x00000000"
HU QUA: Khong hieu bootloader, loi khi porting
```

### Misconception 6
```
MISCONCEPTION: "CPU tu tim ISR bang ten function (string)"

THUC TE:
- CPU KHONG hieu ten function
- CPU chi lam: VTOR + (exception_number * 4) = dia chi trong vector table
- Doc 4 bytes tai dia chi do = dia chi ISR
- Jump den dia chi do
- Ten function la khai niem cua C/Assembler, khong ton tai sau khi link

TAI SAO NHAM: Lap trinh C quen voi khai niem ten ham
HU QUA: Khong hieu qua trinh link, kho debug
```

### Misconception 7
```
MISCONCEPTION: "ISR co the goi bat ky API nao"

THUC TA:
- KHONG the goi ham co the block (delay, mutex, malloc thong thuong)
- KHONG the goi FreeRTOS API binh thuong (phai dung FromISR variant)
- KHONG the in printf (neu dung UART blocking)
- KHONG the goi ham phu thuoc vao scheduler
- Moi thu trong ISR phai non-blocking va ngan

TAI SAO NHAM: ISR trong nhu function binh thuong
HU QUA: Deadlock, priority inversion, crash RTOS
```

### Misconception 8
```
MISCONCEPTION: "Priority so lon thi priority cao"

THUC TE (Cortex-M):
- So NHAT = Priority CAO NHAT (0 = cao nhat)
- FreeRTOS ngược lai: so LON = task priority CAO (nhung day la task priority, khong phai IRQ priority)
- NVIC: 0 = highest, 255 = lowest
- Nham lan giua NVIC priority va FreeRTOS task priority la loi pho bien nhat

TAI SAO NHAM: Common sense "so lon = quan trong hon"
HU QUA: ISR quan trong bi preempt boi ISR it quan trong
```

### Misconception 9
```
MISCONCEPTION: "Interrupt khong the bi interrupt khac preempt"

THUC TE:
- Cortex-M ho tro NESTED interrupt (preemption)
- IRQ co priority cao HON co the preempt IRQ priority thap dang chay
- Nest co the sau nhieu cap (chi gioi han boi stack size)
- Tai sao FreeRTOS co configMAX_SYSCALL_INTERRUPT_PRIORITY

TAI SAO NHAM: Nghi rang interrupt la "atomic" voi cac interrupt khac
HU QUA: Race condition trong ISR, loi RTOS
```

### Misconception 10
```
MISCONCEPTION: "vector table chi lien quan den startup code"

THUC TE:
- Vector table duoc su dung LIEN TUC trong qua trinh chay firmware
- Moi khi co interrupt: CPU doc vector table
- Bootloader dung vector table de redirect interrupt
- FreeRTOS thay the SysTick/PendSV/SVC handlers trong vector table
- Vector table co the bi thay doi runtime (VTOR)

TAI SAO NHAM: Chi thay vector table trong startup.c
HU QUA: Khong hieu architecture tong the
```

### Misconception 11
```
MISCONCEPTION: "RTOS tu xu ly toan bo interrupt, toi chi can viet code"

THUC TE:
- RTOS chi quan ly mot so exception: SysTick, PendSV, SVC
- Moi peripheral interrupt (UART, TIM, SPI...) van phai:
  * Implement ISR rieng
  * Enable trong NVIC
  * Xu ly flag
  * Dung FromISR API khi tuong tac voi RTOS

TAI SAO NHAM: RTOS tao cam giac "quan ly het"
HU QUA: Firmware khong hoat dong, debug mat thoi gian
```

### Misconception 12
```
MISCONCEPTION: "ISR ngan thi tot, khong can quan tam gi them"

THUC TE:
- "Ngan" la DIEU KIEN CAN nhung chua du
- Van can: volatile cho bien chia se, memory barrier, clear flag, dung FromISR API
- Van co the co race condition du ISR rat ngan
- ISR qua ngan co the bi "interrupt storm" (re-enter lien tuc)
- Design pattern ISR -> queue/semaphore phai chinh xac

TAI SAO NHAM: Nghi rang "ngan" giai quyet moi thu
HU QUA: Race condition bi an, loi sau, kho reproduce
```

### Misconception 13
```
MISCONCEPTION: "Float trong ISR thi phai turn off FPU"

THUC TE:
- Cortex-M4/M7 co FPU (Floating Point Unit)
- CPU tu dong luu FPU registers khi can (lazy stacking)
- Van co the dung float trong ISR
- Nhung: neu ca task va ISR dung float thi stack can lon hon (26 regs thay vi 8)
- Khong phai "turn off FPU" ma la "dam bao stack du lon"
- __FPU_PRESENT = 1 va __FPU_USED = 1 trong project

TAI SAO NHAM: Doc tai lieu khong day du
HU QUA: Stack overflow do FPU context save, kho debug
```

### Misconception 14
```
MISCONCEPTION: "Tat ca Cortex-M deu giong nhau ve interrupt"

THUC TE:
- Cortex-M0/M0+: KHONG co VTOR, khong co MPU, it priority bits, khong nested
- Cortex-M3: Co VTOR, MPU, 8-bit priority, nested interrupt
- Cortex-M4: Giong M3 + FPU
- Cortex-M7: Co ITCM/DTCM, dual-issue pipeline, advanced cache
- Khac biet ve so luong priority bits: M0=2 bits, M3/M4=3-8 bits (chip-specific)

TAI SAO NHAM: Cung la "Cortex-M" nen nghi giong nhau
HU QUA: Porting sai, code khong portable
```

### Misconception 15
```
MISCONCEPTION: "Dung sai ten ISR thi se co loi compile"

THUC TE:
- Weak symbol mechanism: neu ISR chua implement -> weak alias -> Default_Handler
- Sai ten ISR (typo) = KHONG CO LOI! Chi co warning (neu bat)
- Firmware compile va link thanh cong
- Runtime: interrupt xay ra -> vao Default_Handler -> while(1)
- Day la bug DAC BIET KHO DEBUG vi compiler khong canh bao

TAI SAO NHAM: Quen rang weak symbol boc lot loi name mismatch
HU QUA: Firmware "bi treo" bi an khi co interrupt, kho reproduce
```

---

<a name="ch12"></a>
## CHUONG 12: SO SANH KIEN TRUC CPU

### 12.1 Bang So Sanh Tong Quan

```
+------------------+----------+----------+---------+---------+
| Dac Diem         |Cortex-M  |Cortex-A  | RISC-V  |  x86   |
+------------------+----------+----------+---------+---------+
| Vector Table     | Array    | Array    | Array   | IDT     |
|                  | in Flash |in RAM/  |in RAM  | in RAM  |
|                  |          |  Flash   |         |         |
+------------------+----------+----------+---------+---------+
| Interrupt Ctrl   | NVIC     | GIC      |PLIC/    | APIC/   |
|                  |(trong CPU|(ngoai CPU)| CLIC   | PIC     |
+------------------+----------+----------+---------+---------+
| Context Save     | Hardware | Software | Software| Hardware|
|                  | Auto     |(OS/SW)  |(OS/SW) | partial |
+------------------+----------+----------+---------+---------+
| Privilege        | Thread / | EL0-EL3  |U/S/M   | Ring0-3|
|                  | Handler  |          | mode    |         |
+------------------+----------+----------+---------+---------+
| Fixed Vector     | No       | No       | No      | No      |
| Address          |(VTOR)   |(VBAR)    |(mtvec) | (IDTR)  |
+------------------+----------+----------+---------+---------+
| Nested Interrupt | Yes      | Yes      | Yes     | Yes     |
+------------------+----------+----------+---------+---------+
| NMI              | Yes      | Yes(FIQ) | NMI ext | NMI     |
+------------------+----------+----------+---------+---------+
```

### 12.2 Cortex-A vs Cortex-M (Diem Khac Quan Trong Nhat)

```
CORTEX-M                          CORTEX-A
========================          ========================
ISR "baremetal" style:            Exception handler voi MMU:
  void IRQHandler(void) {}          void do_IRQ(struct pt_regs *regs) {}

Context save: HARDWARE             Context save: SOFTWARE (OS)
  -> CPU tu push 8 registers          -> OS phai push ALL registers
  -> Nhanh, deterministic             -> Cham hon nhung flexible

No MMU (thong thuong)             MMU mandatory
  -> Physical address               -> Virtual address
  -> Vector table = physical          -> VBAR = virtual address cua VT

Stack: MSP/PSP (2 stacks)        Stack: per-mode stack (IRQ, SVC, FIQ...)
  -> Thread dung PSP                  -> IRQ mode co IRQ_SP rieng
  -> OS/Exception dung MSP            -> FIQ mode co FIQ_SP rieng

FreeRTOS / Zephyr                 Linux / RTOS phuc tap hon
```

### 12.3 RISC-V Interrupt Mechanism

```c
/* RISC-V su dung CSR (Control and Status Registers) */
/* Khac voi ARM dung Memory-Mapped registers */

/* Set interrupt handler address */
write_csr(mtvec, handler_address | 0x1);  /* 0x1 = vectored mode */

/* Enable interrupt */
set_csr(mstatus, MSTATUS_MIE);  /* Machine Interrupt Enable */
set_csr(mie, MIE_MEIE);         /* Machine External Interrupt Enable */

/* ISR trong RISC-V */
__attribute__((interrupt))
void trap_handler(void) {
    uint32_t mcause = read_csr(mcause);
    if (mcause & 0x80000000) {
        /* Interrupt */
        uint32_t irq_num = mcause & 0xFF;
        /* Xu ly IRQ */
    } else {
        /* Exception (fault) */
    }
}
```

---

<a name="ch13"></a>
## CHUONG 13: PHAN TICH STARTUP CODE THUC TE

### 13.1 Startup Code Chi Tiet

```c
/* startup_stm32f407xx.c - Phan tich tung dong */

/* Compiler lam gi? */
/* 1. Tao object code cho tung function */
/* 2. Xac dinh dia chi cua tung function (chua biet tuyet doi) */
/* 3. Ghi dia chi vao .isr_vector section (relocation entries) */

/* Linker lam gi? */
/* 1. Ghep toan bo .isr_vector tu tat ca .o files */
/* 2. Phan giai tat ca dia chi function (tuyet doi) */
/* 3. Dat .isr_vector tai dia chi dau cua Flash (theo linker script) */
/* 4. Viet gia tri cuoi vao tung entry */

extern uint32_t __StackTop;   /* Linker symbol: cuoi RAM */

/* Weak declaration - user co the override */
__attribute__((weak)) void NMI_Handler(void)       { while(1); }
__attribute__((weak)) void HardFault_Handler(void)  { while(1); }
/* ... */

/* Vector table - dat vao section dac biet */
__attribute__((section(".isr_vector"), used))
const uint32_t g_pfnVectors[] = {
    /*
     * Entry [0]: Stack Pointer
     * - Khong phai dia chi ISR
     * - La GIA TRI se nap vao MSP khi boot
     * - CPU doc 4 bytes tai VTOR[0] -> nap vao MSP
     * - &__StackTop: lay dia chi cua linker symbol
     * - (uint32_t): cast de tranh warning
     */
    (uint32_t)&__StackTop,

    /*
     * Entry [1]: Reset Handler
     * - Dia chi cua ham Reset_Handler
     * - Compiler tu dong set Thumb bit (bit 0 = 1)
     * - Vi du: Reset_Handler tai 0x08000100 -> entry = 0x08000101
     * - CPU doc entry nay -> nap vao PC
     * - PC = 0x08000101 -> CPU chay tu 0x08000100 (bo Thumb bit)
     */
    (uint32_t)Reset_Handler,

    /* Tuong tu cho NMI, HardFault, ... */
    (uint32_t)NMI_Handler,
    (uint32_t)HardFault_Handler,
    /* ... */
};

/*
 * MCU Boot Sequence Chi Tiet:
 *
 * 1. Hardware Reset xay ra (NRST pin, power-on, watchdog)
 *
 * 2. CPU Core state:
 *    - Tat ca thanh ghi = undefined (ngoai SP, PC)
 *    - CPU doc 4 bytes tai 0x00000000 (= Flash alias 0x08000000)
 *    - CPU nap gia tri do vao MSP (Stack Pointer)
 *    - MSP = 0x20020000 (cuoi 128KB RAM)
 *
 * 3. CPU doc 4 bytes tai 0x00000004
 *    - Gia tri = 0x08000101 (Reset_Handler | Thumb bit)
 *    - CPU nap vao PC
 *    - PC = 0x08000100 (bo bit 0)
 *
 * 4. CPU bat dau thuc hien Reset_Handler()
 *    - Stack da san sang (MSP da duoc set)
 *    - Co the goi function ngay
 */
```

### 13.2 Co Che Weak Symbol Sau Hon

```c
/*
 * WEAK SYMBOL - Giai thich o buoc Linker, KHONG phai Compiler
 *
 * Compiler step:
 *   - Tao symbol "NMI_Handler" trong object file voi flag WEAK
 *   - Tao symbol "Default_Handler" trong object file binh thuong
 *
 * Linker step:
 *   - Gap WEAK symbol "NMI_Handler" -> ghi nho nhung chua dung ngay
 *   - Gap STRONG symbol "NMI_Handler" tu user code -> uu tien STRONG
 *   - Gap WEAK symbol "NMI_Handler" va KHONG co STRONG -> dung alias
 */

/* Startup code: */
void Default_Handler(void) __attribute__((section(".after_vectors")));
void Default_Handler(void) { while (1); }

void NMI_Handler(void)     __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void) __attribute__((weak, alias("Default_Handler")));

/* User code (user.c): */
/* Neu co: */
void NMI_Handler(void) {
    /* STRONG symbol - ghi de weak */
    log_nmi();
    NVIC_SystemReset();
}
/* Linker dung dinh nghia nay cho NMI_Handler */

/* Neu KHONG co user NMI_Handler: */
/* Linker dung alias -> NMI_Handler tro den Default_Handler */
```

---

<a name="ch14"></a>
## CHUONG 14: THIET KE ISR CHUAN SENIOR

### 14.1 ISR Nen Ngan Den Muc Nao?

**Nguyen tac co ban:**

```
ISR chi nen lam:
1. Xac nhan nguon interrupt (doc flag)
2. Clear flag cua peripheral
3. Doc/ghi du lieu toi thieu
4. Signal den task (semaphore/queue/event)
5. Return

ISR KHONG nen lam:
1. Xu ly data phuc tap
2. String processing
3. File I/O
4. Memory allocation (malloc)
5. Blocking call bat ky loai nao
6. Goi ham voi unknown execution time
```

**So sanh hai approach:**

```c
/* APPROACH SAI - ISR Nang */
void UART1_IRQHandler(void) {
    uint8_t byte = USART1->DR;

    /* Xu ly protocol ngay trong ISR - SAI! */
    if (byte == 0xAA) {
        frame_started = 1;
        frame_index = 0;
    } else if (frame_started) {
        frame_buffer[frame_index++] = byte;
        if (frame_index == FRAME_SIZE) {
            calculate_checksum();   /* Ton thoi gian */
            parse_frame();          /* Ton thoi gian */
            update_database();      /* Ton thoi gian, co the block */
            send_response();        /* UART khac, co the block */
        }
    }
}

/* APPROACH DUNG - ISR Nhe */
void UART1_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;

    uint8_t byte = USART1->DR;  /* Doc byte */

    /* Chi gui byte vao queue */
    xQueueSendFromISR(uart_rx_queue, &byte, &xHigherPriorityTaskWoken);

    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

/* UART Task - Chay trong Thread context */
void uart_task(void *pvParameters) {
    uint8_t byte;
    while (1) {
        /* Block cho den khi co du lieu */
        xQueueReceive(uart_rx_queue, &byte, portMAX_DELAY);

        /* Xu ly protocol o day - co the lam bat cu thu gi */
        process_protocol_byte(byte);
    }
}
```

### 14.2 Cac Pattern ISR Hieu Qua

```c
/* PATTERN 1: ISR -> Semaphore -> Task */
SemaphoreHandle_t adc_done_sem;

void ADC_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    ADC1->SR &= ~ADC_SR_EOC;  /* Clear flag */

    /* ADC conversion done, signal task */
    xSemaphoreGiveFromISR(adc_done_sem, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

void adc_task(void *pvParameters) {
    while (1) {
        /* Wait for ADC done */
        xSemaphoreTake(adc_done_sem, portMAX_DELAY);

        /* Xu ly ADC data o day */
        uint16_t adc_val = ADC1->DR;
        process_adc_data(adc_val);
    }
}

/* PATTERN 2: ISR -> Ring Buffer (Lock-free cho 1 writer, 1 reader) */
#define RX_BUFFER_SIZE 256
volatile uint8_t rx_buf[RX_BUFFER_SIZE];
volatile uint16_t rx_head = 0;  /* ISR writes */
volatile uint16_t rx_tail = 0;  /* Task reads */

void UART1_IRQHandler(void) {
    uint8_t byte = USART1->DR;

    uint16_t next_head = (rx_head + 1) % RX_BUFFER_SIZE;
    if (next_head != rx_tail) {  /* Buffer chua day */
        rx_buf[rx_head] = byte;
        rx_head = next_head;     /* Atomic write (single write) */
    }
    /* Neu day: drop byte (co the set error flag) */
}

/* Task doc */
uint8_t uart_read_byte(uint8_t *byte) {
    if (rx_head == rx_tail) return 0;  /* Khong co du lieu */
    *byte = rx_buf[rx_tail];
    rx_tail = (rx_tail + 1) % RX_BUFFER_SIZE;
    return 1;
}

/* PATTERN 3: DMA + Interrupt (Zero-copy) */
void SPI_DMA_IRQHandler(void) {
    /* DMA transfer hoan thanh */
    DMA1->IFCR = DMA_IFCR_CTCIF3;  /* Clear flag */

    /* Buffer da san sang, chi swap pointer */
    uint8_t *ready_buf = dma_buffer_current;
    dma_buffer_current = dma_buffer_next;

    /* Re-arm DMA voi buffer moi */
    DMA1_Channel3->CMAR = (uint32_t)dma_buffer_current;
    DMA1_Channel3->CCR |= DMA_CCR_EN;

    /* Signal task de xu ly ready_buf */
    xQueueSendFromISR(dma_queue, &ready_buf, &xHigherPriorityTaskWoken);
}
```

### 14.3 Critical Section Va Memory Ordering

```c
/* Critical section tren bare-metal */
void update_shared_data_baremetal(void) {
    uint32_t saved = __get_PRIMASK();
    __disable_irq();              /* Bat dau critical section */

    /* Thao tac voi du lieu chia se */
    shared_counter++;

    __set_PRIMASK(saved);         /* Ket thuc critical section */
}

/* Critical section tren FreeRTOS - uu tien */
void update_shared_data_freertos(void) {
    taskENTER_CRITICAL();         /* BASEPRI = configMAX_SYSCALL, khong disable NMI */

    shared_counter++;

    taskEXIT_CRITICAL();
}

/* Memory Barrier - can thiet khi chia se bien voi ISR */
volatile uint8_t data_ready = 0;
uint32_t data_value = 0;

void sensor_isr(void) {
    data_value = read_sensor();
    __DMB();                      /* Dam bao data_value duoc ghi truoc data_ready */
    data_ready = 1;
}

void main_loop(void) {
    if (data_ready) {
        __DMB();                  /* Dam bao doc data_ready truoc data_value */
        process(data_value);
        data_ready = 0;
    }
}
```

---

<a name="ch15"></a>
## CHUONG 15: PERFORMANCE VA REAL-TIME

### 15.1 Cac Khai Niem Thoi Gian

```
INTERRUPT LATENCY:
  Thoi gian tu khi event xay ra den khi ISR bat dau thuc hien
  = Event -> IRQ signal -> NVIC accept -> CPU context save -> ISR first instruction
  Tren Cortex-M4: ~12-16 cycles (khoang 100-200ns tai 168MHz)

ISR EXECUTION TIME:
  Thoi gian ISR chay tu dau den cuoi
  Can do bang logic analyzer hoac cycle counter

INTERRUPT JITTER:
  Su bien dong cua latency giua cac lan interrupt
  Do: cache miss, pipeline flush, instruction latency
  Gia tri tuyet doi va do bien dong ca hai quan trong

RESPONSE TIME:
  Thoi gian toan bo tu event den khi system phan hoi
  = Latency + ISR time + Task wake-up + Task execution

WCET (Worst-Case Execution Time):
  Thoi gian lau nhat ISR/Task co the chay
  Quan trong cho real-time analysis
  Phai do ben canh hay debug mode (opt off)
```

### 15.2 Phan Tich ISR Architecture Thuc Te

```
He thong: UART 115200 baud + Timer 1kHz + ADC 20kHz

UART 115200 baud:
  Chu ky byte: 1/115200 * 10 bits = 86.8 microseconds
  ISR phai hoan thanh truoc 86.8us hoac phai co buffer DU LON

Timer 1kHz (1ms):
  ISR chay moi 1ms = 1000 lan/giay
  Neu ISR mat 100us = 10% CPU time chi cho ISR nay

ADC 20kHz (50us):
  ISR chay moi 50us = 20000 lan/giay
  Neu ISR mat 10us = 20% CPU time

Tong CPU load chi tu ISR (kem nhat):
  UART: 86.8us period, ISR ~5us = 5.8%
  Timer: 1000us period, ISR ~10us = 1%
  ADC: 50us period, ISR ~10us = 20%
  Tong ISR load: ~27% CPU

Van de neu ISR qua nang:
  - ADC ISR mat 30us thay vi 10us
  - 30/50 = 60% CPU -> system bi qua tai
  - Timer ISR bi delay -> jitter trong timing
  - UART co the mat byte vi khong xu ly kip

GIAI PHAP:
  - ADC: Dung DMA thay vi ISR-per-sample
  - UART: Ring buffer + DMA
  - Timer: Chi lam minimum trong ISR, defer sang task
```

### 15.3 Priority Inversion Va Interrupt Storm

```
PRIORITY INVERSION:
  1. Low-priority task giu mutex
  2. High-priority interrupt muon tai nguyen do
  3. High-priority bi block boi low-priority
  Giai phap: Priority inheritance mutex (FreeRTOS co)

INTERRUPT STORM:
  Xay ra khi ISR KHONG clear flag cua peripheral
  -> Peripheral lien tuc assert IRQ
  -> CPU bi cuon vao ISR vo han
  -> System bi "treo" vi main loop khong chay duoc

  Debug: Logic analyzer hoac oscilloscope tren IRQ line
  Trieu chung: CPU load 100%, moi thu bi dong bang

  Code fix:
  void TIM2_IRQHandler(void) {
      TIM2->SR &= ~TIM_SR_UIF;  /* PHAI co dong nay - clear flag */
      /* ... */
  }

INTERRUPT STARVATION:
  ISR co priority cao chay qua nhieu/qua lau
  -> Low-priority task khong bao gio duoc chay
  -> Watchdog timeout (neu co)
  Fix: Giam execution time cua high-priority ISR
```

---

<a name="ch16"></a>
## CHUONG 16: 10 BAI TAP TANG DAN DO KHO

### Level 1: Doc Vector Table

```
Problem:
  Ban co firmware da build cho STM32F407.
  Su dung GDB de doc va giai thich noi dung vector table.

Context:
  - Firmware tai 0x08000000
  - He thong dung TIM2 va UART1

Constraints:
  - Chi duoc dung GDB commands
  - Khong duoc nhin source code

Expected Behavior:
  - Liet ke 20 entries dau cua vector table
  - Giai thich y nghia tung entry
  - Xac dinh dia chi cua TIM2_IRQHandler va UART1_IRQHandler
  - Xac dinh Initial Stack Pointer

What You Should Investigate:
  - x/20xw 0x08000000
  - info symbol <address>
  - arm-none-eabi-nm firmware.elf
```

### Level 2: Viet ISR Dau Tien

```
Problem:
  Implement TIM6 interrupt de toggle LED (PA5) moi 500ms.
  Khong duoc dung HAL_TIM_IRQHandler.

Context:
  - STM32F407 Discovery board
  - TIM6: Basic timer, chi co Update interrupt
  - LED xanh o PA5
  - Clock: 168MHz

Constraints:
  - Viết ISR tu zero, khong dung HAL wrapper
  - ISR phai clear flag correctly
  - LED toggle phai dung timing

What You Should Investigate:
  - TIM6 clock source va prescaler calculation
  - TIM6->DIER bit UIE
  - NVIC_EnableIRQ(TIM6_DAC_IRQn)
  - TIM6->SR bit UIF clear mechanism
  - GPIOA ODR toggle
```

### Level 3: Debug Default_Handler

```
Problem:
  Firmware chay duoc nhung khi connect debugger: CPU dang trong vong lap tai
  Default_Handler. Khong ro interrupt nao gay ra.

Context:
  - STM32F4, FreeRTOS
  - He thong co SPI, UART, I2C, TIM
  - Firmware chay khoang 30 giay roi "treo"

Constraints:
  - Khong co source code cua Default_Handler (binary only)
  - Chi co GDB va binary (.elf)

What You Should Investigate:
  - Doc IPSR de biet exception number dang active
  - Tinh toan: exception number -> IRQ name
  - Kiem tra NVIC ISER vs vector table
  - Tim doan code gay ra interrupt
```

### Level 4: Relocate Vector Table

```
Problem:
  Implement chuc nang: Sau khi boot, copy vector table tu Flash vao RAM
  va doi VTOR sang RAM. Sau do co the thay doi ISR handler runtime.

Context:
  - Cortex-M4, STM32F4
  - RAM: 128KB tai 0x20000000
  - Vector table: 98 entries (16 core + 82 IRQ cua STM32F4)
  - Can thay the SysTick_Handler runtime

Constraints:
  - Alignment requirement cua VTOR
  - Khong duoc break any existing interrupt
  - Phai verify sau khi relocate

What You Should Investigate:
  - VTOR alignment requirement
  - memcpy vector table
  - SCB->VTOR = new_address
  - Kiem tra bang GDB sau khi relocate
```

### Level 5: Debug HardFault

```
Problem:
  Firmware bi HardFault sau khoang 5 giay chay. Bug khong reproducible ngay
  (xay ra sau thoi gian chay nhat dinh).

Context:
  - STM32F4, FreeRTOS
  - 4 tasks: UART, CAN, ADC, MainControl
  - HardFault xay ra ngau nhien

Constraints:
  - Khong the dung debugger (firmware chay tren device thuc)
  - Chi co log qua UART

What You Should Investigate:
  - Implement HardFault handler de log: stacked PC, CFSR, HFSR, BFAR
  - Luu log vao NvM truoc khi reset
  - Phan tich PC: tim doan code gay fault
  - Kiem tra stack usage (stack watermark FreeRTOS)
```

### Level 6: Bootloader + Application

```
Problem:
  Implement bootloader don gian tai 0x08000000 va application tai 0x08010000.
  Bootloader kiem tra button, neu nhan = o lai BL mode, neu khong = jump App.
  App phai nhan duoc tat ca interrupt sau khi duoc jump vao tu BL.

Context:
  - STM32F407
  - Button: PC13
  - BL size: 64KB (0x08000000 - 0x0800FFFF)
  - App size: 960KB (0x08010000 - 0x080FFFFF)

Constraints:
  - App linker script phai thay doi
  - VTOR phai duoc relocate
  - MSP phai duoc cap nhat
  - Tat ca peripheral state phai sach truoc khi jump

What You Should Investigate:
  - BL linker script va App linker script
  - bootloader_jump_to_app() implementation
  - App phai co vector table dung dia chi
  - Test: App interrupt co hoat dong sau jump?
```

### Level 7: Interrupt + DMA

```
Problem:
  Doc 1000 mau ADC tai 100kHz su dung DMA. Khi buffer day, ISR phai
  xu ly data va kich hoat DMA buffer tiep theo (ping-pong buffer).
  Khong duoc mat mau nao.

Context:
  - STM32F4, ADC1, DMA2 Stream0
  - Sample rate: 100kHz
  - Buffer size: 1000 samples per buffer
  - 2 buffers (ping-pong)
  - Processing time < 5ms

Constraints:
  - DMA transfer complete interrupt
  - Double buffering mandatory
  - ISR time < 10us
  - Khong the dung blocking operation trong ISR

What You Should Investigate:
  - DMA circular mode vs normal mode
  - DMA half-transfer interrupt + full-transfer interrupt
  - Ping-pong buffer swap trong ISR
  - Memory barrier khi swap buffer pointer
```

### Level 8: Interrupt + RTOS

```
Problem:
  He thong co UART RX interrupt va task xu ly protocol. Khi nhan 0xAA 0xBB 0xCC 0xDD,
  task phai wakeup va xu ly trong 1ms. Hien tai co do tre 50ms.
  Tim nguyen nhan va fix.

Context:
  - STM32F4, FreeRTOS
  - UART 115200 baud
  - Task priority: 5 (trung binh)
  - Co 3 task khac priority: 8, 6, 3

Constraints:
  - Khong duoc thay doi protocol
  - Response time phai < 5ms
  - Khong duoc increase CPU load qua 50%

What You Should Investigate:
  - ISR -> Queue -> Task wakeup flow
  - Task priority vs other tasks
  - portYIELD_FROM_ISR usage
  - FreeRTOS trace (Segger SystemView)
  - Stack size cua task xu ly
```

### Level 9: Thiet Ke Interrupt Architecture

```
Problem:
  Thiet ke interrupt system cho ECU xe dien:
  - CAN Bus: 1Mbit/s, can xu ly trong 100us
  - UART Debug: 921600 baud
  - ADC Battery: 10kHz, 12 kenh
  - PWM Motor Control: 20kHz PWM, ISR update duty cycle
  - Safety Monitor: phai co response < 50us bat ky luc nao
  - FreeRTOS: 5 tasks tu priority 1-5

Context:
  - STM32H7 (480MHz)
  - Cac system clock: APB1=120MHz, APB2=240MHz
  - 16-bit priority grouping

Constraints:
  - Safety Monitor khong duoc bi delay qua 50us
  - CAN latency < 100us
  - Motor PWM update phai chinh xac den 1us
  - Tong CPU load < 60% (de lai margin)

What You Should Investigate:
  - Priority assignment cho tung IRQ
  - configMAX_SYSCALL_INTERRUPT_PRIORITY setting
  - CPU load budget analysis
  - DMA usage cho ADC va UART
  - Safety interrupt isolation
```

### Level 10: Debug Production Bug

```
Problem:
  Firmware EV (Electric Vehicle) bi bao cao: Sau 2-3 gio hoat dong,
  dieu khien motor bi mat response trong ~100ms, sau do phuc hoi.
  Bug xay ra ngau nhien, kho reproduce. Khach hang report crash.
  Firmware da ship, khong co debugger. Chi co black box log.

Context:
  - STM32H7, FreeRTOS
  - Motor control: ISR moi 50us (20kHz)
  - CAN Bus: Nhan lenh motor
  - Safety Monitor: Giam sat tat ca
  - Temperature sensor: Doc moi 10ms

Constraints:
  - Khong co debugger tren target
  - Log chi 4KB vong trong RAM (CircularLog)
  - Phai fix trong 48h
  - Khong duoc lam slow down motor control (safety critical)

What You Should Investigate:
  - Tich hop runtime stack watermark monitoring
  - Log trang thai interrupt truoc khi "mat response"
  - Phan tich xem co interrupt starvation
  - Kiem tra priority inversion co xay ra khong
  - Kiem tra memory leak qua 2-3 gio
  - Kiem tra watchdog co duoc kick trong ISR khong
```

---

<a name="ch17"></a>
## CHUONG 17: SENIOR MINDSET - UNDERSTANDING VS MEMORIZATION

### 17.1 10 Cap Junior Thinking vs Senior Thinking

**Cap 1: Ve VTOR**
```
JUNIOR:
"VTOR la thanh ghi chua dia chi vector table."

SENIOR:
"VTOR cho phep he thong thay doi base address cua exception vector table.
Dieu nay quan trong trong bootloader/multi-image architecture,
nhung relocation con lien quan den memory mapping (alignment 512-byte boundary),
startup sequence (khi nao set VTOR - truoc hay sau enable interrupt),
interrupt state (phai disable truoc khi relocate),
va implications voi NVIC pending state (co the can clear pending truoc khi relocate)."
```

**Cap 2: Ve ISR**
```
JUNIOR:
"ISR la function duoc goi khi interrupt xay ra."

SENIOR:
"ISR la exception handler chay o privilege Handler mode, duoc trigger boi hardware
exception mechanism qua vector table lookup. ISR khac function binh thuong o:
execution context (Handler vs Thread mode), stack su dung (MSP vs PSP),
register luu tru (auto-stacking), return mechanism (EXC_RETURN vs binh thuong),
va nhung gi co the goi (RTOS FromISR API, khong blocking, khong malloc).
Thiet ke ISR dung = ISR ngan + defer work = thong luong cao + latency thap."
```

**Cap 3: Ve Enable Interrupt**
```
JUNIOR:
"Toi enable NVIC la xong."

SENIOR:
"Enable interrupt la mot chuoi dieu kien: peripheral clock, peripheral event config,
peripheral interrupt enable, NVIC enable, priority config, global interrupt enable,
va vector table entry hop le. Miss bat ky dieu kien nao = interrupt khong chay.
Debug methodology: check tung dieu kien theo thu tu, khong guess."
```

**Cap 4: Ve HardFault**
```
JUNIOR:
"HardFault la loi kho hieu, thuong khoi dong lai."

SENIOR:
"HardFault la tin hieu diagnostics cua CPU. No cho biet: loai fault (CFSR),
dia chi loi (BFAR/MMFAR), lenh gay fault (stacked PC), va stack state luc do.
Implement HardFault handler de log tat ca thong tin nay truoc khi reset
la dieu kien bat buoc cho bat ky production firmware nao."
```

**Cap 5: Ve Priority**
```
JUNIOR:
"Priority cao thi so priority lon."

SENIOR:
"Priority trong ARM: so NHAT = cao nhat. FreeRTOS task priority: so LON = cao hon.
IRQ priority va task priority la 2 he thong rieng biet, dung theo nghia nguoc nhau.
configMAX_SYSCALL_INTERRUPT_PRIORITY la nguong bao ve RTOS critical sections -
IRQ co priority so NHAT hon nguong nay KHONG the goi RTOS API.
Priority grouping (PRIGROUP) quyet dinh so bit preemption vs sub-priority."
```

**Cap 6: Ve Stack**
```
JUNIOR:
"Stack overflow la bi het RAM, them RAM vao la xong."

SENIOR:
"Stack overflow tren embedded co nhieu dang: ISR nested qua sau,
recursion trong task, local variable lon, function call chain sau,
float context save (26 regs thay vi 8). Tren Cortex-M, stack overflow
khong co hardware protection (tru MPU). Nen dung FreeRTOS stack watermark
monitoring va MPU stack guard. Stack size phai tinh cho worst-case,
bao gom nested interrupt depth."
```

**Cap 7: Ve DMA va Interrupt**
```
JUNIOR:
"DMA tu chay, interrupt bao hieu hoan thanh, the la xong."

SENIOR:
"DMA + interrupt la thiet ke system quan trong: DMA giam CPU load, nhung
ISR van can xu ly dung luc (clear flag, re-arm DMA, swap buffer, signal task).
Ping-pong buffer la pattern pho bien cho continuous streaming. Memory barrier
(DMB) can thiet khi DMA va CPU truy cap cung buffer. Cache coherency (Cortex-M7
co cache) la nguon loi tinh vi neu khong duoc quan ly."
```

**Cap 8: Ve Bootloader**
```
JUNIOR:
"Bootloader jump vao Reset_Handler cua app la xong."

SENIOR:
"Bootloader jump vao app yeu cau: tat peripheral (khong de lai state),
disable tat ca NVIC + clear pending, tat SysTick, cap nhat MSP tu app stack pointer,
relocate VTOR sang app vector table, validate app (CRC, magic number),
va jump vao Reset_Handler. Thieu bat ky buoc nao co the dan den app
chay duoc nhung crash sau khi co interrupt dau tien."
```

**Cap 9: Ve Real-Time**
```
JUNIOR:
"He thong real-time nghia la phai nhanh."

SENIOR:
"Real-time = deterministic, khong nhat thiet la nhanh. He thong real-time
can: WCET biet truoc, priority assignment dung, interrupt latency xac dinh,
schedulability analysis (utilization < 69% cho RMS), jitter nho cho critical tasks.
ISR architecture anh huong den tat ca cac chi tieu nay. Mot ISR nang co the
pha vo ca he thong real-time du CPU co 'sat' hon."
```

**Cap 10: Ve Debug**
```
JUNIOR:
"Bug lien quan den interrupt kho debug, cu restart la no mat."

SENIOR:
"Bug interrupt co phuong phap debug he thong: IPSR cho biet exception dang active,
CFSR/HFSR/BFAR cho biet loai fault, stacked PC cho biet lenh gay fault,
logic analyzer cho thay IRQ timing, FreeRTOS trace cho thay context switch.
Bug restart mat co nghia la: race condition khong reproducible (khong co volatile),
bug phu thuoc timing (priority sai, jitter), hoac bug phu thuoc gia tri chua khoi tao."
```

---

<a name="ch18"></a>
## CHUONG 18: MASTER DEBUG CHECKLIST

### 18.1 Checklist Debug Interrupt - 20 Buoc

```
PHASE 1: SETUP VERIFICATION (truoc khi code chay)
  [ ] 1. Peripheral clock enable?
  [ ] 2. GPIO/Pin config (alternate function)?
  [ ] 3. Peripheral cau hinh dung?
  [ ] 4. Peripheral interrupt enable (DIER, CR1, ...)?
  [ ] 5. NVIC enable (NVIC_EnableIRQ)?
  [ ] 6. NVIC priority set?
  [ ] 7. ISR ten chinh xac (dung cap chu hoa)?
  [ ] 8. ISR chua trong .c file duoc include trong build?
  [ ] 9. Global interrupt enable (__enable_irq)?
  [ ] 10. Vector table hop le tai dung dia chi?

PHASE 2: RUNTIME VERIFICATION (khi dang chay)
  [ ] 11. PRIMASK = 0 (khong bi mask)?
  [ ] 12. BASEPRI khong mask priority cua IRQ?
  [ ] 13. Peripheral flag duoc set khi event xay ra?
  [ ] 14. ISR clear flag sau khi xu ly?
  [ ] 15. Khong co priority inversion?

PHASE 3: FAULT ANALYSIS (khi co loi)
  [ ] 16. IPSR: Exception nao dang active?
  [ ] 17. CFSR: Loai fault gi?
  [ ] 18. Stacked PC: Lenh nao gay fault?
  [ ] 19. Stack co du khong (SP vs stack_bottom)?
  [ ] 20. VTOR tro dung vector table?
```

### 18.2 Quick Reference Commands

```gdb
# Xem vector table
x/32xw 0x08000000

# Xem VTOR
x/xw 0xE000ED08

# Xem CFSR (fault status)
x/xw 0xE000ED28

# Xem HFSR (hardfault status)
x/xw 0xE000ED2C

# Xem BFAR (bus fault address)
x/xw 0xE000ED34

# Xem IPSR (current exception)
info registers xpsr

# Xem stacked PC khi fault
info registers sp
# x/8xw <sp_value> -> element [6] la stacked PC

# Tim symbol tai dia chi
info symbol 0x08001234

# Xem NVIC enable registers
x/8xw 0xE000E100

# Xem NVIC priority registers
x/16xw 0xE000E400
```

### 18.3 Mental Model Tong The (ASCII Diagram)

```
+===========================================================================+
|                    INTERRUPT SYSTEM OVERVIEW                              |
+===========================================================================+
|                                                                           |
|  HARDWARE EVENT                                                           |
|  (Timer, UART, GPIO, ADC...)                                              |
|         |                                                                 |
|         v IRQ Signal (Wire)                                               |
|  +------+------+                                                          |
|  |    NVIC     |  Hardware block trong CPU                                |
|  | - Enable    |  Quan ly: enable/disable, priority                       |
|  | - Priority  |  pending/active state                                    |
|  | - Pending   |  Mask: PRIMASK, BASEPRI, FAULTMASK                      |
|  | - Active    |                                                          |
|  +------+------+                                                          |
|         |                                                                 |
|         v "exception_number" va nIRQ signal                               |
|  +------+------+                                                          |
|  |  CPU CORE   |  Hoan thanh lenh hien tai                                |
|  |             |  Auto-push context (8 regs)                              |
|  |  Exception  |  Tinh vector address:                                    |
|  |  Mechanism  |  VTOR + exception_number*4                              |
|  +------+------+                                                          |
|         |                                                                 |
|         v Vector address                                                  |
|  +------+------+                                                          |
|  | VECTOR TABLE|  Mang dia chi trong Flash/RAM                            |
|  | (Flash)     |  [0] Stack Pointer value                                 |
|  |             |  [1] Reset_Handler addr                                  |
|  |             |  ...                                                     |
|  |             |  [n] IRQn_Handler addr                                   |
|  +------+------+                                                          |
|         |                                                                 |
|         v ISR address                                                     |
|  +------+------+                                                          |
|  |     ISR     |  Chay o Handler mode                                     |
|  |             |  Clear peripheral flag                                   |
|  |             |  Xu ly su kien hoac signal task                          |
|  |             |  Return (EXC_RETURN)                                     |
|  +------+------+                                                          |
|         |                                                                 |
|         v Auto-pop context                                                |
|  MAIN CODE TIEP TUC (hoac RTOS task sau context switch)                   |
|                                                                           |
+===========================================================================+
```

---

## TAI LIEU THAM KHAO

- ARM Cortex-M4 Technical Reference Manual (DDI0439C)
- ARMv7-M Architecture Reference Manual (DDI0403E)
- ARM Cortex-M for Beginners (Joseph Yiu) - White Paper
- FreeRTOS Reference Manual - https://www.freertos.org/Documentation/
- STM32F4 Reference Manual (RM0090)
- Embedded Systems: Real-Time Operating Systems for ARM Cortex-M (Jonathan Valvano)
- MISRA-C:2012 Guidelines for the use of the C language
- AN4838: Managing memory protection unit in STM32 MCUs

---

*Tai lieu nay duoc tao cho viec tu hoc va tham khao ky thuat. Tat ca code example chi mang tinh minh hoa - kiem tra ky truoc khi su dung trong production.*
