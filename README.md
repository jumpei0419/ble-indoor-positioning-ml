# BLE Fingerprinting & Dummy Beacon Indoor Positioning System

高専卒業研究（BLE Eddystone + Seeed Studio XIAO ESP32C3 + 機械学習による屋内位置推定）の復元コード群です。

## 概要
3×3グリッドの屋内環境において、BLE（Eddystone）と機械学習を用いたフィンガープリント法、ダミービーコンを併用したハイブリッド手法、およびユークリッド距離による近接性方式を比較評価するための構成です。

## 構成
- `esp32c3/beacon_tx_eddystone/`: ターゲット／ダミービーコン用ESP32-C3スケッチ
- `collector/`: RSSIデータ収集スクリプト・MySQLスキーマ
- `ml/`: 決定木・ランダムフォレスト・ガウシアンNB・SVM・近接性方式の評価コード