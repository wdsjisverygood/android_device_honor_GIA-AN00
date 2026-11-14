$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/base.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/embedded.mk)
$(call inherit-product, vendor/twrp/config/common.mk)
$(call inherit-product, device/honor/gia/device.mk)

PRODUCT_DEVICE := gia
PRODUCT_NAME := twrp_gia
PRODUCT_BRAND := HONOR
PRODUCT_MODEL := GIA-AN00
PRODUCT_MANUFACTURER := HONOR

PRODUCT_GMS_CLIENTID_BASE := android-honor

TARGET_RECOVERY_DEVICE_DIRS := device/honor/gia
