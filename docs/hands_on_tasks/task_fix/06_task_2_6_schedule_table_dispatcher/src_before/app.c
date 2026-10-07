/**
 * AS - the open source Automotive Software on https://github.com/parai
 *
 * Copyright (C) 2015  AS <parai@foxmail.com>
 *
 * This source code is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License version 2 as published by the
 * Free Software Foundation; See <http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt>.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 * for more details.
 */
/* ============================ [ INCLUDES  ] ====================================================== */
#include "Os.h"
#ifdef USE_SG
#include "Sg.h"
#endif
#ifdef USE_LCD
#include "Lcd.h"
#endif
#ifdef USE_XCP
#include "Xcp.h"
#endif
#ifdef USE_FTP
#include "ftpd.h"
#endif
#if( defined(USE_PTHREAD) || defined(RT_USING_PTHREADS) || defined(__LINUX__) || defined(__WINDOWS__))
#include "pthread.h"
#include <unistd.h>
#endif
#ifdef USE_TRACE
#include "trace.h"
#endif

#ifdef USE_SD
#include "SD.h"
#endif
// #define AS_PERF_ENABLED
#include "asdebug.h"
/* ============================ [ MACROS    ] ====================================================== */
#define AS_LOG_OS 0
/* ============================ [ TYPES     ] ====================================================== */
/* ============================ [ DECLARES  ] ====================================================== */
#ifdef USE_CPLUSPLUS
extern void cppapp_start(void);
#endif
/* ============================ [ DATAS     ] ====================================================== */
#ifdef USE_XCP
#if defined(__LINUX__) || defined(__WINDOWS__)
uint8_t xcpSimMTAMemory[1024];
#else
uint8_t xcpSimMTAMemory[32];
#endif
#endif

//#define PROTOTHREAD_TEST
#if defined(USE_PROTOTHREAD) && (defined(__LINUX__) || defined(__WINDOWS__))
#if defined(PROTOTHREAD_TEST)
extern struct process protoDemoProductProc;
extern struct process protoDemoConsumerProc;
#endif
#if defined(USE_UIP)
extern struct process protoUIPMain;
#endif
struct process * const autostart_processes[] = {
#if defined(PROTOTHREAD_TEST)
	&protoDemoProductProc,
	&protoDemoConsumerProc,
#endif
#if defined(USE_UIP)
	&protoUIPMain,
#endif
	NULL
};
#endif
/* ============================ [ LOCALS    ] ====================================================== */

/* ============================ [ FUNCTIONS ] ====================================================== */
void StartupHook(void)
{
	uint32 endian = 0xdeadbeef;
	printf(" start application BUILD @ %s %s\n",__DATE__,__TIME__);

	if(0xde == (*(uint8_t*)&endian))
	{
		printf(" cpu is big endian\n");
	}
	else
	{
		printf(" cpu is little endian\n");
	}

#ifdef USE_LCD
	Lcd_Init();
#endif
#ifdef USE_SG
	Sg_Init();
#endif

#ifdef USE_LVGL
    /*Initialize LittlevGL*/
	extern void lv_init(void);
	extern void lv_hw_dsp_init(void);
	extern void lv_hw_mouse_init(void);
    lv_init();
    lv_hw_dsp_init();
    lv_hw_mouse_init();
#if USE_LV_BENCHMARK
    extern void benchmark_create(void);
    benchmark_create();
#endif
#if USE_LV_DEMO
    extern void demo_create(void);
    demo_create();
#endif
#if USE_LV_SYSMON
    extern void sysmon_create(void);
    sysmon_create();
#endif
#if USE_LV_TERMINAL
    extern void terminal_create(void);
    terminal_create();
#endif
#if USE_LV_TPCAL
    extern void tpcal_create(void);
    tpcal_create();
#endif
#endif

#ifdef USE_XCP
	printf(" XCP MTA memory address %p\n",xcpSimMTAMemory);
	for(int i=0;i<sizeof(xcpSimMTAMemory);i++)
	{
		xcpSimMTAMemory[i] = i;
	}
#endif

#ifdef USE_TRACE
	Trace_Init();
#endif
}

void SchM_StartupHook(void)
{
	OsSetRelAlarm(AlarmApp, MS2TICKS(10), MS2TICKS(5));
}

#ifdef USE_LVGL
#if( (OS_PTHREAD_NUM > 0) || defined(RT_USING_PTHREADS) || defined(__LINUX__) || defined(__WINDOWS__))
extern void lv_task_handler(void);
void* lv_task_thread(void* args)
{
	while(TRUE)
	{
		lv_task_handler();
#if defined(RT_USING_PTHREADS)
		rt_thread_delay(1);
#else
		usleep(1000);
#endif
	}
	return NULL;
}
#endif
#endif

#include "Com.h"
#include "Com_PbCfg.h"

void __weak TaskAppHook(void) { }
TASK(TaskApp)
{
	OS_TASK_BEGIN();
	ASLOG(OFF,("TaskApp is running\n"));

	TaskAppHook();
#ifdef USE_SG
	ASPERF_MEASURE_START();
	Sg_ManagerTask();
	ASPERF_MEASURE_STOP("Sg_ManagerTask");
#endif
#ifdef USE_LVGL
#if( (OS_PTHREAD_NUM > 0) || defined(RT_USING_PTHREADS) || defined(__LINUX__) || defined(__WINDOWS__))
{
	static int flag = 0;
	static pthread_t lvThread;
	if(0 == flag)
	{
		(void)pthread_create(&lvThread, NULL, lv_task_thread, NULL);
		flag = 1;
	}
}

	extern void lv_tick_inc(uint32_t inc);
	lv_tick_inc(10);
#endif
#endif

#ifndef USE_STDRT
#ifdef USE_LWIP
	OsActivateTask(TaskLwip);
#endif
#endif

#ifdef USE_FTP
	{
		static int flag = 0;
		if(0 == flag)
		{
			if(0u == ftpd_init())
			{
				flag = 1;
			}
			else
			{
				/* try init ftpd next time */
			}
		}
	}
#endif

#ifdef USE_CPLUSPLUS
{
	static int flag = 0;
	if(0 == flag) {
		cppapp_start();
		flag = 1;
	}
}
#endif

#ifdef USE_SD
{
	static int flag = 0;
	if(0 == flag) {
		Sd_LocalIpAddrAssignmentChg(SOADIF_ID_SD_MULTICAST_TX,TCPIP_IPADDR_STATE_ASSIGNED);
		Sd_ClientServiceSetState(0, SD_CLIENT_SERVICE_REQUESTED);
		Sd_ServerServiceSetState(0, SD_SERVER_SERVICE_AVAILABLE);
		flag = 1;
	}
}
#endif
	OsTerminateTask(TaskApp);

	OS_TASK_END();
}

ALARM(AlarmApp)
{
	OsActivateTask(TaskApp);
}

/* ========================================================================= */
/* TASK 2.3: Basic Task & Alarm Periodic 50ms + Conformance Test (BCC1/BCC2) */
/* ========================================================================= */
static uint32_t task_instance_counter = 0;

TASK(Task_Periodic_50ms)
{
	task_instance_counter++;
	printf("   --> [Task_Periodic_50ms] Running instance #%u\n", (unsigned int)task_instance_counter);
	(void)TerminateTask();
}

void Simulate_ISR_CanRx_Cat2(uint32_t can_id);

TASK(Task_QueueTester)
{
	StatusType ret;

	printf("\n=================================================================\n");
	printf("[TASK 2.3] TESTING OSEK CONFORMANCE CLASS (BCC1 vs BCC2)\n");
	printf("=================================================================\n");

	/* Lần 1: Kích hoạt Task_Periodic_50ms đưa vào trạng thái READY */
	printf("[Tester] Activating Task_Periodic_50ms (Call 1)...\n");
	ret = ActivateTask(Task_Periodic_50ms);
	printf("         --> Result: ret = %s (Task moved to READY state)\n", (ret == E_OK) ? "E_OK" : "ERROR");

	/* Lần 2: Task đang READY (chưa kịp chạy vì Priority 2 < 5), kích hoạt tiếp */
	printf("[Tester] Activating Task_Periodic_50ms (Call 2 - Burst activation)...\n");
	ret = ActivateTask(Task_Periodic_50ms);
	if (ret == E_OS_LIMIT)
	{
		printf("         --> Result: E_OS_LIMIT! (BCC1 Verified: Activation Limit = 1 Reached!)\n");
	}
	else if (ret == E_OK)
	{
		printf("         --> Result: E_OK! (BCC2 Verified: Activation Queued Successfully!)\n");
	}
	else
	{
		printf("         --> Result: Unexpected error code %u\n", (unsigned int)ret);
	}

	printf("=================================================================\n\n");

	/* ================================================================= */
	/* [TASK 2.4] TESTING EXTENDED TASK & ISR CAT 2 PREEMPTION           */
	/* ================================================================= */
	Simulate_ISR_CanRx_Cat2(0x180);

	(void)TerminateTask();
}

/* ========================================================================= */
/* TASK 2.4: Extended Task Event-Driven & ISR Cat 1 vs Cat 2 Verification    */
/* ========================================================================= */
static volatile uint32_t rx_can_message_id = 0;

/* Extended Task hướng sự kiện với chu trình 4 bước chuẩn mực */
TASK(Task_CanRxHandler)
{
	EventMaskType active_events;
	printf("[Task_CanRxHandler] Initialized (Priority 10). Entering WaitEvent()...\n");

	while (1)
	{
		/* BƯỚC 1: Ngủ giải phóng 100% CPU, chuyển sang trạng thái WAITING */
		(void)WaitEvent(Event_CanFrameRx | Event_CanError);

		/* BƯỚC 2: Thức dậy khi nhận sự kiện, lấy mask sự kiện đã được kích hoạt */
		(void)GetEvent(Task_CanRxHandler, &active_events);

		/* BƯỚC 3: XÓA CỜ SỰ KIỆN — BẮT BUỘC ĐỂ TRÁNH 100% CPU LOCKUP */
		(void)ClearEvent(active_events);

		/* BƯỚC 4: Xử lý logic nghiệp vụ tương ứng với sự kiện */
		if (active_events & Event_CanFrameRx)
		{
			printf("   --> [Task_CanRxHandler] WAKEUP from WAITING state!\n");
			printf("   --> [Task_CanRxHandler] CAN Rx Frame processed: ID = 0x%X\n", (unsigned int)rx_can_message_id);
		}
		if (active_events & Event_CanError)
		{
			printf("   --> [Task_CanRxHandler] CAN Bus Error handled!\n");
		}
	}
	(void)TerminateTask();
}

/* Hàm kiểm chứng mô phỏng hành vi ISR Cat 2 (Được OS quản lý, gọi SetEvent) */
void Simulate_ISR_CanRx_Cat2(uint32_t can_id)
{
	printf("\n[ISR Cat 2 Simulation] CAN Rx Interrupt Triggered! ID = 0x%X\n", (unsigned int)can_id);
	rx_can_message_id = can_id;
	
	/* Kích hoạt Event đánh thức Task_CanRxHandler */
	printf("[ISR Cat 2 Simulation] Calling SetEvent(Task_CanRxHandler, Event_CanFrameRx)...\n");
	(void)SetEvent(Task_CanRxHandler, Event_CanFrameRx);
	printf("[ISR Cat 2 Simulation] Interrupt Handler completed.\n\n");
}

/* ========================================================================= */
/* TASK 2.5: Immediate Priority Ceiling Protocol (IPCP) & Zero Context Switch */
/* ========================================================================= */
TASK(Task_Low)
{
	printf("\n=================================================================\n");
	printf("[TASK 2.5] TESTING IMMEDIATE PRIORITY CEILING PROTOCOL (IPCP)\n");
	printf("=================================================================\n");
	printf("[TIMELINE 1] Task_Low starts executing (Static Priority = 1)...\n");

	/* GỌI GETRESOURCE: QUAN SÁT KHÔNG CÓ CONTEXT SWITCH */
	(void)GetResource(Res_SharedBuffer);
	printf("[TIMELINE 2] Task_Low GOT Resource! ActualPriority elevated to 3 (NO Context Switch).\n");

	/* KÍCH HOẠT TASK HIGH VÀ TASK MID */
	printf("[TIMELINE 3] Activating Task_High (Prio 3) & Task_Mid (Prio 2)...\n");
	(void)ActivateTask(Task_High);
	(void)ActivateTask(Task_Mid);
	printf("[TIMELINE 4] Task_Low STILL RUNNING! Neither Mid nor High could preempt Task_Low!\n");

	/* TRẢ RESOURCE: CONTEXT SWITCH XẢY RA TẠI ĐÂY */
	printf("[TIMELINE 5] Task_Low calling ReleaseResource(Res_SharedBuffer)...\n");
	(void)ReleaseResource(Res_SharedBuffer);
	/* ActualPriority hạ về 1 -> Kernel Sched_Schedule() -> Context Switch sang Task_High! */

	printf("[TIMELINE 8] Task_Low resumed and finished.\n");
	printf("=================================================================\n\n");
	(void)TerminateTask();
}

TASK(Task_High)
{
	printf("[TIMELINE 6] Task_High DISPATCHED! (Context Switch from Low -> High occurred).\n");
	(void)GetResource(Res_SharedBuffer);
	printf("             Task_High GOT Resource instantly! (Zero Contention, O(1)).\n");
	(void)ReleaseResource(Res_SharedBuffer);
	(void)TerminateTask();
}

TASK(Task_Mid)
{
	printf("[TIMELINE 7] Task_Mid executing (Prio 2). (High has terminated, Mid now highest).\n");
	(void)TerminateTask();
}


#if defined(USE_PROTOTHREAD) && defined(PROTOTHREAD_TEST)
PROCESS(protoDemoProductProc,"protoDemoProductProc");
PROTO_AUTOSTART_PROCESS_EXPORT(protoDemoProductProc);
/* each bit means a product */
uint32_t buffer = 0;
#define NUM_ITEMS 10000

static struct pt_sem mutex, full, empty;

PROCESS_THREAD(protoDemoProductProc, ev, data)
{
	static int produced;
	static struct etimer et;
	process_poll(&protoDemoProductProc);
	PROCESS_BEGIN();
	PROCESS_SEM_INIT(&mutex, 1);
	PROCESS_SEM_INIT(&full, 0);
	PROCESS_SEM_INIT(&empty, 32);
	etimer_set(&et,OS_TICKS_PER_SECOND);
	PROCESS_YIELD();
	for(produced = 0; produced < NUM_ITEMS; ++produced) {

		PROCESS_WAIT_UNTIL(ev == PROCESS_EVENT_TIMER);
		PROCESS_SEM_WAIT(&empty);

		PROCESS_SEM_WAIT(&mutex);
		asAssert(0 == (buffer&(1<<(produced%32))));
		buffer |= 1<<(produced%32);
		printf("-->%d : %d\n", produced, produced%32);
		PROCESS_SEM_SIGNAL(&mutex);

		PROCESS_SEM_SIGNAL(&full);
	}
	PROCESS_END();
}

PROCESS(protoDemoConsumerProc,"protoDemoConsumerProc");
PROTO_AUTOSTART_PROCESS_EXPORT(protoDemoConsumerProc);

PROCESS_THREAD(protoDemoConsumerProc, ev, data)
{
	static int consumed;
	process_poll(&protoDemoConsumerProc);
	PROCESS_BEGIN();
	PROCESS_YIELD();
	for(consumed = 0; consumed < NUM_ITEMS; ++consumed) {

		PROCESS_SEM_WAIT(&full);

		PROCESS_SEM_WAIT(&mutex);
		asAssert(buffer&(1<<(consumed%32)));
		buffer &= ~(1<<(consumed%32));
		printf("<--%d : %d\n", consumed, consumed%32);
		PROCESS_SEM_SIGNAL(&mutex);

		PROCESS_SEM_SIGNAL(&empty);
	}
	PROCESS_END();
}
#endif

void ErrorHook(StatusType ercd)
{

	switch(ercd)
	{
		case E_OS_ACCESS:
			ASLOG(OS,("ercd = %d E_OS_ACCESS!\r\n",ercd));
			break;
		case E_OS_CALLEVEL:
			ASLOG(OS,("ercd = %d E_OS_CALLEVEL!\r\n",ercd));
			break;
		case E_OS_ID:
			ASLOG(OS,("ercd = %d E_OS_ID!\r\n",ercd));
			break;
		case E_OS_LIMIT:
			ASLOG(OS,("ercd = %d E_OS_LIMIT!\r\n",ercd));
			break;
		case E_OS_NOFUNC:
			ASLOG(OS,("ercd = %d E_OS_NOFUNC!\r\n",ercd));
			break;
		case E_OS_RESOURCE:
			ASLOG(OS,("ercd = %d E_OS_RESOURCE!\r\n",ercd));
			break;
		case E_OS_STATE:
			ASLOG(OS,("ercd = %d E_OS_STATE!\r\n",ercd));
			break;
		case E_OS_VALUE	:
			ASLOG(OS,("ercd = %d E_OS_VALUE!\r\n",ercd));
			break;
		default:
			ASLOG(OS,("ercd = %d unknown error!\r\n",ercd));
			break;
	}

	if(E_OS_CALLEVEL == ercd)
	{
		ShutdownOS(E_OS_CALLEVEL);
	}
	else
	{
		/* recover-able error */
	}
}

void PreTaskHook(void)
{
#ifdef USE_TRACE
	TaskType TaskID;
	GetTaskID(&TaskID);
	Trace_PerfStart(TaskID);
#endif
}
void PostTaskHook(void)
{
#ifdef USE_TRACE
	TaskType TaskID;
	GetTaskID(&TaskID);
	Trace_PerfStop(TaskID);
#endif
}

void ShutdownHook(StatusType ercd)
{
	printf("ShutdownHook(%X)\n",ercd);

	asAssert(0);
}

#if defined(__TOPPERS_ATK2_SC4__)
ProtectionReturnType ProtectionHook(StatusType FatalError)
{
	printf("ProtectionHook(%X)\n",FatalError);

	return PRO_SHUTDOWN;
}
#endif

void __error__(char *pcFilename, unsigned long ulLine)
{
	printf(" error @ %d of %s\n",(int)ulLine,pcFilename);
}

#if 0
#ifndef USE_STDRT
void abort(void) { printf("%s\n",__func__); asAssert(0); while(1); }
#endif
void _sbrk(void) { printf("%s\n",__func__); asAssert(0); }
void _write(void) { printf("%s\n",__func__); asAssert(0); }
void _close(void) { printf("%s\n",__func__); asAssert(0); }
void _fstat(void) { printf("%s\n",__func__); asAssert(0); }
void _isatty(void) { printf("%s\n",__func__); asAssert(0); }
void _lseek(void) { printf("%s\n",__func__); asAssert(0); }
void _read(void) { printf("%s\n",__func__); asAssert(0); }
#endif
