# BLE Fingerprinting & Dummy Beacon Indoor Positioning System

茨城工業高等専門学校 卒業研究「機械学習及びダミービーコンを用いたフィンガープリント方式による屋内位置測定システムに関する研究」の復元コードおよび実験評価パイプラインです。

## 概要
3×3グリッド（各1m四方）の屋内エリアにおいて、Seeed Studio XIAO ESP32C3 と BLE（Eddystone）を用いた以下の3手法を比較・検証します。

1. **近接性方式（Proximity Baseline）**: ターゲットとダミービーコンのRSSIパターンのユークリッド距離による推定
2. **機械学習フィンガープリント法（ML Fingerprinting）**: ターゲット単体のRSSIを用いた4モデル（決定木・ランダムフォレスト・ガウシアンナイーブベイズ・SVM）による分類
3. **ハイブリッド手法（Hybrid Method）**: ターゲットとダミービーコン9台のRSSIを統合した高次元特徴量による環境変動補正

## 主な実験結果（平均測位精度）

| 手法 | 近接性方式 | 決定木 | ランダムフォレスト | ナイーブベイズ | SVM |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **従来・単体手法** | 19.33% | 69.00% | 88.89% | **100.00%** | 99.11% |
| **ハイブリッド手法** | - | 63.89% | **98.56%** | **98.78%** | 85.44% |

## ディレクトリ構成
- `esp32c3/`: Seeed Studio XIAO ESP32C3 向け送信機・受信機ファームウェア
- `collector/`: RSSIデータ収集スクリプトおよびMySQLスキーマ
- `ml/`: 前処理・学習評価・近接性ベースライン・結果可視化スクリプト
- `data/`: 実験データ格納用ディレクトリ

## 実行方法（シミュレーションデータによる一連の検証）
```bash
pip install -r requirements.txt
python ml/train_evaluate.py
python ml/proximity_baseline.py
python ml/plot_results.py
