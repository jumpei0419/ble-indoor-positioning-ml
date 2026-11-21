#include <Arduino.h>
#include <NimBLEDevice.h>

// 四隅の受信機ID（"RX_1" 〜 "RX_4"）
static const char* RECEIVER_ID = "RX_1";
static const uint16_t EDDYSTONE_UUID = 0xFEAA;
static const int SCAN_TIME_SEC = 1;

NimBLEScan* pBLEScan;

class BeaconScanCallbacks : public NimBLEAdvertisedDeviceCallbacks {
  void onResult(NimBLEAdvertisedDevice* advertisedDevice) override {
    if (!advertisedDevice->haveServiceData()) return;

    std::string serviceData = advertisedDevice->getServiceData(NimBLEUUID(EDDYSTONE_UUID));
    if (serviceData.length() < 18) return;
    if (static_cast<uint8_t>(serviceData[0]) != 0x00) return;

    char beaconId[7] = {0};
    for (int i = 0; i < 6; ++i) {
      beaconId[i] = serviceData[12 + i];
    }

    String idStr = String(beaconId);
    idStr.trim();

    if (idStr.startsWith("TGT_") || idStr.startsWith("DUM_")) {
      const char* sourceType = idStr.startsWith("TGT_") ? "target" : "dummy";
      int rssi = advertisedDevice->getRSSI();

      Serial.printf(
          "{\"receiver_id\":\"%s\",\"source_type\":\"%s\",\"beacon_id\":\"%s\",\"rssi\":%d}\n",
          RECEIVER_ID, sourceType, idStr.c_str(), rssi);
    }
  }
};

void setup() {
  Serial.begin(115200);
  NimBLEDevice::init(RECEIVER_ID);

  pBLEScan = NimBLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new BeaconScanCallbacks(), true);
  pBLEScan->setActiveScan(false);
  pBLEScan->setInterval(100);
  pBLEScan->setWindow(99);
}

void loop() {
  pBLEScan->start(SCAN_TIME_SEC, false);
  pBLEScan->clearResults();
}