/* -*- Mode: C; tab-width: 8; indent-tabs-mode: t; c-basic-offset: 8 -*-
 *
 * Copyright (C) 2015 Richard Hughes <richard@hughsie.com>
 *
 * Licensed under the GNU Lesser General Public License Version 2.1
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
 */

#ifndef __DFU_DEVICE_PRIVATE_H
#define __DFU_DEVICE_PRIVATE_H

#include <glib-object.h>
#include <gio/gio.h>
#include <gusb.h>

#include "dfu-device.h"

G_BEGIN_DECLS

#define DFU_DEVICE_REPLUG_TIMEOUT	5000	/* ms */

/**
 * DfuDeviceQuirks:
 * @DFU_DEVICE_QUIRK_NONE:			No device quirks
 * @DFU_DEVICE_QUIRK_IGNORE_POLLTIMEOUT:	Ignore the device download timeout
 * @DFU_DEVICE_QUIRK_FORCE_DFU_MODE:		Force DFU mode
 * @DFU_DEVICE_QUIRK_IGNORE_INVALID_VERSION:	Ignore invalid version numbers
 * @DFU_DEVICE_QUIRK_USE_PROTOCOL_ZERO:		Fix up the protocol number
 * @DFU_DEVICE_QUIRK_NO_PID_CHANGE:		Accept the same VID:PID when changing modes
 * @DFU_DEVICE_QUIRK_NO_GET_STATUS_UPLOAD:	Do not do GetStatus when uploading
 * @DFU_DEVICE_QUIRK_NO_DFU_RUNTIME:		No DFU runtime interface is provided
 * @DFU_DEVICE_QUIRK_ATTACH_UPLOAD_DOWNLOAD:	An upload or download is required for attach
 *
 * The workarounds for different devices.
 **/
typedef enum {
	DFU_DEVICE_QUIRK_NONE			= 0,
	DFU_DEVICE_QUIRK_IGNORE_POLLTIMEOUT	= (1 << 0),
	DFU_DEVICE_QUIRK_FORCE_DFU_MODE		= (1 << 1),
	DFU_DEVICE_QUIRK_IGNORE_INVALID_VERSION	= (1 << 2),
	DFU_DEVICE_QUIRK_USE_PROTOCOL_ZERO	= (1 << 3),
	DFU_DEVICE_QUIRK_NO_PID_CHANGE		= (1 << 4),
	DFU_DEVICE_QUIRK_NO_GET_STATUS_UPLOAD	= (1 << 5),
	DFU_DEVICE_QUIRK_NO_DFU_RUNTIME		= (1 << 6),
	DFU_DEVICE_QUIRK_ATTACH_UPLOAD_DOWNLOAD	= (1 << 7),
	/*< private >*/
	DFU_DEVICE_QUIRK_LAST
} DfuDeviceQuirks;

/**
 * DfuDeviceAttributes:
 * @DFU_DEVICE_ATTRIBUTE_NONE:			No attributes set
 * @DFU_DEVICE_ATTRIBUTE_CAN_DOWNLOAD:		Can download from host->device
 * @DFU_DEVICE_ATTRIBUTE_CAN_UPLOAD:		Can upload from device->host
 * @DFU_DEVICE_ATTRIBUTE_MANIFEST_TOL:		Can answer GetStatus in manifest
 * @DFU_DEVICE_ATTRIBUTE_WILL_DETACH:		Will self-detach
 * @DFU_DEVICE_ATTRIBUTE_CAN_ACCELERATE:	Use a larger transfer size for speed
 *
 * The device DFU attributes.
 **/
typedef enum {
	DFU_DEVICE_ATTRIBUTE_NONE		= 0,
	DFU_DEVICE_ATTRIBUTE_CAN_DOWNLOAD	= (1 << 0),
	DFU_DEVICE_ATTRIBUTE_CAN_UPLOAD		= (1 << 1),
	DFU_DEVICE_ATTRIBUTE_MANIFEST_TOL	= (1 << 2),
	DFU_DEVICE_ATTRIBUTE_WILL_DETACH	= (1 << 3),
	DFU_DEVICE_ATTRIBUTE_CAN_ACCELERATE	= (1 << 7),
	/*< private >*/
	DFU_DEVICE_ATTRIBUTE_LAST
} DfuDeviceAttributes;

GUsbDevice	*dfu_device_get_usb_dev			(DfuDevice	*device);

gboolean	 dfu_device_has_dfuse_support		(DfuDevice	*device);
gboolean	 dfu_device_has_attribute		(DfuDevice	*device,
							 DfuDeviceAttributes attribute);
gboolean	 dfu_device_has_quirk			(DfuDevice	*device,
							 DfuDeviceQuirks quirk);

void		 dfu_device_error_fixup			(DfuDevice	*device,
							 GCancellable	*cancellable,
							 GError		**error);
guint		 dfu_device_get_download_timeout	(DfuDevice	*device);
gchar		*dfu_device_get_quirks_as_string	(DfuDevice	*device);
gboolean	 dfu_device_set_new_usb_dev		(DfuDevice	*device,
							 GUsbDevice	*dev,
							 GCancellable	*cancellable,
							 GError		**error);

G_END_DECLS

#endif /* __DFU_DEVICE_PRIVATE_H */
