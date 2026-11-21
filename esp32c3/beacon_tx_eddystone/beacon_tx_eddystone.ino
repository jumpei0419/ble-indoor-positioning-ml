#include <Arduino.h>
#include <NimBLEDevice.h>

static const char* BEACON_ID = "DUM_01";
static const uint16_t EDDYSTONE_UUID = 0xFEAA;
static const uint8_t FRAME_TYPE_UID = 0x00;

NimBLEAdvertising* pAdvertising;

void buildEddystoneUIDPayload(uint8_t* buf, size_t& len, int8_t txPower, const char* idStr) {
  size_t idx = 0;
  buf[idx++] = EDDYSTONE_UUID & 0xFF;
  buf[idx++] = (EDDYSTONE_UUID >> 8) & 0xFF;
  buf[idx++] = FRAME_TYPE_UID;
  buf[idx++] = static_cast<uint8_t>(txPower);

  for (size_t i = 0; i < 10; ++i) {
    buf[idx++] = (i < 3) ? static_cast<uint8_t>('I') : 0x00;
  }
  for (size_t i = 0; i < 6; ++i) {
    buf[idx++] = (idStr[i] != '\0') ? static_cast<uint8_t>(idStr[i]) : 0x00;
  }
  buf[idx++] = 0x00;
  buf[idx++] = 0x00;
  len = idx;
}

void setup() {
  Serial.begin(115200);
  NimBLEDevice::init(BEACON_ID);
  NimBLEDevice::setPower(ESP_PWR_LVL_P3);

  pAdvertising = NimBLEDevice::getAdvertising();
  NimBLEAdvertisementData advData;
  advData.setFlags(0x06);

  uint8_t serviceData[20];
  size_t serviceDataLen = 0;
  buildEddystoneUIDPayload(serviceData, serviceDataLen, -20, BEACON_ID);
  advData.setServiceData(
      NimBLEUUID(EDDYSTONE_UUID),
      std::string(reinterpret_cast<char*>(serviceData), serviceDataLen));

  pAdvertising->setAdvertisementData(advData);
  pAdvertising->setScanResponse(false);
  pAdvertising->start();
  Serial.printf("Started Eddystone beacon: %s\n", BEACON_ID);
}

void loop() {
  delay(1000);
}