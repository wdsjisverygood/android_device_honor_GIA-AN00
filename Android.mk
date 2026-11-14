LOCAL_PATH := $(call my-dir)

ifeq ($(TARGET_DEVICE),gia)
include $(call all-makefiles-under,$(LOCAL_PATH))
endif
