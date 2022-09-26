from enum import Enum
import re
import humanfriendly
from typing import Iterator, Union, List


class NvmeStatus(Enum):
    # Codes have been extraced from https://github.com/RobinTMiller/dt/blob/master/nvme_lib.h
    # Copyright (c) 2011-2014, Intel Corporation.

    # Generic Command
    NVME_SC_SUCCESS = 0X0
    NVME_SC_INVALID_OPCODE = 0X1
    NVME_SC_INVALID_FIELD = 0X2
    NVME_SC_CMDID_CONFLICT = 0X3
    NVME_SC_DATA_XFER_ERROR = 0X4
    NVME_SC_POWER_LOSS = 0X5
    NVME_SC_INTERNAL = 0X6
    NVME_SC_ABORT_REQ = 0X7
    NVME_SC_ABORT_QUEUE = 0X8
    NVME_SC_FUSED_FAIL = 0X9
    NVME_SC_FUSED_MISSING = 0XA
    NVME_SC_INVALID_NS = 0XB
    NVME_SC_CMD_SEQ_ERROR = 0XC
    NVME_SC_SGL_INVALID_LAST = 0XD
    NVME_SC_SGL_INVALID_COUNT = 0XE
    NVME_SC_SGL_INVALID_DATA = 0XF
    NVME_SC_SGL_INVALID_METADATA = 0X10
    NVME_SC_SGL_INVALID_TYPE = 0X11
    NVME_SC_CMB_INVALID_USE = 0X12
    NVME_SC_PRP_INVALID_OFFSET = 0X13
    NVME_SC_ATOMIC_WRITE_UNIT_EXCEEDED = 0X14
    NVME_SC_OPERATION_DENIED = 0X15
    NVME_SC_SGL_INVALID_OFFSET = 0X16

    NVME_SC_INCONSISTENT_HOST_ID = 0X18
    NVME_SC_KEEP_ALIVE_EXPIRED = 0X19
    NVME_SC_KEEP_ALIVE_INVALID = 0X1A
    NVME_SC_PREEMPT_ABORT = 0X1B
    NVME_SC_SANITIZE_FAILED = 0X1C
    NVME_SC_SANITIZE_IN_PROGRESS = 0X1D

    NVME_SC_NS_WRITE_PROTECTED = 0X20
    NVME_SC_CMD_INTERRUPTED = 0X21
    NVME_SC_TRANSIENT_TRANSPORT = 0X22

    NVME_SC_LBA_RANGE = 0X80
    NVME_SC_CAP_EXCEEDED = 0X81
    NVME_SC_NS_NOT_READY = 0X82
    NVME_SC_RESERVATION_CONFLICT = 0X83
    NVME_SC_FORMAT_IN_PROGRESS = 0X84

    # Command Specific Status:
    NVME_SC_CQ_INVALID = 0X100
    NVME_SC_QID_INVALID = 0X101
    NVME_SC_QUEUE_SIZE = 0X102
    NVME_SC_ABORT_LIMIT = 0X103
    NVME_SC_ABORT_MISSING = 0X104
    NVME_SC_ASYNC_LIMIT = 0X105
    NVME_SC_FIRMWARE_SLOT = 0X106
    NVME_SC_FIRMWARE_IMAGE = 0X107
    NVME_SC_INVALID_VECTOR = 0X108
    NVME_SC_INVALID_LOG_PAGE = 0X109
    NVME_SC_INVALID_FORMAT = 0X10A
    NVME_SC_FW_NEEDS_CONV_RESET = 0X10B
    NVME_SC_INVALID_QUEUE = 0X10C
    NVME_SC_FEATURE_NOT_SAVEABLE = 0X10D
    NVME_SC_FEATURE_NOT_CHANGEABLE = 0X10E
    NVME_SC_FEATURE_NOT_PER_NS = 0X10F
    NVME_SC_FW_NEEDS_SUBSYS_RESET = 0X110
    NVME_SC_FW_NEEDS_RESET = 0X111
    NVME_SC_FW_NEEDS_MAX_TIME = 0X112
    NVME_SC_FW_ACTIVATE_PROHIBITED = 0X113
    NVME_SC_OVERLAPPING_RANGE = 0X114
    NVME_SC_NS_INSUFFICIENT_CAP = 0X115
    NVME_SC_NS_ID_UNAVAILABLE = 0X116
    NVME_SC_NS_ALREADY_ATTACHED = 0X118
    NVME_SC_NS_IS_PRIVATE = 0X119
    NVME_SC_NS_NOT_ATTACHED = 0X11A
    NVME_SC_THIN_PROV_NOT_SUPP = 0X11B
    NVME_SC_CTRL_LIST_INVALID = 0X11C
    NVME_SC_DEVICE_SELF_TEST_IN_PROGRESS = 0X11D
    NVME_SC_BP_WRITE_PROHIBITED = 0X11E
    NVME_SC_INVALID_CTRL_ID = 0X11F
    NVME_SC_INVALID_SECONDARY_CTRL_STATE = 0X120
    NVME_SC_INVALID_NUM_CTRL_RESOURCE = 0X121
    NVME_SC_INVALID_RESOURCE_ID = 0X122
    NVME_SC_PMR_SAN_PROHIBITED = 0X123
    NVME_SC_ANA_INVALID_GROUP_ID = 0X124
    NVME_SC_ANA_ATTACH_FAIL = 0X125

    # Command Set Specific - Namespace Types commands:
    NVME_SC_IOCS_NOT_SUPPORTED = 0X129
    NVME_SC_IOCS_NOT_ENABLED = 0X12A
    NVME_SC_IOCS_COMBINATION_REJECTED = 0X12B
    NVME_SC_INVALID_IOCS = 0X12C

    # I/O Command Set Specific - NVM commands:
    NVME_SC_BAD_ATTRIBUTES = 0X180
    NVME_SC_INVALID_PI = 0X181
    NVME_SC_READ_ONLY = 0X182
    NVME_SC_CMD_SIZE_LIMIT_EXCEEDED = 0X183

    # I/O Command Set Specific - Fabrics commands:
    NVME_SC_CONNECT_FORMAT = 0X180
    NVME_SC_CONNECT_CTRL_BUSY = 0X181
    NVME_SC_CONNECT_INVALID_PARAM = 0X182
    NVME_SC_CONNECT_RESTART_DISC = 0X183
    NVME_SC_CONNECT_INVALID_HOST = 0X184

    NVME_SC_DISCOVERY_RESTART = 0X190
    NVME_SC_AUTH_REQUIRED = 0X191

    # I/O Command Set Specific - Zoned Namespace commands:
    NVME_SC_ZONE_BOUNDARY_ERROR = 0X1B8
    NVME_SC_ZONE_IS_FULL = 0X1B9
    NVME_SC_ZONE_IS_READ_ONLY = 0X1BA
    NVME_SC_ZONE_IS_OFFLINE = 0X1BB
    NVME_SC_ZONE_INVALID_WRITE = 0X1BC
    NVME_SC_TOO_MANY_ACTIVE_ZONES = 0X1BD
    NVME_SC_TOO_MANY_OPEN_ZONES = 0X1BE
    NVME_SC_ZONE_INVALID_STATE_TRANSITION = 0X1BF

    # Media and Data Integrity Errors:
    NVME_SC_WRITE_FAULT = 0X280
    NVME_SC_READ_ERROR = 0X281
    NVME_SC_GUARD_CHECK = 0X282
    NVME_SC_APPTAG_CHECK = 0X283
    NVME_SC_REFTAG_CHECK = 0X284
    NVME_SC_COMPARE_FAILED = 0X285
    NVME_SC_ACCESS_DENIED = 0X286
    NVME_SC_UNWRITTEN_BLOCK = 0X287

    # Path-related Errors:
    NVME_SC_INTERNAL_PATH_ERROR = 0X300
    NVME_SC_ANA_PERSISTENT_LOSS = 0X301
    NVME_SC_ANA_INACCESSIBLE = 0X302
    NVME_SC_ANA_TRANSITION = 0X303

    # Controller Detected Path errors
    NVME_SC_CTRL_PATHING_ERROR = 0X360

    # Host Detected Path Errors
    NVME_SC_HOST_PATHING_ERROR = 0X370
    NVME_SC_HOST_CMD_ABORT = 0X371

    NVME_SC_CRD = 0X1800
    NVME_SC_DNR = 0X4000


class NvmeError(object):
    """This class stores the nvme detected errors
    The expected error table looks like:

    Num   ErrCount  SQId   CmdId  Status  PELoc          LBA  NSID    VS
    0       1356     0  0x0012  0xc005  0x028            -     0     -

    Attributes:
        id                      : The error number or id
        count                   : The number of errors detected
        sqid                    : The submission queue id
        cmdid                   : The command id
        status                  : The status of the error
        peloc                   : The physical error location
        lba                     : The logical block address
        nsid                    : The namespace id
        vs                      : The vendor specific
        cs                      : The command specific
    """

    def __init__(self, id: int = None, count: int = None, sqid: int = None, cmdid: int = None, status: int = None, peloc: int = None, lba: int = None, nsid: int = None, vs: int = None):
        self.id: int = id
        self.count: int = count
        self.sqid: int = sqid
        self.cmdid: int = cmdid
        self.status: int = status
        self.peloc: int = peloc
        self.lba: Union[int, None] = lba
        self.nsid: Union[int, None] = nsid
        self.vs: Union[int, None] = vs
        self.cs: Union[int, None] = None

    @property
    def status_str(self) -> str:
        # try to convert the status to a string

        # Strings have been extraced from https://github.com/RobinTMiller/dt/blob/master/nvme_lib.c
        # Copyright (c) 2011-2014, Intel Corporation.

        status = self.status & 0x7ff

        if status == NvmeStatus.NVME_SC_SUCCESS:
            status_str = "SUCCESS: The command completed successfully"
        elif status == NvmeStatus.NVME_SC_INVALID_OPCODE:
            status_str = "INVALID_OPCODE: The associated command opcode field is not valid"
        elif status == NvmeStatus.NVME_SC_INVALID_FIELD:
            status_str = "INVALID_FIELD: A reserved coded value or an unsupported value in a defined field"
        elif status == NvmeStatus.NVME_SC_CMDID_CONFLICT:
            status_str = "CMDID_CONFLICT: The command identifier is already in use"
        elif status == NvmeStatus.NVME_SC_DATA_XFER_ERROR:
            status_str = "DATA_XFER_ERROR: Error while trying to transfer the data or metadata"
        elif status == NvmeStatus.NVME_SC_POWER_LOSS:
            status_str = "POWER_LOSS: Command aborted due to power loss notification"
        elif status == NvmeStatus.NVME_SC_INTERNAL:
            status_str = "INTERNAL: The command was not completed successfully due to an internal error"
        elif status == NvmeStatus.NVME_SC_ABORT_REQ:
            status_str = "ABORT_REQ: The command was aborted due to a Command Abort request"
        elif status == NvmeStatus.NVME_SC_ABORT_QUEUE:
            status_str = "ABORT_QUEUE: The command was aborted due to a Delete I/O Submission Queue request"
        elif status == NvmeStatus.NVME_SC_FUSED_FAIL:
            status_str = "FUSED_FAIL: The command was aborted due to the other command in a fused operation failing"
        elif status == NvmeStatus.NVME_SC_FUSED_MISSING:
            status_str = "FUSED_MISSING: The command was aborted due to a Missing Fused Command"
        elif status == NvmeStatus.NVME_SC_INVALID_NS:
            status_str = "INVALID_NS: The namespace or the format of that namespace is invalid"
        elif status == NvmeStatus.NVME_SC_CMD_SEQ_ERROR:
            status_str = "CMD_SEQ_ERROR: The command was aborted due to a protocol violation in a multicommand sequence"
        elif status == NvmeStatus.NVME_SC_SGL_INVALID_LAST:
            status_str = "SGL_INVALID_LAST: The command includes an invalid SGL Last Segment or SGL Segment descriptor."
        elif status == NvmeStatus.NVME_SC_SGL_INVALID_COUNT:
            status_str = "SGL_INVALID_COUNT: There is an SGL Last Segment descriptor or an SGL Segment descriptor in a location other than the last descriptor of a segment based on the length indicated."
        elif status == NvmeStatus.NVME_SC_SGL_INVALID_DATA:
            status_str = "SGL_INVALID_DATA: This may occur if the length of a Data SGL is too short."
        elif status == NvmeStatus.NVME_SC_SGL_INVALID_METADATA:
            status_str = "SGL_INVALID_METADATA: This may occur if the length of a Metadata SGL is too short"
        elif status == NvmeStatus.NVME_SC_SGL_INVALID_TYPE:
            status_str = "SGL_INVALID_TYPE: The type of an SGL Descriptor is a type that is not supported by the controller."
        elif status == NvmeStatus.NVME_SC_CMB_INVALID_USE:
            status_str = "CMB_INVALID_USE: The attempted use of the Controller Memory Buffer is not supported by the controller."
        elif status == NvmeStatus.NVME_SC_PRP_INVALID_OFFSET:
            status_str = "PRP_INVALID_OFFSET: The Offset field for a PRP entry is invalid."
        elif status == NvmeStatus.NVME_SC_ATOMIC_WRITE_UNIT_EXCEEDED:
            status_str = "ATOMIC_WRITE_UNIT_EXCEEDED: The length specified exceeds the atomic write unit size."
        elif status == NvmeStatus.NVME_SC_OPERATION_DENIED:
            status_str = "OPERATION_DENIED: The command was denied due to lack of access rights."
        elif status == NvmeStatus.NVME_SC_SGL_INVALID_OFFSET:
            status_str = "SGL_INVALID_OFFSET: The offset specified in a descriptor is invalid."
        elif status == NvmeStatus.NVME_SC_INCONSISTENT_HOST_ID:
            status_str = "INCONSISTENT_HOST_ID: The NVM subsystem detected the simultaneous use of 64-bit and 128-bit Host Identifier values on different controllers."
        elif status == NvmeStatus.NVME_SC_KEEP_ALIVE_EXPIRED:
            status_str = "KEEP_ALIVE_EXPIRED: The Keep Alive Timer expired."
        elif status == NvmeStatus.NVME_SC_KEEP_ALIVE_INVALID:
            status_str = "KEEP_ALIVE_INVALID: The Keep Alive Timeout value specified is invalid."
        elif status == NvmeStatus.NVME_SC_PREEMPT_ABORT:
            status_str = "PREEMPT_ABORT: The command was aborted due to a Reservation Acquire command with the Reservation Acquire Action (RACQA) set to 010b (Preempt and Abort)."
        elif status == NvmeStatus.NVME_SC_SANITIZE_FAILED:
            status_str = "SANITIZE_FAILED: The most recent sanitize operation failed and no recovery actions has been successfully completed"
        elif status == NvmeStatus.NVME_SC_SANITIZE_IN_PROGRESS:
            status_str = "SANITIZE_IN_PROGRESS: The requested function is prohibited while a sanitize operation is in progress"
        elif status == NvmeStatus.NVME_SC_IOCS_NOT_SUPPORTED:
            status_str = "IOCS_NOT_SUPPORTED: The I/O command set is not supported"
        elif status == NvmeStatus.NVME_SC_IOCS_NOT_ENABLED:
            status_str = "IOCS_NOT_ENABLED: The I/O command set is not enabled"
        elif status == NvmeStatus.NVME_SC_IOCS_COMBINATION_REJECTED:
            status_str = "IOCS_COMBINATION_REJECTED: The I/O command set combination is rejected"
        elif status == NvmeStatus.NVME_SC_INVALID_IOCS:
            status_str = "INVALID_IOCS: the I/O command set is invalid"
        elif status == NvmeStatus.NVME_SC_LBA_RANGE:
            status_str = "LBA_RANGE: The command references a LBA that exceeds the size of the namespace"
        elif status == NvmeStatus.NVME_SC_NS_WRITE_PROTECTED:
            status_str = "NS_WRITE_PROTECTED: The command is prohibited while the namespace is write protected by the host."
        elif status == NvmeStatus.NVME_SC_TRANSIENT_TRANSPORT:
            status_str = "TRANSIENT_TRANSPORT: A transient transport error was detected."
        elif status == NvmeStatus.NVME_SC_CAP_EXCEEDED:
            status_str = "CAP_EXCEEDED: The execution of the command has caused the capacity of the namespace to be exceeded"
        elif status == NvmeStatus.NVME_SC_NS_NOT_READY:
            status_str = "NS_NOT_READY: The namespace is not ready to be accessed as a result of a condition other than a condition that is reported as an Asymmetric Namespace Access condition"
        elif status == NvmeStatus.NVME_SC_RESERVATION_CONFLICT:
            status_str = "RESERVATION_CONFLICT: The command was aborted due to a conflict with a reservation held on the accessed namespace"
        elif status == NvmeStatus.NVME_SC_FORMAT_IN_PROGRESS:
            status_str = "FORMAT_IN_PROGRESS: A Format NVM command is in progress on the namespace."
        elif status == NvmeStatus.NVME_SC_ZONE_BOUNDARY_ERROR:
            status_str = "ZONE_BOUNDARY_ERROR: Invalid Zone Boundary crossing"
        elif status == NvmeStatus.NVME_SC_ZONE_IS_FULL:
            status_str = "ZONE_IS_FULL: The accessed zone is in ZSF:Full state"
        elif status == NvmeStatus.NVME_SC_ZONE_IS_READ_ONLY:
            status_str = "ZONE_IS_READ_ONLY: The accessed zone is in ZSRO:Read Only state"
        elif status == NvmeStatus.NVME_SC_ZONE_IS_OFFLINE:
            status_str = "ZONE_IS_OFFLINE: The access zone is in ZSO:Offline state"
        elif status == NvmeStatus.NVME_SC_ZONE_INVALID_WRITE:
            status_str = "ZONE_INVALID_WRITE: The write to zone was not at the write pointer offset"
        elif status == NvmeStatus.NVME_SC_TOO_MANY_ACTIVE_ZONES:
            status_str = "TOO_MANY_ACTIVE_ZONES: The controller does not allow additional active zones"
        elif status == NvmeStatus.NVME_SC_TOO_MANY_OPEN_ZONES:
            status_str = "TOO_MANY_OPEN_ZONES: The controller does not allow additional open zones"
        elif status == NvmeStatus.NVME_SC_ZONE_INVALID_STATE_TRANSITION:
            status_str = "INVALID_ZONE_STATE_TRANSITION: The zone state change was invalid"
        elif status == NvmeStatus.NVME_SC_CQ_INVALID:
            status_str = "CQ_INVALID: The Completion Queue identifier specified in the command does not exist"
        elif status == NvmeStatus.NVME_SC_QID_INVALID:
            status_str = "QID_INVALID: The creation of the I/O Completion Queue failed due to an invalid queue identifier specified as part of the command. An invalid queue identifier is one that is currently in use or one that is outside the range supported by the controller"
        elif status == NvmeStatus.NVME_SC_QUEUE_SIZE:
            status_str = "QUEUE_SIZE: The host attempted to create an I/O Completion Queue with an invalid number of entries"
        elif status == NvmeStatus.NVME_SC_ABORT_LIMIT:
            status_str = "ABORT_LIMIT: The number of concurrently outstanding Abort commands has exceeded the limit indicated in the Identify Controller data structure"
        elif status == NvmeStatus.NVME_SC_ABORT_MISSING:
            status_str = "ABORT_MISSING: The abort command is missing"
        elif status == NvmeStatus.NVME_SC_ASYNC_LIMIT:
            status_str = "ASYNC_LIMIT: The number of concurrently outstanding Asynchronous Event Request commands has been exceeded"
        elif status == NvmeStatus.NVME_SC_FIRMWARE_SLOT:
            status_str = "FIRMWARE_SLOT: The firmware slot indicated is invalid or read only. This error is indicated if the firmware slot exceeds the number supported"
        elif status == NvmeStatus.NVME_SC_FIRMWARE_IMAGE:
            status_str = "FIRMWARE_IMAGE: The firmware image specified for activation is invalid and not loaded by the controller"
        elif status == NvmeStatus.NVME_SC_INVALID_VECTOR:
            status_str = "INVALID_VECTOR: The creation of the I/O Completion Queue failed due to an invalid interrupt vector specified as part of the command"
        elif status == NvmeStatus.NVME_SC_INVALID_LOG_PAGE:
            status_str = "INVALID_LOG_PAGE: The log page indicated is invalid. This error condition is also returned if a reserved log page is requested"
        elif status == NvmeStatus.NVME_SC_INVALID_FORMAT:
            status_str = "INVALID_FORMAT: The LBA Format specified is not supported. This may be due to various conditions"
        elif status == NvmeStatus.NVME_SC_FW_NEEDS_CONV_RESET:
            status_str = "FW_NEEDS_CONVENTIONAL_RESET: The firmware commit was successful, however, activation of the firmware image requires a conventional reset"
        elif status == NvmeStatus.NVME_SC_INVALID_QUEUE:
            status_str = "INVALID_QUEUE: This error indicates that it is invalid to delete the I/O Completion Queue specified. The typical reason for this error condition is that there is an associated I/O Submission Queue that has not been deleted."
        elif status == NvmeStatus.NVME_SC_FEATURE_NOT_SAVEABLE:
            status_str = "FEATURE_NOT_SAVEABLE: The Feature Identifier specified does not support a saveable value"
        elif status == NvmeStatus.NVME_SC_FEATURE_NOT_CHANGEABLE:
            status_str = "FEATURE_NOT_CHANGEABLE: The Feature Identifier is not able to be changed"
        elif status == NvmeStatus.NVME_SC_FEATURE_NOT_PER_NS:
            status_str = "FEATURE_NOT_PER_NS: The Feature Identifier specified is not namespace specific. The Feature Identifier settings apply across all namespaces"
        elif status == NvmeStatus.NVME_SC_FW_NEEDS_SUBSYS_RESET:
            status_str = "FW_NEEDS_SUBSYSTEM_RESET: The firmware commit was successful, however, activation of the firmware image requires an NVM Subsystem"
        elif status == NvmeStatus.NVME_SC_FW_NEEDS_RESET:
            status_str = "FW_NEEDS_RESET: The firmware commit was successful; however, the image specified does not support being activated without a reset"
        elif status == NvmeStatus.NVME_SC_FW_NEEDS_MAX_TIME:
            status_str = "FW_NEEDS_MAX_TIME_VIOLATION: The image specified if activated immediately would exceed the Maximum Time for Firmware Activation (MTFA) value reported in Identify Controller. To activate the firmware, the Firmware Commit command needs to be re-issued and the image activated using a reset"
        elif status == NvmeStatus.NVME_SC_FW_ACTIVATE_PROHIBITED:
            status_str = "FW_ACTIVATION_PROHIBITED: The image specified is being prohibited from activation by the controller for vendor specific reasons"
        elif status == NvmeStatus.NVME_SC_OVERLAPPING_RANGE:
            status_str = "OVERLAPPING_RANGE: This error is indicated if the firmware image has overlapping ranges"
        elif status == NvmeStatus.NVME_SC_NS_INSUFFICIENT_CAP:
            status_str = "NS_INSUFFICIENT_CAPACITY: Creating the namespace requires more free space than is currently available. The Command Specific Information field of the Error Information Log specifies the total amount of NVM capacity required to create the namespace in bytes"
        elif status == NvmeStatus.NVME_SC_NS_ID_UNAVAILABLE:
            status_str = "NS_ID_UNAVAILABLE: The number of namespaces supported has been exceeded"
        elif status == NvmeStatus.NVME_SC_NS_ALREADY_ATTACHED:
            status_str = "NS_ALREADY_ATTACHED: The controller is already attached to the namespace specified"
        elif status == NvmeStatus.NVME_SC_NS_IS_PRIVATE:
            status_str = "NS_IS_PRIVATE: The namespace is private and is already attached to one controller"
        elif status == NvmeStatus.NVME_SC_NS_NOT_ATTACHED:
            status_str = "NS_NOT_ATTACHED: The request to detach the controller could not be completed because the controller is not attached to the namespace"
        elif status == NvmeStatus.NVME_SC_THIN_PROV_NOT_SUPP:
            status_str = "THIN_PROVISIONING_NOT_SUPPORTED: Thin provisioning is not supported by the controller"
        elif status == NvmeStatus.NVME_SC_CTRL_LIST_INVALID:
            status_str = "CONTROLLER_LIST_INVALID: The controller list provided is invalid"
        elif status == NvmeStatus.NVME_SC_DEVICE_SELF_TEST_IN_PROGRESS:
            status_str = "DEVICE_SELF_TEST_IN_PROGRESS: The controller or NVM subsystem already has a device self-test operation in process."
        elif status == NvmeStatus.NVME_SC_BP_WRITE_PROHIBITED:
            status_str = "BOOT PARTITION WRITE PROHIBITED: The command is trying to modify a Boot Partition while it is locked"
        elif status == NvmeStatus.NVME_SC_INVALID_CTRL_ID:
            status_str = "INVALID_CTRL_ID: An invalid Controller Identifier was specified."
        elif status == NvmeStatus.NVME_SC_INVALID_SECONDARY_CTRL_STATE:
            status_str = "INVALID_SECONDARY_CTRL_STATE: The action requested for the secondary controller is invalid based on the current state of the secondary controller and its primary controller."
        elif status == NvmeStatus.NVME_SC_INVALID_NUM_CTRL_RESOURCE:
            status_str = "INVALID_NUM_CTRL_RESOURCE: The specified number of Flexible Resources is invalid"
        elif status == NvmeStatus.NVME_SC_INVALID_RESOURCE_ID:
            status_str = "INVALID_RESOURCE_ID: At least one of the specified resource identifiers was invalid"
        elif status == NvmeStatus.NVME_SC_ANA_INVALID_GROUP_ID:
            status_str = "ANA_INVALID_GROUP_ID: The specified ANA Group Identifier (ANAGRPID) is not supported in the submitted command."
        elif status == NvmeStatus.NVME_SC_ANA_ATTACH_FAIL:
            status_str = "ANA_ATTACH_FAIL: The controller is not attached to the namespace as a result of an ANA condition"
        elif status == NvmeStatus.NVME_SC_BAD_ATTRIBUTES:
            status_str = "BAD_ATTRIBUTES: Bad attributes were given"
        elif status == NvmeStatus.NVME_SC_INVALID_PI:
            status_str = "INVALID_PROTECION_INFO: The Protection Information Field settings specified in the command are invalid"
        elif status == NvmeStatus.NVME_SC_READ_ONLY:
            status_str = "WRITE_ATTEMPT_READ_ONLY_RANGE: The LBA range specified contains read-only blocks"
        elif status == NvmeStatus.NVME_SC_CMD_SIZE_LIMIT_EXCEEDED:
            status_str = "CMD_SIZE_LIMIT_EXCEEDED: Command size limit exceeded"
        elif status == NvmeStatus.NVME_SC_WRITE_FAULT:
            status_str = "WRITE_FAULT: The write data could not be committed to the media"
        elif status == NvmeStatus.NVME_SC_READ_ERROR:
            status_str = "READ_ERROR: The read data could not be recovered from the media"
        elif status == NvmeStatus.NVME_SC_GUARD_CHECK:
            status_str = "GUARD_CHECK: The command was aborted due to an end-to-end guard check failure"
        elif status == NvmeStatus.NVME_SC_APPTAG_CHECK:
            status_str = "APPTAG_CHECK: The command was aborted due to an end-to-end application tag check failure"
        elif status == NvmeStatus.NVME_SC_REFTAG_CHECK:
            status_str = "REFTAG_CHECK: The command was aborted due to an end-to-end reference tag check failure"
        elif status == NvmeStatus.NVME_SC_COMPARE_FAILED:
            status_str = "COMPARE_FAILED: The command failed due to a miscompare during a Compare command"
        elif status == NvmeStatus.NVME_SC_ACCESS_DENIED:
            status_str = "ACCESS_DENIED: Access to the namespace and/or LBA range is denied due to lack of access rights"
        elif status == NvmeStatus.NVME_SC_UNWRITTEN_BLOCK:
            status_str = "UNWRITTEN_BLOCK: The command failed due to an attempt to read from an LBA range containing a deallocated or unwritten logical block"
        elif status == NvmeStatus.NVME_SC_INTERNAL_PATH_ERROR:
            status_str = "INTERNAL_PATH_ERROT: The command was not completed as the result of a controller internal error"
        elif status == NvmeStatus.NVME_SC_ANA_PERSISTENT_LOSS:
            status_str = "ASYMMETRIC_NAMESPACE_ACCESS_PERSISTENT_LOSS: The requested function (e.g., command) is not able to be performed as a result of the relationship between the controller and the namespace being in the ANA Persistent Loss state"
        elif status == NvmeStatus.NVME_SC_ANA_INACCESSIBLE:
            status_str = "ASYMMETRIC_NAMESPACE_ACCESS_INACCESSIBLE: The requested function (e.g., command) is not able to be performed as a result of the relationship between the controller and the namespace being in the ANA Inaccessible state"
        elif status == NvmeStatus.NVME_SC_ANA_TRANSITION:
            status_str = "ASYMMETRIC_NAMESPACE_ACCESS_TRANSITION: The requested function (e.g., command) is not able to be performed as a result of the relationship between the controller and the namespace transitioning between Asymmetric Namespace Access states"
        elif status == NvmeStatus.NVME_SC_CTRL_PATHING_ERROR:
            status_str = "CONTROLLER_PATHING_ERROR: A pathing error was detected by the controller"
        elif status == NvmeStatus.NVME_SC_HOST_PATHING_ERROR:
            status_str = "HOST_PATHING_ERROR: A pathing error was detected by the host"
        elif status == NvmeStatus.NVME_SC_HOST_CMD_ABORT:
            status_str = "HOST_COMMAND_ABORT: The command was aborted as a result of host action"
        elif status == NvmeStatus.NVME_SC_CMD_INTERRUPTED:
            status_str = "CMD_INTERRUPTED: Command processing was interrupted and the controller is unable to successfully complete the command. The host should retry the command."
        elif status == NvmeStatus.NVME_SC_PMR_SAN_PROHIBITED:
            status_str = "Sanitize Prohibited While Persistent Memory Region is Enabled: A sanitize operation is prohibited while the Persistent Memory Region is enabled."
        else:
            status_str = "Unknown"

        # return str(self.status)+f': ({status_str})'
        return status_str

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'{self.status}: ({self.status_str()})'

    def __getstate__(self, all_info=True):
        """
        Allows us to send a pySMART diagnostics object over a serializable
        medium which uses json (or the likes of json) payloads
        """
        return vars(self)

    def __setstate__(self, state):
        self.__dict__.update(state)


class NvmeAttributes(object):
    """This class represents the attributes of a NVMe device

    Attributes:
        criticalWarning          : Number of critical warnings
        temperature              : Temperature in Celsius
        availableSpare           : Available spare in percentage
        availableSpareThreshold  : Available spare threshold in percentage
        percentageUsed           : Data units used in percentage
        dataUnitsRead            : Data units (sectors) read
        bytesRead                : Bytes read
        dataUnitsWritten         : Data units (sectors) written
        bytesWritten             : Bytes written
        hostReadCommands         : Host read commands
        hostWriteCommands        : Host write commands
        controllerBusyTime       : Controller busy time in minutes
        powerCycles              : Power on cycles
        powerOnHours             : Power on hours
        unsafeShutdowns          : Unsafe shutdowns
        integrityErrors          : Integrity errors
        errorEntries             : Error log entries
        warningTemperatureTime   : Time in minutes at warning temperature
        criticalTemperatureTime  : Time in minutes at critical temperature

        errors                   : List of errors
    """

    def __init__(self, data: Iterator[str] = None):
        """Initializes the attributes

        Args:
            data (Iterator[str], optional): Iterator of the lines of the output of the command nvme smart-log. Defaults to None.

        """

        self.critialWarning: int = None
        self.temperature: int = None
        self.availableSpare: int = None
        self.availableSpareThreshold: int = None
        self.percentageUsed: int = None
        self.dataUnitsRead: int = None
        self.bytesRead: int = None
        self.dataUnitsWritten: int = None
        self.bytesWritten: int = None
        self.hostReadCommands: int = None
        self.hostWriteCommands: int = None
        self.controllerBusyTime: int = None
        self.powerCycles: int = None
        self.powerOnHours: int = None
        self.unsafeShutdowns: int = None
        self.integrityErrors: int = None
        self.errorEntries: int = None
        self.warningTemperatureTime: int = None
        self.criticalTemperatureTime: int = None

        self.errors: List[NvmeError] = []

        if data is not None:
            self.parse(data)

    def parse(self, data: Iterator[str]) -> None:
        """Parses the attributes from the raw data
        """

        # Advance data until detect Nvme Log
        for line in data:

            # Smart section: 'SMART/Health Information (NVMe Log 0x02)'
            if line.startswith('SMART/Health Information (NVMe Log 0x02)'):

                # Parse attributes
                for line in data:
                    line = line.strip()

                    if not line or len(line) == 0:
                        break

                    # Parse attribute
                    match = re.match(
                        r'^\s*(?P<name>.+)\s*:\s*(?P<value>.+)\s*$', line)
                    if match:
                        name = match.group('name')
                        value = match.group('value')

                        if name == 'Critical Warning':
                            self.criticalWarning = int(value, 16)
                        elif name == 'Temperature':
                            # Check if temperature is in Celsius or Fahrenheit
                            if value.endswith('Celsius'):
                                self.temperature = int(value[:-7])
                            elif value.endswith('Fahrenheit'):
                                self.temperature = int(
                                    (int(value[:-10]) - 32) / 1.8)
                        elif name == 'Available Spare':
                            self.availableSpare = int(value[:-1])
                        elif name == 'Available Spare Threshold':
                            self.availableSpareThreshold = int(value[:-1])
                        elif name == 'Percentage Used':
                            self.percentageUsed = int(value[:-1])
                        elif name == 'Data Units Read':
                            # Format: 1,234,567 [2.00 TB]
                            self.dataUnitsRead = int(
                                value.split(' ')[0].replace(',', '').replace('.', ''))
                            self.bytesRead = humanfriendly.parse_size(
                                value.split(' ', 1)[1][1:-1].replace(',', '.'))
                        elif name == 'Data Units Written':
                            # Format: 1,234,567 [2.00 TB]
                            self.dataUnitsWritten = int(
                                value.split(' ')[0].replace(',', '').replace('.', ''))
                            self.bytesWritten = humanfriendly.parse_size(
                                value.split(' ', 1)[1][1:-1].replace(',', '.'))
                        elif name == 'Host Read Commands':
                            self.hostReadCommands = int(
                                value.replace(',', '').replace('.', ''))
                        elif name == 'Host Write Commands':
                            self.hostWriteCommands = int(
                                value.replace(',', '').replace('.', ''))
                        elif name == 'Controller Busy Time':
                            self.controllerBusyTime = int(
                                value.replace(',', '').replace('.', ''))
                        elif name == 'Power Cycles':
                            self.powerCycles = int(
                                value.replace(',', '').replace('.', ''))
                        elif name == 'Power On Hours':
                            self.powerOnHours = int(
                                value.replace(',', '').replace('.', ''))
                        elif name == 'Unsafe Shutdowns':
                            self.unsafeShutdowns = int(
                                value.replace(',', '').replace('.', ''))
                        elif name == 'Media and Data Integrity Errors':
                            self.integrityErrors = int(
                                value.replace(',', '').replace('.', ''))
                        elif name == 'Error Information Log Entries':
                            self.errorEntries = int(
                                value.replace(',', '').replace('.', ''))
                        elif name == 'Warning Comp. Temperature Time':
                            self.warningTemperatureTime = int(
                                value.replace(',', '').replace('.', ''))
                        elif name == 'Critical Comp. Temperature Time':
                            self.criticalTemperatureTime = int(
                                value.replace(',', '').replace('.', ''))

            # Smart section: Error Information (NVMe Log 0x01, <num_entries> of <max_entries> entries)
            elif line.startswith('Error Information (NVMe Log 0x01, '):

                # check next line is:
                # Num   ErrCount  SQId   CmdId  Status  PELoc          LBA  NSID    VS
                # but be careful with the spaces

                line = next(data)
                if not re.match(r'^\s*Num\s+ErrCount\s+SQId\s+CmdId\s+Status\s+PELoc\s+LBA\s+NSID\s+VS\s*$', line):
                    continue

                # Parse errors
                for line in data:
                    line = line.strip()

                    if not line or len(line) == 0:
                        break

                    # Parse error
                    # Format:    Num   ErrCount  SQId   CmdId  Status  PELoc          LBA  NSID    VS
                    # example 1:   0       1356     0  0x0012  0xc005  0x028            -     0     -
                    # example 2:   3          1     3  0x0045  0xc006  0x049           56     3     2

                    match = re.match(
                        r'^\s*(?P<num>\d+)\s+(?P<errCount>\d+)\s+(?P<sqId>\d+)\s+(?P<cmdId>\w+)\s+(?P<status>\w+)\s+(?P<peLoc>\w+)\s+(?P<lba>\S+)\s+(?P<nsid>\S+)\s+(?P<vs>\S+)\s*$', line)

                    if match:
                        error = NvmeError()

                        error.num = int(match.group('num'))
                        error.errCount = int(match.group('errCount'))
                        error.sqId = int(match.group('sqId'))
                        error.cmdId = int(match.group('cmdId'), 16)
                        error.status = int(match.group('status'), 16)
                        error.peLoc = int(match.group('peLoc'), 16)

                        if match.group('lba') == '-':
                            error.lba = None
                        else:
                            error.lba = int(match.group('lba'), 16)

                        if match.group('nsid') == '-':
                            error.nsid = None
                        else:
                            error.nsid = int(match.group('nsid'))

                        if match.group('vs') == '-':
                            error.vs = None
                        else:
                            error.vs = int(match.group('vs'), 16)

                        self.errors.append(error)

    def __getstate__(self, all_info=True):
        """
        Allows us to send a pySMART diagnostics object over a serializable
        medium which uses json (or the likes of json) payloads
        """
        ret = vars(self)

        if ret['errors'] is not None:
            ret['errors'] = [vars(e) for e in ret['errors']]

    def __setstate__(self, state):
        self.__dict__.update(state)
