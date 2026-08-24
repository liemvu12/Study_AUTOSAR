/**
 * AS - the open source Automotive Software on https://github.com/parai
 *
 * Copyright (C) 2021  AS <parai@foxmail.com>
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
#ifndef _LINTP_SLAVE_H_
#define _LINTP_SLAVE_H_
/* ============================ [ INCLUDES  ] ====================================================== */
#include "ComStack_Types.h"

/* ============================ [ MACROS    ] ====================================================== */
/* ============================ [ TYPES     ] ====================================================== */
typedef enum {
	LINSTP_IDLE,
	LINSTP_RX_BUSY,
	LINSTP_RX_PROVIDED_TO_DCM,
	LINSTP_TX_BUSY,
} LinSTp_StateType;

typedef struct {
	PduInfoType PduInfo;
	PduLengthType index;
	uint16_t timer;
	uint8_t SN;
	uint8_t state;
} LinSTp_ContextType;

typedef struct {
	PduIdType dcmRxId;
	PduIdType dcmTxId;
	uint16_t timeout;
	uint8_t NA;
} LinSTp_ChannelConfigType;

typedef struct {
	const LinSTp_ChannelConfigType* channelConfigs;
	uint32_t channelNums;
	LinSTp_ContextType* contexts;
} LinSTp_ConfigType;

#include "LinSTp_Cfg.h"
/* ============================ [ DECLARES  ] ====================================================== */
/* ============================ [ DATAS     ] ====================================================== */
/* ============================ [ LOCALS    ] ====================================================== */
/* ============================ [ FUNCTIONS ] ====================================================== */
void LinSTp_RxIndication(PduIdType Instance, const PduInfoType *PduInfo);
Std_ReturnType LinSTp_Transmit(PduIdType Instance, const PduInfoType *PduInfo);
Std_ReturnType LinSTp_TriggerTransmit(PduIdType Instance, PduInfoType *PduInfoPtr);
void LinSTp_MainFunction(void);
#endif /* _LINTP_SLAVE_H_ */
