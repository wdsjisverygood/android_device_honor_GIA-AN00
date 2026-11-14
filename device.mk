LOCAL_PATH := device/honor/gia

PRODUCT_PACKAGES += \
    libtar

# 分区表
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/recovery.fstab:$(TARGET_COPY_OUT_RECOVERY)/root/system/etc/recovery.fstab

# 原机 recovery init
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/recovery/root/init.recovery.mt6877.rc:$(TARGET_COPY_OUT_RECOVERY)/root/init.recovery.mt6877.rc
