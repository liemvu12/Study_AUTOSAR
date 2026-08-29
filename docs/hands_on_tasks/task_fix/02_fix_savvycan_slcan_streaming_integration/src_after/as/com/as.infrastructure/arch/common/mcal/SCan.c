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
#include "Can.h"
#include "Mcu.h"
#include "CanIf_Cbk.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include "Os.h"
#include "asdebug.h"
#include "ringbuffer.h"
/* ============================ [ MACROS    ] ====================================================== */
#ifndef CAN_SERIAL_Q_SIZE
#define CAN_SERIAL_Q_SIZE 32
#endif
#define CAN_EMPTY_MESSAGE_BOX 0xFFFF
/* ============================ [ TYPES     ] ====================================================== */
/* ============================ [ DECLARES  ] ====================================================== */

/* ============================ [ DATAS     ] ====================================================== */
RB_DECLARE(canin,  Can_SerialInPduType, CAN_SERIAL_Q_SIZE);
RB_DECLARE(canout, Can_SerialOutPduType, CAN_SERIAL_Q_SIZE);

/* stub data */
const Can_ControllerConfigType __attribute__((weak)) Can_ControllerCfgData[1] ;
const Can_ConfigSetType __attribute__((weak)) Can_ConfigSetData =
{
  .CanController =	NULL,
  .CanCallbacks =	NULL,
};

const Can_ConfigType __attribute__((weak)) Can_ConfigData = {
  .CanConfigSet =	&Can_ConfigSetData,
};
/* ============================ [ LOCALS    ] ====================================================== */
/* ============================ [ FUNCTIONS ] ====================================================== */
void Can_Init( const Can_ConfigType *Config )
{
	(void)Config;
}

void Can_InitController( uint8 controller, const Can_ControllerConfigType *config)
{
	(void)controller;
	(void)config;
}

Can_ReturnType __weak CanHW_SetControllerMode( uint8 Controller, Can_StateTransitionType transition )
{
	(void)Controller;
	switch(transition )
	{
		case CAN_T_START:	/* no break here */
		case CAN_T_WAKEUP:
		break;
		case CAN_T_SLEEP:
		case CAN_T_STOP:
		default:
		break;
	}
	return E_OK;
}
Can_ReturnType Can_SetControllerMode( uint8 Controller, Can_StateTransitionType transition )
{
	return CanHW_SetControllerMode(Controller,transition);
}

extern void Can_SendSLCAN(const char* str);

Can_ReturnType Can_Write( Can_Arc_HTHType hth, Can_PduType *pduInfo )
{
	imask_t imask;
	Can_ReturnType rv = CAN_OK;
	Can_SerialOutPduType pdu;
	rb_size_t r;
	char slcan_buf[64];
	int offset = 0;

	SETSCANID(pdu.canid, pduInfo->id);
	pdu.busid = hth;
	pdu.dlc=pduInfo->length;
	memcpy(pdu.data, pduInfo->sdu, pdu.dlc);
	pdu.swPduHandle = pduInfo->swPduHandle;

	/* 1. Send SLCAN string to UART1 (Dedicated CAN Channel for SavvyCAN via COM1) */
	if (pduInfo->id <= 0x7FF) {
		offset = sprintf(slcan_buf, "t%03X%d", (unsigned int)pduInfo->id, (int)pduInfo->length);
	} else {
		offset = sprintf(slcan_buf, "T%08X%d", (unsigned int)pduInfo->id, (int)pduInfo->length);
	}
	for (int i = 0; i < pduInfo->length; i++) {
		offset += sprintf(&slcan_buf[offset], "%02X", pduInfo->sdu[i]);
	}
	sprintf(&slcan_buf[offset], "\r");
	Can_SendSLCAN(slcan_buf);

	/* 2. Print human-readable log to UART0 (Console Terminal stdout) */
	printf(">>> [CAN Tx Event] ID=0x%03X DLC=%d Data=[", (unsigned int)pduInfo->id, (int)pduInfo->length);
	for (int i = 0; i < pduInfo->length; i++) {
		printf("%02X%s", pduInfo->sdu[i], (i == pduInfo->length - 1) ? "" : " ");
	}
	printf("]\n");

	Irq_Save(imask);
	r = RB_PUSH(canout, &pdu, sizeof(pdu));
	Irq_Restore(imask);
	if(0 == r)
	{
		rv = CAN_BUSY;
	}

	return rv;
}

void __weak CanHW_DisableControllerInterrupts( uint8 controller )
{
	(void)controller;
}
void Can_DisableControllerInterrupts( uint8 controller )
{
	CanHW_DisableControllerInterrupts(controller);
}

void __weak  CanHW_EnableControllerInterrupts( uint8 controller )
{
	(void)controller;
}
void Can_EnableControllerInterrupts( uint8 controller )
{
	CanHW_EnableControllerInterrupts(controller);
}

void Can_Cbk_CheckWakeup( uint8 controller ){(void)controller;}

void __weak Can_MainFunction_Write( void )
{
}

void __weak Can_MainFunction_Read_InISR( void )
{
}

void Can_MainFunction_Read( void )
{
	imask_t imask;
	rb_size_t r;
	Can_SerialInPduType pdu;

	do
	{
		Irq_Save(imask);
		r = RB_POP(canin, &pdu, sizeof(pdu));
		Irq_Restore(imask);
		if(r > 0)
		{
			CanIf_RxIndication(pdu.busid,SCANID(pdu.canid),pdu.dlc,pdu.data);
		}
	} while(r > 0);
}
void Can_MainFunction_BusOff( void ){}
void Can_MainFunction_Wakeup( void ){}
void Can_MainFunction_Error ( void ){}

void Can_Arc_GetStatistics( uint8 controller, Can_Arc_StatisticsType * stat){(void)controller;(void)stat;}
