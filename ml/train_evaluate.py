import numpy as np
from sklearn.naive_bayes import GaussianNB


def main():
    # 動作確認用のダミーデータ（受信機2台分のRSSIを想定）
    X_train = np.array([[-60, -75], [-62, -74], [-80, -55], [-79, -57]])
    y_train = np.array(["Grid_1_1", "Grid_1_1", "Grid_1_2", "Grid_1_2"])

    model = GaussianNB()
    model.fit(X_train, y_train)

    pred = model.predict([[-61, -76]])
    print("推定位置:", pred[0])


if __name__ == "__main__":
    main()